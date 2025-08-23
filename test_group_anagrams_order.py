#!/usr/bin/env python3

import requests
import json


def test_group_anagrams():
    """Test group-anagrams to see the order issue"""

    payload = {
        "player_id": "test_player",
        "code": """class Solution {
    public List<List<String>> groupAnagrams(String[] strs) {
        Map<String, List<String>> map = new HashMap<>();
        
        for (String str : strs) {
            char[] chars = str.toCharArray();
            Arrays.sort(chars);
            String key = String.valueOf(chars);
            
            map.computeIfAbsent(key, k -> new ArrayList<>()).add(str);
        }
        
        return new ArrayList<>(map.values());
    }
}""",
        "language": "java",
        "question_name": "group-anagrams",
        "timer": 300,
    }

    try:
        response = requests.post(
            "http://localhost:8000/api/group-anagrams/test-sample",
            json=payload,
            timeout=30,
        )

        print(f"Response status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Success: {result.get('success', False)}")
            print(f"Total passed: {result.get('total_passed', 0)}")
            print(f"Total failed: {result.get('total_failed', 0)}")

            if result.get("test_results"):
                for i, test in enumerate(result["test_results"]):
                    print(f"\n--- Test {i+1} ---")
                    print(f"Input: {test.get('input', 'N/A')}")
                    print(f"Expected: {test.get('expected_output', 'N/A')}")
                    print(f"Actual: {test.get('actual_output', 'N/A')}")
                    print(f"Passed: {'✅' if test.get('passed', False) else '❌'}")
                    if test.get("error"):
                        print(f"Error: {test['error']}")
        else:
            print(f"Response: {response.text}")

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    test_group_anagrams()
