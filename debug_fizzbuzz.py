#!/usr/bin/env python3

import sys
import os

sys.path.append(".")

from backend.code_testing.docker_runner import run_code_in_docker
from backend.models.questions import DockerRunRequest


def test_fizzbuzz():
    print("Testing fizzbuzz harness...")

    # Simple working fizzbuzz solution
    test_code = """
class Solution {
public:
    vector<string> fizzBuzz(int n) {
        vector<string> result;
        for (int i = 1; i <= n; i++) {
            if (i % 15 == 0) {
                result.push_back("FizzBuzz");
            } else if (i % 3 == 0) {
                result.push_back("Fizz");
            } else if (i % 5 == 0) {
                result.push_back("Buzz");
            } else {
                result.push_back(to_string(i));
            }
        }
        return result;
    }
};
"""

    # Test cases
    test_cases = ['{"n":3}', '{"n":5}', '{"n":15}']

    expected_results = [
        '["1","2","Fizz"]',
        '["1","2","Fizz","4","Buzz"]',
        '["1","2","Fizz","4","Buzz","Fizz","7","8","Fizz","Buzz","11","Fizz","13","14","FizzBuzz"]',
    ]

    for i, (test_input, expected) in enumerate(zip(test_cases, expected_results), 1):
        print(f"\nTest {i}:")
        print(f"Input: {test_input}")
        print(f"Expected: {expected}")

        try:
            request = DockerRunRequest(
                code=test_code,
                language="cpp",
                test_input={"input": test_input},
                question_name="fizzbuzz",
            )
            result = run_code_in_docker(request)
            print(f"Raw result: {result}")

        except Exception as e:
            print(f"❌ ERROR: {e}")
            import traceback

            traceback.print_exc()


if __name__ == "__main__":
    test_fizzbuzz()
