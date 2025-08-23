#!/usr/bin/env python3

import requests
import json


def test_container_with_most_water():
    """Test container-with-most-water API"""

    payload = {
        "player_id": "test_player",
        "code": """class Solution:
    def maxArea(self, height: list[int]) -> int:
        left, right = 0, len(height) - 1
        max_area = 0
        
        while left < right:
            width = right - left
            area = min(height[left], height[right]) * width
            max_area = max(max_area, area)
            
            if height[left] < height[right]:
                left += 1
            else:
                right -= 1
        
        return max_area""",
        "language": "python",
        "question_name": "container-with-most-water",
        "timer": 300,
    }

    try:
        response = requests.post(
            "http://localhost:8000/api/container-with-most-water/test-sample",
            json=payload,
            timeout=30,
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
    test_container_with_most_water()
