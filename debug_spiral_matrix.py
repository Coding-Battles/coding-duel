#!/usr/bin/env python3

import sys
import os

sys.path.append(".")

from backend.code_testing.docker_runner import run_code_in_docker
from backend.models.questions import DockerRunRequest


def test_spiral_matrix():
    print("Testing spiral-matrix harness...")

    # Simple working spiral matrix solution
    test_code = """
class Solution {
public:
    vector<int> spiralOrder(vector<vector<int>>& matrix) {
        vector<int> result;
        if (matrix.empty() || matrix[0].empty()) return result;
        
        int top = 0, bottom = matrix.size() - 1;
        int left = 0, right = matrix[0].size() - 1;
        
        while (top <= bottom && left <= right) {
            // Go right
            for (int j = left; j <= right; j++) {
                result.push_back(matrix[top][j]);
            }
            top++;
            
            // Go down
            for (int i = top; i <= bottom; i++) {
                result.push_back(matrix[i][right]);
            }
            right--;
            
            // Go left
            if (top <= bottom) {
                for (int j = right; j >= left; j--) {
                    result.push_back(matrix[bottom][j]);
                }
                bottom--;
            }
            
            // Go up
            if (left <= right) {
                for (int i = bottom; i >= top; i--) {
                    result.push_back(matrix[i][left]);
                }
                left++;
            }
        }
        
        return result;
    }
};
"""

    # Test cases from the Cypress test
    test_cases = [
        '{"matrix":[[1,2,3],[4,5,6],[7,8,9]]}',
        '{"matrix":[[1,2,3,4],[5,6,7,8],[9,10,11,12]]}',
        '{"matrix":[[1]]}',
    ]

    expected_results = ["[1,2,3,6,9,8,7,4,5]", "[1,2,3,4,8,12,11,10,9,5,6,7]", "[1]"]

    for i, (test_input, expected) in enumerate(zip(test_cases, expected_results), 1):
        print(f"\nTest {i}:")
        print(f"Input: {test_input}")
        print(f"Expected: {expected}")

        try:
            request = DockerRunRequest(
                code=test_code,
                language="cpp",
                test_input={"input": test_input},
                question_name="spiral-matrix",
            )
            result = run_code_in_docker(request)
            output = result.get("output", "")
            print(f"Actual: {output}")

            if output.strip() == expected:
                print("✅ PASS")
            else:
                print("❌ FAIL")
                print(f"Raw result: {result}")

        except Exception as e:
            print(f"❌ ERROR: {e}")
            import traceback

            traceback.print_exc()


if __name__ == "__main__":
    test_spiral_matrix()
