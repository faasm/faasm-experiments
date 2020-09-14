from os import cpu_count, makedirs, mkdir
from os.path import exists, join

from faasmcli.util.env import (
    FAASM_INSTALL_DIR,
    FAASM_RUNTIME_ROOT,
    FAASM_TOOLCHAIN_FILE,
    PROJ_ROOT,
    SYSROOT_INSTALL_PREFIX,
    THIRD_PARTY_DIR,
    WASM_DIR,
)
from faasmcli.util.files import clean_dir
from faasmcli.util.toolchain import (
    BASE_CONFIG_CMD,
    BASE_CONFIG_FLAGS,
    WASM_AR,
    WASM_BUILD,
    WASM_CC,
    WASM_CFLAGS,
    WASM_CXX,
    WASM_CXXFLAGS,
    WASM_HOST,
    WASM_LD,
    WASM_LDFLAGS,
    WASM_RANLIB,
    WASM_SYSROOT,
)
from invoke import task


@task
def lulesh(
    ctx, lulesh_dir, mpi=False, omp=False, clean=True, debug=False, cp=True
):
    """
    Compile and install the LULESH code
    """
    work_dir = lulesh_dir

    if omp and mpi:
        build_dir = "ompi"
        target = "lulesh_ompi"
    elif omp:
        build_dir = "omp-only"
        target = "lulesh_omp"
    elif mpi:
        build_dir = "mpi-only"
        target = "lulesh_mpi"
    else:
        build_dir = "bare"
        target = "lulesh_bare"
    build_dir = join(work_dir, "build", build_dir)

    if clean and exists(build_dir):
        print("rm {}".format(build_dir))
        rmtree(build_dir)

    if not exists(build_dir):
        makedirs(build_dir)

    cmd = " ".join(
        [
            "cmake",
            "-G Ninja",
            "-DWITH_MPI={}".format("TRUE" if mpi else "FALSE"),
            "-DWITH_OPENMP={}".format("TRUE" if omp else "FALSE"),
            "-DWITH_SILO=FALSE",
            "-DFAASM_BUILD_TYPE=wasm",
            "-DCMAKE_TOOLCHAIN_FILE={}".format(FAASM_TOOLCHAIN_FILE),
            "-DCMAKE_BUILD_TYPE=Release",
            "-DCMAKE_INSTALL_PREFIX={}".format(SYSROOT_INSTALL_PREFIX),
            work_dir,
        ]
    )
    if debug:
        print("Running {}".format(cmd))
    res = call(cmd, shell=True, cwd=build_dir)
    if res != 0:
        raise RuntimeError("Failed on cmake init for {}".format(target))

    cmd = " ".join(
        [
            "cmake",
            "--build {}".format(build_dir),
            "--target {}".format(target),
        ]
    )
    if debug:
        print("Running {}".format(cmd))
    res = call(cmd, shell=True)
    if res != 0:
        raise RuntimeError("Failed on make for {}".format(target))

    if cp:
        dest_dir = join(WASM_DIR, "lulesh", target)
        if clean and exists(dest_dir):
            rmtree(dest_dir)

        if not exists(dest_dir):
            makedirs(dest_dir)

        cmd = " ".join(
            [
                "cp",
                "{}.wasm".format(target),
                join(dest_dir, "function.wasm"),
            ]
        )
        if debug:
            print("Running {}".format(cmd))
        res = call(cmd, shell=True, cwd=build_dir)
        if res != 0:
            raise RuntimeError("Failed to copy {}".format(target))
