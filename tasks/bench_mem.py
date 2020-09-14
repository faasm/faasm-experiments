from datetime import datetime
from decimal import Decimal
from multiprocessing import Process
from os import makedirs, remove
from os.path import exists, join
from subprocess import call, check_output
from time import sleep

from faasmcli.util.env import (
    BENCHMARK_BUILD,
    PROJ_ROOT,
    RESULT_DIR,
    set_benchmark_env,
)
from faasmcli.util.memory import (
    get_total_memory_for_pid,
    get_total_memory_for_pids,
)
from faasmcli.util.process import (
    count_threads_for_name,
    get_all_pids_for_name,
    get_docker_parent_pids,
    get_pid_for_name,
)
from invoke import task

from tasks.util.env import EXPERIMENTS_ROOT

OUTPUT_FILE = join(RESULT_DIR, "runtime-bench-mem.csv")
FAASM_LOCK_DIR = "/usr/local/faasm/runtime_root/tmp"
FAASM_LOCK_FILE = join(FAASM_LOCK_DIR, "demo.lock")

FAASM_BATCH_SIZE = 200

# NOTE - this is the calculation working out how long to let Faasm benchmark run before measuring
# memory overhead. We need to let it warm up and run for about 50/75% of the time
FAASM_SLEEP_FUNCTION_DURATION_SECS = 25.0


def _exec_cmd(cmd_str):
    print(cmd_str)
    ret_code = call(cmd_str, shell=True, cwd=PROJ_ROOT)

    if ret_code != 0:
        raise RuntimeError("Command failed: {} ({})".format(cmd_str, ret_code))


@task
def spawn_containers(ctx, n_containers, network="host"):
    """
    Memory benchmark - spawn a number of containers
    """
    _start_docker_mem(int(n_containers), network)


@task
def kill_containers(ctx):
    """
    Memory benchmark - kill running containers
    """
    _stop_docker_mem()


@task
def container_count(ctx):
    """
    Memory benchmark - get container count
    """
    res = check_output("docker ps -q", shell=True).decode("utf-8")
    ids = res.split("\n")
    ids = [i for i in ids if i]

    print("Docker containers: {}".format(len(ids)))


@task
def kill_faasm(ctx):
    """
    Memory benchmark - kill Faasm instances
    """
    remove(FAASM_LOCK_FILE)


@task
def faasm_count(ctx):
    """
    Memory benchmark - count Faasm instances
    """
    threads = count_threads_for_name("bench_mem", exact=True, exclude_main=True)
    print("Faasm threads = {}".format(threads))


@task
def bench_mem(ctx, runtime=None):
    """
    Run memory benchmark
    """
    if not exists(RESULT_DIR):
        makedirs(RESULT_DIR)

    csv_out = open(OUTPUT_FILE, "w")
    csv_out.write("Runtime,Measure,Value,Workers,ValuePerWorker\n")

    for repeat in range(0, 1):

        def do_faasm_run(faasm_name, this_workers, this_delays):
            cmd = " ".join(
                [
                    join(BENCHMARK_BUILD, "bin", "bench_mem"),
                    "warm" if faasm_name == "faasm-warm" else "cold",
                    "sleep_short",
                ]
            )

            for worker_chunks, this_delay in zip(this_workers, this_delays):
                _run_sleep_bench(
                    faasm_name,
                    worker_chunks,
                    cmd,
                    this_delay,
                    "bench_mem",
                    csv_out,
                )

        # Note: we need to run the workers over multiple processes to avoid memory allocation issues
        # There MUST be the same number of processes, all with at least one function in
        faasm_worker_chunks = [
            [500, 500, 500, 500],
            [750, 750, 750, 750],
            [1000, 1000, 1000, 1000],
        ]

        # As we get more threads, need to measure later
        faasm_delays = [
            FAASM_SLEEP_FUNCTION_DURATION_SECS * 0.5,
            FAASM_SLEEP_FUNCTION_DURATION_SECS * 0.6,
            FAASM_SLEEP_FUNCTION_DURATION_SECS * 0.65,
        ]

        if runtime == "faasm-warm" or runtime is None:
            do_faasm_run("faasm-warm", faasm_worker_chunks, faasm_delays)

        if runtime == "faasm-cold" or runtime is None:
            do_faasm_run("faasm-cold", faasm_worker_chunks, faasm_delays)

        if runtime == "docker" or runtime is None:
            for n_workers in [100, 200, 300]:
                _run_docker_bench(
                    n_workers,
                    csv_out,
                )

        if runtime is None:
            _run_sleep_bench(
                "thread",
                faasm_worker_chunks,
                join(BENCHMARK_BUILD, "bin", "thread_bench_mem"),
                5,
                "thread_bench_mem",
                csv_out,
            )

    print("\nDONE - output written to {}".format(OUTPUT_FILE))


def _run_sleep_bench(
    bench_name, worker_chunks, cmd, measure_delay, process_name, csv_out
):
    total_n_workers = sum(worker_chunks)
    print(
        "BENCH: {} - {} workers (chunks: {})".format(
            bench_name, total_n_workers, worker_chunks
        )
    )

    start_time = datetime.utcnow()

    # Set up environment
    set_benchmark_env()

    sleep_procs = []
    for idx, n_workers in enumerate(worker_chunks):
        # Build the command
        cmd_str = [
            cmd,
            str(n_workers),
        ]
        cmd_str = " ".join(cmd_str)
        print("RUNNING: " + cmd_str)

        # Launch subprocess
        sleep_proc = Process(target=_exec_cmd, args=[cmd_str])
        sleep_proc.start()
        sleep_procs.append(sleep_proc)

        stagger_time = 1.5
        print("Staggering after {} by {}".format(idx, stagger_time))
        sleep(1)

    # Wait for everything to get started
    print("Waiting {}s before measuring".format(measure_delay))
    sleep(measure_delay)

    pids = get_all_pids_for_name(process_name)
    if len(pids) != len(sleep_procs):
        print(
            "ERROR: got {} pids but expected {}".format(
                len(pids), len(sleep_procs)
            )
        )
        exit(1)

    mem_outputs = []
    for pid in pids:
        print("Measuring memory of process {}".format(pid))
        mem_outputs.append(get_total_memory_for_pid(pid))

    for idx, label in enumerate(mem_outputs[0].get_labels()):
        total_value = sum([m.get_data()[idx] for m in mem_outputs])

        csv_out.write(
            "{},{},{},{},{}\n".format(
                bench_name,
                label,
                total_value,
                total_n_workers,
                Decimal(total_value) / total_n_workers,
            )
        )

    csv_out.flush()

    # Rejoin the background processes
    for s in sleep_procs:
        s.join()

    time_taken = datetime.utcnow() - start_time
    print("BENCH FINISHED in {}s".format(time_taken.seconds))


def _run_function_in_batches(n_total, batch_size, func):
    batch_remainder = n_total % batch_size
    n_batches = n_total // batch_size + (batch_remainder > 0)

    for b in range(n_batches):
        if (b == n_batches - 1) and (batch_remainder > 0):
            this_batch_size = batch_remainder
        else:
            this_batch_size = batch_size

        func(this_batch_size)


def _start_docker_mem(n_workers, network):
    def _do_docker_mem(n):
        start_cmd = "./bin/docker_mem_start.sh {} {}".format(network, n)
        print(
            "Kicking off Docker batch size {} on network {}".format(n, network)
        )
        start_ret_code = call(start_cmd, shell=True, cwd=EXPERIMENTS_ROOT)
        if start_ret_code != 0:
            raise RuntimeError("Start Docker benchmark failed")

    _run_function_in_batches(n_workers, 50, _do_docker_mem)


def _run_docker_bench(n_workers, csv_out):
    _start_docker_mem(n_workers, "host")

    # Get total mem and write
    pids = get_docker_parent_pids()
    mem_total = get_total_memory_for_pids(pids)

    for label, value in zip(mem_total.get_labels(), mem_total.get_data()):
        csv_out.write(
            "{},{},{},{},{}\n".format(
                "docker",
                label,
                value,
                n_workers,
                Decimal(value) / n_workers,
            )
        )

    csv_out.flush()

    _stop_docker_mem()


def _stop_docker_mem():
    end_cmd = "./bin/docker_mem_end.sh"
    end_ret_code = call(end_cmd, shell=True, cwd=EXPERIMENTS_ROOT)
    if end_ret_code != 0:
        raise RuntimeError("Ending Docker benchmark failed")


@task
def pid_mem(ctx, pid):
    """
    Show the memory usage for the given PID
    """
    pid = int(pid)
    _print_pid_mem(pid)


@task
def plot_pid_mem(ctx, pid):
    """
    Plot a PID's memory usage
    """
    pid = int(pid)
    _plot_pid_mem(pid)


@task
def proc_mem(ctx, proc_name):
    """
    Show the memory usage for the given process name
    """
    pid = get_pid_for_name(proc_name)
    _print_pid_mem(pid)


@task
def plot_proc_mem(ctx, proc_name):
    """
    Plot the memory usage for the given process name
    """
    pid = get_pid_for_name(proc_name)
    _plot_pid_mem(pid)


@task
def print_docker_mem(ctx):
    """
    Print the memory used by Docker
    """
    pids = get_docker_parent_pids()
    mem_total = get_total_memory_for_pids(pids)
    mem_total.print()


def _plot_pid_mem(pid):
    mem_total = get_total_memory_for_pid(pid)
    mem_total.plot()


def _print_pid_mem(pid):
    mem_total = get_total_memory_for_pid(pid)
    mem_total.print()
