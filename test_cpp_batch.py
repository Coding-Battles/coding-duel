#!/usr/bin/env python3
import requests
import json

# Simple C++ two sum solution
cpp_code = """class Solution {
public:
    vector<int> twoSum(vector<int>& nums, int target) {
        for (int i = 0; i < nums.size(); i++) {
            for (int j = i + 1; j < nums.size(); j++) {
                if (nums[i] + nums[j] == target) {
                    return {i, j};
                }
            }
        }
        return {};
    }
};"""


def test_cpp_batch():
    print("🧪 Testing C++ batch execution...")

    url = "http://localhost:8000/api/run-sample-tests"
    payload = {
        "code": cpp_code,
        "language": "cpp",
        "question_name": "two-sum",
        "timeout": 10,
        "player_id": "test_player",
        "timer": 300,
    }

    try:
        response = requests.post(url, json=payload)
        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print(f"Success: {result.get('success', 'Unknown')}")
            print(f"Tests passed: {result.get('tests_passed', 0)}")
            print(f"Tests failed: {result.get('tests_failed', 0)}")
            print(f"Execution time: {result.get('total_execution_time', 0)}ms")

            # Look for batch execution logs
            if "test_results" in result:
                print(f"Total test cases: {len(result['test_results'])}")
                for i, test in enumerate(result["test_results"]):
                    print(
                        f"  Test {i+1}: {'PASS' if test.get('passed') else 'FAIL'} ({test.get('execution_time', 0)}ms)"
                    )
        else:
            print(f"Error: {response.text}")

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    test_cpp_batch()
