class Solution:
    def longestIncreasingPath(self, matrix: list[list[int]]) -> int:
        if not matrix or not matrix[0]:
            return 0
        
        m, n = len(matrix), len(matrix[0])
        memo = {}
        
        def dfs(i, j):
            if (i, j) in memo:
                return memo[(i, j)]
            
            max_path = 1
            directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
            
            for di, dj in directions:
                ni, nj = i + di, j + dj
                if 0 <= ni < m and 0 <= nj < n and matrix[ni][nj] > matrix[i][j]:
                    max_path = max(max_path, 1 + dfs(ni, nj))
            
            memo[(i, j)] = max_path
            return max_path
        
        result = 0
        for i in range(m):
            for j in range(n):
                result = max(result, dfs(i, j))
        
        return result