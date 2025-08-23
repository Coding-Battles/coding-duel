#!/usr/bin/env python3

import json
from backend.code_testing.docker_runner import run_code_in_docker
from backend.models.questions import DockerRunRequest


def test_all_implementations():
    """Test all the implementations we've fixed"""

    # Test 1: house-robber (should work)
    print("🏠 Testing house-robber...")
    test_house_robber()

    print("\n" + "=" * 50 + "\n")

    # Test 2: rotate-image (now fixed)
    print("🔄 Testing rotate-image...")
    test_rotate_image()

    print("\n" + "=" * 50 + "\n")

    # Test 3: find-all-anagrams (now fixed)
    print("🔍 Testing find-all-anagrams...")
    test_find_anagrams()


def test_house_robber():
    """Test house robber Java implementation"""
    test_input = {"nums": [1, 2, 3, 1]}

    code = """class Solution {
    public int rob(int[] nums) {
        if (nums.length == 0) return 0;
        if (nums.length == 1) return nums[0];
        
        int prev1 = 0, prev2 = 0;
        for (int num : nums) {
            int temp = prev1;
            prev1 = Math.max(prev2 + num, prev1);
            prev2 = temp;
        }
        return prev1;
    }
}"""

    request = DockerRunRequest(
        code=code, test_input=test_input, language="java", function_name="rob"
    )

    try:
        result = run_code_in_docker(request)
        print(f"✅ House Robber Result: {result}")
    except Exception as e:
        print(f"❌ House Robber Error: {e}")


def test_rotate_image():
    """Test rotate image Java implementation"""
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

    try:
        result = run_code_in_docker(request)
        print(f"✅ Rotate Image Result: {result}")
        expected = [[7, 4, 1], [8, 5, 2], [9, 6, 3]]
        actual = result.get("output")
        if actual == expected:
            print("🎉 Rotate result matches expected output!")
        else:
            print(f"❌ Expected: {expected}, Got: {actual}")
    except Exception as e:
        print(f"❌ Rotate Image Error: {e}")


def test_find_anagrams():
    """Test find anagrams Java implementation"""
    test_input = {"s": "abab", "p": "ab"}

    code = """class Solution {
    public java.util.List<Integer> findAnagrams(String s, String p) {
        java.util.List<Integer> result = new java.util.ArrayList<>();
        if (s.length() < p.length()) return result;
        
        int[] pCount = new int[26];
        int[] sCount = new int[26];
        
        // Count characters in p
        for (char c : p.toCharArray()) {
            pCount[c - 'a']++;
        }
        
        int windowSize = p.length();
        
        // Initial window
        for (int i = 0; i < windowSize; i++) {
            sCount[s.charAt(i) - 'a']++;
        }
        
        // Check if initial window is an anagram
        if (java.util.Arrays.equals(pCount, sCount)) {
            result.add(0);
        }
        
        // Sliding window
        for (int i = windowSize; i < s.length(); i++) {
            // Add new character
            sCount[s.charAt(i) - 'a']++;
            // Remove old character
            sCount[s.charAt(i - windowSize) - 'a']--;
            
            if (java.util.Arrays.equals(pCount, sCount)) {
                result.add(i - windowSize + 1);
            }
        }
        
        return result;
    }
}"""

    request = DockerRunRequest(
        code=code, test_input=test_input, language="java", function_name="findAnagrams"
    )

    try:
        result = run_code_in_docker(request)
        print(f"✅ Find Anagrams Result: {result}")
        expected = [0, 2]  # "ab" appears at indices 0 and 2 in "abab"
        actual = result.get("output")
        if actual == expected:
            print("🎉 Find Anagrams result matches expected output!")
        else:
            print(f"❌ Expected: {expected}, Got: {actual}")
    except Exception as e:
        print(f"❌ Find Anagrams Error: {e}")


if __name__ == "__main__":
    test_all_implementations()
