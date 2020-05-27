include_directories(${EXPERIMENTS_INCLUDE_DIR}/profiler)

add_library(profiler
        ${EXPERIMENTS_INCLUDE_DIR}/profiler/Profiler.h
        ${EXPERIMENTS_INCLUDE_DIR}/profiler/function.h
        function.cpp
        Profiler.cpp
        )

# Faasm internal libs needed for benchmarking/ profiling
set(PROFILER_LIBS
        worker_lib
        wasm
        wavmmodule
        util
        module_cache
        system
        emulator
        faasm
        )

target_link_libraries(profiler ${PROFILER_LIBS})
