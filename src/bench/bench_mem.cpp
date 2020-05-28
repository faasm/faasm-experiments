#include <profiler/function.h>

#include <wasm/WasmModule.h>

#define USER "demo"

int main(int argc, char *argv[]) {
    util::initLogging();
    const std::shared_ptr<spdlog::logger> logger = util::getLogger();

    if (argc < 4) {
        logger->error("Must provide mode, function and number of workers");
        return 1;
    }

    std::string mode(argv[1]);
    if (mode == "cold") {
        logger->info("Using Faasm cold starts");
        runner::setUseZygotes(false);
    } else if (mode == "warm") {
        logger->info("Using Faasm warm starts");
        runner::setUseZygotes(true);
    } else {
        logger->error("Unrecognised mode: {}", mode);
        exit(1);
    }

    // Get args
    std::string function(argv[2]);
    int nWorkers = std::stoi(argv[3]);

    // Pre-flight
    runner::benchmarkExecutor(USER, function);

    logger->info("Running benchmark on demo/{} with {} workers", function, nWorkers);

    // Spawn worker threads to run the task in parallel
    std::vector<std::thread> threads(nWorkers);
    for (int w = 0; w < nWorkers; w++) {
        logger->info("Running worker {}", w);
        threads.emplace_back(std::thread(runner::benchmarkExecutor, USER, function));
    }

    // Wait for things to finish
    for (auto &t : threads) {
        if (t.joinable()) {
            t.join();
        }
    }

    return 0;
}