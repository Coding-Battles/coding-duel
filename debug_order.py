#!/usr/bin/env python3

import sys
import os

sys.path.append("/Users/andriysapeha/Documents/coding_duel/coding-duel")

from backend.code_testing.docker_runner import generate_java_wrapper

# Test the problematic case
code = """class Solution {
    public String alienOrder(String[] words) {
        return "test";
    }
}"""

wrapper = generate_java_wrapper("alienOrder", code)

# Find the extractParametersInJsonOrder method
lines = wrapper.split("\n")
in_method = False
for i, line in enumerate(lines):
    if "extractParametersInJsonOrder" in line and "private static Object[]" in line:
        in_method = True
        print("=== extractParametersInJsonOrder method ===")
    elif (
        in_method and line.strip() == "}" and "return params.toArray()" in lines[i - 2]
    ):
        print(line)
        break

    if in_method:
        print(line)
