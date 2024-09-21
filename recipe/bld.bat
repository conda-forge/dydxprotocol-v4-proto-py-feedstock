echo source %SYS_PREFIX:\=/%/etc/profile.d/conda.sh    > conda_build.sh
echo conda activate "${PREFIX}"                       >> conda_build.sh
echo conda activate --stack "${BUILD_PREFIX}"         >> conda_build.sh
echo CONDA_PREFIX=${CONDA_PREFIX//\\//}               >> conda_build.sh
type "%RECIPE_DIR%\build.sh"                          >> conda_build.sh

set PREFIX=%PREFIX:\=/%
set BUILD_PREFIX=%BUILD_PREFIX:\=/%
set CONDA_PREFIX=%CONDA_PREFIX:\=/%
set SRC_DIR=%SRC_DIR:\=/%
set MSYSTEM=UCRT64
set MSYS2_PATH_TYPE=inherit
set CHERE_INVOKING=1
bash -lc "./conda_build.sh"
if errorlevel 1 exit 1

:: @echo on
:: setlocal enabledelayedexpansion
::
:: cd %SRC_DIR%
::
:: powershell -Command "(Get-Content %SRC_DIR%/v4-proto-py/setup.py) -replace 'version=\"0.0.0\"', 'version=\"%PKG_VERSION%\"' | Set-Content %SRC_DIR%/v4-proto-py/setup.py"
:: if errorlevel 1 exit 1
::
:: bash -c make -e -w debug -f %SRC_DIR%\\Makefile v4-proto-py-gen
:: if errorlevel 1 exit 1
