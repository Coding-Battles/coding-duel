#include <vector>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <queue>
#include <algorithm>
using namespace std;

class Solution {
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
};