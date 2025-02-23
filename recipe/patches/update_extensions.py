#!/usr/bin/env python3
r"""
update_extensions.py

This script reads a .proto file, finds extension declarations (inside blocks
starting with "extend google.protobuf.MessageOptions", "extend google.protobuf.FieldOptions",
or "extend google.protobuf.FeatureSet"), and updates each extension field name by
prepending a given prefix if it is not already present.

Additionally, it builds a mapping (definition registry) of the old extension field
names to their new names. This mapping can later be used to update references to the
old names in other proto files.

Usage:
    python update_extensions.py input.proto output.proto --prefix dydx_v4_

Example:
    Given an extension block in input.proto:

      extend google.protobuf.MessageOptions {
        string name = 11110001;
        string message_encoding = 11110002;
      }

    Running:
      python update_extensions.py input.proto output.proto --prefix dydx_v4_

    Will transform it into:

      extend google.protobuf.MessageOptions {
        string dydx_v4_name = 11110001;
        string dydx_v4_message_encoding = 11110002;
      }

    And the script will output a mapping like:
      {'name': 'dydx_v4_name', 'message_encoding': 'dydx_v4_message_encoding'}

Note: This script assumes that extension declarations are in a block delimited by "{" and "}"
and that each extension field is declared on its own line in the form:
    <type> <field_name> = <number>;
It does not attempt to reformat comments or handle multiline field declarations.
"""

import re
import argparse
import sys
import json

def update_extensions(content: str, prefix: str, proto_file: str) -> (str, dict):
    """
    Update extension field names inside extension blocks and build a mapping from
    the old field name to the new field name.

    Args:
        content: The original .proto file content as a string.
        prefix: The prefix to prepend to each extension field name (e.g., "dydx_v4_").

    Returns:
        A tuple (updated_content, mapping) where updated_content is the modified
        content and mapping is a dict mapping original field names to new field names.
    """
    mapping = {}
    lines = content.splitlines()
    in_extension_block = False
    updated_lines = []

    # Detect package name.
    package_block_re = re.compile(r'^package\s+(\S+)\s*;')
    # Detect extension blocks for MessageOptions, FieldOptions, or FeatureSet.
    extension_block_re = re.compile(r'^\s*extend\s+\.?google\.protobuf\.((?:Enum|EnumValue|Field|File|Message|Method|Service)Options|FeatureSet)\s*\{')
    # Capture: optional whitespace, type, whitespace, field_name, then "=", number, etc.
    field_line_re = re.compile(r'^(\s*\S+\s+(?:\S+\s+)?)(\w+)(\s*=\s*\d+\s*;.*)$')
    end_block_re = re.compile(r'^\s*\}')

    package_name = None
    for line in lines:
        if package_block_re.match(line) and package_name is None:
            package_name = package_block_re.match(line).group(1)
            updated_lines.append(line)
            continue

        if extension_block_re.match(line):
            in_extension_block = True
            updated_lines.append(line)
            continue

        if in_extension_block and end_block_re.match(line):
            in_extension_block = False
            updated_lines.append(line)
            continue

        if in_extension_block and package_name:
            if m := field_line_re.match(line):
                orig_field = m[2]
                # If the field name does not already have the prefix, update it.
                if not orig_field.startswith(prefix):
                    new_field = f"{prefix}{orig_field}"
                    line = m[1] + new_field + m[3]
                    mapping[f"{package_name}.{orig_field}"] = f"{package_name}.{new_field}"
        updated_lines.append(line)
    updated_content = "\n".join(updated_lines) + "\n"
    return updated_content, mapping

def main():
    parser = argparse.ArgumentParser(
        description="Update extension field names in a .proto file by prepending a prefix and build a definition registry."
    )
    parser.add_argument("input_file", help="Path to the input .proto file")
    parser.add_argument("output_file", help="Path to the output .proto file")
    parser.add_argument("--prefix", required=True,
                        help="Prefix to prepend to extension field names (e.g., dydx_v4_)")
    parser.add_argument("--proto_file", required=True,
                        help="Prefix to prepend to extension field names (e.g., amino)")
    parser.add_argument("--map_file", required=True, help="Path to output JSON file for the combined mapping")
    args = parser.parse_args()

    try:
        with open(args.input_file, "r", encoding="utf-8") as infile:
            content = infile.read()
    except Exception as e:
        print(f"Error reading file {args.input_file}: {e}", file=sys.stderr)
        sys.exit(1)

    updated_content, mapping = update_extensions(content, args.prefix, args.proto_file)

    try:
        with open(args.map_file, "r", encoding="utf-8") as infile:
            map = json.load(infile)
    except Exception as e:
        if not isinstance(e, FileNotFoundError):
            print(f"Error reading JSON file {args.map_file}: {e}", file=sys.stderr)
            sys.exit(1)
        map = {}

    try:
        map.update(mapping)
        with open(args.map_file, "w", encoding="utf-8") as outfile:
            json.dump(map, outfile, indent=2)

    except Exception as e:
        print(f"Error updating/writing JSON file {args.map_file}: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        with open(args.output_file, "w", encoding="utf-8") as outfile:
            outfile.write(updated_content)
    except Exception as e:
        print(f"Error writing file {args.output_file}: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
