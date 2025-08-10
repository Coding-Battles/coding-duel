class Solution {
    isValid(s) {
        const stack = [];
        const mapping = {')': '(', '}': '{', ']': '['};
        
        for (const char of s) {
            if (char in mapping) {
                if (!stack.length || stack.pop() !== mapping[char]) {
                    return false;
                }
            } else {
                stack.push(char);
            }
        }
        
        return stack.length === 0;
    }
}