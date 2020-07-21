#!/bin/bash

set -e

PROJ_ROOT=$(dirname $(dirname $(readlink -f $0)))
pushd ${PROJ_ROOT}/third-party/gem3-mapper >> /dev/null

echo "Cleaning native build"
make clean

echo "Cleaning wasm build"
export WASM_BUILD=1
make clean

popd >> /dev/null