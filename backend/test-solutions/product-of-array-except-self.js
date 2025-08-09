class Solution {
    productExceptSelf(nums) {
        const n = nums.length;
        const result = new Array(n).fill(1);
        
        // Left pass: result[i] contains product of all elements to the left of i
        for (let i = 1; i < n; i++) {
            result[i] = result[i - 1] * nums[i - 1];
        }
        
        // Right pass: multiply with product of all elements to the right of i
        let rightProduct = 1;
        for (let i = n - 1; i >= 0; i--) {
            result[i] *= rightProduct;
            rightProduct *= nums[i];
        }
        
        return result;
    }
}