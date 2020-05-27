#!/bin/bash

set -e

mkdir -p ${HOME}/faasm/bench
pushd ${HOME}/faasm/bench

# Prepare out of tree build
cmake -GNinja -DCMAKE_CXX_COMPILER=/usr/bin/clang++ -DCMAKE_C_COMPILER=/usr/bin/clang -DCMAKE_BUILD_TYPE=Release /usr/local/code/faasm-experiments

# Build benchmarks
cmake --build . --target emulator
cmake --build . --target codegen_func
cmake --build . --target codegen_shared_obj
cmake --build . --target bench_mem
cmake --build . --target bench_time
cmake --build . --target bench_tpt
cmake --build . --target thread_bench_mem
cmake --build . --target thread_bench_time
cmake --build . --target max_thread_experiment
cmake --build . --target max_mem_experiment
cmake --build . --target rlimit_experiment
cmake --build . --target poly_bench
cmake --build . --target python_bench
cmake --build . --target upload

# Run codegen for functions
./bin/codegen_func demo noop
./bin/codegen_func demo lock
./bin/codegen_func demo sleep_long
./bin/codegen_func demo sleep_short

popd

pushd /usr/local/code/faasm-experiments/third-party/faasm

# Build docker image
docker build -t faasm/noop -f docker/noop.dockerfile .

popd
