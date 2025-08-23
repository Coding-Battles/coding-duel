#!/usr/bin/env python3
"""
Test script to verify the comparison logic fix.
"""
import sys
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent / "backend"))

from backend.services.test_execution_service import TestExecutionService


def test_comparison_logic():
    """Test the fixed comparison logic."""
    print("Testing comparison logic fix...")

    # Test cases that were failing
    test_cases = [
        {"actual": 49, "expected": [49], "should_pass": True},
        {"actual": 1, "expected": [1], "should_pass": True},
        {"actual": 16, "expected": [16], "should_pass": True},
        {"actual": 50, "expected": [49], "should_pass": False},  # Different values
        {"actual": "49", "expected": [49], "should_pass": True},  # String vs int
        {"actual": [1, 2], "expected": [[1, 2]], "should_pass": True},  # Array expected
    ]

    all_passed = True
    for i, test_case in enumerate(test_cases, 1):
        actual = test_case["actual"]
        expected = test_case["expected"]
        should_pass = test_case["should_pass"]

        result = TestExecutionService.check_answer_in_expected(actual, expected)

        if result == should_pass:
            print(
                f"✅ Test {i}: {actual} vs {expected} -> {result} (expected {should_pass})"
            )
        else:
            print(
                f"❌ Test {i}: {actual} vs {expected} -> {result} (expected {should_pass})"
            )
            all_passed = False

    if all_passed:
        print("\n🎉 All tests passed! The comparison logic fix is working correctly.")
    else:
        print("\n❌ Some tests failed. The fix needs more work.")

    return all_passed


if __name__ == "__main__":
    test_comparison_logic()
