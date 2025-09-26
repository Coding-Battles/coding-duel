#!/usr/bin/env python3

import os

# Test the harness file logic
function_name = "burst-balloons"
harness_path = (
    f"backend/code_testing/cpp_harnesses/harnesses/{function_name}/harness.cpp"
)

print(f"Looking for harness file: {harness_path}")
print(f"File exists: {os.path.exists(harness_path)}")

if os.path.exists(harness_path):
    with open(harness_path, "r") as f:
        harness_content = f.read()

    print("\nOriginal harness content (first 200 chars):")
    print(harness_content[:200])

    # Test user code
    processed_code = """
class Solution {
public:
    int maxCoins(vector<int>& nums) {
        return 167;
    }
};"""

    # Replace #include "userfunc.h" with the actual user code
    wrapped_code = harness_content.replace(
        '#include "userfunc.h"', f"// User solution code\n{processed_code}"
    )

    print("\nWrapped code (first 400 chars):")
    print(wrapped_code[:400])

    print(f"\nTotal wrapped code length: {len(wrapped_code)} characters")
else:
    print("Harness file not found!")
