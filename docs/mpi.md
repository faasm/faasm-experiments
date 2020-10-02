# MPI Benchmarks

We benchmark Faasm against OpenMPI by running both on the same set of bare metal
machines or VMs. The steps to do this are as follows.

## 0. Check SSH

Note that all the machines must be able to SSH to each other without any 
prompt or passwords. 

## 1. Set up the VMs

Follow the normal Faasm [bare metal setup](https://github.com/faasm/faasm/blob/master/docs/bare_metal.md).

Then run the following from the root of _this_ repository:

```bash
cd ansible
ansible-playbook -i ../third-party/faasm/ansible/inventory/bare_metal.yml mpi_benchmark.yml
```

## 3. Run native code

The set-up process will create a hostfile at `~/mpi_hostfile` according to your inventory.
This is automatically used by the underlying scripts to run the benchmarks.

To check the native code works, you can run:

```bash
inv prk.invoke nstream --native
```

## 4. Run wasm code

Faasm functions using MPI can be run as with any others. To check the basic WASM MPI set-up, run:

```bash
inv upload.user mpi
inv invoke mpi mpi_checks
```

To check this works you can run:

```bash
inv upload.user prk
inv prk.invoke nstream
``` 

## Troubleshooting Native MPI

Remember that all machines must be able to SSH onto each other with no prompts (passwords or confirmations).

Machines with multiple network interfaces may sometimes need to specify which interfaces to use, e.g.:

```bash
mpirun ... -mca btl_tcp_if_include eth1 ...
```

You can also specify CIDR address ranges:

```bash
mpirun ... -mca btl_tcp_if_include 192.168.0.0/16 ...
```
