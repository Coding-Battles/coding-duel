class Solution:
    def productExceptSelf(self, nums: list[int]) -> list[int]:
        n = len(nums)
        result = [1] * n
        
        # Left pass: result[i] contains product of all elements to the left of i
        for i in range(1, n):
            result[i] = result[i - 1] * nums[i - 1]
        
        # Right pass: multiply with product of all elements to the right of i
        right_product = 1
        for i in range(n - 1, -1, -1):
            result[i] *= right_product
            right_product *= nums[i]
        
        return result