# CPython Build

The CPython build uses a [fork](https://github.com/Shillaker/cpython) of the 
main [CPython repo](https://github.com/python/cpython). The changes in the fork
live on the [`faasm` branch](https://github.com/Shillaker/cpython/tree/faasm).

To avoid having to dynamically link C-extensions from Python modules, we build 
CPython and all requires modules as a single static WebAssembly library.

Some notes on building CPython statically can be found
[here](https://wiki.python.org/moin/BuildStatically). The Faasm CPython build 
adopts some of the changes made in 
[pyodide](https://github.com/iodide-project/pyodide).

## Building

You can build CPython by running:

```
inv cpython.lib
```

The result is installed at `third-party/cpython/install/wasm`.

CPython needs to access certain files at runtime. These can be put in place with
the following:

```
inv cpython.runtime
```

