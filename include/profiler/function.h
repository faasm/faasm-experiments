#pragma once

#include <string>

namespace runner {
    void setTrueNoops(bool value);

    void setUseZygotes(bool value);

    void benchmarkExecutor(const std::string &user, const std::string &func);
}