#!/usr/bin/env python3
"""
Test the actual comparison logic with moveZeroes-like data
"""
import sys
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent / "backend"))

from backend.services.test_execution_service import TestExecutionService


def test_comparison():
    """Test the comparison logic directly."""

    # Test cases that mirror what moveZeroes should produce
    test_cases = [
        {"actual": [1, 3, 12, 0, 0], "expected": [1, 3, 12, 0, 0], "should_pass": True},
        {
            "actual": "[1, 3, 12, 0, 0]",  # String version
            "expected": [1, 3, 12, 0, 0],
            "should_pass": True,  # normalize_answer should handle this
        },
        {
            "actual": [1, 3, 12, 0, 0],
            "expected": [1, 3, 12],  # Different expected
            "should_pass": False,
        },
    ]

    print("Testing comparison logic:")
    print("=" * 50)

    for i, case in enumerate(test_cases):
        result = TestExecutionService.check_answer_in_expected(
            case["actual"], case["expected"]
        )

        status = "✅ PASS" if result == case["should_pass"] else "❌ FAIL"
        print(f"Test {i+1}: {status}")
        print(f"  Actual: {repr(case['actual'])} (type: {type(case['actual'])})")
        print(f"  Expected: {repr(case['expected'])} (type: {type(case['expected'])})")
        print(f"  Result: {result} (expected: {case['should_pass']})")
        print()

        if result != case["should_pass"]:
            return False

    print("🎉 All comparison tests pass!")
    return True


if __name__ == "__main__":
    test_comparison()
