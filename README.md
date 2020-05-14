# Faasm experiments

Repository for holding all experimental/ transient code related to 
[Faasm](https://github.com/lsds/Faasm.git).

Each directory contains the experiment and its associated README.

## General set-up

### Faasm

You should set up Faasm for 
[local development](https://github.com/lsds/Faasm/blob/master/docs/local_dev.md).

If you already have Faasm checked out, you can do the following:

```bash
cd third-party/
rm -r faasm
ln -s <path_to_faasm> faasm
```

Or, you can use the submodule in this directory:

```bash
git submodule update --init
```

You must then make sure WAVM and WAMR are up to date:

```
cd third-party/faasm
git submodule update --init third-party/WAVM
git submodule update --init third-party/wamr
``` 

### Python

This project adds extra tasks to the existing Faasm CLI, which it imports
using the `faasmcli` module. So you can set up a virtual env for this project:

```
python3 -m venv venv
source venv/bin/activate
```

Or, if you've already got some Python deps installed globally (e.g. in a 
bare-metal deploy), you can just rely on those.

Then you need to install the Faasm requirements:

```
cd third-party/faasm/faasmcli
pip install -r requirements.txt 
pip install -e .
```

