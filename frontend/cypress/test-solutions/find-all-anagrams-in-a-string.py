class Solution:
    def findAnagrams(self, s: str, p: str) -> list[int]:
        if len(p) > len(s):
            return []
        
        result = []
        p_count = {}
        window_count = {}
        
        for char in p:
            p_count[char] = p_count.get(char, 0) + 1
        
        window_size = len(p)
        
        for i in range(len(s)):
            window_count[s[i]] = window_count.get(s[i], 0) + 1
            
            if i >= window_size:
                left_char = s[i - window_size]
                window_count[left_char] -= 1
                if window_count[left_char] == 0:
                    del window_count[left_char]
            
            if window_count == p_count:
                result.append(i - window_size + 1)
        
        return result