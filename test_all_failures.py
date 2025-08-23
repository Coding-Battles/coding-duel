#!/usr/bin/env python3
"""
Comprehensive test script to check all failing Cypress test cases
Based on the 25 failures reported earlier.
"""

import requests
import json


def test_problem(problem_id, language, test_cases):
    """Test a specific problem with given test cases"""
    print(f"\n{'='*60}")
    print(f"Testing {problem_id.upper()} - {language.upper()}")
    print(f"{'='*60}")

    try:
        response = requests.post(
            "http://localhost:8000/run-code",
            json={
                "problem_id": problem_id,
                "language": language,
                "code": "",  # Will use default starter code
                "input": test_cases[0]["input"] if test_cases else {},
            },
            timeout=30,
        )

        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Success: {result.get('success', False)}")
            print(
                f"Passed: {result.get('passed_tests', 0)}/{result.get('total_tests', 0)}"
            )

            if not result.get("success", False):
                failures = result.get("test_failures", [])
                for i, failure in enumerate(failures[:2], 1):  # Show first 2 failures
                    print(f"Failure {i}:")
                    print(f"  Input: {failure.get('input', 'N/A')}")
                    print(f"  Expected: {failure.get('expected', 'N/A')}")
                    print(f"  Actual: {failure.get('actual', 'N/A')}")
        else:
            print(f"HTTP Error: {response.text}")

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")


def main():
    """Run all the failing test cases"""

    # TreeNode/ListNode issues (6 failures)
    treenode_problems = [
        ("same-tree", "java", [{"input": {"p": [1, 2, 3], "q": [1, 2, 3]}}]),
        ("invert-binary-tree", "java", [{"input": {"root": [4, 2, 7, 1, 3, 6, 9]}}]),
        (
            "maximum-depth-of-binary-tree",
            "python",
            [{"input": {"root": [3, 9, 20, None, None, 15, 7]}}],
        ),
        ("add-two-numbers", "java", [{"input": {"l1": [2, 4, 3], "l2": [5, 6, 4]}}]),
        ("same-tree", "cpp", [{"input": {"p": [1, 2, 3], "q": [1, 2, 3]}}]),
        (
            "maximum-depth-of-binary-tree",
            "cpp",
            [{"input": {"root": [3, 9, 20, None, None, 15, 7]}}],
        ),
    ]

    # Java wrapper issues (6 failures)
    java_problems = [
        ("add-binary", "java", [{"input": {"a": "11", "b": "1"}}]),
        (
            "merge-intervals",
            "java",
            [{"input": {"intervals": [[1, 3], [2, 6], [8, 10], [15, 18]]}}],
        ),
        ("valid-anagram", "java", [{"input": {"s": "anagram", "t": "nagaram"}}]),
        ("two-sum", "java", [{"input": {"nums": [2, 7, 11, 15], "target": 9}}]),
        ("palindrome-number", "java", [{"input": {"x": 121}}]),
        ("reverse-integer", "java", [{"input": {"x": 123}}]),
    ]

    # C++ harness issues (5 failures)
    cpp_problems = [
        ("edit-distance", "cpp", [{"input": {"word1": "horse", "word2": "ros"}}]),
        ("add-binary", "cpp", [{"input": {"a": "11", "b": "1"}}]),
        (
            "merge-intervals",
            "cpp",
            [{"input": {"intervals": [[1, 3], [2, 6], [8, 10], [15, 18]]}}],
        ),
        ("valid-anagram", "cpp", [{"input": {"s": "anagram", "t": "nagaram"}}]),
        ("palindrome-number", "cpp", [{"input": {"x": 121}}]),
    ]

    # Array manipulation issues (4 failures)
    array_problems = [
        ("two-sum", "python", [{"input": {"nums": [2, 7, 11, 15], "target": 9}}]),
        ("reverse-integer", "python", [{"input": {"x": 123}}]),
        (
            "merge-intervals",
            "python",
            [{"input": {"intervals": [[1, 3], [2, 6], [8, 10], [15, 18]]}}],
        ),
        ("valid-anagram", "python", [{"input": {"s": "anagram", "t": "nagaram"}}]),
    ]

    # Infrastructure issues (4 failures)
    infra_problems = [
        ("edit-distance", "python", [{"input": {"word1": "horse", "word2": "ros"}}]),
        (
            "edit-distance",
            "javascript",
            [{"input": {"word1": "horse", "word2": "ros"}}],
        ),
        ("add-binary", "javascript", [{"input": {"a": "11", "b": "1"}}]),
        ("palindrome-number", "javascript", [{"input": {"x": 121}}]),
    ]

    print("🔍 COMPREHENSIVE FAILURE ANALYSIS")
    print("=" * 60)

    print("\n📊 TESTING CATEGORIES:")
    print("1. TreeNode/ListNode Issues (6 failures)")
    print("2. Java Wrapper Issues (6 failures)")
    print("3. C++ Harness Issues (5 failures)")
    print("4. Array Manipulation Issues (4 failures)")
    print("5. Infrastructure Issues (4 failures)")

    all_problems = (
        treenode_problems
        + java_problems
        + cpp_problems
        + array_problems
        + infra_problems
    )

    print(f"\n🎯 TOTAL PROBLEMS TO TEST: {len(all_problems)}")

    try:
        # Test server connectivity first
        response = requests.get("http://localhost:8000/health", timeout=5)
        print(f"✅ Server is running (status: {response.status_code})")
    except requests.exceptions.RequestException:
        print("❌ Server is not running or not responding")
        print("💡 Please start the server with: cd backend && python main.py")
        return

    # Run all tests
    for problem_id, language, test_cases in all_problems:
        test_problem(problem_id, language, test_cases)

    print(f"\n{'='*60}")
    print("🏁 ANALYSIS COMPLETE")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
