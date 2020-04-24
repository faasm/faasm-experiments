# Faasm experiments

Repository for holding all experimental/ transient code related to 
[Faasm](https://github.com/lsds/Faasm.git).

Each directory contains the experiment and its associated README.

## General set-up

### Faasm

You should set up Faasm for 
[local development](https://github.com/lsds/Faasm/blob/master/docs/local_dev.md).

To build code in this repo, make sure you update Faasm and its WAVM and WAMR submodules:

```bash
git submodule update --init
cd third-party/faasm
git submodule update --init third-party/WAVM
git submodule update --init third-party/wamr
``` 

### Python

This project adds extra tasks to the existing Faasm CLI, which it imports
using the `faasmcli` module. So you need to set up a virtual env for this project:

```
python3 -m venv venv
source venv/bin/activate
cd third-party/faasm/faasmcli
pip install -r requirements.txt 
pip install -e .
```
