class Solution:
    def groupAnagrams(self, strs: list[str]) -> list[list[str]]:
        from collections import defaultdict
        
        groups = defaultdict(list)
        
        for s in strs:
            # Sort the string to create a key for anagrams
            key = ''.join(sorted(s))
            groups[key].append(s)
        
        return list(groups.values())