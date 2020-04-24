#pragma once

#include <runner/Profiler.h>

namespace runner {
    class PythonProfiler : public Profiler {
    public:
        explicit PythonProfiler(std::string pythonFunc);

        void runNative() override;
    };
}