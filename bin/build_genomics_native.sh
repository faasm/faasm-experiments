#!/bin/bash

set -e

PROJ_ROOT=$(dirname $(dirname $(readlink -f $0)))
FAASM_DIR=${PROJ_ROOT}/third-party/faasm

source ${FAASM_DIR}/toolchain/native_clang.sh

pushd ${PROJ_ROOT}/third-party/gem3-mapper

./configure --enable-cuda=no

# Release build
make -j

# Debug build
# make debug

popd
