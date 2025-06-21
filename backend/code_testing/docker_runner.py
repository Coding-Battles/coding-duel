import os
import tempfile
import json
import docker

# Simple language config - add this to your file
LANGUAGE_CONFIG = {
    "python": {
        "image": "python:3.9-slim",
        "file_extension": ".py",
        "wrapper_template": """import json
import sys
import time
import os

# User's code goes here
{code}

def solution_wrapper():
    try:
        start_time = time.time()
        
        # Read input from file instead of command line
        try:
            with open('/code/input.json', 'r') as f:
                test_input = json.load(f)
        except FileNotFoundError:
            test_input = {{}}
        
        # Call solution function
        if callable(globals().get('solution')):
            if isinstance(test_input, dict):
                result = solution(**test_input)
            else:
                result = solution(test_input)
        else:
            result = "No solution function found"
        
        end_time = time.time()
        
        output = {{
            "result": result,
            "execution_time": end_time - start_time
        }}
        
        print(json.dumps(output))
        
    except Exception as e:
        output = {{
            "result": None,
            "execution_time": None,
            "error": str(e)
        }}
        print(json.dumps(output))

if __name__ == "__main__":
    solution_wrapper()
""",
        "run_command": "python {filename}",
    }
}


def run_code_in_docker(
    code: str, language: str, test_input: dict, timeout: int, docker_client=None
):
    """Run code in a Docker container and return the result."""

    if not docker_client:
        docker_client = docker.from_env()

    config = LANGUAGE_CONFIG.get(language)
    if not config:
        raise ValueError(f"Unsupported language: {language}")

    container = None
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            wrapped_code = config["wrapper_template"].format(code=code)

            code_file = os.path.join(temp_dir, f"solution{config['file_extension']}")
            with open(code_file, "w") as f:
                f.write(wrapped_code)

            # Write input to JSON file instead of command line
            input_file = os.path.join(temp_dir, "input.json")
            with open(input_file, "w") as f:
                json.dump(test_input, f)

            run_command = config["run_command"].format(
                filename=f"solution{config['file_extension']}"
            )

            print(f"Running command: {run_command}")  # Debug output

            # Create and start container
            container = docker_client.containers.run(
                config["image"],
                command=f"/bin/sh -c '{run_command}'",
                volumes={temp_dir: {"bind": "/code", "mode": "ro"}},
                working_dir="/code",
                detach=True,
                mem_limit="128m",
                nano_cpus=500000000,
                remove=False,
            )

            # Wait for container to finish
            try:
                result = container.wait(timeout=timeout)
            except Exception as e:
                try:
                    container.kill()
                except:
                    pass
                return {
                    "success": False,
                    "output": None,
                    "execution_time": None,
                    "error": f"Container execution failed: {str(e)}",
                }

            # Get logs
            logs = container.logs(stdout=True, stderr=True).decode("utf-8")

            if result["StatusCode"] == 0:
                try:
                    # Find the JSON output line
                    output_lines = [
                        line.strip()
                        for line in logs.strip().split("\n")
                        if line.strip()
                    ]

                    for line in reversed(output_lines):
                        try:
                            output_data = json.loads(line)
                            if (
                                isinstance(output_data, dict)
                                and "result" in output_data
                            ):
                                return {
                                    "success": True,
                                    "output": output_data.get("result"),
                                    "execution_time": output_data.get(
                                        "execution_time", 0
                                    ),
                                    "error": output_data.get("error"),
                                }
                        except json.JSONDecodeError:
                            continue

                    return {
                        "success": False,
                        "output": None,
                        "execution_time": None,
                        "error": f"Could not parse JSON from any output line. Raw logs: {logs}",
                    }
                except Exception as e:
                    return {
                        "success": False,
                        "output": None,
                        "execution_time": None,
                        "error": f"Failed to parse output: {logs}. Exception: {str(e)}",
                    }
            else:
                return {
                    "success": False,
                    "output": None,
                    "execution_time": None,
                    "error": f"Container failed: {logs}",
                }

    except docker.errors.ImageNotFound as e:
        return {
            "success": False,
            "output": None,
            "execution_time": None,
            "error": f"Docker image not found: {str(e)}. Run: docker pull python:3.9-slim",
        }
    except Exception as e:
        return {
            "success": False,
            "output": None,
            "execution_time": None,
            "error": f"Error: {str(e)}",
        }
    finally:
        if container:
            try:
                container.remove(force=True)
            except:
                pass


# Test it
if __name__ == "__main__":
    test_code = """def solution(nums, target):
    lookup = {}
    for i, num in enumerate(nums):
        if target - num in lookup:
            return [lookup[target - num], i]
        lookup[num] = i"""

    result = run_code_in_docker(
        code=test_code,
        language="python",
        test_input={"nums": [2, 7, 11, 15], "target": 9},
        timeout=5,
    )

    print(json.dumps(result, indent=2))
