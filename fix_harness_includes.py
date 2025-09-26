#!/usr/bin/env python3
"""
Script to replace bits/stdc++.h with explicit standard headers in all harness files
for better portability across different compilers and systems
"""

import os
import glob


def update_harness_file(filepath):
    """Replace bits/stdc++.h with explicit headers in a harness file"""
    print(f"Updating: {filepath}")

    with open(filepath, "r") as f:
        content = f.read()

    # Check if it uses bits/stdc++.h
    if "#include <bits/stdc++.h>" in content:
        # Replace with comprehensive explicit headers
        explicit_headers = """// Comprehensive standard library includes for portability
#include <iostream>
#include <string>
#include <vector>
#include <unordered_map>
#include <unordered_set>
#include <map>
#include <set>
#include <queue>
#include <stack>
#include <deque>
#include <list>
#include <algorithm>
#include <numeric>
#include <climits>
#include <cmath>
#include <sstream>
#include <utility>
#include <chrono>
#include <functional>
#include <iomanip>
#include <bitset>
#include <array>
#include <memory>
#include <iterator>
#include <random>"""

        content = content.replace("#include <bits/stdc++.h>", explicit_headers)

        with open(filepath, "w") as f:
            f.write(content)
        print(f"  ✅ Updated: {filepath}")
    else:
        print(f"  ⚠️  No bits/stdc++.h found: {filepath}")


def main():
    # Find all harness.cpp files
    harness_pattern = "backend/code_testing/cpp_harnesses/harnesses/*/harness.cpp"
    harness_files = glob.glob(harness_pattern)

    print(f"Found {len(harness_files)} harness files to update")

    for filepath in harness_files:
        update_harness_file(filepath)

    print("\n✅ All harness files updated with explicit headers!")
    print(
        "This should fix compilation issues on macOS and other systems where bits/stdc++.h is not available."
    )


if __name__ == "__main__":
    main()
