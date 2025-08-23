class Solution {
  minCut(s) {
    const n = s.length;
    if (n <= 1) return 0;

    // Precompute palindrome table
    const isPalindrome = Array(n)
      .fill(null)
      .map(() => Array(n).fill(false));

    // Every single character is a palindrome
    for (let i = 0; i < n; i++) {
      isPalindrome[i][i] = true;
    }

    // Check for length 2 palindromes
    for (let i = 0; i < n - 1; i++) {
      if (s[i] === s[i + 1]) {
        isPalindrome[i][i + 1] = true;
      }
    }

    // Check for palindromes of length 3 and more
    for (let length = 3; length <= n; length++) {
      for (let i = 0; i <= n - length; i++) {
        const j = i + length - 1;
        if (s[i] === s[j] && isPalindrome[i + 1][j - 1]) {
          isPalindrome[i][j] = true;
        }
      }
    }

    // DP to find minimum cuts
    // dp[i] = minimum cuts needed for s[0:i+1]
    const dp = new Array(n).fill(0);

    for (let i = 0; i < n; i++) {
      if (isPalindrome[0][i]) {
        dp[i] = 0;
      } else {
        dp[i] = i; // worst case: each character is its own partition
        for (let j = 0; j < i; j++) {
          if (isPalindrome[j + 1][i]) {
            dp[i] = Math.min(dp[i], dp[j] + 1);
          }
        }
      }
    }

    return dp[n - 1];
  }
}
