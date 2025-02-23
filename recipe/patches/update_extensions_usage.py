#!/usr/bin/env python3
"""
update_proto_references.py

This script updates .proto files in a target directory by:
  1. Updating import and option references to reflect a new file name.
  2. Updating extension references using a dynamically generated mapping.

It computes a "source" reference from the file’s relative path (from a given base directory)
and then constructs a "target" reference by prepending a specified prefix to the basename.
It then applies those substitutions throughout the file, and finally updates any extension
references using a mapping provided in a JSON file.

Usage:
  python update_proto_references.py --dir <target_dir> --base_dir <base_dir> \
      --proto_file_prefix dydx_v4_ --proto_dir_prefix dydx_v4_ --mapping mapping.json

Example:
  If a file’s relative path (from base_dir) is:
      cosmos/app/v1alpha1/module.proto
  and you set:
      --proto_file_prefix dydx_v4_
  then the target file reference becomes:
      cosmos/app/v1alpha1/dydx_v4_module.proto
  which (after converting slashes to dots and removing .proto) yields the option reference:
      cosmos.app.v1alpha1.dydx_v4_module

The JSON mapping file should be a simple dictionary mapping old extension references to new ones.
For example:
{
  "(dydx_v4_amino.name)": "(dydx_v4_amino.dydx_v4_name)",
  "(dydx_v4_amino.message_encoding)": "(dydx_v4_amino.dydx_v4_message_encoding)",
  ...
}
"""

import os
import re
import json
import argparse
import sys


def update_file(file_path, mapping, prefix):

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading {file_path}: {e}", file=sys.stderr)
        return

    # Then update extension references using the mapping.
    for old_ext, new_ext in mapping.items():
        content = re.sub(rf'\b({re.escape(prefix)})?{re.escape(old_ext)}\b', new_ext, content)

    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
    except Exception as e:
        print(f"Error writing {file_path}: {e}", file=sys.stderr)


def process_directory(target_dir, mapping, prefix):
    for root, _, files in os.walk(target_dir):
        for file in files:
            if file.endswith(".proto"):
                file_path = os.path.join(root, file)
                update_file(file_path, mapping, prefix)


def main():
    parser = argparse.ArgumentParser(
        description="Update .proto file references and extension usage using a mapping file."
    )
    parser.add_argument("--dir", required=True, help="Directory containing .proto files to update")
    parser.add_argument("--prefix", required=True,
                        help="Path to JSON file containing extension mapping (old -> new)")
    parser.add_argument("--mapping", required=True,
                        help="Path to JSON file containing extension mapping (old -> new)")
    args = parser.parse_args()

    try:
        with open(args.mapping, "r", encoding="utf-8") as mfile:
            mapping = json.load(mfile)
    except Exception as e:
        print(f"Error reading mapping file {args.mapping}: {e}", file=sys.stderr)
        sys.exit(1)

    process_directory(args.dir, mapping, args.prefix)


if __name__ == "__main__":
    main()
