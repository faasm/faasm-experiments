cmake_minimum_required(VERSION 3.8.0)
project(faasm-experiments)

set(CMAKE_CXX_FLAGS "-Wall -Werror")
set(CMAKE_CXX_FLAGS_DEBUG "-g")
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

set(EXPERIMENTS_INCLUDE_DIR ${CMAKE_CURRENT_LIST_DIR}/include)

include_directories(
        ${EXPERIMENTS_INCLUDE_DIR}
        third-party/faasm/include
        ${CMAKE_CURRENT_BINARY_DIR}/third-party/faasm/src # Required for protobuf
)

add_subdirectory(third-party/faasm)

add_subdirectory(src/bench)
add_subdirectory(src/capacity)
add_subdirectory(src/omp)
add_subdirectory(src/profiler)
add_subdirectory(src/polybench)
add_subdirectory(src/python)
add_subdirectory(src/sgd)
add_subdirectory(src/state_tpt)

