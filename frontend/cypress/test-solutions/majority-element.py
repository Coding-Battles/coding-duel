class Solution:
    def majorityElement(self, nums: list[int]) -> int:
        # Boyer-Moore Voting Algorithm
        candidate = None
        count = 0
        
        for num in nums:
            if count == 0:
                candidate = num
            count += 1 if num == candidate else -1
        
        return candidate