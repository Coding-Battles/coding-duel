#!/usr/bin/env python3

import sys
import os

sys.path.append("/Users/andriysapeha/Documents/coding_duel/coding-duel")

from backend.code_testing.docker_runner import generate_java_wrapper

code = """class Solution {
    public int trap(int[] height) {
        return 42;
    }
}"""

wrapper = generate_java_wrapper("trap", code)
print("=== GENERATED JAVA WRAPPER FOR TRAP ===")

# Check if there's any JavaScript in the wrapper
if "var " in wrapper or "let " in wrapper or "function(" in wrapper:
    print("❌ FOUND JAVASCRIPT IN JAVA WRAPPER!")
    lines = wrapper.split("\n")
    for i, line in enumerate(lines):
        if "var " in line or "let " in line or "function(" in line:
            print(f"Line {i+1}: {line}")
else:
    print("✅ No JavaScript found in Java wrapper")

print("\nFirst 20 lines:")
lines = wrapper.split("\n")
for i, line in enumerate(lines[:20]):
    print(f"{i+1:2d}: {line}")
