class Solution {
    isAnagram(s, t) {
        if (s.length !== t.length) {
            return false;
        }
        
        const charCount = {};
        for (const char of s) {
            charCount[char] = (charCount[char] || 0) + 1;
        }
        
        for (const char of t) {
            if (!(char in charCount)) {
                return false;
            }
            charCount[char]--;
            if (charCount[char] < 0) {
                return false;
            }
        }
        
        return Object.values(charCount).every(count => count === 0);
    }
}