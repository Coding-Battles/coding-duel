#!/usr/bin/env python3

import subprocess
import tempfile
import os
import json


def test_platform_independent_compilation():
    """Test C++ compilation for multiple problems to ensure platform independence"""

    # Test cases: Different problems with different C++ features
    test_cases = [
        {
            "name": "two-sum",
            "code": """class Solution {
public:
    vector<int> twoSum(vector<int>& nums, int target) {
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
};""",
            "input": '{"nums": [2,7,11,15], "target": 9}',
        },
        {
            "name": "container-with-most-water",
            "code": """class Solution {
public:
    int maxArea(vector<int>& height) {
        int left = 0, right = height.size() - 1;
        int maxWater = 0;
        
        while (left < right) {
            int width = right - left;
            int minHeight = min(height[left], height[right]);
            maxWater = max(maxWater, width * minHeight);
            
            if (height[left] < height[right]) {
                left++;
            } else {
                right--;
            }
        }
        
        return maxWater;
    }
};""",
            "input": '{"height": [1,8,6,2,5,4,8,3,7]}',
        },
    ]

    for test_case in test_cases:
        print(f"\n=== Testing {test_case['name']} ===")
        test_problem(test_case["name"], test_case["code"], test_case["input"])


def test_problem(problem_name, user_code, test_input):
    """Test a specific problem with user code"""

    harness_path = f"/Users/andriysapeha/Documents/coding_duel/coding-duel/backend/code_testing/cpp_harnesses/harnesses/{problem_name}/harness.cpp"

    if not os.path.exists(harness_path):
        print(f"❌ Harness not found: {harness_path}")
        return

    with open(harness_path, "r") as f:
        harness_content = f.read()

    # Apply the EXACT same replacement as backend
    user_code_with_namespace = f"""// User solution code with namespace access
using namespace std;

{user_code}"""

    wrapped_code = harness_content.replace(
        '#include "userfunc.h"',
        user_code_with_namespace,
    )

    # Create temporary files
    with tempfile.NamedTemporaryFile(mode="w", suffix=".cpp", delete=False) as cpp_file:
        cpp_file.write(wrapped_code)
        cpp_file.flush()

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as input_file:
            input_file.write(test_input)
            input_file.flush()

            try:
                # Use docker for platform-independent testing
                docker_cmd = [
                    "docker",
                    "run",
                    "--rm",
                    "-v",
                    f"{cpp_file.name}:/tmp/solution.cpp:ro",
                    "-v",
                    f"{input_file.name}:/tmp/input.json:ro",
                    "frolvlad/alpine-gxx:latest",
                    "sh",
                    "-c",
                    """
                    cd /tmp &&
                    echo "=== Compiling ===" &&
                    g++ -std=c++17 -o solution solution.cpp 2>&1 &&
                    echo "=== Running ===" &&
                    timeout 5 ./solution < input.json 2>&1
                    """,
                ]

                result = subprocess.run(
                    docker_cmd, capture_output=True, text=True, timeout=15
                )

                if result.returncode == 0:
                    print("✅ SUCCESS - Compilation and execution completed")
                    output_lines = result.stdout.strip().split("\n")
                    for line in output_lines:
                        if line.startswith('{"result"'):
                            print(f"   Result: {line}")
                else:
                    print("❌ FAILED")
                    if "error:" in result.stdout.lower():
                        print("   Compilation errors found:")
                        for line in result.stdout.split("\n"):
                            if "error:" in line.lower():
                                print(f"   {line}")
                    else:
                        print(f"   Output: {result.stdout[:500]}")

            except subprocess.TimeoutExpired:
                print("⏱️ TIMEOUT")
            except Exception as e:
                print(f"💥 ERROR: {e}")
            finally:
                # Cleanup
                try:
                    os.unlink(cpp_file.name)
                    os.unlink(input_file.name)
                except:
                    pass


if __name__ == "__main__":
    test_platform_independent_compilation()
