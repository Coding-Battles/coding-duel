#!/usr/bin/env python3
"""
Debug script to understand Java class structure injection
"""
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), "backend"))

from backend.code_testing.docker_runner import generate_java_wrapper


def debug_class_structure():
    """Debug the class structure injection logic"""

    # Simple test case
    sample_user_code = """
    class Solution {
        public int test(int x) {
            return x + 1;
        }
    }
    """

    print("🧪 Original user code:")
    lines = sample_user_code.strip().split("\n")
    for i, line in enumerate(lines):
        print(f"{i+1:2}: {line}")

    print("\n🔧 Testing class structure detection...")

    # Simulate the injection logic
    import re

    # Find the Solution class line
    solution_class_line = -1
    for i, line in enumerate(lines):
        if re.search(r"(public\s+)?class\s+Solution", line):
            solution_class_line = i
            print(f"Found Solution class at line {i+1}: {line.strip()}")
            break

    if solution_class_line != -1:
        # Count braces to find the matching closing brace for Solution class
        brace_count = 0
        injection_line = -1

        print(f"\n🔍 Brace counting starting from line {solution_class_line+1}:")
        for i in range(solution_class_line, len(lines)):
            line = lines[i]
            open_braces = line.count("{")
            close_braces = line.count("}")
            brace_count += open_braces
            brace_count -= close_braces

            print(
                f"Line {i+1:2}: '{line.strip()}' | Open: {open_braces}, Close: {close_braces}, Count: {brace_count}"
            )

            # When brace_count reaches 0, we found the matching closing brace
            if brace_count == 0 and i > solution_class_line:
                injection_line = i
                print(f"✅ Found injection point at line {i+1}")
                break

        if injection_line != -1:
            print(
                f"\n🎯 Would inject at line {injection_line+1} (before: '{lines[injection_line].strip()}')"
            )

            # Test injection
            test_injection = "    // INJECTED CODE HERE"
            lines.insert(injection_line, test_injection)

            print(f"\n📝 Result after injection:")
            for i, line in enumerate(lines):
                print(f"{i+1:2}: {line}")
        else:
            print("❌ Could not find injection point")


if __name__ == "__main__":
    debug_class_structure()
