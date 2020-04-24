include_directories(${EXPERIMENTS_INCLUDE_DIR}/profiler)

add_library(profiler ${EXPERIMENTS_INCLUDE_DIR}/profiler/Profiler.h Profiler.cpp)
target_link_libraries(profiler bench)
