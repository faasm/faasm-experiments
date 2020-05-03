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
def multi_cr(ctx, number_times=6):
    backoff = lambda x: min(max(1, x // 2),  number_times)

    output_file = "/usr/local/code/faasm/wasm/omp/multi_cr/benchWasm.csv"
    # * 2 in this experiment since starting from `- iterations` instead of 0
    sizes = {
        "Tiny": 200000,
        "Small": 20000000,
        "Big": 20000000,
    }

    modes = {
        "wasm": -1,
    }
    threads = [1] + list(range(2, 25, 2))

    r = redis.Redis(host="koala10")
    times_key = "multi_pi_times"
    r.delete(times_key)
    num_times = 0
    for mode in modes.values():
        for iter_size in sizes.values():
            for num_threads in threads:
                for _ in range(backoff(num_threads)):
                    cmd = f"{num_threads} {iter_size} {mode}"
                    print(f"running omp/multi_cr-- {cmd}")
                    invoke_impl("omp", "multi_cr", knative=True, cmdline=cmd)
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
