class Solution {
    isPalindrome(x) {
        if (x < 0) {
            return false;
        }
        
        const original = x;
        let reversedNum = 0;
        
        while (x > 0) {
            reversedNum = reversedNum * 10 + x % 10;
            x = Math.floor(x / 10);
        }
        
        return original === reversedNum;
    }
}