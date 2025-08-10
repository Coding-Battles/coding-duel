class Solution {
    merge(intervals) {
        if (intervals.length === 0) {
            return [];
        }
        
        // Sort intervals by start time
        intervals.sort((a, b) => a[0] - b[0]);
        
        const merged = [intervals[0]];
        
        for (let i = 1; i < intervals.length; i++) {
            const current = intervals[i];
            const lastMerged = merged[merged.length - 1];
            
            if (current[0] <= lastMerged[1]) {
                // Overlapping intervals, merge them
                lastMerged[1] = Math.max(lastMerged[1], current[1]);
            } else {
                // Non-overlapping interval, add to result
                merged.push(current);
            }
        }
        
        return merged;
    }
}