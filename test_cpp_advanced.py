#!/usr/bin/env python3

import sys
import os

# Add the backend directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), "backend"))

from backend.models.questions import DockerRunRequest
from backend.code_testing.docker_runner import run_code_in_docker


def test_palindrome_number():
    """Test the palindrome-number problem to verify integer input/output."""

    user_code = """
class Solution {
public:
    bool isPalindrome(int x) {
        if (x < 0) return false;
        
        long original = x;
        long reversed = 0;
        
        while (x > 0) {
            reversed = reversed * 10 + x % 10;
            x /= 10;
        }
        
        return original == reversed;
    }
};
"""

    request = DockerRunRequest(
        code=user_code,
        language="cpp",
        function_name="isPalindrome",
        test_input={"x": 121},
        timeout=10,
    )

    print("🧪 Testing palindrome-number problem...")
    print(f"Function: {request.function_name}")
    print(f"Input: {request.test_input}")
    print()

    result = run_code_in_docker(request)

    print("📋 Result:")
    print(f"Success: {result.get('success')}")
    print(f"Output: {result.get('output')}")
    print(f"Expected: True")
    print(f"Execution time: {result.get('execution_time')}ms")
    if result.get("error"):
        print(f"Error: {result.get('error')}")

    return result


def test_climbing_stairs():
    """Test the climbing-stairs problem to verify integer input/output."""

    user_code = """
class Solution {
public:
    int climbStairs(int n) {
        if (n <= 2) return n;
        
        int prev2 = 1;
        int prev1 = 2;
        
        for (int i = 3; i <= n; i++) {
            int current = prev1 + prev2;
            prev2 = prev1;
            prev1 = current;
        }
        
        return prev1;
    }
};
"""

    request = DockerRunRequest(
        code=user_code,
        language="cpp",
        function_name="climbStairs",
        test_input={"n": 5},
        timeout=10,
    )

    print("\n🧪 Testing climbing-stairs problem...")
    print(f"Function: {request.function_name}")
    print(f"Input: {request.test_input}")
    print()

    result = run_code_in_docker(request)

    print("📋 Result:")
    print(f"Success: {result.get('success')}")
    print(f"Output: {result.get('output')}")
    print(f"Expected: 8")
    print(f"Execution time: {result.get('execution_time')}ms")
    if result.get("error"):
        print(f"Error: {result.get('error')}")

    return result


def test_container_with_most_water():
    """Test the container-with-most-water problem to verify array input handling."""

    user_code = """
class Solution {
public:
    int maxArea(const vector<int>& height) {
        int left = 0, right = height.size() - 1;
        int maxWater = 0;
        
        while (left < right) {
            int currentWater = min(height[left], height[right]) * (right - left);
            maxWater = max(maxWater, currentWater);
            
            if (height[left] < height[right]) {
                left++;
            } else {
                right--;
            }
        }
        
        return maxWater;
    }
};
"""

    request = DockerRunRequest(
        code=user_code,
        language="cpp",
        function_name="maxArea",
        test_input={"height": [1, 8, 6, 2, 5, 4, 8, 3, 7]},
        timeout=10,
    )

    print("\n🧪 Testing container-with-most-water problem...")
    print(f"Function: {request.function_name}")
    print(f"Input: {request.test_input}")
    print()

    result = run_code_in_docker(request)

    print("📋 Result:")
    print(f"Success: {result.get('success')}")
    print(f"Output: {result.get('output')}")
    print(f"Expected: 49")
    print(f"Execution time: {result.get('execution_time')}ms")
    if result.get("error"):
        print(f"Error: {result.get('error')}")

    return result


if __name__ == "__main__":
    print("🧪 Testing C++ Harness with Various Problem Types")
    print("=" * 60)

    # Test various problem types
    test_palindrome_number()
    test_climbing_stairs()
    test_container_with_most_water()

    print("\n✅ All advanced tests completed!")
