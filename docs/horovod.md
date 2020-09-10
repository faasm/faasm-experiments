# Horovod

[Horovod](https://github.com/horovod/horovod) is a distributed machine learning
training framework that uses MPI under the hood.

We support using Horovod with [MXNet](https://mxnet.apache.org/). 

Before building, make sure all the horovod 3rd party deps are up to date:

```
cd third-party/horovod
git submodule update --init
```

To build:

```
# Build MXNet
inv mxnet.lib

# Build Horovod
inv horovod.lib
```

## Forks

To get Horovod running in Faasm we had to make a few tweaks on the following
forks (usually on a `faasm` branch):

- [Shillaker/Horovod](https://github.com/Shillaker/horovod/tree/faasm)
- [Shillaker/incubator-mxnet](https://github.com/Shillaker/incubator-mxnet/tree/faasm)
- [Shillaker/dmlc-core](https://github.com/Shillaker/dmlc-core/tree/faasm)

