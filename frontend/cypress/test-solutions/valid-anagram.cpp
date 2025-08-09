#include <string>
#include <unordered_map>
using namespace std;

class Solution {
public:
    bool isAnagram(string s, string t) {
        if (s.length() != t.length()) {
            return false;
        }
        
        unordered_map<char, int> charCount;
        for (char c : s) {
            charCount[c]++;
        }
        
        for (char c : t) {
            if (charCount.find(c) == charCount.end()) {
                return false;
            }
            charCount[c]--;
            if (charCount[c] < 0) {
                return false;
            }
        }
        
        for (auto& pair : charCount) {
            if (pair.second != 0) {
                return false;
            }
        }
        
        return true;
    }
};