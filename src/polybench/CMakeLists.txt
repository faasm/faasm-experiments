
add_executable(poly_bench PolybenchProfiler.h PolybenchProfiler.cpp poly_bench.cpp)
target_link_libraries(poly_bench profiler)
