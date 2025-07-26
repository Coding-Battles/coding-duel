class Solution {
public:
    bool isPalindrome(int x) {
        if (x < 0) {
            return false;
        }
        
        int original = x;
        int reversedNum = 0;
        
        while (x > 0) {
            reversedNum = reversedNum * 10 + x % 10;
            x /= 10;
        }
        
        return original == reversedNum;
    }
};