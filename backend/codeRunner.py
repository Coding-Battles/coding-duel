import importlib.util
import sys
import inspect


# Read input
with open("input.txt") as f:
    input_data = f.read().strip().split()

# Load user code
with open("user_code.py") as f:
    user_code = f.read()

# Write user code to a file so we can import it
with open("exec_user_code.py", "w") as f:
    f.write(user_code)

spec = importlib.util.spec_from_file_location("user_module", "exec_user_code.py")
user_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(user_module)

functions = [obj for name, obj in inspect.getmembers(user_module) if inspect.isfunction(obj)]

# Run the code with input
if functions:
    func = functions[0]  # Call the first function
    # Convert input strings to numbers if possible
    args = [int(x) if x.isdigit() else x for x in input_data]
    result = func(*args)
    if result is not None:
        print(result)
else:
    print("No callable function found.")