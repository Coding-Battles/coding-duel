#!/usr/bin/env python3
"""
Test findAnagrams implementation across languages
"""
import sys
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent / "backend"))

from backend.models.questions import DockerRunRequest
from backend.code_testing.docker_runner import run_code_in_docker


def test_find_anagrams_java():
    java_code = """
import java.util.*;

class Solution {
    public List<Integer> findAnagrams(String s, String p) {
        List<Integer> result = new ArrayList<>();
        if (s.length() < p.length()) return result;
        
        Map<Character, Integer> pCount = new HashMap<>();
        for (char c : p.toCharArray()) {
            pCount.put(c, pCount.getOrDefault(c, 0) + 1);
        }
        
        Map<Character, Integer> windowCount = new HashMap<>();
        int windowSize = p.length();
        
        for (int i = 0; i < s.length(); i++) {
            char c = s.charAt(i);
            windowCount.put(c, windowCount.getOrDefault(c, 0) + 1);
            
            if (i >= windowSize) {
                char leftChar = s.charAt(i - windowSize);
                windowCount.put(leftChar, windowCount.get(leftChar) - 1);
                if (windowCount.get(leftChar) == 0) {
                    windowCount.remove(leftChar);
                }
            }
            
            if (windowCount.equals(pCount)) {
                result.add(i - windowSize + 1);
            }
        }
        
        return result;
    }
}
"""

    test_input = {"s": "abab", "p": "ab"}

    request = DockerRunRequest(
        language="java",
        code=java_code,
        function_name="findAnagrams",
        test_input=test_input,
    )

    result = run_code_in_docker(request)
    print(f"Java findAnagrams result: {result}")
    return result


if __name__ == "__main__":
    print("🧪 Testing findAnagrams")
    test_find_anagrams_java()
