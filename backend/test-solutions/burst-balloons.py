from typing import List


class Solution:
    def maxCoins(self, nums: List[int]) -> int:
        # Add boundary balloons with value 1
        balloons = [1] + nums + [1]
        n = len(balloons)

        # dp[i][j] represents max coins we can get by bursting balloons between i and j (exclusive)
        dp = [[0] * n for _ in range(n)]

        # len is the length of the interval
        for length in range(2, n):  # interval length from 2 to n-1
            for left in range(n - length):
                right = left + length
                # Try bursting each balloon k between left and right
                for k in range(left + 1, right):
                    # Cost of bursting balloon k last in interval (left, right)
                    coins = balloons[left] * balloons[k] * balloons[right]
                    # Add coins from optimal bursting of left and right sub-intervals
                    total = coins + dp[left][k] + dp[k][right]
                    dp[left][right] = max(dp[left][right], total)

        return dp[0][n - 1]
