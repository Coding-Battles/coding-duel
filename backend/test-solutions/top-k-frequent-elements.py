import heapq
from collections import Counter

class Solution:
    def topKFrequent(self, nums: list[int], k: int) -> list[int]:
        # Count frequency of each number
        count = Counter(nums)
        
        # Use heap to find k most frequent elements
        return heapq.nlargest(k, count.keys(), key=count.get)