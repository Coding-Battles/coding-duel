#!/usr/bin/env python3
"""
Test rotate image implementation
"""
import sys
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent / "backend"))

from backend.models.questions import DockerRunRequest
from backend.code_testing.docker_runner import run_code_in_docker


def test_rotate_java():
    java_code = """
class Solution {
    public void rotate(int[][] matrix) {
        int n = matrix.length;
        
        // Transpose the matrix
        for (int i = 0; i < n; i++) {
            for (int j = i; j < n; j++) {
                int temp = matrix[i][j];
                matrix[i][j] = matrix[j][i];
                matrix[j][i] = temp;
            }
        }
        
        // Reverse each row
        for (int i = 0; i < n; i++) {
            for (int j = 0; j < n / 2; j++) {
                int temp = matrix[i][j];
                matrix[i][j] = matrix[i][n - 1 - j];
                matrix[i][n - 1 - j] = temp;
            }
        }
    }
}
"""

    test_input = {"matrix": [[1, 2, 3], [4, 5, 6], [7, 8, 9]]}

    request = DockerRunRequest(
        language="java", code=java_code, function_name="rotate", test_input=test_input
    )

    result = run_code_in_docker(request)
    print(f"Java rotate result: {result}")
    return result


def test_rotate_cpp():
    cpp_code = """
#include <vector>
#include <algorithm>
using namespace std;

class Solution {
public:
    void rotate(vector<vector<int>>& matrix) {
        int n = matrix.size();
        
        // Transpose the matrix
        for (int i = 0; i < n; i++) {
            for (int j = i; j < n; j++) {
                swap(matrix[i][j], matrix[j][i]);
            }
        }
        
        // Reverse each row
        for (int i = 0; i < n; i++) {
            reverse(matrix[i].begin(), matrix[i].end());
        }
    }
};
"""

    test_input = {"matrix": [[1, 2, 3], [4, 5, 6], [7, 8, 9]]}

    request = DockerRunRequest(
        language="cpp", code=cpp_code, function_name="rotate", test_input=test_input
    )

    result = run_code_in_docker(request)
    print(f"C++ rotate result: {result}")
    return result


if __name__ == "__main__":
    print("🧪 Testing rotate implementation")
    test_rotate_java()
    test_rotate_cpp()
