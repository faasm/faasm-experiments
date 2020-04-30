# OpenMP benchmarks

## Local Native V Wasm

Our experiment program relies heavily on the CPP standard Mersenne Twister 19937 pseudo-random number generator which by its high arithmetic nature shows big disrepancies between the different maths libc implementations used in Faasm (`glibc` for native and `musl` for Wasm). To eliminate this phenomenon from the experiment, the native code is ran in a container with a distribution that has a native musl toolchain (here Alpine).

The dockerfile for the container as well as the native program and benchmark code can be found [in the musl-container directory](musl-container). And is then invoke once via the [native & Wasm benchmarker](bench_omp.cpp), watch our to change the docker invokation command in there to tune to your container.
