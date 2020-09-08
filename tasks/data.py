import multiprocessing
from os import listdir, makedirs
from os.path import exists, join
from shutil import rmtree
from subprocess import check_output

from faasmcli.util.endpoints import get_kubernetes_upload_host
from faasmcli.util.env import DATA_S3_BUCKET, FAASM_DATA_DIR
from faasmcli.util.state import upload_binary_state, upload_sparse_matrix
from faasmcli.util.upload_util import download_file_from_s3, upload_file_to_s3
from invoke import task

from tasks.util.matrices import get_matrix_dir

_GENOMICS_TAR_NAME = "genomics.tar.gz"
_GENOMICS_TAR_PATH = "/tmp/{}".format(_GENOMICS_TAR_NAME)
_GENOMICS_TAR_DIR_NAME = "genomics"
_GENOMICS_DATA_DIR = join(FAASM_DATA_DIR, _GENOMICS_TAR_DIR_NAME)

_REUTERS_TAR_NAME = "reuters.tar.gz"
_REUTERS_TAR_PATH = "/tmp/{}".format(_REUTERS_TAR_NAME)
_REUTERS_TAR_DIR_NAME = "reuters"
_REUTERS_DATA_DIR = join(FAASM_DATA_DIR, _REUTERS_TAR_DIR_NAME)

_REUTERS_MICRO_TAR_NAME = "reuters_micro.tar.gz"
_REUTERS_MICRO_TAR_PATH = "/tmp/{}".format(_REUTERS_MICRO_TAR_NAME)
_REUTERS_MICRO_TAR_DIR_NAME = "reuters_micro"
_REUTERS_MICRO_DATA_DIR = join(FAASM_DATA_DIR, _REUTERS_MICRO_TAR_DIR_NAME)

_MATRIX_TAR_NAME = "matrix.tar.gz"
_MATRIX_TAR_PATH = "/tmp/{}".format(_MATRIX_TAR_NAME)
_MATRIX_TAR_DIR_NAME = "matrix"
_MATRIX_DATA_DIR = join(FAASM_DATA_DIR, _MATRIX_TAR_DIR_NAME)

_ALL_REUTERS_STATE_KEYS = [
    "feature_counts",
    "inputs_innr",
    "inputs_nonz",
    "inputs_outr",
    "inputs_size",
    "inputs_vals",
    "outputs",
]


# -------------------------------------------------
# S3 UPLOAD/ DOWNLOAD
# -------------------------------------------------


@task
def reuters_upload_s3(ctx, micro=False):
    """
    Upload data for the reuters experiment to S3
    """
    if not micro:
        _do_s3_upload(_REUTERS_TAR_PATH, _REUTERS_TAR_DIR_NAME, _REUTERS_TAR_NAME)

    _do_s3_upload(
        _REUTERS_MICRO_TAR_PATH, _REUTERS_MICRO_TAR_DIR_NAME, _REUTERS_MICRO_TAR_NAME
    )


@task
def matrix_upload_s3(ctx):
    """
    Upload data for the matrix experiment to S3
    """
    _do_s3_upload(_MATRIX_TAR_PATH, _MATRIX_TAR_DIR_NAME, _MATRIX_TAR_NAME)


@task
def genomics_upload_s3(ctx):
    """
    Upload data for the genomics experiment to S3
    """
    _do_s3_upload(_GENOMICS_TAR_PATH, _GENOMICS_TAR_DIR_NAME, _GENOMICS_TAR_NAME)


def _do_s3_upload(tar_path, tar_dir, tar_name):
    # Compress
    print("Creating archive of data {}".format(tar_path))
    check_output(
        "tar -cf {} {}".format(tar_path, tar_dir), shell=True, cwd=FAASM_DATA_DIR
    )

    # Upload
    print("Uploading archive to S3")
    upload_file_to_s3(tar_path, DATA_S3_BUCKET, tar_name)

    # Remove old tar
    print("Removing archive")
    check_output("rm {}".format(tar_path), shell=True)


@task
def reuters_download_s3(ctx, micro=False):
    """
    Download data for the reuters experiment from S3
    """
    if not micro:
        _do_s3_download(_REUTERS_TAR_PATH, _REUTERS_TAR_DIR_NAME, _REUTERS_TAR_NAME)

    _do_s3_download(
        _REUTERS_MICRO_TAR_PATH, _REUTERS_MICRO_TAR_DIR_NAME, _REUTERS_MICRO_TAR_NAME
    )


@task
def matrix_download_s3(ctx):
    """
    Download data for the matrix experiment from S3
    """
    _do_s3_download(_MATRIX_TAR_PATH, _MATRIX_TAR_DIR_NAME, _MATRIX_TAR_NAME)


@task
def genomics_download_s3(ctx):
    """
    Download data for the genomics experiment from S3
    """
    _do_s3_download(_GENOMICS_TAR_PATH, _GENOMICS_TAR_DIR_NAME, _GENOMICS_TAR_NAME)


def _do_s3_download(tar_path, tar_dir, tar_name):
    # Clear out existing
    print("Removing existing {}".format(tar_dir))
    full_tar_dir = join(FAASM_DATA_DIR, tar_dir)
    if exists(full_tar_dir):
        rmtree(full_tar_dir)

    if not exists(FAASM_DATA_DIR):
        makedirs(FAASM_DATA_DIR)

    # Download the bundle
    print("Downloading from S3 to {}".format(tar_path))
    download_file_from_s3(DATA_S3_BUCKET, tar_name, tar_path)

    # Extract
    print("Extracting")
    check_output("tar -xf {}".format(tar_path), shell=True, cwd=FAASM_DATA_DIR)


# -------------------------------------------------
# REUTERS UPLOAD
# -------------------------------------------------


@task
def reuters_state(ctx, host=None, knative=True, micro=False):
    """
    Upload reuters experiment state
    """
    user = "sgd"

    host = get_kubernetes_upload_host(knative, host)

    data_dir = _REUTERS_MICRO_DATA_DIR if micro else _REUTERS_DATA_DIR

    # Upload the inputs data
    upload_sparse_matrix(user, "inputs", data_dir, host=host)

    # Upload the outputs data
    outputs_path = join(data_dir, "outputs")
    upload_binary_state(user, "outputs", outputs_path, host=host)

    # Upload the feature counts
    counts_path = join(data_dir, "feature_counts")
    upload_binary_state(user, "feature_counts", counts_path, host=host)


# -------------------------------------------------
# MATRIX UPLOAD
# -------------------------------------------------


def _do_upload(data_dir, file_name, user, host, key=None):
    print("Uploading state {}".format(file_name))
    file_path = join(data_dir, file_name)

    key = key if key else file_name
    upload_binary_state(user, key, file_path, host=host)


@task
def matrix_state(ctx, mat_size, n_splits, host=None, knative=True):
    """
    Upload matrix experiment state
    """
    user = "python"

    host = get_kubernetes_upload_host(knative, host)
    data_dir = get_matrix_dir(mat_size, n_splits)
    file_names = listdir(data_dir)

    if len(file_names) == 0:
        print("Invalid matrix data: {} {}".format(mat_size, n_splits))
        exit(1)

    # Multiple uploaders as there may be lots of files
    args = [(data_dir, f, user, host) for f in file_names]
    p = multiprocessing.Pool(multiprocessing.cpu_count() - 1)
    p.starmap(_do_upload, args)
