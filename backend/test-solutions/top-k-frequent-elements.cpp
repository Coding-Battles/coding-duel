class Solution {
public:
    vector<int> topKFrequent(vector<int>& nums, int k) {
        // Count frequency of each number
        unordered_map<int, int> count;
        for (int num : nums) {
            count[num]++;
        }
        
        // Use min heap to keep track of k most frequent elements
        priority_queue<pair<int, int>, vector<pair<int, int>>, greater<pair<int, int>>> heap;
        
        for (auto& p : count) {
            heap.push({p.second, p.first});
            if (heap.size() > k) {
                heap.pop();
            }
        }
        
        // Extract result
        vector<int> result;
        while (!heap.empty()) {
            result.push_back(heap.top().second);
            heap.pop();
        }
        
        return result;
    }
};