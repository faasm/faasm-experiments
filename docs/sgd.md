# SGD (Hogwild)

To use the original Hogwild dataset we must download it and parse it into a Faasm-friendly form.

This can be done once and uploaded to S3 (see below). From then on it can just be downloaded directly 
from S3 on relevant machines.

From there it must be uploaded into the relevant state storage for running the algorithm
(see the experiment notes).

## Downloading from S3

To download the pre-processed data from S3, run the following:

```
inv data.reuters-download-s3
```

If running on a remote host you can then move the files:

```
rsync -r ~/faasm/data <USER>@<HOST>:/home/<USER>/faasm/
```

# Preparing data from scratch (one off)

To actually generate the parsed data in the first place, we must use exactly the same RCV1 data as the original
Hogwild experiments. The original code can be found on their [website](http://i.stanford.edu/hazy/victor/Hogwild/).
To set up locally you can run:

```
# Clone fork of Hogwild
cd ansible
ansible-playbook hogwild.yml

# Put the data into a suitable format (output at ~/faasm/rcv1/test)
cd /usr/local/code/hogwild
./bin/svm_data

# Parse (run from build dir for this repo)
./bin/reuters

# Upload data from ~/faasm/data/reuters
inv data.reuters-upload-s3
```

## Running the Experiment on Knative

Assuming around 20 nodes here. Number of workers in native is number of containers, 
whereas number of workers in Faasm is number of Faasm runtimes (which host multiple
workers).

```bash

# ---------------------
# Native
# ---------------------

# Build container
inv knative.build-native sgd reuters_svm

# Deploy
inv knative.deploy-native sgd reuters_svm --replicas=36

# State and run - full
inv data.reuters-state
inv experiments.sgd-multi --native

# State and run - micro
inv data.reuters-state --micro
inv experiments.sgd-multi --native --micro

# Clean up
inv knative.delete-native --hard sgd reuters_svm

# ---------------------
# Wasm
# ---------------------

# Deploy 
inv knative.deploy --replicas=10

# Check workers present (make sure there's not _more_ than there should be)
inv redis.all-workers  

# Upload function
inv upload sgd reuters_svm

# State and run - full
inv data.reuters-state
inv experiments.sgd-multi 

# State and run - micro
inv data.reuters-state --micro
inv experiments.sgd-multi --micro

# Clean up
inv knative.delete-worker --hard
```

## Results

```bash
# SGD
inv experiments.sgd-pull-results <user> <host>
```

Data will be downloaded to `~/faasm/sgd_reuters_svm`.