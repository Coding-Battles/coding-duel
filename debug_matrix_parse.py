#!/usr/bin/env python3

import requests
import json


def test_rotate_via_api():
    """Test rotate function via the proper API endpoint"""

    # Test Java implementation
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

    print("🔍 Testing Java rotate implementation via API")
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
                print(f"Error: {result['error']}")
            if result.get("test_results"):
                for i, test in enumerate(result["test_results"]):
                    print(
                        f"Test {i+1}: {'✅' if test['passed'] else '❌'} {test.get('error', '')}"
                    )
        else:
            print(f"Response: {response.text}")

    except Exception as e:
        print(f"❌ Java Error: {e}")

    print("\n" + "=" * 50 + "\n")

    # Test C++ implementation
    cpp_payload = {
        "player_id": "test_player",
        "code": """#include <algorithm>
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
};""",
        "language": "cpp",
        "question_name": "rotate-image",
        "timer": 300,
    }

    print("🔍 Testing C++ rotate implementation via API")
    try:
        response = requests.post(
            "http://localhost:8000/api/rotate-image/test-sample",
            json=cpp_payload,
            timeout=30,
        )

        print(f"✅ C++ Response status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Success: {result.get('success', False)}")
            print(f"Total passed: {result.get('total_passed', 0)}")
            print(f"Total failed: {result.get('total_failed', 0)}")
            if result.get("error"):
                print(f"Error: {result['error']}")
            if result.get("test_results"):
                for i, test in enumerate(result["test_results"]):
                    print(
                        f"Test {i+1}: {'✅' if test['passed'] else '❌'} {test.get('error', '')}"
                    )
        else:
            print(f"Response: {response.text}")

    except Exception as e:
        print(f"❌ C++ Error: {e}")


if __name__ == "__main__":
    test_rotate_via_api()
