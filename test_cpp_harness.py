#!/usr/bin/env python3

import sys
import os

# Add the backend directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), "backend"))

from backend.models.questions import DockerRunRequest
from backend.code_testing.docker_runner import run_code_in_docker


def test_two_sum():
    """Test the two-sum problem with C++ harness."""

    user_code = """
class Solution {
public:
    vector<int> twoSum(const vector<int>& nums, int target) {
        unordered_map<int, int> numMap;
        for (int i = 0; i < nums.size(); i++) {
            int complement = target - nums[i];
            if (numMap.find(complement) != numMap.end()) {
                return {numMap[complement], i};
            }
            numMap[nums[i]] = i;
        }
        return {};
    }
};
"""

    request = DockerRunRequest(
        code=user_code,
        language="cpp",
        function_name="twoSum",
        test_input={"nums": [2, 7, 11, 15], "target": 9},
        timeout=10,
    )

    print("🧪 Testing C++ harness with two-sum problem...")
    print(f"Function: {request.function_name}")
    print(f"Input: {request.test_input}")
    print()

    result = run_code_in_docker(request)

    print("📋 Result:")
    print(f"Success: {result.get('success')}")
    print(f"Output: {result.get('output')}")
    print(f"Execution time: {result.get('execution_time')}ms")
    if result.get("error"):
        print(f"Error: {result.get('error')}")

    return result


def test_fizz_buzz():
    """Test the fizz-buzz problem with C++ harness."""

    user_code = """
class Solution {
public:
    vector<string> fizzBuzz(int n) {
        vector<string> result;
        for (int i = 1; i <= n; i++) {
            if (i % 15 == 0) {
                result.push_back("FizzBuzz");
            } else if (i % 3 == 0) {
                result.push_back("Fizz");
            } else if (i % 5 == 0) {
                result.push_back("Buzz");
            } else {
                result.push_back(to_string(i));
            }
        }
        return result;
    }
};
"""

    request = DockerRunRequest(
        code=user_code,
        language="cpp",
        function_name="fizzBuzz",
        test_input={"n": 15},
        timeout=10,
    )

    print("\n🧪 Testing C++ harness with fizz-buzz problem...")
    print(f"Function: {request.function_name}")
    print(f"Input: {request.test_input}")
    print()

    result = run_code_in_docker(request)

    print("📋 Result:")
    print(f"Success: {result.get('success')}")
    print(f"Output: {result.get('output')}")
    print(f"Execution time: {result.get('execution_time')}ms")
    if result.get("error"):
        print(f"Error: {result.get('error')}")

    return result


def test_unknown_function():
    """Test with an unknown function to verify fallback behavior."""

    user_code = """
class Solution {
public:
    int unknownFunction(int x) {
        return x * 2;
    }
};
"""

    request = DockerRunRequest(
        code=user_code,
        language="cpp",
        function_name="unknownFunction",
        test_input={"x": 5},
        timeout=10,
    )

    print("\n🧪 Testing C++ harness with unknown function (should use fallback)...")
    print(f"Function: {request.function_name}")
    print(f"Input: {request.test_input}")
    print()

    result = run_code_in_docker(request)

    print("📋 Result:")
    print(f"Success: {result.get('success')}")
    print(f"Output: {result.get('output')}")
    print(f"Execution time: {result.get('execution_time')}ms")
    if result.get("error"):
        print(f"Error: {result.get('error')}")

    return result


if __name__ == "__main__":
    print("🚀 Testing C++ Harness Implementation")
    print("=" * 50)

    # Test known functions
    test_two_sum()
    test_fizz_buzz()

    # Test unknown function fallback
    test_unknown_function()

    print("\n✅ All tests completed!")
