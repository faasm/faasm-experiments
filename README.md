# Faasm experiments

Repository for holding all experimental/ transient code related to 
[Faasm](https://github.com/lsds/Faasm.git).

Each directory contains the experiment and its associated README.

## Local Set-up

If building and these experiments locally, you should set up Faasm for 
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

## Remote Set-up

If you're running experiments from a remote client somewhere, you can set it up 
by creating an inventory file at `ansible/inventory/experiments.ini` that looks
like:

```ini
[all]
<client_host>
```

You can then intall the relevant code and deps with:

```bash
cd ansible
ansible-playbook -i inventory/experiments.ini experiment_client.yml
```

From there you should be able to run the set-up described above.

## Python

From your client machine (local or remote), you'll need to run Python tasks. This 
project adds extra tasks to the existing Faasm CLI.

If running locally you can set up a virtual env for this project:

```bash
python3 -m venv venv
source venv/bin/activate
```

Or, if running remotely you can just install the deps locally (especially given 
they may already be set-up on an existing bare-metal deployment).

You then need to set up the Faasm CLI and requirements:

```bash
cd third-party/faasm/faasmcli
pip install -r requirements.txt 
pip install -e .

# Check it's all working
cd ../../..
inv -l
```

## Billing Estimates

To get resource measurements from the hosts running experiments we need an inventory file that 
includes all the hosts we want to measure at `ansible/inventory/billing.ini`, something like:

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
