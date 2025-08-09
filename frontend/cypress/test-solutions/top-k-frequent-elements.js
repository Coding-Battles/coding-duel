class Solution {
    topKFrequent(nums, k) {
        // Count frequency of each number
        const count = new Map();
        for (const num of nums) {
            count.set(num, (count.get(num) || 0) + 1);
        }
        
        // Sort by frequency and take top k
        return Array.from(count.keys())
            .sort((a, b) => count.get(b) - count.get(a))
            .slice(0, k);
    }
}