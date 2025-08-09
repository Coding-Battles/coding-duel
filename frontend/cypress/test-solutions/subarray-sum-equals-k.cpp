class Solution {
public:
    int subarraySum(vector<int>& nums, int k) {
        int count = 0;
        unordered_map<int, int> sumCount;
        sumCount[0] = 1; // prefix sum -> count
        int prefixSum = 0;
        
        for (int num : nums) {
            prefixSum += num;
            
            // If (prefixSum - k) exists, it means there's a subarray ending here with sum k
            if (sumCount.find(prefixSum - k) != sumCount.end()) {
                count += sumCount[prefixSum - k];
            }
            
            // Update prefix sum count
            sumCount[prefixSum]++;
        }
        
        return count;
    }
};