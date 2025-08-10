import java.util.*;

class Solution {
    public int[] topKFrequent(int[] nums, int k) {
        // Count frequency of each number
        Map<Integer, Integer> count = new HashMap<>();
        for (int num : nums) {
            count.put(num, count.getOrDefault(num, 0) + 1);
        }
        
        // Use min heap to keep track of k most frequent elements
        PriorityQueue<Integer> heap = new PriorityQueue<>((a, b) -> count.get(a) - count.get(b));
        
        for (int num : count.keySet()) {
            heap.offer(num);
            if (heap.size() > k) {
                heap.poll();
            }
        }
        
        // Convert to array
        int[] result = new int[k];
        for (int i = 0; i < k; i++) {
            result[i] = heap.poll();
        }
        
        return result;
    }
}