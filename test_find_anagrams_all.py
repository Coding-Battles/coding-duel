#!/usr/bin/env python3

import json
from backend.code_testing.docker_runner import run_code_in_docker
from backend.models.questions import DockerRunRequest


def test_find_anagrams_all_languages():
    """Test find anagrams in all languages"""

    test_input = {"s": "abab", "p": "ab"}

    # Python implementation
    print("🐍 Testing Python find-all-anagrams...")
    python_code = """class Solution:
    def findAnagrams(self, s: str, p: str) -> list[int]:
        if len(s) < len(p):
            return []
        
        result = []
        p_count = {}
        s_count = {}
        
        # Count characters in p
        for char in p:
            p_count[char] = p_count.get(char, 0) + 1
        
        window_size = len(p)
        
        # Initial window
        for i in range(window_size):
            char = s[i]
            s_count[char] = s_count.get(char, 0) + 1
        
        # Check if initial window is an anagram
        if s_count == p_count:
            result.append(0)
        
        # Sliding window
        for i in range(window_size, len(s)):
            # Add new character
            new_char = s[i]
            s_count[new_char] = s_count.get(new_char, 0) + 1
            
            # Remove old character
            old_char = s[i - window_size]
            s_count[old_char] -= 1
            if s_count[old_char] == 0:
                del s_count[old_char]
            
            if s_count == p_count:
                result.append(i - window_size + 1)
        
        return result
"""

    test_language("python", python_code, test_input, "findAnagrams")

    print("\n" + "=" * 50 + "\n")

    # JavaScript implementation
    print("🟨 Testing JavaScript find-all-anagrams...")
    js_code = """class Solution {
    findAnagrams(s, p) {
        if (s.length < p.length) return [];
        
        const result = [];
        const pCount = {};
        const sCount = {};
        
        // Count characters in p
        for (const char of p) {
            pCount[char] = (pCount[char] || 0) + 1;
        }
        
        const windowSize = p.length;
        
        // Initial window
        for (let i = 0; i < windowSize; i++) {
            const char = s[i];
            sCount[char] = (sCount[char] || 0) + 1;
        }
        
        // Check if initial window is an anagram
        if (this.isEqual(sCount, pCount)) {
            result.push(0);
        }
        
        // Sliding window
        for (let i = windowSize; i < s.length; i++) {
            // Add new character
            const newChar = s[i];
            sCount[newChar] = (sCount[newChar] || 0) + 1;
            
            // Remove old character
            const oldChar = s[i - windowSize];
            sCount[oldChar]--;
            if (sCount[oldChar] === 0) {
                delete sCount[oldChar];
            }
            
            if (this.isEqual(sCount, pCount)) {
                result.push(i - windowSize + 1);
            }
        }
        
        return result;
    }
    
    isEqual(obj1, obj2) {
        const keys1 = Object.keys(obj1);
        const keys2 = Object.keys(obj2);
        
        if (keys1.length !== keys2.length) return false;
        
        for (const key of keys1) {
            if (obj1[key] !== obj2[key]) return false;
        }
        
        return true;
    }
}"""

    test_language("javascript", js_code, test_input, "findAnagrams")

    print("\n" + "=" * 50 + "\n")

    # Java implementation
    print("☕ Testing Java find-all-anagrams...")
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

    test_language("java", java_code, test_input, "findAnagrams")

    print("\n" + "=" * 50 + "\n")

    # C++ implementation
    print("⚡ Testing C++ find-all-anagrams...")
    cpp_code = """#include <algorithm>
class Solution {
public:
    vector<int> findAnagrams(string s, string p) {
        vector<int> result;
        if (s.length() < p.length()) return result;
        
        vector<int> pCount(26, 0);
        vector<int> sCount(26, 0);
        
        // Count characters in p
        for (char c : p) {
            pCount[c - 'a']++;
        }
        
        int windowSize = p.length();
        
        // Initial window
        for (int i = 0; i < windowSize; i++) {
            sCount[s[i] - 'a']++;
        }
        
        // Check if initial window is an anagram
        if (pCount == sCount) {
            result.push_back(0);
        }
        
        // Sliding window
        for (int i = windowSize; i < s.length(); i++) {
            // Add new character
            sCount[s[i] - 'a']++;
            // Remove old character
            sCount[s[i - windowSize] - 'a']--;
            
            if (pCount == sCount) {
                result.push_back(i - windowSize + 1);
            }
        }
        
        return result;
    }
};"""

    test_language("cpp", cpp_code, test_input, "findAnagrams")


def test_language(language, code, test_input, function_name):
    """Test a specific language implementation"""
    request = DockerRunRequest(
        code=code, test_input=test_input, language=language, function_name=function_name
    )

    try:
        result = run_code_in_docker(request)
        print(f"✅ {language.title()} Result: {result}")
        expected = [0, 1, 2]  # For "abab" with pattern "ab"
        actual = result.get("output")
        if actual == expected:
            print(f"🎉 {language.title()} result matches expected output!")
        else:
            print(f"❌ {language.title()} Expected: {expected}, Got: {actual}")
    except Exception as e:
        print(f"❌ {language.title()} Error: {e}")


if __name__ == "__main__":
    test_find_anagrams_all_languages()
