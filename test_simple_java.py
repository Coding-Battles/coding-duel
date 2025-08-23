import sys

sys.path.append("backend")
from code_testing.docker_runner import CodeRunner
import json

# Create a simple test
runner = CodeRunner()

# Simple test - basic integer return
request_data = {
    "language": "java",
    "code": """
public class Solution {
    public int maxDepth(TreeNode root) {
        if (root == null) return 0;
        return 1 + Math.max(maxDepth(root.left), maxDepth(root.right));
    }
}
""",
    "function_name": "maxDepth",
    "inputs": {"root": [3, 9, 20, None, None, 15, 7]},
}

print("Testing simple Java TreeNode execution...")
result = runner.run_code_in_docker(request_data)
print(f"Success: {result.success}")
print(f"Output: {result.output}")
print(f"Error: {result.error}")

expected = 3
if result.success and result.output:
    try:
        output_data = json.loads(result.output)
        actual = output_data.get("result")
        print(f"Expected: {expected}")
        print(f"Actual: {actual}")
        print(f"Match: {actual == expected}")
    except Exception as e:
        print(f"Failed to parse output: {e}")
else:
    print("Test failed - no output")
