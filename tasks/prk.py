import re
from os import mkdir
from os.path import exists, join
from shutil import copy
from subprocess import run

from faasmcli.util.call import invoke_impl
from faasmcli.util.endpoints import get_invoke_host_port
from faasmcli.util.env import FAASM_HOME, WASM_DIR
from faasmcli.util.maths import is_power_of_two
from faasmcli.util.mpi import mpi_run
from invoke import task

from tasks.util.env import EXPERIMENTS_THIRD_PARTY

ITERATIONS = 20
FAASM_USER = "prk"

# Sparse requires grid size to be a multiple of the number of processes.
# The script expects the grid size to be passed as its log2, hence
# we must pass n = log2(grid_size) (i.e. 10 for a 1024 grid).
SPARSE_GRID_SIZE_2LOG = 10
SPARSE_GRID_SIZE = pow(2, SPARSE_GRID_SIZE_2LOG)

# See the scripts in third-party/ParResKernels/scripts for the arguments they
# recommend for running the kernels:
#
# $MPIRUN -np $NUMPROCS MPI1/DGEMM/dgemm               $NUMITERS -50000 32 1;    echo $SEPLINE
# $MPIRUN -np $NUMPROCS MPI1/Nstream/nstream           $NUMITERS 2000000000L 0;  echo $SEPLINE
# $MPIRUN -np $NUMPROCS MPI1/Random/random             $NUMITERS 32;             echo $SEPLINE
# $MPIRUN -np $NUMPROCS MPI1/Reduce/reduce             $NUMITERS 2000000000L;    echo $SEPLINE
# $MPIRUN -np $NUMPROCS MPI1/Sparse/sparse             $NUMITERS 13 7;           echo $SEPLINE
# $MPIRUN -np $NUMPROCS MPI1/Stencil/stencil           $NUMITERS 50000;          echo $SEPLINE
# $MPIRUN -np $NUMPROCS MPI1/Synch_global/global       $NUMITERS 2000000000L;    echo $SEPLINE
# $MPIRUN -np $NUMPROCS MPI1/Synch_p2p/p2p             $NUMITERS 70000 70000;    echo $SEPLINE
# $MPIRUN -np $NUMPROCS MPI1/Transpose/transpose       $NUMITERS 50000 64;       echo $SEPLINE
#
PRK_CMDLINE = {
    "dgemm": "{} 500 32 1".format(
        ITERATIONS
    ),  # iterations, matrix order, outer block size (?)
    "nstream": "{} 2000000 0".format(ITERATIONS),  # iterations, vector length, offset
    "random": "16 16",  # update ratio, table size
    "reduce": "{} 2000000".format(ITERATIONS),  # iterations, vector length
    "sparse": "{} {} 4".format(
        ITERATIONS, SPARSE_GRID_SIZE_2LOG
    ),  # iterations, log2 grid size, stencil radius
    "stencil": "{} 1000".format(ITERATIONS),  # iterations, array dimension
    "global": "{} 10000".format(ITERATIONS),  # iterations, scramble string length
    "p2p": "{} 1000 100".format(
        ITERATIONS
    ),  # iterations, 1st array dimension, 2nd array dimension
    "transpose": "{} 2000 64".format(ITERATIONS),  # iterations, matrix order, tile size
}

PRK_NATIVE_BUILD = join(FAASM_HOME, "ParResKernels")

PRK_NATIVE_EXECUTABLES = {
    "dgemm": join(PRK_NATIVE_BUILD, "MPI1", "DGEMM", "dgemm"),
    "nstream": join(PRK_NATIVE_BUILD, "MPI1", "Nstream", "nstream"),
    "random": join(PRK_NATIVE_BUILD, "MPI1", "Random", "random"),
    "reduce": join(PRK_NATIVE_BUILD, "MPI1", "Reduce", "reduce"),
    "sparse": join(PRK_NATIVE_BUILD, "MPI1", "Sparse", "sparse"),
    "stencil": join(PRK_NATIVE_BUILD, "MPI1", "Stencil", "stencil"),
    "global": join(PRK_NATIVE_BUILD, "MPI1", "Synch_global", "global"),
    "p2p": join(PRK_NATIVE_BUILD, "MPI1", "Synch_p2p", "p2p"),
    "transpose": join(PRK_NATIVE_BUILD, "MPI1", "Transpose", "transpose"),
}

PRK_STATS = {
    "dgemm": ("Avg time (s)", "Rate (MFlops/s)"),
    "nstream": ("Avg time (s)", "Rate (MB/s)"),
    "random": ("Rate (GUPS/s)", "Time (s)"),
    "reduce": ("Rate (MFlops/s)", "Avg time (s)"),
    "sparse": ("Rate (MFlops/s)", "Avg time (s)"),
    "stencil": ("Rate (MFlops/s)", "Avg time (s)"),
    "global": ("Rate (synch/s)", "time (s)"),
    "p2p": ("Rate (MFlops/s)", "Avg time (s)"),
    "transpose": ("Rate (MB/s)", "Avg time (s)"),
}

PRK_DIR = join(EXPERIMENTS_THIRD_PARTY, "ParResKernels")


@task
def func(ctx, clean=False):
    """
    Compile and install the ParRes Kernels
    """

    # Pairs of (directory, make target). See top-level ParResKernels
    # Makefile for more examples
    make_targets = [
        ("MPI1/Synch_global", "global"),
        ("MPI1/Synch_p2p", "p2p"),
        ("MPI1/Sparse", "sparse"),
        ("MPI1/Transpose", "transpose"),
        ("MPI1/Stencil", "stencil"),
        ("MPI1/DGEMM", "dgemm"),
        ("MPI1/Nstream", "nstream"),
        ("MPI1/Reduce", "reduce"),
        ("MPI1/Random", "random"),
        # ("MPI1/PIC-static", "pic"),
        # ("MPI1/AMR", "amr"),
    ]

    if clean:
        run("make clean", shell=True, cwd=PRK_DIR)

    has_failed = False
    for subdir, make_target in make_targets:
        make_cmd = "make {}".format(make_target)
        make_dir = join(PRK_DIR, subdir)
        res = run(make_cmd, shell=True, cwd=make_dir)

        if res.returncode != 0:
            print(
                "Making kernel in {} with target {} failed".format(subdir, make_target)
            )
            has_failed = True

        print("Built kernel {}".format(make_target))

    if has_failed:
        print("At least one kernel failed")
        exit(1)

    # Make sure wasm dir exists
    prk_wasm_dest = join(WASM_DIR, "prk")
    if not exists(prk_wasm_dest):
        mkdir(prk_wasm_dest)

    # Copy the functions into place
    prk_wasm_src = join(PRK_DIR, "wasm")
    for target in [t[1] for t in make_targets]:
        wasm_src = join(prk_wasm_src, "{}.wasm".format(target))
        wasm_dest = join(prk_wasm_dest, target)
        if not exists(wasm_dest):
            mkdir(wasm_dest)

        copy(wasm_src, join(wasm_dest, "function.wasm"))


@task
def invoke(ctx, func, native=False, iface=None, np=8):
    """
    Invoke one of the ParRes Kernels functions
    """
    if func not in PRK_CMDLINE:
        print("Invalid PRK function {}".format(func))
        return 1

    cmdline = PRK_CMDLINE[func]

    if func == "random" and not is_power_of_two(np):
        print("Must have a power of two number of processes for random")
        exit(1)
    elif func == "sparse" and not (SPARSE_GRID_SIZE % np == 0):
        print(
            "To run sparse, grid size must be a multiple of --np (currently grid_size={} and np={})".format(
                SPARSE_GRID_SIZE, np
            )
        )
        exit(1)

    if native:
        executable = PRK_NATIVE_EXECUTABLES[func]
        cmd_out = mpi_run(executable, iface=iface, cmdline=cmdline, np=np)
        cmd_out = cmd_out.decode()
        print(cmd_out)
    else:
        host, port = get_invoke_host_port()
        cmd_out = invoke_impl(
            FAASM_USER, func, cmdline=cmdline, host=host, port=port, mpi_world_size=np
        )

    _parse_prk_out(func, cmd_out)


def _parse_prk_out(func, cmd_out):
    stats = PRK_STATS.get(func)

    if not stats:
        print("No stats for {}".format(func))
        return

    print("----- {} stats -----".format(func))

    for stat in stats:
        spilt_str = "{}: ".format(stat)

        stat_val = [c for c in cmd_out.split(spilt_str) if c.strip()]
        if not stat_val:
            print("{} = MISSING".format(stat))
            continue

        stat_val = stat_val[1]
        stat_val = re.split("\s+", stat_val)[0]
        stat_val = stat_val.rstrip(",")
        stat_val = float(stat_val)

        print("{} = {}".format(stat, stat_val))
