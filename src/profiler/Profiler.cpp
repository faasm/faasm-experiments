#include "Profiler.h"

#include <proto/faasm.pb.h>
#include <util/config.h>
#include <util/func.h>
#include <util/logging.h>
#include <util/timing.h>

#include <fstream>
#include <module_cache/WasmModuleCache.h>
#include <wamr/WAMRWasmModule.h>

namespace runner {
Profiler::Profiler(const std::string userIn,
                   const std::string funcNameIn,
                   const std::string inputDataIn)
  : user(userIn)
  , funcName(funcNameIn)
  , inputData(inputDataIn)
{
    outputName = funcNameIn;
}

void Profiler::preflightWasm()
{
    message::Message call = util::messageFactory(this->user, this->funcName);

    module_cache::WasmModuleCache& moduleCache =
      module_cache::getWasmModuleCache();
    moduleCache.getCachedModule(call);
}

void Profiler::runWasm(int nIterations, std::ofstream& profOut)
{
    message::Message call = util::messageFactory(this->user, this->funcName);
    call.set_pythonuser(this->pythonUser);
    call.set_pythonfunction(this->pythonFunction);
    call.set_inputdata(this->inputData);

    runWasmWithWamr(call, nIterations, profOut);
    runWasmWithWavm(call, nIterations, profOut);
}

void Profiler::runWasmWithWavm(message::Message& call,
                               int nIterations,
                               std::ofstream& profOut)
{
    const std::shared_ptr<spdlog::logger>& logger = util::getLogger();

    // Initialise WAVM
    const util::TimePoint tpInit = util::startTimer();
    module_cache::WasmModuleCache& moduleCache =
      module_cache::getWasmModuleCache();
    wasm::WAVMWasmModule& cachedModule = moduleCache.getCachedModule(call);
    util::logEndTimer("WAVM initialisation", tpInit);

    logger->info("Running WAVM benchmark");
    for (int i = 0; i < nIterations; i++) {
        logger->info("WAVM - {} run {}", this->outputName, i);

        // Create module
        wasm::WAVMWasmModule module(cachedModule);

        // Time just the execution
        const util::TimePoint wasmTp = util::startTimer();

        module.execute(call);

        long wasmTime = util::getTimeDiffMicros(wasmTp);
        profOut << this->outputName << ",wavm," << wasmTime << std::endl;

        // Reset
        module = cachedModule;
    }
}

void Profiler::runWasmWithWamr(message::Message& call,
                               int nIterations,
                               std::ofstream& profOut)
{
    const std::shared_ptr<spdlog::logger>& logger = util::getLogger();

    wasm::initialiseWAMRGlobally();

    logger->info("Running WAMR benchmark");
    for (int i = 0; i < nIterations; i++) {
        logger->info("WAMR - {} run {}", this->outputName, i);

        wasm::WAMRWasmModule module;
        module.bindToFunction(call);

        // Exec the function
        const util::TimePoint wasmTp = util::startTimer();
        module.execute(call);

        long wasmTime = util::getTimeDiffMicros(wasmTp);
        profOut << this->outputName << ",wamr," << wasmTime << std::endl;
    }

    wasm::tearDownWAMRGlobally();
}

void Profiler::runBenchmark(int nNativeIterations,
                            int nWasmIterations,
                            std::ofstream& profOut)
{
    const std::shared_ptr<spdlog::logger>& logger = util::getLogger();
    logger->info("Benchmarking {} (input {}) ({}x native and {}x wasm)",
                 this->outputName,
                 inputData,
                 nNativeIterations,
                 nWasmIterations);

    logger->info("Running benchmark natively");
    for (int i = 0; i < nNativeIterations; i++) {
        const util::TimePoint wasmTp = util::startTimer();
        logger->info("NATIVE - {} run {}", this->outputName, i);

        runNative();
        long nativeTime = util::getTimeDiffMicros(wasmTp);
        profOut << this->outputName << ",native," << nativeTime << std::endl;
    }

    this->runWasm(nWasmIterations, profOut);

    logger->info("Finished benchmark - {}", this->outputName);
}
}
