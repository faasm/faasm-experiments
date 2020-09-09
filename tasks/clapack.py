from os.path import join
from subprocess import run

from invoke import task

from tasks.util.env import EXPERIMENTS_THIRD_PARTY

CLAPACK_DIR = join(EXPERIMENTS_THIRD_PARTY, "faasm-clapack")

# See the CLAPACK docs: http://www.netlib.org/clapack/


@task
def lib(ctx, clean=False):
    work_dir = CLAPACK_DIR

    if clean:
        run("make clean", cwd=work_dir, shell=True)

    res = run("make", shell=True, cwd=work_dir)
    if res.returncode != 0:
        raise RuntimeError("Make command failed")

    res = run("make install", shell=True, cwd=work_dir)

