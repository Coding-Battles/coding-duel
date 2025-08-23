def maxCoins(nums):
    """
    Burst Balloons - Dynamic Programming Solution
    """
    # Remove zeros first as they don't contribute any coins
    nums = [x for x in nums if x > 0]

    # Add boundary balloons with value 1
    nums = [1] + nums + [1]
    n = len(nums)

    # dp[i][j] represents the maximum coins we can get by bursting balloons between i and j (exclusive)
    dp = [[0] * n for _ in range(n)]

    # length is the length of the interval
    for length in range(3, n + 1):  # minimum length is 3 (i, k, j)
        for i in range(n - length + 1):
            j = i + length - 1
            # Try all possible last balloons to burst in the interval (i, j)
            for k in range(i + 1, j):
                # k is the last balloon to burst between i and j
                coins = nums[i] * nums[k] * nums[j] + dp[i][k] + dp[k][j]
                dp[i][j] = max(dp[i][j], coins)

    return dp[0][n - 1]


# Test cases
test_cases = [
    ([3, 1, 5, 8], 167),
    ([1, 5], 10),
    ([8, 2, 6, 8, 9, 8, 1, 4, 1, 5, 3, 0, 7, 7, 0, 4, 2], 3414),
    ([7, 9, 8, 0, 2], 637),
    ([9, 76, 64, 21, 97, 60], 1086136),
    ([1], 1),
    ([2, 3, 4], 36),
    ([5, 10], 60),
]

print("Testing Burst Balloons solution:")
for i, (nums, expected) in enumerate(test_cases, 1):
    result = maxCoins(nums)
    status = "✓" if result == expected else "✗"
    print(f"Test {i}: {status} nums={nums} -> got {result}, expected {expected}")
