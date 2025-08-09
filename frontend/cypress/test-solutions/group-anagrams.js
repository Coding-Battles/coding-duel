class Solution {
    groupAnagrams(strs) {
        const groups = new Map();
        
        for (const s of strs) {
            // Sort the string to create a key for anagrams
            const key = s.split('').sort().join('');
            
            if (!groups.has(key)) {
                groups.set(key, []);
            }
            groups.get(key).push(s);
        }
        
        return Array.from(groups.values());
    }
}