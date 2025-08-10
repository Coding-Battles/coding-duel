class Solution:
    def reverse(self, x: int) -> int:
        INT_MIN, INT_MAX = -2**31, 2**31 - 1
        
        result = 0
        sign = -1 if x < 0 else 1
        x = abs(x)
        
        while x:
            digit = x % 10
            x //= 10
            
            # Check for overflow before actually updating result
            if result > (INT_MAX - digit) // 10:
                return 0
                
            result = result * 10 + digit
        
        result *= sign
        return result if INT_MIN <= result <= INT_MAX else 0