# Python Benchmarks

To benchmark CPython execution we use the [Python Performance Benchmark
Suite](https://github.com/python/pyperformance).

All python code runs in the same function which can be set up according to the
`local_dev.md` docs in this repo. In short this is:

```bash
inv python.codegen
inv codegen.local
inv upload.user python --py --local-copy
```

Before running, you can check both the native and wasm python versions with:

```bash
~/faasm/bench/bin/python_bench bench_version 1 1
```

The set of benchmarks can be run with the `python_bench` target, e.g.:

```bash
~/faasm/bench/bin/python_bench all 5 5
```

Output is written to `/tmp/pybench.csv`.

Each benchmark requires porting the required dependencies, so some were
unfeasible and other were too much work:

- `chameleon` - too many deps
- `django_template` - pulls in too many dependencies
- `hg_startup` - runs a shell command
- `html5lib` - dependencies (might be fine)
- `pathlib` - requires more access to the filesystem that we support
- `python_startup` - runs a shell command
- `regex_compile` - needs to import several other local modules (should be possible, just fiddly)
- SQL-related - SQLAlchemy not worth porting for now. SQLite also not supported but could be
- `sympy` - sympy module not yet ported but could be
- `tornado` - Tornado not ported (and don't plan to)
