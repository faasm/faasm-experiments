#pragma once

#include <profiler/Profiler.h>

namespace runner {
class PolybenchProfiler : public Profiler
{
  public:
    explicit PolybenchProfiler(std::string funcName);

    void runNative() override;
};
}
