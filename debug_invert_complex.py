#!/usr/bin/env python3

import sys
import os

# Add the backend directory to the path
backend_path = os.path.join(os.path.dirname(__file__), "backend")
sys.path.append(backend_path)


def test_invert_binary_tree_complex():
    print("Testing invert-binary-tree C++ harness - complex case...")

    # Read the test solution
    with open("backend/test-solutions/invert-binary-tree.cpp", "r") as f:
        user_code = f.read()

    # Import the docker runner module
    from code_testing import docker_runner

    # Test the complex case
    print("\nComplex tree test:")
    print("Input: [4,2,7,1,3,6,9]")
    print("Expected: [4,7,2,9,6,3,1]")

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

    request = MockRequest("[4,2,7,1,3,6,9]")
    result = docker_runner.run_code_in_docker(request)
    print(f"Result: {result}")

    if result["success"]:
        actual = result["output"]
        expected = [4, 7, 2, 9, 6, 3, 1]
        print(f"Expected: {expected}")
        print(f"Actual:   {actual}")
        print(f"Match: {actual == expected}")


if __name__ == "__main__":
    test_invert_binary_tree_complex()
