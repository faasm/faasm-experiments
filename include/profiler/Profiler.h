#pragma once

#include <string>
#include <proto/faasm.pb.h>

namespace runner {

    class Profiler {
    public:
        Profiler(std::string user, std::string funcName, std::string inputData);

        void preflightWasm();

        void runBenchmark(int nNativeIterations, int nWasmIterations, std::ofstream &profOut);

        void runWasm(int nIterations, std::ofstream &profOut);

        virtual void runNative() = 0;

    protected:
        const std::string user;
        const std::string funcName;
        const std::string inputData;
        std::string pythonUser;
        std::string pythonFunction;
        std::string outputName;

        void runWasmWithWavm(message::Message &call, int nIterations, std::ofstream &profOut);

        void runWasmWithWamr(message::Message &call, int nIterations, std::ofstream &profOut);
    };
}