#!/usr/bin/env python3
"""
Test subarray-sum-equals-k implementation across all languages
"""
import sys
from pathlib import Path
import argparse
import json

# Add backend to path
sys.path.append(str(Path(__file__).parent / "backend"))

from backend.models.questions import DockerRunRequest
from backend.code_testing.docker_runner import run_code_in_docker


def test_subarray_sum_java():
    java_code = """
import java.util.*;

class Solution {
    public int subarraySum(int[] nums, int k) {
        Map<Integer, Integer> prefixSumCount = new HashMap<>();
        prefixSumCount.put(0, 1);
        
        int count = 0;
        int prefixSum = 0;
        
        for (int num : nums) {
            prefixSum += num;
            
            if (prefixSumCount.containsKey(prefixSum - k)) {
                count += prefixSumCount.get(prefixSum - k);
            }
            
            prefixSumCount.put(prefixSum, prefixSumCount.getOrDefault(prefixSum, 0) + 1);
        }
        
        return count;
    }
}
"""

    test_input = {"nums": [1, 1, 1], "k": 2}

    request = DockerRunRequest(
        language="java",
        code=java_code,
        function_name="subarraySum",
        test_input=test_input,
    )

    result = run_code_in_docker(request)
    print(f"Java subarraySum result: {result}")
    return result


def test_subarray_sum_cpp():
    cpp_code = """
#include <vector>
#include <unordered_map>
using namespace std;

class Solution {
public:
    int subarraySum(vector<int>& nums, int k) {
        unordered_map<int, int> prefixSumCount;
        prefixSumCount[0] = 1;
        
        int count = 0;
        int prefixSum = 0;
        
        for (int num : nums) {
            prefixSum += num;
            
            if (prefixSumCount.find(prefixSum - k) != prefixSumCount.end()) {
                count += prefixSumCount[prefixSum - k];
            }
            
            prefixSumCount[prefixSum]++;
        }
        
        return count;
    }
};
"""

    test_input = {"nums": [1, 1, 1], "k": 2}

    request = DockerRunRequest(
        language="cpp",
        code=cpp_code,
        function_name="subarraySum",
        test_input=test_input,
    )

    result = run_code_in_docker(request)
    print(f"C++ subarraySum result: {result}")
    return result


if __name__ == "__main__":
    print("🧪 Testing subarraySum across multiple languages")
    test_subarray_sum_java()
    test_subarray_sum_cpp()
