class Solution {
    longestIncreasingPath(matrix) {
        if (!matrix || !matrix.length || !matrix[0].length) return 0;
        
        const m = matrix.length, n = matrix[0].length;
        const memo = new Map();
        
        const dfs = (i, j) => {
            const key = `${i},${j}`;
            if (memo.has(key)) return memo.get(key);
            
            let maxPath = 1;
            const directions = [[0, 1], [1, 0], [0, -1], [-1, 0]];
            
            for (const [di, dj] of directions) {
                const ni = i + di, nj = j + dj;
                if (ni >= 0 && ni < m && nj >= 0 && nj < n && matrix[ni][nj] > matrix[i][j]) {
                    maxPath = Math.max(maxPath, 1 + dfs(ni, nj));
                }
            }
            
            memo.set(key, maxPath);
            return maxPath;
        };
        
        let result = 0;
        for (let i = 0; i < m; i++) {
            for (let j = 0; j < n; j++) {
                result = Math.max(result, dfs(i, j));
            }
        }
        
        return result;
    }
}