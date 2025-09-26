#!/usr/bin/env python3
"""
Test to see what the final wrapped C++ code looks like after harness injection
"""

import requests
import json


def test_code_injection():
    """Test what happens when user code without includes gets injected"""

    # User code WITHOUT includes (like a real user would submit)
    user_code_without_includes = """class Solution {
public:
    int ladderLength(string beginWord, string endWord, vector<string>& wordList) {
        unordered_set<string> wordSet(wordList.begin(), wordList.end());
        if (wordSet.find(endWord) == wordSet.end()) {
            return 0;
        }
        
        queue<pair<string, int>> q;
        q.push({beginWord, 1});
        
        unordered_set<string> visited;
        visited.insert(beginWord);
        
        while (!q.empty()) {
            string currentWord = q.front().first;
            int level = q.front().second;
            q.pop();
            
            if (currentWord == endWord) {
                return level;
            }
            
            for (int i = 0; i < currentWord.length(); ++i) {
                char originalChar = currentWord[i];
                for (char c = 'a'; c <= 'z'; ++c) {
                    currentWord[i] = c;
                    if (wordSet.count(currentWord) && !visited.count(currentWord)) {
                        q.push({currentWord, level + 1});
                        visited.insert(currentWord);
                    }
                }
                currentWord[i] = originalChar;
            }
        }
        return 0;
    }
};"""

    payload = {
        "code": user_code_without_includes,
        "function_name": "ladderLength",
        "question_name": "word-ladder",
        "language": "cpp",
        "test_input": {
            "beginWord": "hit",
            "endWord": "cog",
            "wordList": ["hot", "dot", "dog", "lot", "log", "cog"],
        },
        "timeout": 10,
    }

    try:
        response = requests.post(
            "http://localhost:8000/api/docker-run", json=payload, timeout=30
        )
        print(f"Status Code: {response.status_code}")
        result = response.json()

        if result.get("success"):
            print(f"✅ SUCCESS: {result['output']}")
        else:
            print(f"❌ FAILED: {result.get('error', 'Unknown error')}")

        return result

    except Exception as e:
        print(f"❌ Exception: {e}")
        return None


if __name__ == "__main__":
    print("Testing C++ code injection without includes...")
    test_code_injection()
