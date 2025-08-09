class Solution {
public:
    string minWindow(string s, string t) {
        if (s.empty() || t.empty()) return "";
        
        // Count of each character in t
        unordered_map<char, int> tCount;
        for (char c : t) {
            tCount[c]++;
        }
        
        int required = tCount.size();
        int formed = 0;
        unordered_map<char, int> windowCounts;
        
        int left = 0, right = 0;
        int minLen = INT_MAX;
        int minLeft = 0;
        
        while (right < s.length()) {
            // Add the right character to the window
            char c = s[right];
            windowCounts[c]++;
            
            // Check if this character contributes to the desired frequency
            if (tCount.find(c) != tCount.end() && windowCounts[c] == tCount[c]) {
                formed++;
            }
            
            // Try to shrink the window from left
            while (left <= right && formed == required) {
                char leftChar = s[left];
                
                // Update the result if this window is smaller
                if (right - left + 1 < minLen) {
                    minLen = right - left + 1;
                    minLeft = left;
                }
                
                // Remove the leftmost character from the window
                windowCounts[leftChar]--;
                if (tCount.find(leftChar) != tCount.end() && windowCounts[leftChar] < tCount[leftChar]) {
                    formed--;
                }
                
                left++;
            }
            
            right++;
        }
        
        return minLen == INT_MAX ? "" : s.substr(minLeft, minLen);
    }
};