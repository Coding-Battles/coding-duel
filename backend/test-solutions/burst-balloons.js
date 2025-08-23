class Solution {
  maxCoins(nums) {
    // Add boundary balloons with value 1
    const balloons = [1, ...nums, 1];
    const n = balloons.length;

    // dp[i][j] represents max coins we can get by bursting balloons between i and j (exclusive)
    const dp = Array(n)
      .fill(null)
      .map(() => Array(n).fill(0));

    // len is the length of the interval
    for (let length = 2; length < n; length++) {
      for (let left = 0; left < n - length; left++) {
        const right = left + length;
        // Try bursting each balloon k between left and right
        for (let k = left + 1; k < right; k++) {
          // Cost of bursting balloon k last in interval (left, right)
          const coins = balloons[left] * balloons[k] * balloons[right];
          // Add coins from optimal bursting of left and right sub-intervals
          const total = coins + dp[left][k] + dp[k][right];
          dp[left][right] = Math.max(dp[left][right], total);
        }
      }
    }

    return dp[0][n - 1];
  }
}
