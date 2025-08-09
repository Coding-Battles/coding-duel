#include <stack>
#include <unordered_map>
using namespace std;

class Solution {
public:
    bool isValid(string s) {
        stack<char> stk;
        unordered_map<char, char> mapping = {
            {')', '('},
            {'}', '{'},
            {']', '['}
        };
        
        for (char c : s) {
            if (mapping.count(c)) {
                if (stk.empty() || stk.top() != mapping[c]) {
                    return false;
                }
                stk.pop();
            } else {
                stk.push(c);
            }
        }
        
        return stk.empty();
    }
};