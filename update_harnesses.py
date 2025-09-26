#!/usr/bin/env python3
"""
Script to update all C++ harness files to use the common_includes.h header
instead of individual includes or bits/stdc++.h
"""

import os
import glob
import re


def update_harness_file(filepath):
    """Update a single harness file to use common_includes.h"""
    print(f"Updating: {filepath}")

    with open(filepath, "r") as f:
        content = f.read()

    # Pattern to match the current include section
    # Look for #include "userfunc.h" followed by either:
    # - #include <bits/stdc++.h>
    # - Multiple #include statements
    # - Already updated common_includes.h

    # If already using common_includes.h, skip
    if '#include "../../common_includes.h"' in content:
        print(f"  Already updated: {filepath}")
        return

    # Replace the include section
    patterns = [
        # Pattern 1: userfunc.h + bits/stdc++.h
        (
            r'#include "userfunc\.h"\s*\n#include <bits/stdc\+\+\.h>\s*\nusing namespace std;',
            '#include "userfunc.h"\n#include "../../common_includes.h"',
        ),
        # Pattern 2: userfunc.h + multiple individual includes
        (
            r'#include "userfunc\.h"\s*\n(?:#include <[^>]+>\s*\n)*using namespace std;',
            '#include "userfunc.h"\n#include "../../common_includes.h"',
        ),
        # Pattern 3: Just userfunc.h (no other includes)
        (
            r'#include "userfunc\.h"\s*\n(?!#include)',
            '#include "userfunc.h"\n#include "../../common_includes.h"\n',
        ),
    ]

    updated = False
    for pattern, replacement in patterns:
        if re.search(pattern, content):
            content = re.sub(pattern, replacement, content)
            updated = True
            break

    if updated:
        with open(filepath, "w") as f:
            f.write(content)
        print(f"  ✅ Updated: {filepath}")
    else:
        print(f"  ⚠️  No matching pattern found: {filepath}")


def main():
    # Find all harness.cpp files
    harness_pattern = "backend/code_testing/cpp_harnesses/harnesses/*/harness.cpp"
    harness_files = glob.glob(harness_pattern)

    print(f"Found {len(harness_files)} harness files to update")

    for filepath in harness_files:
        update_harness_file(filepath)

    print("\n✅ All harness files updated!")
    print(
        "Note: You may need to reload VS Code window for IntelliSense to work properly."
    )


if __name__ == "__main__":
    main()
