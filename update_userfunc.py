#!/usr/bin/env python3
"""
Script to update all userfunc.h files to use the common_includes.h header
instead of bits/stdc++.h
"""

import os
import glob
import re


def update_userfunc_file(filepath):
    """Update a single userfunc.h file to use common_includes.h"""
    print(f"Updating: {filepath}")

    with open(filepath, "r") as f:
        content = f.read()

    # If already using common_includes.h, skip
    if '#include "../../../common_includes.h"' in content:
        print(f"  Already updated: {filepath}")
        return

    # Replace #include <bits/stdc++.h> with common_includes.h
    if "#include <bits/stdc++.h>" in content:
        content = content.replace(
            "#include <bits/stdc++.h>\nusing namespace std;",
            '#include "../../../common_includes.h"',
        )

        with open(filepath, "w") as f:
            f.write(content)
        print(f"  ✅ Updated: {filepath}")
    else:
        print(f"  ⚠️  No bits/stdc++.h found: {filepath}")


def main():
    # Find all userfunc.h files
    userfunc_pattern = "backend/code_testing/cpp_harnesses/harnesses/*/userfunc.h"
    userfunc_files = glob.glob(userfunc_pattern)

    print(f"Found {len(userfunc_files)} userfunc.h files to update")

    for filepath in userfunc_files:
        update_userfunc_file(filepath)

    print("\n✅ All userfunc.h files updated!")


if __name__ == "__main__":
    main()
