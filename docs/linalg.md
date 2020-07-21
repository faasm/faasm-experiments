# Linear Algebra - Matrix Multiplication

## Data

The matrix experiment data needs to be generated in bulk locally, uploaded to S3 then downloaded on the client machine (or directly copied with `scp`). You must have the native tooling and pyfaasm installed to generate it up front (but
this doesn't need to be done if it's already in S3):

```bash
# Generate it
inv libs.native
inv matrix-data.generate-all

# Direct SCP from local machine
export HOST=<your_host>
export HOST_USER=<user_on_your_host>
rsync -r ~/faasm/data/matrix $HOST_USER@$HOST:/home/$HOST_USER/faasm/data

# Upload (note - >4GB)
inv data.matrix-upload-s3

# Download
inv data.matrix-download-s3
```

## Running the Experiment on Knative

```bash
# -- Build/ Upload --
inv upload python mat_mul --py

# Number of workers kept the same throughout
export N_WORKERS=<number of workers>

# -- Deploy --

# Native
inv knative.deploy-native-python --replicas=$N_WORKERS

# Wasm
inv knative.deploy --replicas=$N_WORKERS

# -- Run experiment --

# Native
inv experiments.matrix-multi $N_WORKERS --native

# Wasm
inv experiments.matrix-multi $N_WORKERS
```

## Results

```bash
# Matrices
inv experiments.matrix-pull-results <user> <host>
```

Data will be downloaded to `~/faasm/python_mat_mul`.
