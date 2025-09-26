#!/usr/bin/env python3

import sys
import os

# Add the backend directory to the path
backend_path = os.path.join(os.path.dirname(__file__), "backend")
sys.path.append(backend_path)


def test_invert_binary_tree():
    print("Testing invert-binary-tree C++ harness...")

    # Read the test solution
    with open("backend/test-solutions/invert-binary-tree.cpp", "r") as f:
        user_code = f.read()

    print("Test solution code:")
    print(user_code[:300] + "...")

    # Import the docker runner module
    from code_testing import docker_runner

    test_cases = [
        ("[4,2,7,1,3,6,9]", "[4,7,2,9,6,3,1]"),
        ("[2,1,3]", "[2,3,1]"),
        ("[]", "[]"),
        ("[1]", "[1]"),
    ]

    for i, (input_root, expected) in enumerate(test_cases, 1):
        print(f"\nTest {i}:")
        print(f"Input: {input_root}")
        print(f"Expected: {expected}")

        # Create a proper request object
        class MockRequest:
            def __init__(self, input_root):
                self.function_name = "invertTree"
                self.language = "cpp"
                self.code = user_code
                self.input = f'{{"root":{input_root}}}'
                # Parse the input string to create test_input object
                import json

                self.test_input = json.loads(f'{{"root":{input_root}}}')
                self.question = "invert-binary-tree"
                self.question_name = "invert-binary-tree"  # Add this field
                self.timeout = 30

        request = MockRequest(input_root)
        result = docker_runner.run_code_in_docker(request)
        print(f"Result: {result}")


if __name__ == "__main__":
    test_invert_binary_tree()
