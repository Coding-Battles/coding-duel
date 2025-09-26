#!/usr/bin/env python3
"""
Test the new signature-based Java wrapper implementation
"""
import sys
import os

sys.path.append("/Users/andriysapeha/Documents/coding_duel/coding-duel")

from backend.code_testing.docker_runner import (
    generate_java_wrapper,
    load_question_signature,
)


def test_signature_loading():
    """Test signature loading for different problems"""

    # Test 1: Two Sum - should have int[] nums, int target
    print("=== Testing Signature Loading ===")
    sig = load_question_signature("two-sum")
    print(f"Two Sum signature: {sig}")

    # Test 2: Merge Two Sorted Lists - should have ListNode list1, ListNode list2
    sig2 = load_question_signature("merge-two-sorted-lists")
    print(f"Merge Two Sorted Lists signature: {sig2}")

    # Test 3: Invert Binary Tree - should have TreeNode root
    sig3 = load_question_signature("invert-binary-tree")
    print(f"Invert Binary Tree signature: {sig3}")


def test_wrapper_generation():
    """Test Java wrapper generation with signature"""

    print("\n=== Testing Wrapper Generation ===")

    # Simple two-sum code
    java_code = """
class Solution {
    public int[] twoSum(int[] nums, int target) {
        for (int i = 0; i < nums.length; i++) {
            for (int j = i + 1; j < nums.length; j++) {
                if (nums[i] + nums[j] == target) {
                    return new int[]{i, j};
                }
            }
        }
        return new int[]{};
    }
}
"""

    wrapper = generate_java_wrapper("twoSum", java_code, "two-sum")
    print("Generated wrapper (first 500 chars):")
    print(wrapper[:500] + "...")

    # Check if signature is embedded
    if "SIGNATURE_JSON" in wrapper:
        print("✅ Signature embedding: SUCCESS")
    else:
        print("❌ Signature embedding: FAILED")

    # Check if new parameter extraction method is used
    if "extractParametersWithSignature" in wrapper:
        print("✅ New parameter extraction: SUCCESS")
    else:
        print("❌ New parameter extraction: FAILED")


if __name__ == "__main__":
    test_signature_loading()
    test_wrapper_generation()
