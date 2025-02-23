#!/usr/bin/env python3
"""
apply_dummy_field_patch.py

This helper script patches a generated Protobuf file (e.g.,
v4_proto/v4_proto_amino/amino_pb2.py) to modify its descriptor registration.
Instead of directly calling:

    DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'...')

this script replaces that call with code that:
  1. Parses the original serialized FileDescriptorProto,
  2. Adds a dummy uninterpreted option (dummy field),
  3. Reserializes the descriptor, and
  4. Calls AddSerializedFile with the modified bytes.

Usage:
    python apply_dummy_field_patch.py path/to/your/proto_file.py
"""

import re
import sys
import os


def apply_patch(file_path):
    # Read the original file content.
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Regular expression to capture the call to AddSerializedFile with a bytes literal.
    # This regex assumes the generated code uses a single-quoted bytes literal.
    pattern = re.compile(
        r'(DESCRIPTOR\s*=\s*_descriptor_pool\.Default\(\)\.AddSerializedFile\()'  # Match beginning
        r"(b'(?:\\.|[^'])*')"  # Capture the bytes literal (non-greedy)
        r'(\))',  # Match the closing parenthesis
        re.DOTALL
    )

    def replacement(match):
        original_literal = match.group(2)
        # Build the replacement block.
        # This block imports FileDescriptorProto, parses the original bytes,
        # adds a dummy uninterpreted option, reserializes, and registers the new descriptor.
        new_block = (
                'from google.protobuf.descriptor_pb2 import FileDescriptorProto\n'
                '_original_serialized = ' + original_literal + '\n'
                                                               'fd_proto = FileDescriptorProto()\n'
                                                               'fd_proto.ParseFromString(_original_serialized)\n'
                                                               'dydx_v4_proto_option = fd_proto.options.uninterpreted_option.add()\n'
                                                               'dydx_v4_proto_name_part = dydx_v4_proto_option.name.add()\n'
                                                               'dydx_v4_proto_name_part.name_part = "dydx_v4_proto_field"\n'
                                                               'dydx_v4_proto_name_part.is_extension = False\n'
                                                               'dydx_v4_proto_option.string_value = b"dydx_v4_proto"\n'
                                                               '_new_serialized = fd_proto.SerializeToString()\n'
                                                               'DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(_new_serialized)'
        )
        return new_block

    new_content, count = pattern.subn(replacement, content)

    if count == 0:
        print("No patch applied. Pattern not found in file.")
    else:
        print(f"Patch applied {count} time(s).")

    # Write the modified content back to the file.
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print(f"File '{file_path}' updated successfully.")


def main():
    if len(sys.argv) < 2:
        print("Usage: python apply_dummy_field_patch.py <path_to_generated_proto_file>")
        sys.exit(1)

    file_path = sys.argv[1]
    if not os.path.isfile(file_path):
        print(f"Error: File '{file_path}' does not exist.")
        sys.exit(1)

    apply_patch(file_path)


if __name__ == "__main__":
    main()
