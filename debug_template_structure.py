#!/usr/bin/env python3
"""
Debug script to examine the exact template structure
"""
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), "backend"))

from backend.code_testing.docker_runner import generate_java_wrapper


def debug_template_structure():
    """Debug the exact template that's being generated"""

    # Simple user code to focus on the structure
    simple_user_code = """
class Solution {
    public int test() { return 42; }
}
"""

    print("🧪 Testing template structure with simple code...")

    try:
        wrapper_code = generate_java_wrapper("test", simple_user_code, "word-break-ii")

        if wrapper_code:
            lines = wrapper_code.split("\n")

            print(f"📋 Full generated wrapper ({len(lines)} lines):")
            for i, line in enumerate(lines):
                print(f"{i+1:3}: {line}")
        else:
            print("❌ Wrapper generation failed")

    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    debug_template_structure()
