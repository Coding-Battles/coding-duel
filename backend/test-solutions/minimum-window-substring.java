class Solution {
    public String minWindow(String s, String t) {
        if (s == null || t == null || s.length() == 0 || t.length() == 0) {
            return "";
        }
        
        // Count of each character in t
        Map<Character, Integer> tCount = new HashMap<>();
        for (char c : t.toCharArray()) {
            tCount.put(c, tCount.getOrDefault(c, 0) + 1);
        }
        
        int required = tCount.size();
        int formed = 0;
        Map<Character, Integer> windowCounts = new HashMap<>();
        
        int left = 0, right = 0;
        int minLen = Integer.MAX_VALUE;
        int minLeft = 0;
        
        while (right < s.length()) {
            // Add the right character to the window
            char c = s.charAt(right);
            windowCounts.put(c, windowCounts.getOrDefault(c, 0) + 1);
            
            // Check if this character contributes to the desired frequency
            if (tCount.containsKey(c) && windowCounts.get(c).intValue() == tCount.get(c).intValue()) {
                formed++;
            }
            
            // Try to shrink the window from left
            while (left <= right && formed == required) {
                char leftChar = s.charAt(left);
                
                // Update the result if this window is smaller
                if (right - left + 1 < minLen) {
                    minLen = right - left + 1;
                    minLeft = left;
                }
                
                // Remove the leftmost character from the window
                windowCounts.put(leftChar, windowCounts.get(leftChar) - 1);
                if (tCount.containsKey(leftChar) && windowCounts.get(leftChar).intValue() < tCount.get(leftChar).intValue()) {
                    formed--;
                }
                
                left++;
            }
            
            right++;
        }
        
        return minLen == Integer.MAX_VALUE ? "" : s.substring(minLeft, minLeft + minLen);
    }
}