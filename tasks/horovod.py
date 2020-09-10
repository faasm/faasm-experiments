from os.path import join
from subprocess import run
from copy import copy
import os

from faasmcli.util.env import FAASM_TOOLCHAIN_FILE, SYSROOT_INSTALL_PREFIX
from faasmcli.util.files import clean_dir
from invoke import task

from tasks.util.env import EXPERIMENTS_THIRD_PARTY

HOROVOD_DIR = join(EXPERIMENTS_THIRD_PARTY, "horovod")


# See the Horovod Python library set-up for details of their
# CMake configuration
# https://github.com/horovod/horovod/blob/master/setup.py


@task
def lib(ctx, clean=False):
    work_dir = join(HOROVOD_DIR, "build")

    clean_dir(work_dir, clean)

    env_vars = copy(os.environ)
    env_vars.update({
        "HOROVOD_WITHOUT_GLOO": "1",
    })

    cmake_cmd = [
        "cmake",
        "-DFAASM_BUILD_TYPE=wasm",
        "-DCMAKE_TOOLCHAIN_FILE={}".format(FAASM_TOOLCHAIN_FILE),
        "-DCMAKE_BUILD_TYPE=Release",
        "-DCMAKE_INSTALL_PREFIX={}".format(SYSROOT_INSTALL_PREFIX),
        "-DHAVE_CUDA=OFF",
        HOROVOD_DIR,
    ]

    cmake_str = " ".join(cmake_cmd)
    print(cmake_str)

    res = run(cmake_str, shell=True, cwd=work_dir, env=env_vars)
    if res.returncode != 0:
        raise RuntimeError("Horovod CMake config failed")

    res = run("cmake --build .", shell=True, cwd=work_dir)
    if res.returncode != 0:
        raise RuntimeError("Horovod build failed")

