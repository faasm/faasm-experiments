import redis

from invoke import task
from faasmcli.util.call import invoke_imp

@task
def multi_pi(ctx, number_times=6):
    backoff = lambda x: min(max(1, x // 2),  number_times)

    output_file = "/usr/local/code/faasm/wasm/omp/multi_pi/bench.csv"
    # * 2 in this experiment since starting from `- iterations` instead of 0
    sizes = {
        "Tiny": 200000,
        # "Small": 10000000,
        "Big": 200000000,
        "Huge": 10000000000,
    }

    modes = {
        "Local": 0,
        "Distributed": -1,
    }
    threads = list(range(2, 41, 2))

    r = redis.Redis(host="koala10")
    times_key = "multi_pi_times"
    r.delete(times_key)
    num_times = 0
    for mode in modes.values():
        for iter_size in sizes.values():
            for num_threads in threads:
                for _ in range(backoff(num_threads)):
                    cmd = f"{num_threads} {iter_size} {mode}"
                    print(f"running omp/multi_pi -- {cmd}")
                    invoke_impl("omp", "multi_pi", knative=True, cmdline=cmd)
                    # allow for async flag in invoke too
                    while r.llen(times_key) == num_times:
                        print("Waiting for function to finish")
                        time.sleep(1.5)
                    num_times += 1

    times = list(map(int, r.lrange(times_key, 0, num_times)))
    assert(len(times) == num_times)
    idx = 0

    with open(output_file, "w") as csv:
        csv.write("iterations,numThreads,type,milliseconds\n")
        for mode in modes.keys():
            for iter_name in sizes.keys():
                for num_threads in threads:
                    for _ in range(backoff(num_threads)):
                        result = f"{iter_name},{num_threads},{mode},{times[idx]}\n"
                        idx += 1
                        csv.write(result)

@task
def multi_cr(ctx, debug=False, num_times=200, num_threads=1):
    output_file = f"/usr/local/code/faasm/wasm/omp/multi_cr/bench_all.csv"
    modes = {
        "native": 0,
        "wasm": -1,
    }

    func = "multi_cr"

    threads = [1] + list(range(2, 25, 2))

    r = redis.Redis(host="localhost")
    rkey = f"{func}_fork_times"
    rkey1 = f"{func}_local_fork_times"
    r.delete(rkey)
    # rindex = 0

    with open(output_file, "w") as csv:
        csv.write("numThreads,type,microseconds\n")
        for num_threads in threads:
            cmd = f"{num_threads} {num_times} 0"
            print(f"NATIVE: running omp/multi_cr-- {cmd}")
            # t_native = run(["/usr/local/code/faasm/ninja-build/bin/multi_cr", f"{num_threads}", "1", "0"], stdout=subprocess.PIPE).stdout.decode('utf-8')
            t_native = run(["/usr/local/code/faasm/ninja-build/bin/multi_cr", f"{num_threads}", f"{num_times}", "0"], stdout=subprocess.PIPE).stdout.decode('utf-8')
            csv.write(t_native)

            # WasmMP
            cmd = f"{num_threads} {num_times} 0"
            print(f"WASM running omp/multi_cr-- {cmd}")
            invoke_impl("omp", "multi_cr_local", knative=True, cmdline=cmd)
            if r.llen(rkey1) != num_times:
                print("Failed to run wasm")
                exit(1)
            t_wasm = list(map(int, r.lrange(rkey1, 0, num_times)))
            for t in t_wasm:
                wasm_line = f"{num_threads},WasmMP,{t}\n"
                csv.write(wasm_line)
            r.flushall()

            # faasmp
            cmd = f"{num_threads} {num_times} -1"
            print(f"FAASM running omp/multi_cr-- {cmd}")
            invoke_impl("omp", "multi_cr", knative=True, cmdline=cmd)
            if r.llen(rkey) != num_times:
                print("Failed to run faasm")
                exit(1)
            t_wasm = list(map(int, r.lrange(rkey, 0, num_times)))
            r.delete(rkey)
            for t in t_wasm:
                wasm_line = f"{num_threads},FaasMP,{t}\n"
                csv.write(wasm_line)

            r.flushall()


