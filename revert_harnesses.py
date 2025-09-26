#!/usr/bin/env python3
"""
Script to revert all C++ harness files back to using bits/stdc++.h
since the common_includes.h approach has path issues in Docker
"""

import os
import glob


def revert_harness_file(filepath):
    """Revert a single harness file back to bits/stdc++.h"""
    print(f"Reverting: {filepath}")

    with open(filepath, "r") as f:
        content = f.read()

    # Replace common_includes.h with bits/stdc++.h
    if '#include "../../common_includes.h"' in content:
        content = content.replace(
            '#include "../../common_includes.h"',
            "#include <bits/stdc++.h>\nusing namespace std;",
        )

        with open(filepath, "w") as f:
            f.write(content)
        print(f"  ✅ Reverted: {filepath}")
    else:
        print(f"  ⚠️  No common_includes.h found: {filepath}")


def main():
    # Find all harness.cpp files
    harness_pattern = "backend/code_testing/cpp_harnesses/harnesses/*/harness.cpp"
    harness_files = glob.glob(harness_pattern)

    print(f"Found {len(harness_files)} harness files to revert")

    for filepath in harness_files:
        revert_harness_file(filepath)

    print("\n✅ All harness files reverted to bits/stdc++.h!")


if __name__ == "__main__":
    main()
