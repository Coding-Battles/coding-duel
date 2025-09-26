#!/usr/bin/env python3

import sys
import os
import json

# Add the backend directory to the path
backend_path = os.path.join(os.path.dirname(__file__), "backend")
sys.path.append(backend_path)


def test_first_bad_version():
    print("Testing first-bad-version C++ harness...")

    # Read the test solution
    with open("backend/test-solutions/first-bad-version.cpp", "r") as f:
        user_code = f.read()

    print("Test solution code:")
    print(user_code[:200] + "...")

    # Import the docker runner module
    from code_testing import docker_runner

    # Test with simple input
    print("\nTest 1:")
    print("Input: n=5, bad=4")
    print("Expected: 4")

    # Create a proper request object
    class MockRequest:
        def __init__(self):
            self.function_name = "firstBadVersion"
            self.language = "cpp"
            self.code = user_code
            self.input = '{"n":5,"bad":4}'
            self.question = "first-bad-version"
            self.timeout = 30

    request = MockRequest()
    result = docker_runner.run_code_in_docker(request)
    print(f"Raw result: {result}")


if __name__ == "__main__":
    test_first_bad_version()
