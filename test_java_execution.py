#!/usr/bin/env python3
"""
Test the Java wrapper with actual execution
"""
import sys
import os
import json

sys.path.append("/Users/andriysapeha/Documents/coding_duel/coding-duel")

from backend.code_testing.docker_runner import run_code_in_docker
from backend.models.questions import DockerRunRequest


def test_java_execution():
    """Test Java execution with signature-based parameter conversion"""

    print("=== Testing Java Execution with Signature ===")

    # Test two-sum with signature-based conversion
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

    # Create request with question_name for signature loading
    request = DockerRunRequest(
        language="java",
        code=java_code,
        test_input={"nums": [2, 7, 11, 15], "target": 9},
        function_name="twoSum",
        question_name="two-sum",  # This should trigger signature loading
    )

    print(f"Request: {request}")
    print(f"Test input: {request.test_input}")

    try:
        result = run_code_in_docker(request)
        print(f"✅ Execution result: {result}")

        if result and result.get("success"):
            print("🎉 Java signature-based parameter conversion: SUCCESS!")
        else:
            print(f"❌ Execution failed: {result}")

    except Exception as e:
        print(f"❌ Exception during execution: {e}")


if __name__ == "__main__":
    test_java_execution()
