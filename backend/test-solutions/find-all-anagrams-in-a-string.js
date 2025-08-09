class Solution {
    findAnagrams(s, p) {
        if (p.length > s.length) return [];
        
        const result = [];
        const pCount = new Map();
        const windowCount = new Map();
        
        for (const char of p) {
            pCount.set(char, (pCount.get(char) || 0) + 1);
        }
        
        const windowSize = p.length;
        
        for (let i = 0; i < s.length; i++) {
            windowCount.set(s[i], (windowCount.get(s[i]) || 0) + 1);
            
            if (i >= windowSize) {
                const leftChar = s[i - windowSize];
                windowCount.set(leftChar, windowCount.get(leftChar) - 1);
                if (windowCount.get(leftChar) === 0) {
                    windowCount.delete(leftChar);
                }
            }
            
            if (this.mapsEqual(windowCount, pCount)) {
                result.push(i - windowSize + 1);
            }
        }
        
        return result;
    }
    
    mapsEqual(map1, map2) {
        if (map1.size !== map2.size) return false;
        for (const [key, value] of map1) {
            if (map2.get(key) !== value) return false;
        }
        return true;
    }
}