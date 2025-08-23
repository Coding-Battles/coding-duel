import sys

sys.path.append("backend")
from code_testing.docker_runner import generate_java_wrapper

# Simple test code
test_code = """
public class Solution {
    public int maxDepth(TreeNode root) {
        if (root == null) return 0;
        return 1 + Math.max(maxDepth(root.left), maxDepth(root.right));
    }
}
"""

# Generate wrapper
wrapper = generate_java_wrapper("maxDepth", test_code)

# Count braces
open_braces = wrapper.count("{")
close_braces = wrapper.count("}")
print(f"Open braces: {open_braces}")
print(f"Close braces: {close_braces}")
print(f"Balance: {open_braces - close_braces}")

# Look for specific patterns
if "'try' without 'catch'" in wrapper or "'else' without 'if'" in wrapper:
    print("❌ Found problematic patterns")
else:
    print("✅ No obvious pattern issues")

# Save for inspection
with open("debug_wrapper_fixed.java", "w") as f:
    f.write(wrapper)

print(f"Wrapper saved to debug_wrapper_fixed.java ({len(wrapper)} chars)")
