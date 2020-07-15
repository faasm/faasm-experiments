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
        wamrmodule
        wavmmodule
        util
        module_cache
        system
        emulator
        )

target_link_libraries(profiler ${PROFILER_LIBS})

# Have to include WAMR stuff here
set(BUILD_UNTRUST_PART 1)
include(${WAMR_ROOT_DIR}/build-scripts/runtime_lib.cmake)

