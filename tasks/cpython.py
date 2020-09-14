import os
from copy import copy
from multiprocessing import cpu_count
from os.path import join
from subprocess import run

from faasmcli.util.compile import wasm_cmake, wasm_copy_upload
from faasmcli.util.endpoints import get_upload_host_port
from faasmcli.util.env import FAASM_SHARED_STORAGE_ROOT, FUNC_DIR
from faasmcli.util.files import clean_dir
from faasmcli.util.toolchain import (BASE_CONFIG_CMD, WASM_BUILD, WASM_CFLAGS,
                                     WASM_HOST, WASM_LDFLAGS)
from invoke import task

from tasks.util.env import (EXPERIMENTS_FUNC_BUILD_DIR, EXPERIMENTS_FUNC_DIR,
                            EXPERIMENTS_THIRD_PARTY)

CPYTHON_DIR = join(EXPERIMENTS_THIRD_PARTY, "cpython")
LOCAL_PYTHON_BIN = "/usr/local/faasm/python3.8/bin"
WORK_DIR = join(CPYTHON_DIR)
BUILD_DIR = join(WORK_DIR, "build", "wasm")
INSTALL_DIR = join(WORK_DIR, "install", "wasm")

# See the CPython docs for more info:
# - General: https://devguide.python.org/setup/#compile-and-build
# - Static builds: https://wiki.python.org/moin/BuildStatically


def _run_cmd(label, cmd_array, env_vars):
    cmd_str = " ".join(cmd_array)
    print("CPYTHON BUILD STEP: {}".format(label))
    print(cmd_str)
    res = run(cmd_str, shell=True, cwd=WORK_DIR, env=env_vars)

    if res.returncode != 0:
        raise RuntimeError("CPython {} failed ({})".format(label, res.returncode))


@task
def lib(ctx, clean=False, noconf=False):
    clean_dir(BUILD_DIR, clean)
    clean_dir(INSTALL_DIR, clean)
    if clean:
        run("make clean", shell=True, cwd=WORK_DIR)

    # Environment variables
    env_vars = copy(os.environ)
    path_env_var = env_vars.get("PATH", "")
    path_env_var = "{}:{}".format(LOCAL_PYTHON_BIN, path_env_var)
    env_vars.update(
        {
            "PATH": path_env_var,
        }
    )

    # Configure
    configure_cmd = ["CONFIG_SITE=./config.site", "READELF=true", "./configure"]

    configure_cmd.extend(BASE_CONFIG_CMD)
    configure_cmd.extend(
        [
            "--with-pydebug",
            "--disable-ipv6",
            "--without-pymalloc",
            "--disable-shared",
            "--build={}".format(WASM_BUILD),
            "--host={}".format(WASM_HOST),
            "--prefix={}".format(INSTALL_DIR),
        ]
    )

    cflags = [
        WASM_CFLAGS,
    ]
    cflags = " ".join(cflags)

    ldflags = [
        WASM_LDFLAGS,
        "-static",
    ]
    ldflags = " ".join(ldflags)

    configure_cmd.extend(
        [
            'CFLAGS="{}"'.format(cflags),
            'CPPFLAGS="{}"'.format(cflags),
            'LDFLAGS="{}"'.format(ldflags),
        ]
    )

    if not noconf:
        _run_cmd("configure", configure_cmd, env_vars)

    # Copy in extra undefs
    _run_cmd("modify", ["cat", "pyconfig-extra.h", ">>", "pyconfig.h"], env_vars)

    cpus = int(cpu_count()) - 1
    make_cmd = [
        "make -j {}".format(cpus),
        'LDFLAGS="-static"',
        'LINKFORSHARED=" "',
    ]
    _run_cmd("make", make_cmd, env_vars)

    _run_cmd("inclinstall", ["make", "inclinstall"], env_vars)
    _run_cmd("libinstall", ["make", "libinstall"], env_vars)


@task
def func(ctx, clean=False):
    wasm_cmake(EXPERIMENTS_FUNC_DIR, EXPERIMENTS_FUNC_BUILD_DIR, "mini", clean=clean)

    wasm_file = join(EXPERIMENTS_FUNC_BUILD_DIR, "cpy", "mini.wasm")
    wasm_copy_upload("cpy", "mini", wasm_file)
