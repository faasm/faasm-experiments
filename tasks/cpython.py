from os.path import join
from subprocess import run
from copy import copy
import os

from invoke import task

from tasks.util.env import EXPERIMENTS_THIRD_PARTY
from faasmcli.util.toolchain import (
    BASE_CONFIG_CMD,
    WASM_CFLAGS,
    WASM_CXXFLAGS,
    WASM_HOST,
    WASM_LDFLAGS,    
)

CPYTHON_DIR = join(EXPERIMENTS_THIRD_PARTY, "cpython")

# See the CPython docs for more info:
# - General: https://devguide.python.org/setup/#compile-and-build
# - Static builds: https://wiki.python.org/moin/BuildStatically


@task
def lib(ctx, clean=False):
    work_dir = join(CPYTHON_DIR)

    if clean:
        run("make clean", shell=True, cwd=work_dir)

    env_vars = copy(os.environ)       

    configure_cmd = ["./configure"]
    configure_cmd.extend(BASE_CONFIG_CMD)
    configure_cmd.extend([
        "--with-pydebug",
        "--disable-ipv6",
        "--without-gcc",
        "--without-pymalloc",
        "--disable-shared"
        ])

    cflags = [
            WASM_CFLAGS,
            ]
    cflags = " ".join(cflags)

    ldflags = [
            WASM_LDFLAGS,
            ]
    ldflags = " ".join(ldflags)

    configure_cmd.extend([
        'CFLAGS="{}"'.format(cflags),
        'CPPFLAGS="{}"'.format(cflags),
        'LDFLAGS="{}"'.format(ldflags),
    ])

    configure_str = " ".join(configure_cmd)
    print(configure_str)

    print("RUNNING CONFIGURE")
    res = run(configure_str, shell=True, cwd=work_dir, env=env_vars)
    if res.returncode != 0:
        raise RuntimeError("CPython configure failed ({})".format(
            res.returncode
            ))

