import java.util.*;

class Solution {
    public List<List<String>> groupAnagrams(String[] strs) {
        Map<String, List<String>> groups = new HashMap<>();
        
        for (String s : strs) {
            // Sort the string to create a key for anagrams
            char[] chars = s.toCharArray();
            Arrays.sort(chars);
            String key = new String(chars);
            
            groups.computeIfAbsent(key, k -> new ArrayList<>()).add(s);
        }
        
        return new ArrayList<>(groups.values());
    }
}