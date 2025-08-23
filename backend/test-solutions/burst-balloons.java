class Solution {
    public int maxCoins(int[] nums) {
        int n = nums.length;
        // Add boundary balloons with value 1
        int[] balloons = new int[n + 2];
        balloons[0] = 1;
        balloons[n + 1] = 1;
        for (int i = 0; i < n; i++) {
            balloons[i + 1] = nums[i];
        }
        
        // dp[i][j] represents max coins we can get by bursting balloons between i and j (exclusive)
        int[][] dp = new int[n + 2][n + 2];
        
        // len is the length of the interval
        for (int length = 2; length <= n + 1; length++) {
            for (int left = 0; left <= n + 1 - length; left++) {
                int right = left + length;
                // Try bursting each balloon k between left and right
                for (int k = left + 1; k < right; k++) {
                    // Cost of bursting balloon k last in interval (left, right)
                    int coins = balloons[left] * balloons[k] * balloons[right];
                    // Add coins from optimal bursting of left and right sub-intervals
                    int total = coins + dp[left][k] + dp[k][right];
                    dp[left][right] = Math.max(dp[left][right], total);
                }
            }
        }
        
        return dp[0][n + 1];
    }
}
