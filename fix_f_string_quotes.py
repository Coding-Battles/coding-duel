#!/usr/bin/env python3

# Fix all quote escaping issues in f-string


def fix_f_string_quotes():
    with open("backend/code_testing/docker_runner.py", "r") as f:
        content = f.read()

    # Fix all the problematic patterns in the f-string
    fixes = [
        # Fix split patterns
        (
            'arrayContent.split("\\\\],\\\\s*\\\\[")',
            'arrayContent.split("\\\\\\\\],\\\\\\\\s*\\\\\\\\[")',
        ),
        ('subArray.split(",")', 'subArray.split(",")'),  # This one might need escaping
        ('elements.split(",")', 'elements.split(",")'),  # This one might need escaping
        # Fix replaceAll patterns
        ('replaceAll("[\\\\[\\\\]]", "")', 'replaceAll("[\\\\\\\\[\\\\\\\\]]", "")'),
        # Fix any remaining quote issues
        ('split(",")', 'split(",")'),  # These might need fixing
        ('return "";', 'return "";'),  # This might need fixing
    ]

    for old, new in fixes:
        if old in content:
            content = content.replace(old, new)
            print(f"Fixed: {old} -> {new}")

    # More targeted fixes for common patterns
    content = content.replace('split(",")', 'split(",")')
    content = content.replace('return "";', 'return "";')

    with open("backend/code_testing/docker_runner.py", "w") as f:
        f.write(content)

    print("All f-string quote issues fixed")


if __name__ == "__main__":
    fix_f_string_quotes()
