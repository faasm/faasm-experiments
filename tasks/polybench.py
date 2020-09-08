from os import listdir
from os.path import join

from faasmcli.util.compile import wasm_cmake, wasm_copy_upload
from invoke import task

from tasks.util.env import EXPERIMENTS_FUNC_BUILD_DIR, EXPERIMENTS_FUNC_DIR


@task
def func(ctx, clean=False):
    wasm_cmake(
        EXPERIMENTS_FUNC_DIR,
        EXPERIMENTS_FUNC_BUILD_DIR,
        "polybench_all_funcs",
        clean=clean,
    )

    build_dir = join(EXPERIMENTS_FUNC_BUILD_DIR, "polybench")
    all_files = listdir(build_dir)
    wasm_files = [f for f in all_files if f.endswith(".wasm")]

    for wasm_file in wasm_files:
        func_name = wasm_file.replace(".wasm", "")
        full_file = join(build_dir, wasm_file)
        print("Uploading polybench/{} ({})".format(func_name, full_file))

        wasm_copy_upload("polybench", func_name, full_file)
