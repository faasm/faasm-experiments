#pragma once

#include <runner/Profiler.h>

namespace runner {
    class PolybenchProfiler : public Profiler {
    public:
        explicit PolybenchProfiler(std::string funcName);

        void runNative() override;
    };
}
