#include <fstream>
#include <profiler/function.h>
#include <unistd.h>
#include <util/config.h>
#include <util/locks.h>
#include <util/timing.h>
#include <wasm/WasmModule.h>

#define USER "demo"
#define FUNCTION "noop"

static std::mutex latFileMx;
static std::mutex tptFileMx;

static std::string tptLogFile;
static std::string latLogFile;
static std::string durationLogFile;

bool forceNoop = true;
static util::TimePoint startTimer;

void _execFunction(int requestCount)
{
    if (requestCount > 0) {
        std::ofstream tptFile;
        tptFile.open(tptLogFile.c_str(), std::ios_base::app);
        // Log to throughput file
        long elapsed = util::getTimeDiffMillis(startTimer);

        {
            // Write to tpt file with lock
            util::UniqueLock lock(tptFileMx);
            tptFile << elapsed << " REQUEST " << requestCount << std::endl;
            tptFile.flush();
        }

        tptFile.close();
    }

    const util::TimePoint& start = util::startTimer();
    runner::benchmarkExecutor(USER, FUNCTION);
    double elapsedMillis = util::getTimeDiffMillis(start);

    if (requestCount > 0) {
        std::ofstream latFile;
        latFile.open(latLogFile.c_str(), std::ios_base::app);

        {
            // Write to latency file with lock
            util::UniqueLock lock(latFileMx);
            latFile << elapsedMillis << " LATENCY" << std::endl;
            latFile.flush();
        }

        latFile.close();
    }
}

int main(int argc, char* argv[])
{
    util::initLogging();
    const std::shared_ptr<spdlog::logger> logger = util::getLogger();

    if (argc < 4) {
        logger->error(
          "Must provide mode, request delay (ms) and duration (ms)");
        return 1;
    }

    // Pre-flight
    _execFunction(-1);

    std::string mode(argv[1]);
    bool isWarm;
    if (mode == "cold") {
        logger->info("Using Faasm cold starts");
        isWarm = false;
        runner::setUseZygotes(false);
    } else if (mode == "warm") {
        logger->info("Using Faasm zygotes");
        isWarm = true;
        runner::setUseZygotes(true);
    } else {
        logger->error("Unrecognised mode: {}", mode);
        exit(1);
    }

    // Set up
    runner::setTrueNoops(forceNoop);

    // Get args
    int requestDelay = std::stoi(argv[2]);
    int duration = std::stoi(argv[3]);

    logger->info("Faasm throughput bench with delay={}ms and duration={}ms",
                 requestDelay,
                 duration);

    std::string systemName;
    if (isWarm) {
        systemName = "faasm-warm";
    } else {
        systemName = "faasm-cold";
    }

    tptLogFile = "/tmp/" + systemName + "_tpt.log";
    latLogFile = "/tmp/" + systemName + "_lat.log";
    durationLogFile = "/tmp/" + systemName + "_duration.log";

    // Set up files
    truncate(latLogFile.c_str(), 0);
    truncate(tptLogFile.c_str(), 0);
    truncate(durationLogFile.c_str(), 0);

    std::ofstream tptFile;
    tptFile.open(tptLogFile.c_str(), std::ios_base::app);

    startTimer = util::startTimer();
    double elapsed = 0;
    int requestCount = 1;

    std::vector<std::thread> threads;

    while (elapsed < duration) {
        // Spawn execution in background
        threads.emplace_back(_execFunction, requestCount);
        requestCount++;

        // Sleep
        usleep(requestDelay);

        // Update elapsed
        elapsed = util::getTimeDiffMillis(startTimer);
    }

    tptFile.close();

    // Wait for any stragglers
    for (auto& t : threads) {
        if (t.joinable()) {
            t.join();
        }
    }

    // Write final duration
    double finalDuration = util::getTimeDiffMillis(startTimer);
    std::ofstream durationFile;
    durationFile.open(durationLogFile.c_str(), std::ios_base::app);
    durationFile << finalDuration << " DURATION " << std::endl;
    durationFile.close();

    std::cout << "Finished after " << finalDuration << "ms and " << requestCount
              << " requests." << std::endl;

    return 0;
}