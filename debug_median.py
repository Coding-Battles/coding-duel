#!/usr/bin/env python3

import sys
import os

sys.path.append("/Users/andriysapeha/Documents/coding_duel/coding-duel")

from backend.code_testing.docker_runner import generate_java_wrapper

code = """class Solution {
    public double findMedianSortedArrays(int[] nums1, int[] nums2) {
        return 2.5;
    }
}"""

wrapper = generate_java_wrapper("findMedianSortedArrays", code)

# Find the nums1/nums2 pattern in the parameter handling
lines = wrapper.split("\n")
found_pattern = False
for i, line in enumerate(lines):
    if "nums1" in line and "nums2" in line and "contains" in line:
        found_pattern = True
        print("✅ Found nums1/nums2 pattern in Java wrapper:")
        # Print the pattern and a few lines after it
        for j in range(i, min(i + 8, len(lines))):
            print(f"  {lines[j]}")
        break

if not found_pattern:
    print("❌ nums1/nums2 pattern not found in Java wrapper")

print("\nTesting parameter extraction with sample input:")
print('Input: {"nums1": [1, 3], "nums2": [2]}')
print("Expected: Should extract nums1=[1,3] and nums2=[2]")
