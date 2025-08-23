#!/usr/bin/env python3

# Fix all the quote escaping issues in the main_method section

import re


def fix_quotes_in_file(file_path):
    with open(file_path, "r") as f:
        content = f.read()

    # Pattern to match System.out.println with JSON output
    # We need to replace {\\" with {{\\\" and \\": with \\\":

    # First fix the opening braces and quotes
    content = re.sub(
        r'System\.out\.println\("{\\"([^"]*)\\":',
        r'System.out.println("{{\\"\\1\\":',
        content,
    )

    # Fix the closing quotes and braces
    content = re.sub(
        r', \\"([^"]*)\\":\s*([^"]*)\s*}"\);', r', \\"\1\\": \2}}");', content
    )

    # Fix any remaining {\\"result\\": patterns
    content = re.sub(r'{\\"result\\":', r'{{\\"result\\":', content)
    content = re.sub(r', \\"execution_time\\":', r', \\"execution_time\\":', content)
    content = re.sub(r'}\s*"}\s*\);', r'}}");', content)

    with open(file_path, "w") as f:
        f.write(content)

    print("Fixed quote escaping issues")


if __name__ == "__main__":
    fix_quotes_in_file("backend/code_testing/docker_runner.py")
