# Tensorflow Lite in Faasm

[Tensorflow Lite](https://www.tensorflow.org/lite/) is well suited to running 
inference tasks in a resource-constrained serverless context. 
 
It is written in C/C++ hence we can build Tensorflow Lite to WebAssembly using 
the standard Faasm toolchain.  

Faasm currently only supports the C/C++ API.

## Compiling TensorFlow Lite to WebAssembly

To do this, make sure you've checked out this project and updated all the git 
submodules, then:

```bash
inv tensorflow.lib
```

The build output ends up at 
`third-party/tensorflow/tensorflow/lite/tools/make/gen`.

## Building a C/C++ function with TF Lite

A function implementing image classification is included 
[in the examples](../func/tf/image.cc). This is based on the 
[example in the TF Lite repo](https://github.com/tensorflow/tensorflow/tree/master/tensorflow/lite/examples/label_image). 

The data and model for the example are stored in [this repo](../func/tf/data).

To run the example function, you need to run a local Faasm cluster (as 
described in the 
[README](https://github.com/lsds/faasm/blob/master/README.md)), then:

```bash
# Upload files and state
inv tensorflow.upload tensorflow.state

# Upload the function (takes a few seconds)
inv upload tf image

# Invoke
inv invoke tf image
```

## Eigen Fork

To support WASM simd instructions I've hacked about with Eigen on a
[fork](https://github.com/Shillaker/eigen-git-mirror). It _seems_ to work but
isn't well tested. 

TF Lite will be compiled against the version of Eigen downloaded as part of its
3rd party deps, so if you need to change it and rebuild you'll need to run:

```bash
cd third-party/tensorflow/tensorflow/lite/tools/make
rm -r downloads/eigen/
./download_dependencies.sh
```

# Tensorflow Experiment

## Set-up

You need to set the following environment variables for these experiments (through the knative config):

- `COLD_START_DELAY_MS=800`
- `TF_CODEGEN=on`
- `SGD_CODEGEN=off`
- `PYTHON_CODEGEN=off`
- `PYTHON_PRELOAD=off`

Preamble:

```bash
# -- Build/ upload --
inv knative.build-native tf image
inv upload tf image

# -- Upload data (one-off)
inv tf.upload tf.state
```

## Running the Experiment on Knative

Latency:

```bash
# -- Deploy both (note small number of workers) --
inv knative.deploy --replicas=1
inv knative.deploy-native tf image --replicas=1

# -- Run experiment --
inv experiments.tf-lat
```

Throughput:

```bash
# -- Deploy --
# Native
inv knative.deploy-native tf image --replicas=30

# Wasm
inv knative.deploy --replicas=18

# -- Run experiment --

# Native 
inv experiments.tf-tpt --native

# Wasm
inv experiments.tf-tpt
```

## Results

```bash
# Inference latency
inv experiments.tf-lat-pull-results <user> <host>

# Inference throughput
inv experiments.tf-tpt-pull-results <user> <host>
```

Data will be downloaded to `~/faasm/tf_image`.

