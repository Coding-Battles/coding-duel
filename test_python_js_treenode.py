import sys
import os
import json

sys.path.append("/Users/andriysapeha/Documents/coding_duel/coding-duel")

from backend.code_testing.docker_runner import run_code_in_docker
from backend.models.questions import DockerRunRequest

# Test Python TreeNode support
python_code = """
class Solution:
    def maxDepth(self, root):
        if not root:
            return 0
        
        left_depth = self.maxDepth(root.left)
        right_depth = self.maxDepth(root.right)
        
        return max(left_depth, right_depth) + 1
"""

# Test JavaScript TreeNode support
javascript_code = """
class Solution {
    maxDepth(root) {
        if (!root) {
            return 0;
        }
        
        const leftDepth = this.maxDepth(root.left);
        const rightDepth = this.maxDepth(root.right);
        
        return Math.max(leftDepth, rightDepth) + 1;
    }
}
"""

# Test input: [3, 9, 20, null, null, 15, 7] should return 3
test_input = {"root": [3, 9, 20, None, None, 15, 7]}


def test_language(language, code):
    print(f"\n=== Testing {language.upper()} TreeNode Support ===")
    print("Input:", test_input)

    request = DockerRunRequest(
        code=code,
        language=language,
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


if __name__ == "__main__":
    test_language("python", python_code)
    test_language("javascript", javascript_code)
