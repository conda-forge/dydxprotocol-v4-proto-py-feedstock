r"""
update_extensions.py

This script updates a .proto file by applying a series of substitutions for each
package specified. It mimics the following sed commands:

  for pkg in $(PROTO_PACKAGES); do
      sed -i "s|^package \($(PROTO_FILE_PREFIX)\)\?$$pkg\([;\.]\)|package $(PROTO_FILE_PREFIX)$$pkg\2|" "$target_file"
      sed -i "s|\([[:space:]]*\)use_package: {name: \"$$pkg|\1use_package: {name: \"$(PROTO_DIR_PREFIX)$$pkg|" "$target_file"
      sed -i "s|\($$pkg\.|($(PROTO_DIR_PREFIX)$$pkg.|g" "$target_file"
  done

Usage:
    python update_extensions.py --file target.proto --packages cosmos,amino --proto_file_prefix dydx_v4_ --proto_dir_prefix dydx_v4_

This will process target.proto and update any lines referencing each package in the list.
"""

import re
import argparse
import sys


def update_file_content(content, pkg, proto_file_prefix, sub_pkg=None, proto_fold_prefix=None):
    """
    For a given package 'pkg', update the content with the following substitutions:

    1. Package declaration:
       From: ^package (optional prefix)pkg([;|.])
       To:   package proto_file_prefix + pkg + \2

    2. use_package option:
       From: (leading whitespace)use_package: {name: "pkg
       To:   \1use_package: {name: "proto_dir_prefix + pkg

    3. Parenthesized reference:
       From: (pkg.
       To:   (proto_dir_prefix + pkg.
    """
    # Use multiline mode for matching lines
    if sub_pkg:
        pkg = f"{pkg}.{sub_pkg}"

    # Substitution 1: Package declaration
    pattern = re.compile(
        r'^(package\s+)(?:' + re.escape(proto_file_prefix) + r')?(' + re.escape(pkg) + r')([;\.])',
        re.MULTILINE
    )
    content = pattern.sub(r'\1' + proto_file_prefix + r'\2\3', content)

    # Substitution 2: use_package option
    # Match: any leading whitespace, then "use_package: {name: \"" then pkg
    pattern = re.compile(
        r'^([ \t]*use_package:\s*\{name:\s*")(?:' + re.escape(proto_file_prefix) + r')?(' + re.escape(pkg) + r')',
        re.MULTILINE
    )
    content = pattern.sub(r'\1' + proto_file_prefix + r'\2', content)

    # Substitution 3: Replace occurrences of "(pkg." with "(proto_dir_prefix + pkg."
    pattern = re.compile(r'([\("])' + re.escape(f'{pkg}.'), re.MULTILINE)
    content = pattern.sub(r'\1' + proto_file_prefix + pkg + '.', content)

    # Substitution 4: Replace occurrences of \spkg." with "(proto_dir_prefix + pkg."
    pattern = re.compile(r'(^\s*(?:repeated\s|\.)?)' + re.escape(f'{pkg}.'), re.MULTILINE)
    content = pattern.sub(r'\1' + proto_file_prefix + pkg + '.', content)

    if not proto_fold_prefix:
        return content

    # Substitution 5: Handle folder renaming
    pkg = pkg.replace(".", "/")
    pattern = re.compile(r'(^import ")' + re.escape(f'{pkg}/'), re.MULTILINE)
    content = pattern.sub(r'\1' + proto_fold_prefix + pkg + '/', content)

    # Substitution 6: Handle folder renaming
    pattern = re.compile(re.escape(f'"/{pkg}/'), re.MULTILINE)
    content = pattern.sub(f'"/{proto_fold_prefix}{pkg}/', content)

    return content


def main():
    parser = argparse.ArgumentParser(
        description="Update .proto file with new package names and update extensions."
    )
    parser.add_argument("--file", required=True, help="Path to the target .proto file to update")
    parser.add_argument("--packages", required=True,
                        help="Comma-separated list of package names to update (e.g. cosmos,amino)")
    parser.add_argument("--proto_file_prefix", required=True,
                        help="Prefix to use for package declarations (e.g. dydx_v4_)")
    parser.add_argument("--proto_fold_prefix", required=True,
                        help="Prefix to use for folder (e.g. dydx_v4_)")
    args = parser.parse_args()

    # Split the packages list by comma and strip whitespace
    pkgs = [pkg.strip() for pkg in args.packages.split(',') if pkg.strip()]

    try:
        with open(args.file, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading file {args.file}: {e}", file=sys.stderr)
        sys.exit(1)

    original_content = content

    # Process each package in turn.
    for pkg in pkgs:
        sub_pkg = 'api' if pkg == 'google' else None
        content = update_file_content(content, pkg, args.proto_file_prefix, sub_pkg, args.proto_fold_prefix)

    # If content changed, write it back.
    if content != original_content:
        try:
            with open(args.file, "w", encoding="utf-8") as f:
                f.write(content)
            # print(f"Updated file {args.file}")
        except Exception as e:
            print(f"Error writing file {args.file}: {e}", file=sys.stderr)
            sys.exit(1)
    # else:
    #     print(f"No changes made {args.file}.")


if __name__ == "__main__":
    main()
