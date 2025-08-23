#!/usr/bin/env python3
"""
Test Java container with most water with explicit pattern handling
"""
import sys
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent / "backend"))

from backend.models.questions import DockerRunRequest
from backend.code_testing.docker_runner import run_code_in_docker


def test_java_container():
    """Test Java container with most water execution."""

    java_code = """
import java.util.*;

class Solution {
    public int maxArea(int[] height) {
        int left = 0, right = height.length - 1;
        int maxArea = 0;
        
        while (left < right) {
            int width = right - left;
            int area = Math.min(height[left], height[right]) * width;
            maxArea = Math.max(maxArea, area);
            
            if (height[left] < height[right]) {
                left++;
            } else {
                right--;
            }
        }
        
        return maxArea;
    }
}
"""

    request = DockerRunRequest(
        code=java_code,
        language="java",
        test_input={"height": [1, 8, 6, 2, 5, 4, 8, 3, 7]},
        timeout=10,
        function_name="maxArea",
    )

    print("🧪 Testing Java container with most water...")
    print(f"Input: {request.test_input}")
    print(f"Expected: 49")

    result = run_code_in_docker(request)

    print(f"Success: {result.get('success', False)}")
    print(f"Output: {result.get('output')}")
    print(f"Error: {result.get('error')}")

    return result


if __name__ == "__main__":
    test_java_container()
