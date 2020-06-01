set(runner_libs
        faaslet_lib
        wasm
        wavmmodule
        util
        module_cache
        system
        )

add_executable(bench_loops bench_loops.cpp)
target_link_libraries(bench_loops ${runner_libs})
