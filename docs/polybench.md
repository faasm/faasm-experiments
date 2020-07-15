# Polybench/C

To test pure computation against the native environment we can use the
[Polybench/C benchmark](http://web.cse.ohio-state.edu/~pouchet.2/software/polybench/).

The code is checked into this repository and can be compiled to wasm and
uploaded as follows.

```
# Compile to wasm and run codegen
inv compile.user polybench --clean
inv codegen.user polybench
```

We can compile the same functions natively as follows:

```
./bin/build_polybench_native.sh
```

The `poly_bench` target will then run a comparison of the wasm and native
versions. This must be invoked with your desired number of iterations for native
and wasm respectively, e.g.

```
~/faasm/bench/bin/poly_bench all 5 5
```

Results are currently output to `/tmp/polybench.csv`.

_Note - we had to leave out the BLAS benchmarks as BLAS is not supported_.

## Profiling Polybench/C

To profile the native version of the code, you need to run
`./bin/build_polybench_native.sh Debug`

Then you can directly run the native binary:

```
perf record -k 1 ./func/build_native/polybench/poly_ludcmp
mv perf.data perf.data.native
perf report -i perf.data.native
```

Provided you have set up the wasm profiling set-up as described in the profiling
docs, you can do something similar:

```
perf record -k 1 poly_bench poly_ludcmp 0 5
perf inject -i perf.data -j -o perf.data.wasm
perf report -i perf.data.wasm
```

Note that for wasm code the output of the perf reports will be function names
like `functionDef123`.  To generate the mapping of these names to the actual
functions you can run:

```
inv disas.symbols <user> <func>

# For example
inv disas.symbols polybench 3mm
```
