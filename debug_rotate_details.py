#!/usr/bin/env python3

import requests
import json


def debug_rotate_output():
    """Debug what the Java rotate function is actually outputting"""

    # Test Java implementation with detailed error reporting
    java_payload = {
        "player_id": "test_player",
        "code": """class Solution {
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
}""",
        "language": "java",
        "question_name": "rotate-image",
        "timer": 300,
    }

    print("🔍 Testing Java rotate implementation with full details")
    try:
        response = requests.post(
            "http://localhost:8000/api/rotate-image/test-sample",
            json=java_payload,
            timeout=30,
        )

        print(f"✅ Java Response status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Success: {result.get('success', False)}")
            print(f"Total passed: {result.get('total_passed', 0)}")
            print(f"Total failed: {result.get('total_failed', 0)}")

            if result.get("error"):
                print(f"Global Error: {result['error']}")

            if result.get("test_results"):
                for i, test in enumerate(result["test_results"]):
                    print(f"\n--- Test {i+1} ---")
                    print(f"Input: {test.get('input', 'N/A')}")
                    print(f"Expected: {test.get('expected_output', 'N/A')}")
                    print(f"Actual: {test.get('actual_output', 'N/A')}")
                    print(f"Passed: {'✅' if test.get('passed', False) else '❌'}")
                    if test.get("error"):
                        print(f"Error: {test['error']}")
                    print(f"Execution time: {test.get('execution_time', 'N/A')}ms")
        else:
            print(f"Response: {response.text}")

    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    debug_rotate_output()
