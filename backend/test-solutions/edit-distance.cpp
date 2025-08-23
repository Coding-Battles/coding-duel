class Solution {
public:
    int minDistance(string word1, string word2) {
        int m = word1.length();
        int n = word2.length();
        
        // Create DP table
        vector<vector<int>> dp(m + 1, vector<int>(n + 1, 0));
        
        // Initialize base cases
        for (int i = 0; i <= m; i++) {
            dp[i][0] = i; // Delete all characters from word1
        }
        for (int j = 0; j <= n; j++) {
            dp[0][j] = j; // Insert all characters to reach word2
        }
        
        // Fill DP table
        for (int i = 1; i <= m; i++) {
            for (int j = 1; j <= n; j++) {
                if (word1[i-1] == word2[j-1]) {
                    // Characters match, no operation needed
                    dp[i][j] = dp[i-1][j-1];
                } else {
                    // Take minimum of insert, delete, replace
                    dp[i][j] = 1 + min({
                        dp[i-1][j],    // Delete from word1
                        dp[i][j-1],    // Insert into word1
                        dp[i-1][j-1]   // Replace in word1
                    });
                }
            }
        }
        
        return dp[m][n];
    }
};
