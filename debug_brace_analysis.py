with open("debug_wrapper_fixed.java", "r") as f:
    content = f.read()

lines = content.split("\n")
balance = 0
brace_locations = []

for i, line in enumerate(lines, 1):
    for j, char in enumerate(line):
        if char == "{":
            balance += 1
            brace_locations.append(f"Line {i}:{j+1} - '{char}' (balance: {balance})")
        elif char == "}":
            balance -= 1
            brace_locations.append(f"Line {i}:{j+1} - '{char}' (balance: {balance})")

print(f"Final balance: {balance}")
print("Last 10 brace operations:")
for loc in brace_locations[-10:]:
    print(loc)

# If balance is negative, show where we went negative
if balance < 0:
    print("\nWhere balance first went negative:")
    running_balance = 0
    for i, loc in enumerate(brace_locations):
        if "{" in loc:
            running_balance += 1
        else:
            running_balance -= 1
        if running_balance < 0:
            print(f"First negative at: {loc}")
            # Show context around this point
            start = max(0, i - 5)
            end = min(len(brace_locations), i + 5)
            print("Context:")
            for j in range(start, end):
                marker = " >>> " if j == i else "     "
                print(f"{marker}{brace_locations[j]}")
            break
