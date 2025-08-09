import java.util.*;

class Solution {
    public int subarraySum(int[] nums, int k) {
        int count = 0;
        Map<Integer, Integer> sumCount = new HashMap<>();
        sumCount.put(0, 1); // prefix sum -> count
        int prefixSum = 0;
        
        for (int num : nums) {
            prefixSum += num;
            
            // If (prefixSum - k) exists, it means there's a subarray ending here with sum k
            if (sumCount.containsKey(prefixSum - k)) {
                count += sumCount.get(prefixSum - k);
            }
            
            // Update prefix sum count
            sumCount.put(prefixSum, sumCount.getOrDefault(prefixSum, 0) + 1);
        }
        
        return count;
    }
}