class Solution {
    maxArea(height) {
        let left = 0, right = height.length - 1;
        let maxArea = 0;
        
        while (left < right) {
            // Calculate current area
            const width = right - left;
            const area = Math.min(height[left], height[right]) * width;
            maxArea = Math.max(maxArea, area);
            
            // Move the pointer with smaller height
            if (height[left] < height[right]) {
                left++;
            } else {
                right--;
            }
        }
        
        return maxArea;
    }
}