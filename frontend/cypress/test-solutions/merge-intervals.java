import java.util.*;

class Solution {
    public int[][] merge(int[][] intervals) {
        if (intervals.length == 0) {
            return new int[0][0];
        }
        
        // Sort intervals by start time
        Arrays.sort(intervals, (a, b) -> a[0] - b[0]);
        
        List<int[]> merged = new ArrayList<>();
        merged.add(intervals[0]);
        
        for (int i = 1; i < intervals.length; i++) {
            int[] current = intervals[i];
            int[] lastMerged = merged.get(merged.size() - 1);
            
            if (current[0] <= lastMerged[1]) {
                // Overlapping intervals, merge them
                lastMerged[1] = Math.max(lastMerged[1], current[1]);
            } else {
                // Non-overlapping interval, add to result
                merged.add(current);
            }
        }
        
        return merged.toArray(new int[merged.size()][]);
    }
}