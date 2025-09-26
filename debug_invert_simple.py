#!/usr/bin/env python3

import sys
import os

# Add the backend directory to the path
backend_path = os.path.join(os.path.dirname(__file__), "backend")
sys.path.append(backend_path)


def test_invert_binary_tree_simple():
    print("Testing invert-binary-tree C++ harness - simple cases...")

    # Read the test solution
    with open("backend/test-solutions/invert-binary-tree.cpp", "r") as f:
        user_code = f.read()

    # Import the docker runner module
    from code_testing import docker_runner

    # Test with empty tree first - we know this works
    print("\nTest 1: Empty tree")
    print("Input: []")
    print("Expected: []")

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
            self.question_name = "invert-binary-tree"
            self.timeout = 30

    request = MockRequest("[]")
    result = docker_runner.run_code_in_docker(request)
    print(f"Result: {result}")

    # Test with simple tree
    print("\nTest 2: Simple tree")
    print("Input: [2,1,3]")
    print("Expected: [2,3,1]")

    request = MockRequest("[2,1,3]")
    result = docker_runner.run_code_in_docker(request)
    print(f"Result: {result}")


if __name__ == "__main__":
    test_invert_binary_tree_simple()
