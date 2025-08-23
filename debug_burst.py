def maxCoins_debug(nums):
    """
    Burst Balloons - Dynamic Programming Solution with debug
    """
    print(f"Original nums: {nums}")

    # Remove zeros first as they don't contribute any coins
    nums = [x for x in nums if x > 0]
    print(f"After removing zeros: {nums}")

    # Add boundary balloons with value 1
    nums = [1] + nums + [1]
    n = len(nums)
    print(f"With boundaries: {nums}")

    # dp[i][j] represents the maximum coins we can get by bursting balloons between i and j (exclusive)
    dp = [[0] * n for _ in range(n)]

    # length is the length of the interval
    for length in range(3, n + 1):  # minimum length is 3 (i, k, j)
        print(f"\nLength {length}:")
        for i in range(n - length + 1):
            j = i + length - 1
            print(f"  Interval [{i}, {j}] (values: {nums[i]} to {nums[j]})")
            # Try all possible last balloons to burst in the interval (i, j)
            for k in range(i + 1, j):
                # k is the last balloon to burst between i and j
                coins = nums[i] * nums[k] * nums[j] + dp[i][k] + dp[k][j]
                print(
                    f"    k={k} (value {nums[k]}): {nums[i]}*{nums[k]}*{nums[j]} + {dp[i][k]} + {dp[k][j]} = {coins}"
                )
                if coins > dp[i][j]:
                    dp[i][j] = coins
                    print(f"    New max for dp[{i}][{j}] = {coins}")

    print(f"\nFinal DP table:")
    for row in dp:
        print(row)

    return dp[0][n - 1]


# Test the small case
print("Testing [2, 3, 4] case:")
result = maxCoins_debug([2, 3, 4])
print(f"Result: {result}, Expected: 20")
