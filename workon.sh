#!/bin/bash

set -e

THIS_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
pushd ${THIS_DIR} >> /dev/null

# Use the tasks in this directory
# export INVOKE_ROOT=${THIS_DIR}
source third-party/faasm/workon.sh

popd >> /dev/null
