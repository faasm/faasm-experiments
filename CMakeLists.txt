cmake_minimum_required(VERSION 3.8.0)
project(faasm-experiments)

set(CMAKE_CXX_FLAGS "-Wall -Werror")
set(CMAKE_CXX_FLAGS_DEBUG "-g")
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/lib)
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/lib)
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin)

set(FAASM_ROOT_DIR ${CMAKE_CURRENT_LIST_DIR}/third-party/faasm)
set(WAMR_ROOT_DIR ${CMAKE_CURRENT_LIST_DIR}/third-party/faasm/third-party/wamr)

# Annoyingly we have to add the WAMR config here
set(WAMR_BUILD_PLATFORM linux)
set(WAMR_BUILD_INTERP 0)
set(WAMR_BUILD_JIT 0)
set(WAMR_BUILD_AOT 1)
set(WAMR_BUILD_LIBC_WASI 1)
set(WAMR_BUILD_LIB_PTHREAD 1)

# Add Faasm self-tracing
set(FAASM_SELF_TRACING ON)
add_definitions(-DTRACE_ALL=1)

# Includes
set(EXPERIMENTS_INCLUDE_DIR ${CMAKE_CURRENT_LIST_DIR}/include)
include_directories(
        ${EXPERIMENTS_INCLUDE_DIR}
        third-party/faasm/include
        third-party/faasm/libs/cpp
        ${CMAKE_CURRENT_BINARY_DIR}/third-party/faasm/src # Required for protobuf
)

# Faasm code
add_subdirectory(third-party/faasm)

# Targets from this repo
add_subdirectory(src/bench)
add_subdirectory(src/capacity)
add_subdirectory(src/omp)
add_subdirectory(src/profiler)
add_subdirectory(src/polybench)
add_subdirectory(src/python)
add_subdirectory(src/sgd)
add_subdirectory(src/state_tpt)

