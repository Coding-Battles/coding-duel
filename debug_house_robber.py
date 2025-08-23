#!/usr/bin/env python3
"""
Test house-robber implementation across all languages
"""
import sys
from pathlib import Path
import argparse
import json

# Add backend to path
sys.path.append(str(Path(__file__).parent / "backend"))

from backend.models.questions import DockerRunRequest
from backend.code_testing.docker_runner import run_code_in_docker


def test_house_robber_java():
    java_code = """
class Solution {
    public int rob(int[] nums) {
        if (nums.length == 0) return 0;
        if (nums.length == 1) return nums[0];
        
        int prev2 = 0;
        int prev1 = 0;
        
        for (int num : nums) {
            int current = Math.max(prev1, prev2 + num);
            prev2 = prev1;
            prev1 = current;
        }
        
        return prev1;
    }
}
"""

    test_input = {"nums": [2, 7, 9, 3, 1]}

    request = DockerRunRequest(
        language="java", code=java_code, function_name="rob", test_input=test_input
    )

    result = run_code_in_docker(request)
    print(f"Java house-robber result: {result.get('result', 'No result')}")
    return result


def test_house_robber_cpp():
    cpp_code = """
#include <vector>
#include <algorithm>
using namespace std;

class Solution {
public:
    int rob(vector<int>& nums) {
        if (nums.empty()) return 0;
        if (nums.size() == 1) return nums[0];
        
        int prev2 = 0;
        int prev1 = 0;
        
        for (int num : nums) {
            int current = max(prev1, prev2 + num);
            prev2 = prev1;
            prev1 = current;
        }
        
        return prev1;
    }
};
"""

    test_input = {"nums": [2, 7, 9, 3, 1]}

    request = DockerRunRequest(
        language="cpp", code=cpp_code, function_name="rob", test_input=test_input
    )

    result = run_code_in_docker(request)
    print(f"C++ house-robber result: {result.get('result', 'No result')}")
    return result


if __name__ == "__main__":
    print("🧪 Testing house-robber across multiple languages")
    test_house_robber_java()
    test_house_robber_cpp()
