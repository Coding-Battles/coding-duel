#!/usr/bin/env python3

import requests
import json


def test_3sum_api():
    """Test 3sum API directly"""

    payload = {
        "player_id": "test_player",
        "code": """class Solution:
    def threeSum(self, nums: list[int]) -> list[list[int]]:
        nums.sort()
        result = []
        
        for i in range(len(nums) - 2):
            if i > 0 and nums[i] == nums[i - 1]:
                continue
            
            left, right = i + 1, len(nums) - 1
            
            while left < right:
                total = nums[i] + nums[left] + nums[right]
                
                if total < 0:
                    left += 1
                elif total > 0:
                    right -= 1
                else:
                    result.append([nums[i], nums[left], nums[right]])
                    
                    while left < right and nums[left] == nums[left + 1]:
                        left += 1
                    while left < right and nums[right] == nums[right - 1]:
                        right -= 1
                        
                    left += 1
                    right -= 1
        
        return result""",
        "language": "python",
        "question_name": "3sum",
        "timer": 300,
    }

    try:
        response = requests.post(
            "http://localhost:8000/api/3sum/test-sample", json=payload, timeout=30
        )

        print(f"Response status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Success: {result.get('success', False)}")
            print(f"Total passed: {result.get('total_passed', 0)}")
            print(f"Total failed: {result.get('total_failed', 0)}")

            if result.get("test_results"):
                for i, test in enumerate(result["test_results"]):
                    print(f"\n--- Test {i+1} ---")
                    print(f"Input: {test.get('input', 'N/A')}")
                    print(f"Expected: {test.get('expected_output', 'N/A')}")
                    print(f"Actual: {test.get('actual_output', 'N/A')}")
                    print(f"Passed: {'✅' if test.get('passed', False) else '❌'}")
                    if test.get("error"):
                        print(f"Error: {test['error']}")
        else:
            print(f"Response: {response.text}")

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    test_3sum_api()
