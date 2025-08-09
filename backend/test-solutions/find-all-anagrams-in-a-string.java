import java.util.*;

class Solution {
    public List<Integer> findAnagrams(String s, String p) {
        List<Integer> result = new ArrayList<>();
        if (p.length() > s.length()) return result;
        
        Map<Character, Integer> pCount = new HashMap<>();
        Map<Character, Integer> windowCount = new HashMap<>();
        
        for (char c : p.toCharArray()) {
            pCount.put(c, pCount.getOrDefault(c, 0) + 1);
        }
        
        int windowSize = p.length();
        
        for (int i = 0; i < s.length(); i++) {
            char c = s.charAt(i);
            windowCount.put(c, windowCount.getOrDefault(c, 0) + 1);
            
            if (i >= windowSize) {
                char leftChar = s.charAt(i - windowSize);
                windowCount.put(leftChar, windowCount.get(leftChar) - 1);
                if (windowCount.get(leftChar) == 0) {
                    windowCount.remove(leftChar);
                }
            }
            
            if (windowCount.equals(pCount)) {
                result.add(i - windowSize + 1);
            }
        }
        
        return result;
    }
}