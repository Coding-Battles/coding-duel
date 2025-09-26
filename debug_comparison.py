#!/usr/bin/env python3

import sys
import os

sys.path.append(".")

from backend.code_testing.docker_runner import run_code_in_docker
from backend.models.questions import DockerRunRequest


def test_spiral_vs_fizz():
    print("Comparing spiral-matrix vs fizzbuzz input handling...")

    # Test spiral-matrix
    spiral_code = """
class Solution {
public:
    vector<int> spiralOrder(vector<vector<int>>& matrix) {
        vector<int> result = {1, 2, 3};
        return result;
    }
};
"""

    fizz_code = """
class Solution {
public:
    vector<string> fizzBuzz(int n) {
        vector<string> result = {"1", "2", "Fizz"};
        return result;
    }
};
"""

    print("\n=== SPIRAL MATRIX TEST ===")
    try:
        request = DockerRunRequest(
            code=spiral_code,
            language="cpp",
            test_input={"input": '{"matrix":[[1,2,3]]}'},
            question_name="spiral-matrix",
        )
        result = run_code_in_docker(request)
        print(f"Spiral result: {result}")
    except Exception as e:
        print(f"Spiral error: {e}")

    print("\n=== FIZZBUZZ TEST ===")
    try:
        request = DockerRunRequest(
            code=fizz_code,
            language="cpp",
            test_input={"input": '{"n":3}'},
            question_name="fizzbuzz",
        )
        result = run_code_in_docker(request)
        print(f"Fizz result: {result}")
    except Exception as e:
        print(f"Fizz error: {e}")


if __name__ == "__main__":
    test_spiral_vs_fizz()
