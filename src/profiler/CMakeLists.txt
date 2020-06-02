include_directories(${EXPERIMENTS_INCLUDE_DIR}/profiler)

add_library(profiler
        ${EXPERIMENTS_INCLUDE_DIR}/profiler/Profiler.h
        ${EXPERIMENTS_INCLUDE_DIR}/profiler/function.h
        function.cpp
        Profiler.cpp
        )

# Faasm internal libs needed for benchmarking/ profiling
# NOTE - order of linking faasm here is important, should be first
set(PROFILER_LIBS
        faasm
        faaslet_lib
        wasm
        wavmmodule
        util
        module_cache
        system
        emulator
        )

target_link_libraries(profiler ${PROFILER_LIBS})
