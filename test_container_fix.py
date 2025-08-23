#!/usr/bin/env python3
"""
Test the container with most water solution with the fixed comparison logic.
"""
import sys
import json
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent / "backend"))

from backend.services.test_execution_service import TestExecutionService


def test_container_solution():
    """Test a container with most water solution."""

    # Load the test cases
    test_cases = TestExecutionService.load_test_cases("container-with-most-water")

    print("Testing Container with Most Water comparison logic:")
    print("=" * 50)

    # Simulate what happens in the real test execution
    # These are the outputs that would come from running the solution
    simulated_outputs = [49, 1, 16, 2, 4]  # Correct outputs for first 5 test cases

    for i, (test_case, output) in enumerate(zip(test_cases, simulated_outputs)):
        expected = test_case["expected"]

        # This is the key line that was failing before
        passed = TestExecutionService.check_answer_in_expected(output, expected)

        print(f"Test {i+1}:")
        print(f"  Input: {test_case['input']}")
        print(f"  Expected: {expected} (type: {type(expected)})")
        print(f"  Actual: {output} (type: {type(output)})")
        print(f"  Passed: {passed}")
        print()

        if not passed:
            print(f"❌ FAILURE: Output {output} didn't match expected {expected}")
            return False

    print("🎉 All container-with-most-water tests now pass correctly!")
    return True


if __name__ == "__main__":
    test_container_solution()
