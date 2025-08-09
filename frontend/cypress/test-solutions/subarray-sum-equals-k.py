class Solution:
    def subarraySum(self, nums: list[int], k: int) -> int:
        count = 0
        sum_count = {0: 1}  # prefix sum -> count
        prefix_sum = 0
        
        for num in nums:
            prefix_sum += num
            
            # If (prefix_sum - k) exists, it means there's a subarray ending here with sum k
            if prefix_sum - k in sum_count:
                count += sum_count[prefix_sum - k]
            
            # Update prefix sum count
            sum_count[prefix_sum] = sum_count.get(prefix_sum, 0) + 1
        
        return count