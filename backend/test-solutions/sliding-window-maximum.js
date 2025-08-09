class Solution {
    maxSlidingWindow(nums, k) {
        if (!nums || nums.length === 0 || k === 0) return [];
        if (k === 1) return nums;
        
        // Use array as deque to store indices
        const deque = [];
        const result = [];
        
        for (let i = 0; i < nums.length; i++) {
            // Remove indices that are out of current window
            while (deque.length > 0 && deque[0] <= i - k) {
                deque.shift();
            }
            
            // Remove indices whose corresponding values are smaller than nums[i]
            while (deque.length > 0 && nums[deque[deque.length - 1]] < nums[i]) {
                deque.pop();
            }
            
            deque.push(i);
            
            // Add result for current window
            if (i >= k - 1) {
                result.push(nums[deque[0]]);
            }
        }
        
        return result;
    }
}