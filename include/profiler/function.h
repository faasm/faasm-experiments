#pragma once

#include <string>

namespace runner {
void setTrueNoops(bool value);

void setUseZygotes(bool value);

void preflightFunction(const std::string& user, const std::string& func);

void benchmarkExecutor(const std::string& user, const std::string& func);
}