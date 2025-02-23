#!/usr/bin/env python3
"""
Generate public API directories and __init__.py files for specified packages.

Usage:
    python generate_public_api.py amino cosmos google

This script creates a directory structure under the base directory (default: "v4-proto-py/v4_proto")
and generates an __init__.py file for each package that re-exports everything from the corresponding
internal package (e.g. "v4_proto.{PROTO_FOLD_PREFIX}amino"), including all nested submodules.
"""

import os
import argparse

# Parse command-line arguments.
parser = argparse.ArgumentParser(
    description="Generate public API directories and __init__.py files for specified packages."
)
parser.add_argument(
    "packages",
    nargs="+",
    help="List of package names to process (e.g., amino cosmos google)"
)
parser.add_argument(
    "--base_dir",
    default="v4-proto-py/v4_proto",
    help="Base directory for public API generation (default: v4-proto-py/v4_proto)"
)
parser.add_argument(
    "--proto_fold_prefix",
    default="dydx_v4_ns_",
    help="Base directory for public API generation (default: v4-proto-py/v4_proto)"
)
args = parser.parse_args()

PACKAGES = args.packages
BASE_DIR = args.base_dir
PROTO_FOLD_PREFIX = args.proto_fold_prefix


def ensure_init_py(directory: str) -> None:
    """
    Ensure that an __init__.py file exists in the given directory.

    :param directory: The directory in which to create __init__.py if missing.
    """
    init_file = os.path.join(directory, "__init__.py")
    if not os.path.exists(init_file):
        with open(init_file, "w") as f:
            f.write("")
        print(f"Created: {init_file}")


def generate_public_api_for_package(pkg: str, root: str="v4_proto") -> None:
    """
    Generate a public API directory and __init__.py for a given package.

    The __init__.py file re-exports everything from the internal package
    'v4_proto.{PROTO_FOLD_PREFIX}{pkg}' and recursively attaches all its submodules,
    reproducing the internal nested package structure.

    :param pkg: The package name (e.g., "amino")
    """
    pkg_dir = os.path.join(BASE_DIR, pkg)
    os.makedirs(pkg_dir, exist_ok=True)
    ensure_init_py(pkg_dir)

    # Build the __init__.py content with recursive import logic.
    content = f'''"""
Public API for the {pkg} package.
Re-export everything from the internal package {root}.{PROTO_FOLD_PREFIX}{pkg},
including all nested submodules.
"""

import pkgutil
import importlib
import types

def recursive_import_and_attach(internal_pkg, public_module):
    """
    Recursively import all submodules of internal_pkg and attach them to public_module.

    :param internal_pkg: The internal package (e.g., {root}.{PROTO_FOLD_PREFIX}{pkg})
    :param public_module: The public module's globals() dictionary.
    """
    for finder, modname, ispkg in pkgutil.walk_packages(internal_pkg.__path__, prefix=internal_pkg.__name__ + "."):
        try:
            module = importlib.import_module(modname)
        except Exception:
            continue
        # Remove the internal prefix to get the relative module name.
        rel_name = modname[len(internal_pkg.__name__) + 1:]
        parts = rel_name.split(".")
        current = public_module
        for part in parts[:-1]:
            if not hasattr(current, part):
                new_module = types.ModuleType(part)
                setattr(current, part, new_module)
            current = getattr(current, part)
        setattr(current, parts[-1], module)

_internal_pkg = importlib.import_module("{root}.{PROTO_FOLD_PREFIX}{pkg}")
recursive_import_and_attach(_internal_pkg, globals())

__all__ = [name for name in globals() if not name.startswith('_')]
'''

    init_path = os.path.join(pkg_dir, "__init__.py")
    with open(init_path, "w") as f:
        f.write(content)
    print(f"Generated public API for {pkg} at {init_path}")


def generate_public_api() -> None:
    """
    Generate the public API directories and __init__.py files for all specified packages.
    """
    # Ensure the top-level public package exists and is a package.
    os.makedirs(BASE_DIR, exist_ok=True)
    ensure_init_py(BASE_DIR)

    for pkg in PACKAGES:
        generate_public_api_for_package(pkg, os.path.basename(BASE_DIR))


if __name__ == "__main__":
    generate_public_api()
