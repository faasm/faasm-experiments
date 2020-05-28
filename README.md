# Faasm experiments

Repository for holding all experimental/ transient code related to 
[Faasm](https://github.com/lsds/Faasm.git).

Docs on specific experiments are held in the relevant subfolders. 

This code assumes you have Faasm checked out at `/usr/local/code/faasm`, and it 
is symlinked as such from `third-party/faasm`. If you have Faasm checked out 
elsewhere, just change the symlink.

## Local Set-up

If building and these experiments locally, you should set up Faasm for 
[local development](https://github.com/lsds/Faasm/blob/master/docs/local_dev.md).

You must then make sure WAVM and WAMR are up to date:

```
cd third-party/faasm
git submodule update --init third-party/WAVM
git submodule update --init third-party/wamr
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
