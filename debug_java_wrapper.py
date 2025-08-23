#!/usr/bin/env python3
"""
Test Java wrapper generation directly to debug the structure issue.
"""

import sys
import os

sys.path.append("/Users/andriysapeha/Documents/coding_duel/coding-duel")

from backend.code_testing.docker_runner import generate_java_wrapper


def test_java_wrapper():
    # Test with a simple solution
    user_code = """
class Solution {
    public ListNode addTwoNumbers(ListNode l1, ListNode l2) {
        return null;
    }
}
"""

    print("🔍 TESTING JAVA WRAPPER GENERATION")
    print("=" * 50)

    try:
        wrapper = generate_java_wrapper("addTwoNumbers", user_code)

        # Write to file to examine
        with open("debug_wrapper.java", "w") as f:
            f.write(wrapper)

        print("✅ Wrapper generated successfully")
        print(f"📝 Wrapper written to debug_wrapper.java ({len(wrapper)} chars)")

        # Check for common issues
        if (
            "private static" in wrapper
            and "class "
            not in wrapper.split("private static")[0].split("private static")[-1]
        ):
            print("❌ Found private static methods outside of class!")
        else:
            print("✅ All private static methods appear to be inside classes")

        # Count braces
        open_braces = wrapper.count("{")
        close_braces = wrapper.count("}")
        print(f"🔧 Brace count: {open_braces} open, {close_braces} close")

        if open_braces != close_braces:
            print(f"❌ Brace mismatch! Difference: {open_braces - close_braces}")
        else:
            print("✅ Braces are balanced")

    except Exception as e:
        print(f"❌ Error generating wrapper: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    test_java_wrapper()
