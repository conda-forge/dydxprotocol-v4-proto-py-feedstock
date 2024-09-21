#!/usr/bin/env bash

set -euxo pipefail

if [[ "${target_platform}" == win-* ]]; then
  powershell -Command "(Get-Content %SRC_DIR%/v4-proto-py/setup.py) -replace 'version=\"0.0.0\"', 'version=\"%PKG_VERSION%\"' | Set-Content %SRC_DIR%/v4-proto-py/setup.py"
else
  sed -i "s/version=\"0.0.0\"/version=\"${PKG_VERSION}\"/g" v4-proto-py/setup.py
fi

make v4-proto-py-gen
