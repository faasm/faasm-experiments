# Include all Faasm tasks
from faasmcli.tasks import ns
from invoke import Collection

from . import (
    bench_capacity,
    bench_mem,
    bench_omp,
    bench_time,
    bench_tpt,
    data,
    dev,
    experiments,
    genomics,
    polybench,
    prk,
    tensorflow,
)

# Tasks from this repo
ns.add_collection(data)
ns.add_collection(dev)
ns.add_collection(experiments)
ns.add_collection(genomics)
ns.add_collection(polybench)
ns.add_collection(prk)
ns.add_collection(tensorflow)

# Group benchmarking tasks
bench_ns = Collection("bench")
bench_ns.add_task(bench_capacity.max_threads)
bench_ns.add_task(bench_time.bench_time, name="time")
bench_ns.add_task(bench_mem.bench_mem, name="mem")
bench_ns.add_task(bench_tpt.bench_tpt, name="tpt")
bench_ns.add_task(bench_mem.pid_mem, name="pid")
bench_ns.add_task(bench_mem.container_count)
bench_ns.add_task(bench_mem.faasm_count)
bench_ns.add_task(bench_mem.spawn_containers)
bench_ns.add_task(bench_mem.kill_containers)
bench_ns.add_task(bench_mem.kill_faasm)
bench_ns.add_task(bench_mem.plot_pid_mem)
bench_ns.add_task(bench_mem.plot_proc_mem)
bench_ns.add_task(bench_mem.print_docker_mem)
bench_ns.add_task(bench_omp.multi_pi)
ns.add_collection(bench_ns)

# Can only generate matrix data with things installed
try:
    import pyfaasm

    from . import matrix_data

    ns.add_collection(matrix_data)
except:
    pass
