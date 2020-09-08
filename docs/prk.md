# ParRes Kernels

We can benchmark Faasm's MPI implementation using the 
[ParRes Kernels](https://github.com/ParRes/Kernels) modified slightly in the 
fork found in `third-party/ParResKernels`.

To compile you can run the following:

```bash
inv prk.func
```

This builds a number of the kernels written for MPI, e.g. `nstream`. These can 
be invoked using:

```bash
inv prk.invoke nstream
```

