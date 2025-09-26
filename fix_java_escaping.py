#!/usr/bin/env python3
"""
Script to fix Java regex escaping issues in docker_runner.py
"""


def fix_java_escaping():
    file_path = "backend/code_testing/docker_runner.py"

    # Read the file
    with open(file_path, "r") as f:
        content = f.read()

    # Patterns to fix - these are the problematic f-string patterns
    # Pattern: \\\"([stuff])\\\"\\s* should become \\\\\"([stuff])\\\\\"\\\\s*
    patterns_to_fix = [
        (
            '\\\\"([^\\\\"]+)\\\\"\\\\s*:\\\\s*',
            '\\\\\\\\"([^\\\\\\\\"]+)\\\\\\\\"\\\\\\\\s*:\\\\\\\\s*',
        ),
        ("\\\\s*:\\\\s*", "\\\\\\\\s*:\\\\\\\\s*"),
        ("\\\\d+", "\\\\\\\\d+"),
        ("\\\\[", "\\\\\\\\["),
        ("\\\\]", "\\\\\\\\]"),
        ("\\\\\\]", "\\\\\\\\\\\\]"),  # Handle cases where ] was already doubled
        ("([^\\\\])+", "([^\\\\\\\\])+"),
    ]

    print("🔧 Fixing Java regex escaping patterns...")

    # Specific patterns that need fixing based on the error output
    specific_fixes = [
        (
            '"\\\\"" + key + "\\\\\\"\\\\s*:\\\\s*(-?\\\\d+)"',
            '"\\\\\\\\"" + key + "\\\\\\\\\\"\\\\\\\\s*:\\\\\\\\s*(-?\\\\\\\\d+)"',
        ),
        (
            '"\\\\"" + key + "\\\\\\"\\\\s*:\\\\s*\\\\[([^\\\\]]+)\\\\]"',
            '"\\\\\\\\"" + key + "\\\\\\\\\\"\\\\\\\\s*:\\\\\\\\s*\\\\\\\\[([^\\\\\\\\]]+)\\\\\\\\]"',
        ),
        (
            '"\\\\"" + key + "\\\\\\"\\\\s*:\\\\s*\\\\"([^\\\\"]+)\\\\\\"',
            '"\\\\\\\\"" + key + "\\\\\\\\\\"\\\\\\\\s*:\\\\\\\\s*\\\\\\\\"([^\\\\\\\\"]+)\\\\\\\\\\"',
        ),
        (
            '"\\\\"" + paramName + "\\\\\\"\\\\s*:\\\\s*\\\\[([^\\\\]]+)\\\\]"',
            '"\\\\\\\\"" + paramName + "\\\\\\\\\\"\\\\\\\\s*:\\\\\\\\s*\\\\\\\\[([^\\\\\\\\]]+)\\\\\\\\]"',
        ),
        ("\\\\],\\\\s*\\\\[", "\\\\\\\\],\\\\\\\\s*\\\\\\\\["),
        (
            '"\\\\"([^"]+)\\\\\\"\\\\s*:\\\\s*([^,}}]+)"',
            '"\\\\\\\\"([^"]+)\\\\\\\\\\"\\\\\\\\s*:\\\\\\\\s*([^,}}]+)"',
        ),
    ]

    # Apply specific fixes
    for old_pattern, new_pattern in specific_fixes:
        if old_pattern in content:
            content = content.replace(old_pattern, new_pattern)
            print(f"✅ Fixed pattern: {old_pattern[:50]}...")
        else:
            print(f"⚠️  Pattern not found: {old_pattern[:50]}...")

    # Write the file back
    with open(file_path, "w") as f:
        f.write(content)

    print("🎉 Java regex escaping fixes completed!")


if __name__ == "__main__":
    fix_java_escaping()
