class Solution:
    def minWindow(self, s: str, t: str) -> str:
        if not s or not t:
            return ""
        
        # Count of each character in t
        t_count = {}
        for char in t:
            t_count[char] = t_count.get(char, 0) + 1
        
        required = len(t_count)
        formed = 0
        window_counts = {}
        
        left = right = 0
        min_len = float('inf')
        min_left = 0
        
        while right < len(s):
            # Add the right character to the window
            char = s[right]
            window_counts[char] = window_counts.get(char, 0) + 1
            
            # Check if this character contributes to the desired frequency
            if char in t_count and window_counts[char] == t_count[char]:
                formed += 1
            
            # Try to shrink the window from left
            while left <= right and formed == required:
                char = s[left]
                
                # Update the result if this window is smaller
                if right - left + 1 < min_len:
                    min_len = right - left + 1
                    min_left = left
                
                # Remove the leftmost character from the window
                window_counts[char] -= 1
                if char in t_count and window_counts[char] < t_count[char]:
                    formed -= 1
                
                left += 1
            
            right += 1
        
        return "" if min_len == float('inf') else s[min_left:min_left + min_len]