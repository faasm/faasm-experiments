#pragma once

#include <profiler/Profiler.h>

namespace runner {
class GenericFunctionProfiler : public Profiler
{
  public:
    GenericFunctionProfiler(std::string userIn, std::string funcName);

    void runNative() override;
};
}
