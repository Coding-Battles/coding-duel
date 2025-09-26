#!/usr/bin/env python3
"""
Test script to properly capture only the Java code
"""
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), "backend"))

from backend.code_testing.docker_runner import generate_java_wrapper


def test_java_compilation():
    """Test if the generated Java code compiles correctly"""

    # Simple user code with twoSum method for testing
    simple_user_code = """
class Solution {
    public int[] twoSum(int[] nums, int target) {
        for (int i = 0; i < nums.length; i++) {
            for (int j = i + 1; j < nums.length; j++) {
                if (nums[i] + nums[j] == target) {
                    return new int[]{i, j};
                }
            }
        }
        return new int[]{};
    }
}
"""

    # Generate wrapper without debug prints interfering
    import contextlib
    import io

    # Capture stdout to suppress debug prints
    captured_output = io.StringIO()
    with contextlib.redirect_stdout(captured_output):
        wrapper_code = generate_java_wrapper("test", simple_user_code, "word-break-ii")

    if wrapper_code:
        # Write just the Java code to a file
        with open("TestSolution.java", "w") as f:
            f.write(wrapper_code)

        print("✅ Java code written to TestSolution.java")
        print(f"📄 Code length: {len(wrapper_code)} characters")
        print(f"📄 Lines: {len(wrapper_code.split('\\n'))}")

        # Try to compile it
        import subprocess

        try:
            result = subprocess.run(
                ["javac", "TestSolution.java"],
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode == 0:
                print("✅ Java compilation successful!")
                return True
            else:
                print("❌ Java compilation failed:")
                print(f"STDERR: {result.stderr}")
                return False

        except subprocess.TimeoutExpired:
            print("⏰ Compilation timed out")
            return False
        except Exception as e:
            print(f"❌ Compilation error: {e}")
            return False
    else:
        print("❌ No wrapper code generated")
        return False


if __name__ == "__main__":
    success = test_java_compilation()
    exit(0 if success else 1)
