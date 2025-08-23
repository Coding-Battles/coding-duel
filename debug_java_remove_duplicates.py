#!/usr/bin/env python3
"""
Debug the Java remove duplicates issue
"""
import sys
import json
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent / "backend"))

from backend.models.questions import DockerRunRequest
from backend.code_testing.docker_runner import run_code_in_docker


def test_java_remove_duplicates():
    """Test Java remove duplicates execution."""

    java_code = """
import java.util.*;

class Solution {
    public int removeDuplicates(int[] nums) {
        if (nums.length == 0) {
            return 0;
        }
        
        int writeIndex = 1;
        
        for (int readIndex = 1; readIndex < nums.length; readIndex++) {
            if (nums[readIndex] != nums[readIndex - 1]) {
                nums[writeIndex] = nums[readIndex];
                writeIndex++;
            }
        }
        
        return writeIndex;
    }
}
"""

    request = DockerRunRequest(
        code=java_code,
        language="java",
        test_input={"nums": [1, 1, 2]},
        timeout=10,
        function_name="removeDuplicates",
    )

    print("🧪 Testing Java remove duplicates...")
    print(f"Input: {request.test_input}")
    print(f"Expected: 2")

    result = run_code_in_docker(request)

    print(f"Success: {result.get('success', False)}")
    print(f"Output: {result.get('output')}")
    print(f"Error: {result.get('error')}")

    return result


if __name__ == "__main__":
    test_java_remove_duplicates()
