from os.path import join
from subprocess import run
from copy import copy
import os

from faasmcli.util.env import FAASM_TOOLCHAIN_FILE, SYSROOT_INSTALL_PREFIX
from faasmcli.util.files import clean_dir
from invoke import task

from tasks.util.env import EXPERIMENTS_THIRD_PARTY

LAMMPS_DIR = join(EXPERIMENTS_THIRD_PARTY, "lammps")


# The LAMMPS CMake build instructions can be found in the following link
# https://lammps.sandia.gov/doc/Build_cmake.html


@task(default=True)
def build(ctx, clean=False):
    """
    Builds the LAMMPS Molecular Dynamics Simulator
    https://lammps.sandia.gov
    """
    work_dir = join(LAMMPS_DIR, "build")
    cmake_dir = join(LAMMPS_DIR, "cmake")

    clean_dir(work_dir, clean)

    env_vars = copy(os.environ)

    cmake_cmd = [
        "cmake",
        "-GNinja",
        "PKG_BODY=on", # We compile an additional package for experiments
        "-DFAASM_BUILD_TYPE=wasm",
        "-DCMAKE_TOOLCHAIN_FILE={}".format(FAASM_TOOLCHAIN_FILE),
        "-DCMAKE_BUILD_TYPE=Release",
        "-DCMAKE_INSTALL_PREFIX={}".format(SYSROOT_INSTALL_PREFIX),
        cmake_dir,
    ]

    cmake_str = " ".join(cmake_cmd)
    print(cmake_str)

    res = run(cmake_str, shell=True, cwd=work_dir, env=env_vars)
    if res.returncode != 0:
        raise RuntimeError("LAMMPS CMake config failed")

    res = run("ninja", shell=True, cwd=work_dir)
    if res.returncode != 0:
        raise RuntimeError("LAMMPS build failed")

    # @csegarra: Is it advisable to actually install the binaries?
#    res = run("ninja install", shell=True, cwd=work_dir)
#    if res.returncode != 0:
#        raise RuntimeError("LAMMPS install failed")
