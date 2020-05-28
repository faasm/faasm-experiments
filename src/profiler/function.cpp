#include "function.h"

#include <string>
#include <wasm/WasmModule.h>
#include <system/NetworkNamespace.h>
#include <system/CGroup.h>
#include <module_cache/WasmModuleCache.h>

#include <util/config.h>
#include <util/timing.h>
#include <util/func.h>


namespace runner {
    static bool useZygotes = false;
    static bool trueNoop = false;

    void setTrueNoops(bool value) {
        util::getLogger()->info("Setting true noops: {}", value);
        trueNoop = value;
    }

    void setUseZygotes(bool value) {
        util::getLogger()->info("Setting use zygotes: {}", value);
        useZygotes = value;
    }

    /**
     * Designed to replicate what the real system does when executing functions
     */
    void benchmarkExecutor(const std::string &user, const std::string &func) {
        PROF_START(logConfInit)
        const std::shared_ptr<spdlog::logger> &logger = util::getLogger();
        util::SystemConfig &conf = util::getSystemConfig();
        PROF_END(logConfInit)

        // Set up network namespace
        if (conf.netNsMode == "on") {
            PROF_START(netnsAdd)
            std::string netnsName = std::string(BASE_NETNS_NAME) + "1";
            isolation::NetworkNamespace ns(netnsName);
            ns.addCurrentThread();
            PROF_END(netnsAdd)
        }

        if (conf.cgroupMode == "on") {
            // Add this thread to the cgroup
            isolation::CGroup cgroup(BASE_CGROUP_NAME);
            cgroup.addCurrentThread();
        }

        // Allow python function.
        message::Message m;
        if(user == "python") {
            m = util::messageFactory(PYTHON_USER, PYTHON_FUNC);
            m.set_pythonuser(user);
            m.set_pythonfunction(func);
            m.set_ispython(true);
        } else {
            m = util::messageFactory(user, func);
        }

        if(useZygotes) {
            logger->info("Executing function {}/{} from zygote", user, func);
            // This implicitly creates the zygote if needed
            PROF_START(zygoteCacheLookup)
            module_cache::WasmModuleCache &registry = module_cache::getWasmModuleCache();
            wasm::WAVMWasmModule &snapshot = registry.getCachedModule(m);
            PROF_END(zygoteCacheLookup)

            // Copy constructor does the zygote restore
            wasm::WAVMWasmModule module = snapshot;
            module.execute(m, trueNoop);
        } else {
            logger->info("Executing function {}/{} with cold start", user, func);

            PROF_START(coldStart)
            wasm::WAVMWasmModule module;
            module.bindToFunction(m);
            PROF_END(coldStart)

            PROF_START(moduleExecuteCold)
            module.execute(m, trueNoop);
            PROF_END(moduleExecuteCold)

            module.getFileSystem().tearDown();
        }
    }
}