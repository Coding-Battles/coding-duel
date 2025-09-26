#!/usr/bin/env python3

import sys
import os

# Add the backend directory to the path
backend_path = os.path.join(os.path.dirname(__file__), "backend")
sys.path.append(backend_path)


def test_javascript_problems():
    print("Testing JavaScript problems that are failing...")

    # Import the docker runner module
    from code_testing import docker_runner

    # Test cases for the three failing problems
    test_cases = [
        {
            "name": "merge-two-sorted-lists",
            "function_name": "mergeTwoLists",
            "input": {"list1": [1, 2, 4], "list2": [1, 3, 4]},
            "expected": [1, 1, 2, 3, 4, 4],
        },
        {
            "name": "invert-binary-tree",
            "function_name": "invertTree",
            "input": {"root": [4, 2, 7, 1, 3, 6, 9]},
            "expected": [4, 7, 2, 9, 6, 3, 1],
        },
        {
            "name": "same-tree",
            "function_name": "isSameTree",
            "input": {"p": [1, 2, 3], "q": [1, 2, 3]},
            "expected": True,
        },
    ]

    for test_case in test_cases:
        print(f"\n=== Testing {test_case['name']} ===")
        print(f"Input: {test_case['input']}")
        print(f"Expected: {test_case['expected']}")

        # Read the test solution
        with open(f"frontend/cypress/test-solutions/{test_case['name']}.js", "r") as f:
            user_code = f.read()

        print(f"Solution code preview: {user_code[:100]}...")

        # Create a proper request object
        class MockRequest:
            def __init__(self, test_case):
                self.function_name = test_case["function_name"]
                self.language = "javascript"
                self.code = user_code
                self.test_input = test_case["input"]
                self.question = test_case["name"]
                self.question_name = test_case["name"]
                self.timeout = 30

        request = MockRequest(test_case)
        result = docker_runner.run_code_in_docker(request)
        print(f"Result: {result}")

        if result["success"]:
            print(f"✅ Success: {result['output']}")
            if result["output"] == test_case["expected"]:
                print("✅ Output matches expected!")
            else:
                print(
                    f"❌ Output mismatch. Expected: {test_case['expected']}, Got: {result['output']}"
                )
        else:
            print(f"❌ Error: {result['error']}")


if __name__ == "__main__":
    test_javascript_problems()
