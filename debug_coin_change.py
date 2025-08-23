#!/usr/bin/env python3
"""
Test coinChange with explicit pattern handling
"""
import sys
from pathlib import Path
import argparse
import json

# Add backend to path
sys.path.append(str(Path(__file__).parent / "backend"))

from backend.models.questions import DockerRunRequest
from backend.code_testing.docker_runner import run_code_in_docker


def test_coin_change(test_input):
    """Test coinChange function execution."""

    java_code = """
import java.util.*;

class Solution {
    public int coinChange(int[] coins, int amount) {
        if (amount == 0) return 0;
        
        int[] dp = new int[amount + 1];
        Arrays.fill(dp, amount + 1);
        dp[0] = 0;
        
        for (int coin : coins) {
            for (int i = coin; i <= amount; i++) {
                dp[i] = Math.min(dp[i], dp[i - coin] + 1);
            }
        }
        
        return dp[amount] > amount ? -1 : dp[amount];
    }
}
"""

    print(f"🧪 Testing coinChange with input: {test_input}")

    request = DockerRunRequest(
        language="java",
        code=java_code,
        function_name="coinChange",
        test_input=test_input,
    )

    result = run_code_in_docker(request)

    print(f"Success: {result.get('success', False)}")
    print(f"Output: {result.get('result', 'No result')}")
    print(f"Error: {result.get('error', 'No error')}")

    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test coinChange function")
    parser.add_argument(
        "--input",
        default='{"coins": [1, 3, 4], "amount": 6}',
        help="JSON input for coinChange",
    )

    args = parser.parse_args()

    try:
        input_data = json.loads(args.input)
        test_coin_change(input_data)
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON input: {args.input}")
        sys.exit(1)
