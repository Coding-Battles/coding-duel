#!/usr/bin/env python3
"""
Quick test to verify C++ harness compilation works
"""

import requests
import json


def test_alien_dictionary():
    """Test alien-dictionary with C++ to check compilation"""

    # Test solution code
    cpp_code = """    # Test solution code WITHOUT includes (like a real user would submit)
    cpp_code = '''class Solution {
public:
    string alienOrder(vector<string>& words) {
        unordered_map<char, unordered_set<char>> graph;
        unordered_map<char, int> inDegree;
        
        for (const string& word : words) {
            for (char c : word) {
                graph[c] = unordered_set<char>();
                inDegree[c] = 0;
            }
        }
        
        for (int i = 0; i < words.size() - 1; i++) {
            string word1 = words[i];
            string word2 = words[i + 1];
            int minLen = min(word1.length(), word2.length());
            
            if (word1.length() > word2.length() && word1.substr(0, minLen) == word2.substr(0, minLen)) {
                return "";
            }
            
            for (int j = 0; j < minLen; j++) {
                if (word1[j] != word2[j]) {
                    if (graph[word1[j]].find(word2[j]) == graph[word1[j]].end()) {
                        graph[word1[j]].insert(word2[j]);
                        inDegree[word2[j]]++;
                    }
                    break;
                }
            }
        }
        
        queue<char> q;
        for (auto& pair : inDegree) {
            if (pair.second == 0) {
                q.push(pair.first);
            }
        }
        
        string result = "";
        while (!q.empty()) {
            char c = q.front();
            q.pop();
            result += c;
            
            for (char neighbor : graph[c]) {
                inDegree[neighbor]--;
                if (inDegree[neighbor] == 0) {
                    q.push(neighbor);
                }
            }
        }
        
        return result.length() == inDegree.size() ? result : "";
    }
};'''"""

    # Test input
    test_data = {"words": ["wrt", "wrf", "er", "ett", "rftt"]}

    payload = {
        "code": cpp_code,
        "function_name": "alienOrder",
        "question_name": "alien-dictionary",
        "language": "cpp",
        "test_input": test_data,
        "timeout": 10,
    }

    try:
        response = requests.post(
            "http://localhost:8000/api/docker-run", json=payload, timeout=30
        )
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")

        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success: {result}")
        else:
            print(f"❌ Error: {response.text}")

    except Exception as e:
        print(f"❌ Exception: {e}")


if __name__ == "__main__":
    test_alien_dictionary()
