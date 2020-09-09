from os import cpu_count, makedirs, walk
from os.path import exists, join
from shutil import rmtree
from subprocess import call, check_output

from faasmcli.util.compile import wasm_cmake, wasm_copy_upload
from faasmcli.util.endpoints import get_upload_host_port
from faasmcli.util.env import FAASM_SHARED_STORAGE_ROOT, FUNC_DIR
from faasmcli.util.state import upload_binary_state, upload_shared_file
from faasmcli.util.toolchain import (
    BASE_CONFIG_CMD,
    WASM_CFLAGS,
    WASM_CXXFLAGS,
    WASM_HOST,
    WASM_LDFLAGS,
)
from invoke import task

from tasks.util.env import (
    EXPERIMENTS_FUNC_BUILD_DIR,
    EXPERIMENTS_FUNC_DIR,
    EXPERIMENTS_ROOT,
    EXPERIMENTS_THIRD_PARTY,
)


@task
def func(ctx, clean=False):
    wasm_cmake(EXPERIMENTS_FUNC_DIR, EXPERIMENTS_FUNC_BUILD_DIR, "image", clean=clean)

    wasm_file = join(EXPERIMENTS_FUNC_BUILD_DIR, "tf", "image.wasm")
    wasm_copy_upload("tf", "image", wasm_file)


@task
def lib(ctx, clean=False):
    """
    Compile and install Tensorflow Lite
    """
    tf_dir = join(EXPERIMENTS_THIRD_PARTY, "tensorflow")
    tf_lite_dir = join(tf_dir, "tensorflow", "lite")
    tf_make_dir = join(tf_lite_dir, "tools", "make")

    download_check_dir = join(tf_make_dir, "downloads", "absl")
    if not exists(download_check_dir):
        download_script = join(tf_make_dir, "download_dependencies.sh")
        check_output(download_script, shell=True)

    cores = cpu_count()
    make_cores = int(cores) - 1

    make_target = "lib"
    make_cmd = ["make -j {}".format(make_cores)]
    make_cmd.extend(BASE_CONFIG_CMD)
    make_cmd.extend(
        [
            'CFLAGS="{} -ftls-model=local-exec"'.format(WASM_CFLAGS),
            'CXXFLAGS="{}"'.format(WASM_CXXFLAGS),
            'LDFLAGS="{} -Xlinker --max-memory=4294967296"'.format(WASM_LDFLAGS),
            "MINIMAL_SRCS=",
            "TARGET={}".format(WASM_HOST),
            "BUILD_WITH_MMAP=false",
            'LIBS="-lstdc++"',
            '-C "{}"'.format(tf_dir),
            "-f tensorflow/lite/tools/make/Makefile",
        ]
    )

    make_cmd.append(make_target)

    clean_dir = join(tf_make_dir, "gen", "wasm32-unknown-wasi_x86_64")
    if clean and exists(clean_dir):
        rmtree(clean_dir)

    res = call(" ".join(make_cmd), shell=True, cwd=tf_lite_dir)
    if res != 0:
        raise RuntimeError("Failed to compile Tensorflow lite")


@task
def state(ctx, host=None):
    """
    Upload Tensorflow lite demo state
    """
    data_dir = join(FUNC_DIR, "tf", "data")
    model_file = "mobilenet_v1_1.0_224.tflite"
    host, _ = get_upload_host_port(host, None)
    file_path = join(data_dir, model_file)

    upload_binary_state("tf", "mobilenet_v1", file_path, host=host)


@task
def upload(ctx, host=None, local_copy=False):
    """
    Upload Tensorflow lite demo data
    """
    host, port = get_upload_host_port(host, None)

    source_data = join(EXPERIMENTS_FUNC_DIR, "tf", "data")

    dest_root = join(FAASM_SHARED_STORAGE_ROOT, "tfdata")
    if local_copy:
        makedirs(dest_root, exist_ok=True)

    for root, dirs, files in walk(source_data):
        for filename in files:
            file_path = join(source_data, filename)

            if local_copy:
                dest_file = join(dest_root, filename)
                call("cp {} {}".format(file_path, dest_file), shell=True)
            else:
                shared_path = "tfdata/{}".format(filename)
                upload_shared_file(host, file_path, shared_path)
