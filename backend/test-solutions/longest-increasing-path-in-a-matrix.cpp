class Solution {
public:
    int longestIncreasingPath(vector<vector<int>>& matrix) {
        if (matrix.empty() || matrix[0].empty()) return 0;
        
        int m = matrix.size(), n = matrix[0].size();
        vector<vector<int>> memo(m, vector<int>(n, 0));
        int result = 0;
        
        for (int i = 0; i < m; i++) {
            for (int j = 0; j < n; j++) {
                result = max(result, dfs(matrix, i, j, memo));
            }
        }
        
        return result;
    }
    
private:
    int dfs(vector<vector<int>>& matrix, int i, int j, vector<vector<int>>& memo) {
        if (memo[i][j] != 0) return memo[i][j];
        
        int maxPath = 1;
        vector<vector<int>> directions = {{0, 1}, {1, 0}, {0, -1}, {-1, 0}};
        
        for (auto& dir : directions) {
            int ni = i + dir[0], nj = j + dir[1];
            if (ni >= 0 && ni < matrix.size() && nj >= 0 && nj < matrix[0].size() 
                && matrix[ni][nj] > matrix[i][j]) {
                maxPath = max(maxPath, 1 + dfs(matrix, ni, nj, memo));
            }
        }
        
        memo[i][j] = maxPath;
        return maxPath;
    }
};