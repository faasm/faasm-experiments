find_package(PythonLibs)

include_directories(${PYTHON_INCLUDE_DIRS})
add_executable(python_bench PythonProfiler.cpp python_bench.cpp)
target_link_libraries(python_bench bench ${PYTHON_LIBRARIES})
