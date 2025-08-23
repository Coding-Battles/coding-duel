#!/usr/bin/env python3

import json
from backend.code_testing.docker_runner import run_code_in_docker
from backend.models.questions import DockerRunRequest


def test_rotate_all_languages():
    """Test rotate-image in all languages"""

    test_input = {"matrix": [[1, 2, 3], [4, 5, 6], [7, 8, 9]]}
    expected = [[7, 4, 1], [8, 5, 2], [9, 6, 3]]

    # Python implementation
    print("🐍 Testing Python rotate-image...")
    python_code = """class Solution:
    def rotate(self, matrix: list[list[int]]) -> None:
        n = len(matrix)
        # First transpose the matrix
        for i in range(n):
            for j in range(i, n):
                matrix[i][j], matrix[j][i] = matrix[j][i], matrix[i][j]
        
        # Then reverse each row
        for i in range(n):
            matrix[i].reverse()
"""

    test_language("python", python_code, test_input, "rotate", expected)

    print("\n" + "=" * 50 + "\n")

    # JavaScript implementation
    print("🟨 Testing JavaScript rotate-image...")
    js_code = """class Solution {
    rotate(matrix) {
        const n = matrix.length;
        
        // First transpose the matrix
        for (let i = 0; i < n; i++) {
            for (let j = i; j < n; j++) {
                [matrix[i][j], matrix[j][i]] = [matrix[j][i], matrix[i][j]];
            }
        }
        
        // Then reverse each row
        for (let i = 0; i < n; i++) {
            matrix[i].reverse();
        }
    }
}"""

    test_language("javascript", js_code, test_input, "rotate", expected)

    print("\n" + "=" * 50 + "\n")

    # Java implementation
    print("☕ Testing Java rotate-image...")
    java_code = """class Solution {
    public void rotate(int[][] matrix) {
        int n = matrix.length;
        // First transpose the matrix
        for (int i = 0; i < n; i++) {
            for (int j = i; j < n; j++) {
                int temp = matrix[i][j];
                matrix[i][j] = matrix[j][i];
                matrix[j][i] = temp;
            }
        }
        // Then reverse each row
        for (int i = 0; i < n; i++) {
            for (int j = 0; j < n / 2; j++) {
                int temp = matrix[i][j];
                matrix[i][j] = matrix[i][n - 1 - j];
                matrix[i][n - 1 - j] = temp;
            }
        }
    }
}"""

    test_language("java", java_code, test_input, "rotate", expected)

    print("\n" + "=" * 50 + "\n")

    # C++ implementation
    print("⚡ Testing C++ rotate-image...")
    cpp_code = """#include <algorithm>
class Solution {
public:
    void rotate(vector<vector<int>>& matrix) {
        int n = matrix.size();
        // First transpose the matrix
        for (int i = 0; i < n; i++) {
            for (int j = i; j < n; j++) {
                swap(matrix[i][j], matrix[j][i]);
            }
        }
        // Then reverse each row
        for (int i = 0; i < n; i++) {
            reverse(matrix[i].begin(), matrix[i].end());
        }
    }
};"""

    test_language("cpp", cpp_code, test_input, "rotate", expected)


def test_language(language, code, test_input, function_name, expected):
    """Test a specific language implementation"""
    request = DockerRunRequest(
        code=code, test_input=test_input, language=language, function_name=function_name
    )

    try:
        result = run_code_in_docker(request)
        print(f"✅ {language.title()} Result: {result}")
        actual = result.get("output")
        if actual == expected:
            print(f"🎉 {language.title()} result matches expected output!")
        else:
            print(f"❌ {language.title()} Expected: {expected}, Got: {actual}")
            if result.get("error"):
                print(f"Error details: {result['error']}")
    except Exception as e:
        print(f"❌ {language.title()} Error: {e}")


if __name__ == "__main__":
    test_rotate_all_languages()
