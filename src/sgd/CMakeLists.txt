add_executable(reuters reuters.cpp)

# This is a bit of a hack to force linking with the locally built versions of faasm and emulator
find_library(FAASM_LIB NAMES faasm HINTS ${CMAKE_LIBRARY_OUTPUT_DIRECTORY} NO_DEFAULT_PATH)
find_library(EMULATOR_LIB NAMES emulator HINTS ${CMAKE_LIBRARY_OUTPUT_DIRECTORY} NO_DEFAULT_PATH)

target_link_libraries(reuters
        ${EMULATOR_LIB}
        ${FAASM_LIB}
        profiler
        )
