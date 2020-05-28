#include "function.h"

#include <string>
#include <wasm/WasmModule.h>
#include <system/NetworkNamespace.h>
#include <system/CGroup.h>
#include <module_cache/WasmModuleCache.h>

#include <util/config.h>
#include <util/timing.h>


namespace runner {
    /**
     * Designed to replicate what the real system does when executing functions
     */
    void benchmarkExecutor(const std::string &user, const std::string &func, bool useZygote) {
        const std::shared_ptr<spdlog::logger> &logger = util::getLogger();

        util::SystemConfig &conf = util::getSystemConfig();

        // Set up network namespace
        if (conf.netNsMode == "on") {
            PROF_START(netnsAdd)
            std::string netnsName = std::string(BASE_NETNS_NAME) + "1";
            isolation::NetworkNamespace ns(netnsName);
            ns.addCurrentThread();
            PROF_END(netnsAdd)
        }

        if (conf.cgroupMode == "on") {
            PROF_START(cgroupAdd)
            // Add this thread to the cgroup
            isolation::CGroup cgroup(BASE_CGROUP_NAME);
            cgroup.addCurrentThread();
            PROF_END(cgroupAdd)
        }

        // Set up function call
        message::Message m;
        m.set_user(user);
        m.set_function(func);

        if(useZygote) {
            logger->info("Executing function {}/{} from zygote", user, func);
            // This implicitly creates the module if needed
            PROF_START(zygoteCacheLookup)
            module_cache::WasmModuleCache &registry = module_cache::getWasmModuleCache();
            wasm::WAVMWasmModule &snapshot = registry.getCachedModule(m);
            PROF_END(zygoteCacheLookup)

            // Copy constructor does the zygote restore
            PROF_START(zygoteRestore)
            wasm::WAVMWasmModule module = snapshot;
            PROF_END(zygoteCacheLookup)

            PROF_START(moduleExecuteZygote)
            module.execute(m);
            PROF_END(moduleExecuteZygote)
        } else {
            logger->info("Executing function {}/{} with cold start", user, func);

            PROF_START(coldStart)
            wasm::WAVMWasmModule module;
            module.bindToFunction(m);
            PROF_END(coldStart)

            PROF_START(moduleExecuteCold)
            module.execute(m);
            PROF_END(moduleExecuteCold)
        }
    }
}