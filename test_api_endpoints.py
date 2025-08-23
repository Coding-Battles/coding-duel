#!/usr/bin/env python3

import requests
import json


def test_api_endpoints():
    """Test both problematic endpoints via API"""

    # Test rotate-image
    print("🔄 Testing rotate-image API...")
    rotate_payload = {
        "player_id": "test_player",
        "code": """class Solution {
    public void rotate(int[][] matrix) {
        int n = matrix.length;
        for (int i = 0; i < n; i++) {
            for (int j = i; j < n; j++) {
                int temp = matrix[i][j];
                matrix[i][j] = matrix[j][i];
                matrix[j][i] = temp;
            }
        }
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

    try:
        response = requests.post(
            "http://localhost:8000/api/rotate-image/test-sample",
            json=rotate_payload,
            timeout=30,
        )

        print(f"✅ Rotate Response status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print_test_results("Rotate-Image", result)
        else:
            print(f"❌ Response: {response.text}")

    except Exception as e:
        print(f"❌ Rotate Error: {e}")

    print("\n" + "=" * 60 + "\n")

    # Test find-all-anagrams
    print("🔍 Testing find-all-anagrams API...")
    anagrams_payload = {
        "player_id": "test_player",
        "code": """class Solution {
    public java.util.List<Integer> findAnagrams(String s, String p) {
        java.util.List<Integer> result = new java.util.ArrayList<>();
        if (s.length() < p.length()) return result;
        
        int[] pCount = new int[26];
        int[] sCount = new int[26];
        
        for (char c : p.toCharArray()) {
            pCount[c - 'a']++;
        }
        
        int windowSize = p.length();
        
        for (int i = 0; i < windowSize; i++) {
            sCount[s.charAt(i) - 'a']++;
        }
        
        if (java.util.Arrays.equals(pCount, sCount)) {
            result.add(0);
        }
        
        for (int i = windowSize; i < s.length(); i++) {
            sCount[s.charAt(i) - 'a']++;
            sCount[s.charAt(i - windowSize) - 'a']--;
            
            if (java.util.Arrays.equals(pCount, sCount)) {
                result.add(i - windowSize + 1);
            }
        }
        
        return result;
    }
}""",
        "language": "java",
        "question_name": "find-all-anagrams-in-a-string",
        "timer": 300,
    }

    try:
        response = requests.post(
            "http://localhost:8000/api/find-all-anagrams-in-a-string/test-sample",
            json=anagrams_payload,
            timeout=30,
        )

        print(f"✅ Anagrams Response status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print_test_results("Find-All-Anagrams", result)
        else:
            print(f"❌ Response: {response.text}")

    except Exception as e:
        print(f"❌ Anagrams Error: {e}")


def print_test_results(problem_name, result):
    """Print detailed test results"""
    print(f"Success: {result.get('success', False)}")
    print(f"Total passed: {result.get('total_passed', 0)}")
    print(f"Total failed: {result.get('total_failed', 0)}")

    if result.get("error"):
        print(f"Global Error: {result['error']}")

    if result.get("test_results"):
        for i, test in enumerate(result["test_results"]):
            print(f"\n--- {problem_name} Test {i+1} ---")
            print(f"Input: {test.get('input', 'N/A')}")
            print(f"Expected: {test.get('expected_output', 'N/A')}")
            print(f"Actual: {test.get('actual_output', 'N/A')}")
            print(f"Passed: {'✅' if test.get('passed', False) else '❌'}")
            if test.get("error"):
                print(f"Error: {test['error']}")


if __name__ == "__main__":
    test_api_endpoints()
