#!/usr/bin/env python3

import subprocess
import tempfile
import os
import json


def test_comprehensive_cpp_support():
    """Test that users can submit C++ code without includes and it works"""

    test_cases = [
        {
            "name": "two-sum",
            "description": "Basic problem with standard containers",
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
            "name": "merge-two-sorted-lists",
            "description": "Linked list problem requiring ListNode",
            "code": """class Solution {
public:
    ListNode* mergeTwoLists(ListNode* list1, ListNode* list2) {
        ListNode dummy(0);
        ListNode* tail = &dummy;
        
        while (list1 && list2) {
            if (list1->val <= list2->val) {
                tail->next = list1;
                list1 = list1->next;
            } else {
                tail->next = list2;
                list2 = list2->next;
            }
            tail = tail->next;
        }
        
        tail->next = list1 ? list1 : list2;
        return dummy.next;
    }
};""",
            "input": '{"list1": [1,2,4], "list2": [1,3,4]}',
        },
        {
            "name": "maximum-depth-of-binary-tree",
            "description": "Tree problem requiring TreeNode",
            "code": """class Solution {
public:
    int maxDepth(TreeNode* root) {
        if (!root) return 0;
        return 1 + max(maxDepth(root->left), maxDepth(root->right));
    }
};""",
            "input": '{"root": [3,9,20,null,null,15,7]}',
        },
    ]

    print("=== Testing Comprehensive C++ Support (No Includes Required) ===")

    for test_case in test_cases:
        print(f"\n--- {test_case['name']} ---")
        print(f"Description: {test_case['description']}")
        test_problem_compilation(
            test_case["name"], test_case["code"], test_case["input"]
        )


def test_problem_compilation(problem_name, user_code, test_input):
    """Test compilation for a specific problem"""

    harness_path = f"/Users/andriysapeha/Documents/coding_duel/coding-duel/backend/code_testing/cpp_harnesses/harnesses/{problem_name}/harness.cpp"

    if not os.path.exists(harness_path):
        print(f"❌ Harness not found: {harness_path}")
        return

    with open(harness_path, "r") as f:
        harness_content = f.read()

    # Apply backend replacement logic
    user_code_with_namespace = f"""// User solution code with namespace access
using namespace std;

{user_code}"""

    wrapped_code = harness_content.replace(
        '#include "userfunc.h"',
        user_code_with_namespace,
    )

    # Check that data structures are present
    has_listnode = "struct ListNode" in wrapped_code
    has_treenode = "struct TreeNode" in wrapped_code
    has_includes = "#include <vector>" in wrapped_code

    print(f"  📋 Harness validation:")
    print(f"     - Standard includes: {'✅' if has_includes else '❌'}")
    print(f"     - ListNode available: {'✅' if has_listnode else '❌'}")
    print(f"     - TreeNode available: {'✅' if has_treenode else '❌'}")

    # Test compilation
    with tempfile.NamedTemporaryFile(mode="w", suffix=".cpp", delete=False) as cpp_file:
        cpp_file.write(wrapped_code)
        cpp_file.flush()

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as input_file:
            input_file.write(test_input)
            input_file.flush()

            try:
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
                    g++ -std=c++17 -w -o solution solution.cpp 2>&1 &&
                    echo "=== Compilation Successful ===" &&
                    echo "Testing execution..." &&
                    timeout 3 ./solution < input.json 2>&1 || echo "Execution completed"
                    """,
                ]

                result = subprocess.run(
                    docker_cmd, capture_output=True, text=True, timeout=10
                )

                if "Compilation Successful" in result.stdout:
                    print(
                        "  ✅ COMPILATION SUCCESS - User code works without includes!"
                    )
                    # Look for result in output
                    for line in result.stdout.split("\n"):
                        if "result" in line.lower() and ("{" in line or '"' in line):
                            print(f"     Output: {line}")
                else:
                    print("  ❌ COMPILATION FAILED")
                    error_lines = [
                        line
                        for line in result.stdout.split("\n")
                        if "error:" in line.lower()
                    ]
                    for error in error_lines[:3]:  # Show first 3 errors
                        print(f"     {error}")

            except subprocess.TimeoutExpired:
                print("  ⏱️ TIMEOUT")
            except Exception as e:
                print(f"  💥 ERROR: {e}")
            finally:
                try:
                    os.unlink(cpp_file.name)
                    os.unlink(input_file.name)
                except:
                    pass


if __name__ == "__main__":
    test_comprehensive_cpp_support()
