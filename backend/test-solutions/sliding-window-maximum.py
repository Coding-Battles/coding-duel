class Solution:
    def maxSlidingWindow(self, nums: list[int], k: int) -> list[int]:
        from collections import deque
        
        if not nums or k == 0:
            return []
        
        if k == 1:
            return nums
        
        # Use deque to store indices
        dq = deque()
        result = []
        
        for i in range(len(nums)):
            # Remove indices that are out of current window
            while dq and dq[0] <= i - k:
                dq.popleft()
            
            # Remove indices whose corresponding values are smaller than nums[i]
            while dq and nums[dq[-1]] < nums[i]:
                dq.pop()
            
            dq.append(i)
            
            # Add result for current window
            if i >= k - 1:
                result.append(nums[dq[0]])
        
        return result