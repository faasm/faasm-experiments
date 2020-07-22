import os
from copy import copy
from multiprocessing import Pool
from os import mkdir, remove, makedirs
from os.path import exists, basename
from os.path import join
from subprocess import check_output, call
from time import sleep

from faasmcli.tasks.upload import upload
from faasmcli.util.call import invoke_impl, status_call_impl, STATUS_SUCCESS, STATUS_FAILED, STATUS_RUNNING
from faasmcli.util.endpoints import get_invoke_host_port
from faasmcli.util.endpoints import get_upload_host_port
from faasmcli.util.env import FAASM_DATA_DIR, FAASM_SHARED_STORAGE_ROOT
from faasmcli.util.state import download_binary_state
from faasmcli.util.state import upload_shared_file
from faasmcli.util.upload_util import curl_file
from invoke import task

from tasks.util.env import EXPERIMENTS_ROOT, EXPERIMENTS_THIRD_PARTY
from tasks.util.genomics import GENOMICS_DATA_DIR, CHROMOSOME_URLS, CHROMOSOME_NUMBERS, READ_URLS, get_reads_from_dir, \
    get_index_chunks_present_locally
from tasks.util.genomics import INDEX_CHUNKS

GEM3_DIR = join(EXPERIMENTS_THIRD_PARTY, "gem3-mapper")
GEM3_INDEXER = join(GEM3_DIR, "bin", "gem-indexer")
GEM3_MAPPER = join(GEM3_DIR, "bin", "gem-mapper")

GENOMICS_OUTPUT_DIR = join(GENOMICS_DATA_DIR, "output")


@task
def mapping(ctx, download=False):
    """
    Run genomics mapping using Faasm
    """
    read_idxs, _ = get_reads_from_dir()

    # Iterate through and make the calls to the worker
    call_ids = list()
    for read_idx in read_idxs:
        print("Invoking worker for read chunk {}".format(read_idx))
        call_id = invoke_impl("gene", "mapper", input="{}".format(read_idx), asynch=True, poll=False)
        call_ids.append(call_id)

    # Poll for completion of each read
    completed_read_idxs = list()
    host, port = get_invoke_host_port()
    print("Polling workers...")

    while len(completed_read_idxs) < len(read_idxs):
        for i, read_idx in enumerate(read_idxs):
            sleep(0.5)

            # See whether this call is still running
            call_id = call_ids[i]
            result, output = status_call_impl("gene", "mapper", call_id, host, port)
            if result == STATUS_RUNNING:
                continue

            # Check for success or failure
            if result == STATUS_SUCCESS:
                print("Read chunk {} completed.".format(read_idx))

                # Download the results of this read
                if download:
                    print("Downloading output for read chunk {}.".format(read_idx))
                    state_key = "output_read_{}".format(read_idx)

                    if not exists(GENOMICS_OUTPUT_DIR):
                        makedirs(GENOMICS_OUTPUT_DIR)

                    output_file = join(GENOMICS_OUTPUT_DIR, state_key)
                    host, port = get_upload_host_port(None, None)
                    download_binary_state("gene", state_key, output_file, host=host, port=port)

            elif result == STATUS_FAILED:
                print("Read chunk {} failed: {}", read_idx, output)

            # Check if we're done
            completed_read_idxs.append(read_idx)

    print("All read chunks finished")


def _do_native_mapping(reads_file, index_file, output_file):
    if not exists(GEM3_MAPPER):
        print("Did not find gem3 mapper at {}".format(GEM3_MAPPER))
        exit(1)

    print("Native mapping {} -> {}".format(basename(reads_file), basename(index_file)))

    cmd = [
        GEM3_MAPPER,
        "-I {}".format(index_file),
        "-i {}".format(reads_file),
        "-o {}".format(output_file)
    ]

    cmd = " ".join(cmd)
    print(cmd)

    check_output(cmd, cwd=GEM3_DIR, shell=True)


@task
def mapping_native(ctx, nthreads=None):
    """
    Run genomics mapping natively
    """
    read_idxs, read_files = get_reads_from_dir()
    index_chunks, index_files = get_index_chunks_present_locally()

    # Create an appropriately sized pool if not specified
    if not nthreads:
        nthreads = os.cpu_count() - 1

    p = Pool(nthreads)

    if not exists(GENOMICS_OUTPUT_DIR):
        makedirs(GENOMICS_OUTPUT_DIR)

    # Spawn a thread for every read and index chunk
    func_args = list()
    for read_idx, read_file in zip(read_idxs, read_files):
        for index_chunk, index_file in zip(index_chunks, index_files):
            output_file = join(GENOMICS_OUTPUT_DIR, "native_{}_{}.sam".format(read_idx, index_chunk))
            func_args.append((read_file, index_file, output_file))

    p.starmap(_do_native_mapping, func_args)


@task
def download_genome(ctx):
    """
    Download genome data
    """
    if not exists(GENOMICS_DATA_DIR):
        mkdir(GENOMICS_DATA_DIR)

    for url in CHROMOSOME_URLS:
        zip_filename = url.split("/")[-1]

        # Download the file
        download_file = join(GENOMICS_DATA_DIR, zip_filename)
        print("URL: {} -> {}\n".format(url, download_file))
        check_output("wget {} -O {}".format(url, download_file), shell=True)

        # Extract zip
        print("Extracting {}".format(download_file))
        check_output("gunzip -f {}".format(download_file), shell=True, cwd=GENOMICS_DATA_DIR)

        # Check unzipping
        filename = zip_filename.replace(".gz", "")
        unzipped_file = join(GENOMICS_DATA_DIR, filename)
        if not exists(unzipped_file):
            print("Didn't find unzipped file at {} as expected.".format(unzipped_file))
            exit(1)

        print("Unzipped file at {}".format(unzipped_file))


@task
def index_genome(ctx):
    """
    Run indexing
    """
    shell_env = copy(os.environ)
    shell_env["LD_LIBRARY_PATH"] = "/usr/local/lib:{}".format(shell_env.get("LD_LIBRARY_PATH", ""))

    if not exists(GEM3_INDEXER):
        raise RuntimeError("Expected to find executable at {}".format(GEM3_INDEXER))

    for idx, name in enumerate(CHROMOSOME_NUMBERS):
        input_file = join(FAASM_DATA_DIR, "genomics", "Homo_sapiens.GRCh38.dna.chromosome.{}.fa".format(name))
        output_file = join(FAASM_DATA_DIR, "genomics", "index_{}".format(idx))

        cmd = [
            GEM3_INDEXER,
            "-i {}".format(input_file),
            "-o {}".format(output_file),
        ]

        cmd_str = " ".join(cmd)
        print(cmd_str)
        call(cmd_str, shell=True, env=shell_env, cwd=GEM3_DIR)

        # Remove unnecessary files
        info_file = "{}.info".format(output_file)
        remove(input_file)
        remove(info_file)


@task
def download_reads(ctx):
    """
    Download reads data
    """
    if not exists(GENOMICS_DATA_DIR):
        mkdir(GENOMICS_DATA_DIR)

    for url in READ_URLS:
        filename = url.split("/")[-1]
        download_file = join(GENOMICS_DATA_DIR, filename)
        print("URL: {} -> {}\n".format(url, download_file))
        check_output("wget {} -O {}".format(url, download_file), shell=True)


def _do_file_upload(local_copy, file_path, file_name, dest_root):
    if local_copy:
        # Copy directly if local copy
        dest_file = join(dest_root, file_name)
        call("cp {} {}".format(file_path, dest_file), shell=True)
    else:
        # Upload if not local
        shared_path = "genomics/{}".format(file_name)
        upload_shared_file(host, file_path, shared_path)


@task
def upload_data(ctx, host="localhost", local_copy=False):
    """
    Upload index and reads data
    """
    dest_root = join(FAASM_SHARED_STORAGE_ROOT, "genomics")
    if local_copy and not exists(dest_root):
        makedirs(dest_root)

    files_to_upload = list()

    # Reads
    read_idxs, file_paths = get_reads_from_dir()
    for read_idx, file_path in zip(read_idxs, file_paths):
        files_to_upload.append((file_path, "reads_{}.fq".format(read_idx)))

    # Index chunks
    _, index_files = get_index_chunks_present_locally()
    for index_file in index_files:
        filename = basename(index_file)
        files_to_upload.append((index_file, filename))

    # Pool to do the work
    p = Pool(os.cpu_count() - 1)
    task_args = list()
    for file_path, file_name in files_to_upload:
        task_args.append((local_copy, file_path, file_name, dest_root))
    
    p.starmap(_do_file_upload, task_args)


def _do_func_upload(idx, host, port):
    func_name = "mapper_index{}".format(idx)
    print("Uploading function gene/{} to {}:{}".format(func_name, host, port))

    file_path = join(EXPERIMENTS_ROOT, "third-party/gem3-mapper/wasm_bin/gem-mapper")
    url = "http://{}:{}/f/gene/{}".format(host, port, func_name)
    curl_file(url, file_path)


@task
def upload_funcs(ctx, host="localhost", port=None):
    """
    Upload all the genomics functions
    """

    # When uploading genomics, we are uploading the mapper entrypoint as a normal
    # function, but the worker functions are all from the same source file

    # Upload the entrypoint function
    upload(ctx, "gene", "mapper")

    # Upload the worker functions (one for each index chunk)
    host, port = get_upload_host_port(host, port)

    args = [(idx, host, port) for idx in INDEX_CHUNKS]
    p = Pool(3)
    p.starmap(_do_func_upload, args)
