#!/usr/bin/env python3
"""
Test coinChange JavaScript implementation
"""
import sys
from pathlib import Path
import argparse
import json

# Add backend to path
sys.path.append(str(Path(__file__).parent / "backend"))

from backend.models.questions import DockerRunRequest
from backend.code_testing.docker_runner import run_code_in_docker


def test_js_coin_change(test_input):
    """Test JavaScript coinChange function execution."""

    js_code = """
class Solution {
    coinChange(coins, amount) {
        if (amount === 0) return 0;
        
        const dp = new Array(amount + 1).fill(amount + 1);
        dp[0] = 0;
        
        for (const coin of coins) {
            for (let i = coin; i <= amount; i++) {
                dp[i] = Math.min(dp[i], dp[i - coin] + 1);
            }
        }
        
        return dp[amount] > amount ? -1 : dp[amount];
    }
}
"""

    print(f"🧪 Testing JavaScript coinChange with input: {test_input}")

    request = DockerRunRequest(
        language="javascript",
        code=js_code,
        function_name="coinChange",
        test_input=test_input,
    )

    result = run_code_in_docker(request)

    print(f"Success: {result.get('success', False)}")
    print(f"Output: {result.get('result', 'No result')}")
    print(f"Error: {result.get('error', 'No error')}")

    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test JavaScript coinChange function")
    parser.add_argument(
        "--input",
        default='{"coins": [1, 3, 4], "amount": 6}',
        help="JSON input for coinChange",
    )

    args = parser.parse_args()

    try:
        input_data = json.loads(args.input)
        test_js_coin_change(input_data)
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON input: {args.input}")
        sys.exit(1)
