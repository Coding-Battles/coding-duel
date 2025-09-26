#!/usr/bin/env python3
"""
Script to add comprehensive includes to all C++ test solution files
to ensure they compile independently without missing headers
"""

import os
import glob


def add_includes_to_cpp_file(filepath):
    """Add comprehensive includes to a C++ test solution file"""
    print(f"Processing: {filepath}")

    with open(filepath, "r") as f:
        content = f.read()

    # Check if it already has comprehensive includes
    if "#include <vector>" in content and "#include <string>" in content:
        print(f"  ✅ Already has includes: {filepath}")
        return

    # Add comprehensive includes at the top
    includes_header = """// Comprehensive C++ standard library includes
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
#include <random>
using namespace std;

"""

    # Add includes at the beginning
    updated_content = includes_header + content

    with open(filepath, "w") as f:
        f.write(updated_content)

    print(f"  ✅ Added includes: {filepath}")


def main():
    # Find all C++ test solution files
    patterns = ["backend/test-solutions/*.cpp", "frontend/cypress/test-solutions/*.cpp"]

    all_files = []
    for pattern in patterns:
        all_files.extend(glob.glob(pattern))

    print(f"Found {len(all_files)} C++ test solution files to update")

    for filepath in all_files:
        add_includes_to_cpp_file(filepath)

    print("\n✅ All C++ test solution files updated with comprehensive includes!")
    print("This ensures they will compile on any platform with any C++17 compiler.")


if __name__ == "__main__":
    main()
