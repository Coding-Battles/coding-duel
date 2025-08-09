class Solution {
    subarraySum(nums, k) {
        const prefixSumCount = new Map();
        prefixSumCount.set(0, 1);
        
        let count = 0;
        let prefixSum = 0;
        
        for (const num of nums) {
            prefixSum += num;
            
            if (prefixSumCount.has(prefixSum - k)) {
                count += prefixSumCount.get(prefixSum - k);
            }
            
            prefixSumCount.set(prefixSum, (prefixSumCount.get(prefixSum) || 0) + 1);
        }
        
        return count;
    }
}