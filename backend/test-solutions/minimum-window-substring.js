class Solution {
    minWindow(s, t) {
        if (!s || !t) return "";
        
        // Count of each character in t
        const tCount = new Map();
        for (const char of t) {
            tCount.set(char, (tCount.get(char) || 0) + 1);
        }
        
        const required = tCount.size;
        let formed = 0;
        const windowCounts = new Map();
        
        let left = 0, right = 0;
        let minLen = Infinity;
        let minLeft = 0;
        
        while (right < s.length) {
            // Add the right character to the window
            const char = s[right];
            windowCounts.set(char, (windowCounts.get(char) || 0) + 1);
            
            // Check if this character contributes to the desired frequency
            if (tCount.has(char) && windowCounts.get(char) === tCount.get(char)) {
                formed++;
            }
            
            // Try to shrink the window from left
            while (left <= right && formed === required) {
                const leftChar = s[left];
                
                // Update the result if this window is smaller
                if (right - left + 1 < minLen) {
                    minLen = right - left + 1;
                    minLeft = left;
                }
                
                // Remove the leftmost character from the window
                windowCounts.set(leftChar, windowCounts.get(leftChar) - 1);
                if (tCount.has(leftChar) && windowCounts.get(leftChar) < tCount.get(leftChar)) {
                    formed--;
                }
                
                left++;
            }
            
            right++;
        }
        
        return minLen === Infinity ? "" : s.substring(minLeft, minLeft + minLen);
    }
}