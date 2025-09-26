#!/usr/bin/env python3

import sys
import os

# Add the backend directory to the path
backend_path = os.path.join(os.path.dirname(__file__), "backend")
sys.path.append(backend_path)

from code_testing.docker_runner import DockerRunner


def test_merge_k_sorted():
    print("Testing merge-k-sorted-lists harness...")

    docker_runner = DockerRunner()

    user_code = """
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

class Solution:
    def mergeKLists(self, lists):
        if not lists:
            return None
        
        while len(lists) > 1:
            merged_lists = []
            for i in range(0, len(lists), 2):
                l1 = lists[i] if i < len(lists) else None
                l2 = lists[i + 1] if i + 1 < len(lists) else None
                merged_lists.append(self.mergeTwoLists(l1, l2))
            lists = merged_lists
        return lists[0]
    
    def mergeTwoLists(self, l1, l2):
        dummy = ListNode()
        current = dummy
        
        while l1 and l2:
            if l1.val <= l2.val:
                current.next = l1
                l1 = l1.next
            else:
                current.next = l2
                l2 = l2.next
            current = current.next
        
        current.next = l1 or l2
        return dummy.next
"""

    # Test with simple input
    print("\nTest 1:")
    print("Input: [[1,4,5],[1,3,4],[2,6]]")
    print("Expected: [1,1,2,3,4,4,5,6]")

    request_data = {
        "function_name": "mergeKLists",
        "language": "cpp",
        "code": user_code,
        "input": "[[1,4,5],[1,3,4],[2,6]]",
        "question": "merge-k-sorted-lists",
        "timeout": 30,
    }

    result = docker_runner.run_code(request_data)
    print(f"Raw result: {result}")


if __name__ == "__main__":
    test_merge_k_sorted()
