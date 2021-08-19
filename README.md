# ARCHIVAL

This repo is no longer used, and most of the experiments are not maintained.

For more recent experiments see 
[this repo](https://github.com/faasm/experiment-base).

If trying to resurrect experiments in here, be aware that they use various 
utilities since removed from Faasm in 
[this PR](https://github.com/faasm/faasm/pull/464)

# Faasm experiments

This repository holds all experimental/ transient code related to 
[Faasm](https://github.com/lsds/faasm.git).

Docs on specific experiments are held in the relevant subfolders. 

This code assumes you have Faasm checked out at `/usr/local/code/faasm`, and it 
is symlinked as such from `third-party/faasm`. If you have Faasm checked out 
elsewhere, just change the symlink.

## Local Set-up

If building and these experiments locally, you should set up Faasm for [local
development](https://github.com/lsds/faasm/blob/master/docs/development.md).

You must then make sure WAVM and WAMR are up to date:

```
cd third-party/faasm
git submodule update --init third-party/WAVM
git submodule update --init third-party/wamr
``` 

Finally, to use the Faasm CLI, you need to run:

```
# Set up the Faasm CLI
source third-party/faasm/workon.sh

# Check 
inv toolchain.version
```

## Remote Set-up

If you're running experiments from a remote client somewhere, you can set it up 
by creating an inventory file at `ansible/inventory/benchmark.yml` that looks
like:

```ini
[all]
<client_host>
```

You then need to SSH onto the host and make sure Faasm is checked out at 
`/usr/local/code/faasm`:

Then intall the relevant code and deps with:

```bash
cd ansible
ansible-playbook -i inventory/benchmark.yml experiment_client.yml
```

## Microbenchmarks Set-up

To execute the microbenchmarks you'll need to run a few more steps on your
experiment host. First, SSH in and run:

```
./bin/set_up_benchmarks.sh
```

Then download the toolchain, sysroot and runtime root:

```
inv toolchain.download-toolchain
inv toolchain.download-sysroot
inv toolchain.download-runtime
```

## Python

From your client machine (local or remote), you'll need to run Python tasks.
This project adds extra tasks to the existing Faasm CLI.

You can either set up a new virtual env for this project, or use the existing
Faasm CLI environment from your Faasm checkout (via `source workon.sh`). 

You then need to make sure all the python deps are installed:

```bash
cd third-party/faasm/faasmcli
pip install -r requirements.txt 
pip install -e .

# Check it's all working
cd ../../..
inv -l
```

## Knative Experiments

Experiments that are run on a Kubernetes cluster must be run from a machine with
access to the cluster that can run `kubectl` and `kn`.

## Billing Estimates

To get resource measurements from the hosts running experiments we need an
inventory file that includes all the hosts we want to measure at
`ansible/inventory/billing.ini`, something like:

```ini
[all]
myhost1
myhost2
...
```

Then we can run the set-up with:

```bash
cd ansible
ansible-playbook -i inventory/billing.ini billing_setup.yml
```
