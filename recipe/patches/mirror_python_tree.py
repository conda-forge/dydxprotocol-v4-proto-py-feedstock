#!/usr/bin/env python3
"""
mirror_reexports.py

This script creates a mirror of an internal Python module tree by generating re-export
files. For example, if your internal modules live under:

    v4_proto/dydx_v4_ns_cosmos/app/runtime/v1alpha1/

but you want consumers to import them as if they were under:

    v4_proto/cosmos/

then this script will walk the internal tree and, for each Python module it finds,
create a corresponding file under the target tree that re-exports the module.

Usage:
    python mirror_reexports.py --source v4_proto/dydx_v4_ns_cosmos/app/runtime/v1alpha1 --target v4_proto/cosmos

After running the script, a file like:
    v4_proto/dydx_v4_ns_cosmos/app/runtime/v1alpha1/module_pb2.py
will have a corresponding re-export file:
    v4_proto/cosmos/module_pb2.py

whose content will be:
    from v4_proto.dydx_v4_ns_cosmos.app.runtime.v1alpha1.module_pb2 import *
"""

import os
import argparse


def create_reexport_file(source_module_path, target_file_path, full_source_import):
    """
    Create a re-export file that imports everything from the source module.

    Args:
      source_module_path (str): The original source file path (for logging).
      target_file_path (str): The file to create for re-export.
      full_source_import (str): The full Python import path of the source module.
    """
    content = f"from {full_source_import} import *\n"
    with open(target_file_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Created re-export file: {target_file_path}")


def mirror_tree(package_root, proto_fold_prefix, proto_file_prefix):
    """
    Mirror the internal module tree into a target re-export tree.

    Args:
      package_root (str): The directory containing the internal modules (e.g., v4_proto)
      proto_fold_prefix (str): The prefix identifying the internal Python package (e.g., dydx_v4_ns_)
      proto_file_prefix (str): The prefix identifying the internal Python module (e.g., dydx_v4_)
    """
    for root, dirs, files in os.walk(package_root):
        for file in files:
            if proto_fold_prefix in root and file.startswith(proto_file_prefix) and (file.endswith(".py") or file.endswith(".py")):
                rel_path = os.path.relpath(os.path.join(root, file), package_root + os.sep + "..")
                target_file_path = os.path.relpath(os.path.join(root, file), package_root + os.sep + "..")
                target_file_path = target_file_path.replace(proto_fold_prefix, "").replace(proto_file_prefix, "")
                target_dir = os.path.dirname(target_file_path)
                os.makedirs(target_dir, exist_ok=True)

                # Build the full source import path.
                # Assume that base_internal_root corresponds to a Python package.
                # For example, if base_internal_root is "v4_proto/dydx_v4_ns_cosmos/app/runtime/v1alpha1",
                # then its corresponding Python package is "v4_proto.dydx_v4_ns_cosmos.app.runtime.v1alpha1".
                internal_pkg = rel_path.replace(os.sep, ".")
                # Remove a leading dot if present.
                if internal_pkg.startswith("."):
                    internal_pkg = internal_pkg[1:]

                # We want to create re-export files for modules that are not __init__.py
                if file != "__init__.py":
                    create_reexport_file(os.path.join(root, file), target_file_path, internal_pkg)
                elif not os.path.exists(target_file_path):
                    with open(target_file_path, "w", encoding="utf-8") as f:
                        f.write("# Auto-generated __init__.py\n")
                    print(f"Created {target_file_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Mirror an internal module tree by creating re-export files under a new target root."
    )
    parser.add_argument("--source", required=True,
                        help="The root directory of the internal modules (e.g., v4_proto)")
    parser.add_argument("--proto_fold_prefix", required=True,
                        help="The directory prefix corresponding to the internal Python package (e.g., dydx_v4_ns_)")
    parser.add_argument("--proto_file_prefix", required=True,
                        help="The file prefix of the internal Python package (e.g., dydx_v4_)")
    args = parser.parse_args()

    mirror_tree(args.source, args.proto_fold_prefix, args.proto_file_prefix)


if __name__ == "__main__":
    main()
