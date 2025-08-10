class Solution {
    spiralOrder(matrix) {
        if (matrix.length === 0 || matrix[0].length === 0) {
            return [];
        }
        
        const result = [];
        let top = 0, bottom = matrix.length - 1;
        let left = 0, right = matrix[0].length - 1;
        
        while (top <= bottom && left <= right) {
            // Traverse right
            for (let col = left; col <= right; col++) {
                result.push(matrix[top][col]);
            }
            top++;
            
            // Traverse down
            for (let row = top; row <= bottom; row++) {
                result.push(matrix[row][right]);
            }
            right--;
            
            // Traverse left (if we still have rows)
            if (top <= bottom) {
                for (let col = right; col >= left; col--) {
                    result.push(matrix[bottom][col]);
                }
                bottom--;
            }
            
            // Traverse up (if we still have columns)
            if (left <= right) {
                for (let row = bottom; row >= top; row--) {
                    result.push(matrix[row][left]);
                }
                left++;
            }
        }
        
        return result;
    }
}