#!/usr/bin/env bash

set -ex

# Install
cp -r v4-proto-py v4-proto-py-bypass
for file in $(find v4-proto-py-bypass/v4_proto -type f -name '*_pb2.py'); do \
  ${PYTHON} ${RECIPE_DIR}/patches/apply_duplicate_proof_patch.py --file "$file"; \
done

pushd v4-proto-py-bypass
  ${PYTHON} -m pip install . -vv \
    --no-build-isolation \
    --no-deps \
    --only-binary :all: \
    --prefix "${PREFIX}"
popd
