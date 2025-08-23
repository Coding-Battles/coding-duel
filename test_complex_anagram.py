#!/usr/bin/env python3

import json
from backend.code_testing.docker_runner import run_code_in_docker
from backend.models.questions import DockerRunRequest


def test_complex_anagram():
    """Test the complex anagram case: cbaebabacd with pattern abc"""

    test_input = {"s": "cbaebabacd", "p": "abc"}

    java_code = """class Solution {
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
        code=java_code,
        test_input=test_input,
        language="java",
        function_name="findAnagrams",
    )

    print(f"🔍 Testing complex case: s=\"{test_input['s']}\", p=\"{test_input['p']}\"")
    print("Manual verification:")
    s = test_input["s"]
    p = test_input["p"]
    for i in range(len(s) - len(p) + 1):
        substring = s[i : i + len(p)]
        is_anagram = sorted(substring) == sorted(p)
        print(f'  Position {i}: "{substring}" -> {is_anagram}')

    try:
        result = run_code_in_docker(request)
        print(f"✅ Result: {result}")
        expected = [1, 6]
        actual = result.get("output")
        if actual == expected:
            print(f"🎉 Result matches expected output!")
        else:
            print(f"❌ Expected: {expected}, Got: {actual}")
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    test_complex_anagram()
