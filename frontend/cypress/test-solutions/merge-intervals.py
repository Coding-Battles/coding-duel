class Solution:
    def merge(self, intervals: list[list[int]]) -> list[list[int]]:
        if not intervals:
            return []
        
        # Sort intervals by start time
        intervals.sort(key=lambda x: x[0])
        
        merged = [intervals[0]]
        
        for current in intervals[1:]:
            last_merged = merged[-1]
            
            if current[0] <= last_merged[1]:
                # Overlapping intervals, merge them
                last_merged[1] = max(last_merged[1], current[1])
            else:
                # Non-overlapping interval, add to result
                merged.append(current)
        
        return merged