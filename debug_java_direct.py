#!/usr/bin/env python3

# Let's test the direct docker call to see what's happening
import json
from backend.code_testing.docker_runner import run_code_in_docker
from backend.models.questions import DockerRunRequest


def test_java_direct():
    """Test Java rotate directly via docker runner"""

    test_input = {"matrix": [[1, 2, 3], [4, 5, 6], [7, 8, 9]]}

    code = """class Solution {
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

    request = DockerRunRequest(
        code=code, test_input=test_input, language="java", function_name="rotate"
    )

    print("🔍 Testing Java rotate via direct docker call")
    print(f"Input JSON: {json.dumps(test_input)}")

    try:
        result = run_code_in_docker(request)
        print(f"✅ Result: {result}")

    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    test_java_direct()
