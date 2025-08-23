#include <vector>
#include <string>
#include <unordered_set>
#include <unordered_map>
using namespace std;

class Solution {
public:
    vector<string> wordBreak(string s, vector<string>& wordDict) {
        unordered_set<string> wordSet(wordDict.begin(), wordDict.end());
        unordered_map<int, vector<string>> memo;
        
        return dfs(s, 0, wordSet, memo);
    }
    
private:
    vector<string> dfs(const string& s, int start, const unordered_set<string>& wordSet, 
                       unordered_map<int, vector<string>>& memo) {
        if (memo.find(start) != memo.end()) {
            return memo[start];
        }
        
        vector<string> result;
        
        if (start == s.length()) {
            result.push_back("");
            return result;
        }
        
        for (int end = start + 1; end <= s.length(); end++) {
            string word = s.substr(start, end - start);
            if (wordSet.find(word) != wordSet.end()) {
                vector<string> rest = dfs(s, end, wordSet, memo);
                for (const string& sentence : rest) {
                    if (sentence.empty()) {
                        result.push_back(word);
                    } else {
                        result.push_back(word + " " + sentence);
                    }
                }
            }
        }
        
        memo[start] = result;
        return result;
    }
};
