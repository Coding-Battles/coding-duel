#!/usr/bin/env python3

import requests
import json


def test_simple_java():
    """Test a simpler Java function first to isolate the issue"""

    # Test a working Java function first
    working_payload = {
        "player_id": "test_player",
        "code": """class Solution {
    public int[] twoSum(int[] nums, int target) {
        for (int i = 0; i < nums.length; i++) {
            for (int j = i + 1; j < nums.length; j++) {
                if (nums[i] + nums[j] == target) {
                    return new int[]{i, j};
                }
            }
        }
        return new int[0];
    }
}""",
        "language": "java",
        "question_name": "two-sum",
        "timer": 300,
    }

    print("🔍 Testing working Java function (two-sum)")
    try:
        response = requests.post(
            "http://localhost:8000/api/two-sum/test-sample",
            json=working_payload,
            timeout=30,
        )

        print(f"✅ Working Java Response status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Success: {result.get('success', False)}")
            print(f"Total passed: {result.get('total_passed', 0)}")
            print(f"Total failed: {result.get('total_failed', 0)}")
            if result.get("error"):
                print(f"Error: {result['error']}")
        else:
            print(f"Response: {response.text}")

    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    test_simple_java()
