#!/usr/bin/env bash

set -ex

# Install
pushd v4-proto-py
  ${PYTHON} -m pip install . -vv \
    --no-build-isolation \
    --no-deps \
    --only-binary :all: \
    --prefix "${PREFIX}"
popd
