cmake_minimum_required(VERSION 3.8.0)
project(faasm-experiment-func)

set(CMAKE_CXX_STANDARD 17)

if (FAASM_BUILD_TYPE STREQUAL "wasm")
    SET(CMAKE_EXE_LINKER_FLAGS "${FAASM_EXE_LINKER_FLAGS} \
        -Xlinker --export=_faasm_zygote \
        -Xlinker --export=__wasm_call_ctors \
        -Wl,-z,stack-size=4194304 -Wl, \
    ")

    SET(CMAKE_EXECUTABLE_SUFFIX ".wasm")
endif ()

add_subdirectory(tf)

