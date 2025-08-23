import sys
import os
import json

sys.path.append("/Users/andriysapeha/Documents/coding_duel/coding-duel")

from backend.code_testing.docker_runner import run_code_in_docker
from backend.models.questions import DockerRunRequest

# Test the maximum depth binary tree problem with Java
java_code = """
class Solution {
    public int maxDepth(TreeNode root) {
        if (root == null) {
            return 0;
        }
        
        int leftDepth = maxDepth(root.left);
        int rightDepth = maxDepth(root.right);
        
        return Math.max(leftDepth, rightDepth) + 1;
    }
}
"""

# Test input: [3, 9, 20, null, null, 15, 7] should return 3
test_input = {"root": [3, 9, 20, None, None, 15, 7]}

print("Testing Java TreeNode support for maximum depth:")
print("Input:", test_input)

request = DockerRunRequest(
    code=java_code,
    language="java",
    test_input=test_input,
    timeout=10,
    function_name="maxDepth",
)

try:
    result = run_code_in_docker(request)
    print("Success:", result["success"])
    print("Output:", result["output"])
    print("Expected: 3")
    print("Match:", result["output"] == 3)
    if result["error"]:
        print("Error:", result["error"])
except Exception as e:
    print("Exception:", e)
    import traceback

    traceback.print_exc()
