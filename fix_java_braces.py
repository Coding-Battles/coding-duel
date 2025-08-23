import re

# Read the file
with open("backend/code_testing/docker_runner.py", "r") as f:
    content = f.read()

# Split into lines to work with specific ranges
lines = content.split("\n")

# Find the Java template section (starts at line 604, ends at 967)
java_start = 603  # 0-indexed
java_end = 966  # 0-indexed

print(f"Processing lines {java_start+1} to {java_end+1}")

# Process each line in the Java template section
changes_made = 0
for i in range(java_start, java_end + 1):
    if i < len(lines):
        original_line = lines[i]

        # Replace double braces with single braces, but be careful about:
        # 1. f-string literal braces that should remain double (like JSON strings)
        # 2. Only fix Java code braces, not JSON output braces

        # First, replace Java code block braces (structural braces)
        # Pattern: {{ at start of content or after whitespace (not inside strings)
        # Pattern: }} at end of content or before whitespace (not inside strings)

        modified_line = original_line

        # Fix structural opening braces - {{ followed by optional whitespace and newline/comment
        modified_line = re.sub(r"{{(\s*)$", r"{\1", modified_line)
        modified_line = re.sub(r"{{(\s*//)", r"{\1", modified_line)

        # Fix structural closing braces - }} with optional whitespace before
        modified_line = re.sub(r"^(\s*)}}", r"\1}", modified_line)
        modified_line = re.sub(r"(\s+)}}(\s*)$", r"\1}\2", modified_line)
        modified_line = re.sub(r"}}(\s+else)", r"}\1", modified_line)

        # Fix method/class definition braces
        if " {{" in modified_line and (
            "public static" in modified_line or "class " in modified_line
        ):
            modified_line = modified_line.replace(" {{", " {")

        # Fix control structure braces
        if any(
            keyword in modified_line
            for keyword in ["if (", "while (", "for (", "} else {"]
        ):
            modified_line = re.sub(r"{{", "{", modified_line)
            modified_line = re.sub(r"}}", "}", modified_line)

        if modified_line != original_line:
            changes_made += 1
            print(
                f"Line {i+1}: {original_line.strip()[:60]}... -> {modified_line.strip()[:60]}..."
            )
            lines[i] = modified_line

print(f"\nTotal changes made: {changes_made}")

# Write back the modified content
with open("backend/code_testing/docker_runner.py", "w") as f:
    f.write("\n".join(lines))

print("File updated successfully!")
