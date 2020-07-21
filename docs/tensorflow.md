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