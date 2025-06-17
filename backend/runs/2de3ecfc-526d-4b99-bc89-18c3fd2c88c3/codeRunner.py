with open("user_code.py") as f:
    user_code = f.read()

# Write the code to an actual Python file
with open("exec.py", "w") as f:
    f.write(user_code)

# Run the code with input
import subprocess

with open("input.txt") as input_file:
    try:
        result = subprocess.run(
            ["python", "exec.py"],
            stdin=input_file,
            stdout=subprocess.PIPE, #captured by capture_output=True in run_code_in_docker
            stderr=subprocess.PIPE,
            timeout=2,
        )
        print(result.stdout.decode())
        if result.stderr:
            print("Errors:", result.stderr.decode())
    except subprocess.TimeoutExpired:
        print("Execution timed out")