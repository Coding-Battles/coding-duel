class Solution {
public:
    vector<vector<int>> merge(vector<vector<int>>& intervals) {
        if (intervals.empty()) {
            return {};
        }
        
        // Sort intervals by start time
        sort(intervals.begin(), intervals.end());
        
        vector<vector<int>> merged;
        merged.push_back(intervals[0]);
        
        for (int i = 1; i < intervals.size(); i++) {
            vector<int>& current = intervals[i];
            vector<int>& lastMerged = merged.back();
            
            if (current[0] <= lastMerged[1]) {
                // Overlapping intervals, merge them
                lastMerged[1] = max(lastMerged[1], current[1]);
            } else {
                // Non-overlapping interval, add to result
                merged.push_back(current);
            }
        }
        
        return merged;
    }
};