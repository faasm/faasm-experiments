cmake_minimum_required(VERSION 3.8.0)
project(faasm-experiments)

set(CMAKE_CXX_FLAGS "-Wall -Werror")
set(CMAKE_CXX_FLAGS_DEBUG "-g")
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

include_directories(
        third-party/faasm/include
        ${CMAKE_CURRENT_BINARY_DIR}/third-party/faasm/src # Required for protobuf
)

add_subdirectory(third-party/faasm)

add_subdirectory(src/bench)
add_subdirectory(src/capacity)
add_subdirectory(src/omp)
add_subdirectory(src/polybench)
add_subdirectory(src/python)
