class Solution {
    public int longestIncreasingPath(int[][] matrix) {
        if (matrix == null || matrix.length == 0 || matrix[0].length == 0) return 0;
        
        int m = matrix.length, n = matrix[0].length;
        int[][] memo = new int[m][n];
        int result = 0;
        
        for (int i = 0; i < m; i++) {
            for (int j = 0; j < n; j++) {
                result = Math.max(result, dfs(matrix, i, j, memo));
            }
        }
        
        return result;
    }
    
    private int dfs(int[][] matrix, int i, int j, int[][] memo) {
        if (memo[i][j] != 0) return memo[i][j];
        
        int maxPath = 1;
        int[][] directions = {{0, 1}, {1, 0}, {0, -1}, {-1, 0}};
        
        for (int[] dir : directions) {
            int ni = i + dir[0], nj = j + dir[1];
            if (ni >= 0 && ni < matrix.length && nj >= 0 && nj < matrix[0].length 
                && matrix[ni][nj] > matrix[i][j]) {
                maxPath = Math.max(maxPath, 1 + dfs(matrix, ni, nj, memo));
            }
        }
        
        memo[i][j] = maxPath;
        return maxPath;
    }
}