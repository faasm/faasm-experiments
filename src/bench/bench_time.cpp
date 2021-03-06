#include <profiler/function.h>
#include <util/config.h>
#include <util/timing.h>
#include <wasm/WasmModule.h>

#define USER "demo"
// #define USER "python"

#define FUNCTION "noop"

static bool forceNoops = true;

int main(int argc, char* argv[])
{
    util::initLogging();
    const std::shared_ptr<spdlog::logger> logger = util::getLogger();

    if (argc < 3) {
        logger->error("Must provide mode and number iterations");
        return 1;
    }

    std::string mode(argv[1]);
    if (mode == "cold") {
        logger->info("Using Faasm cold starts");
        runner::setUseZygotes(false);
    } else if (mode == "warm") {
        logger->info("Using Faasm zygotes");
        runner::setUseZygotes(true);
    } else {
        logger->error("Unrecognised mode: {}", mode);
        exit(1);
    }

    // Config
    runner::setTrueNoops(forceNoops);

    // Pre-flight
    runner::benchmarkExecutor(USER, FUNCTION);

    // Get args
    int nIterations = std::stoi(argv[2]);

    logger->info("Running Faasm benchmark with {} iterations", nIterations);

    // For each iteration we want to spawn a thread and execute the function
    // (to introduce the overhead we'd see in the real application)
    for (int i = 0; i < nIterations; i++) {
        PROF_START(benchmarkExecRoundTrip)
        logger->info("Running iteration {}", i);

        std::thread t(runner::benchmarkExecutor, USER, FUNCTION);
        t.join();

        PROF_END(benchmarkExecRoundTrip)
    }

    return 0;
}