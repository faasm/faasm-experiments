
add_executable(bench_mem bench_mem.cpp)
target_link_libraries(bench_mem profiler)

add_executable(bench_func GenericFunctionProfiler.h GenericFunctionProfiler.cpp bench_func.cpp)
target_link_libraries(bench_func profiler)

add_executable(bench_time bench_time.cpp)
target_link_libraries(bench_time profiler)

add_executable(bench_tpt bench_tpt.cpp)
target_link_libraries(bench_tpt profiler)

add_executable(thread_bench_mem thread_bench_mem.cpp)
target_link_libraries(thread_bench_mem profiler)

add_executable(thread_bench_time thread_bench_time.cpp)
target_link_libraries(thread_bench_time profiler)
