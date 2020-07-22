#!/bin/bash

set -e

PROJ_ROOT=$(dirname $(dirname $(readlink -f $0)))
pushd ${PROJ_ROOT}/third-party/gem3-mapper >> /dev/null

echo "Cleaning native build"
unset WASM_BUILD
make clean

echo "Cleaning wasm build"
export WASM_BUILD=1
make clean

echo "Remove generated Makefile"
rm Makefile.mk

popd >> /dev/null