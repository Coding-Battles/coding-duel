import os
import tempfile
import json
import docker
from typing import List, Dict, Any, Optional

# Import Pydantic models
from backend.models.submission import DockerRunRequest
from backend.code_testing.language_config import LANGUAGE_CONFIG

# Language config imported from language_config.py


def extract_java_imports_and_methods(code):
    """Extract import statements and method definitions from Java code."""
    lines = code.split('\n')
    imports = []
    methods = []
    in_class = False
    brace_count = 0
    
    for line in lines:
        stripped = line.strip()
        
        # Extract imports
        if stripped.startswith('import ') and stripped.endswith(';'):
            imports.append(line)
            continue
            
        # Detect class declaration
        if stripped.startswith('class ') or stripped.startswith('public class '):
            in_class = True
            brace_count = 0
            continue
        
        # Handle class body content
        if in_class:
            # Count braces
            open_braces = line.count('{')
            close_braces = line.count('}')
            
            # Skip empty opening brace line of class only if it's the first line
            if stripped == '{' and brace_count == 0:
                brace_count = 1
                continue
            
            # Check if we should include this line (before updating brace count)
            # Include if we're already inside the class, or if this line starts a method/field
            should_include = brace_count > 0 or (brace_count == 0 and open_braces > 0)
            
            # Update brace count
            brace_count += open_braces - close_braces
            
            # Include lines that were inside the class
            if should_include:
                methods.append(line)
            
            # If we've reached the end of the class (brace_count is now 0), stop
            if brace_count == 0:
                break
        else:
            # Code outside class
            methods.append(line)
    
    return '\n'.join(imports), '\n'.join(methods)


def run_code_in_docker(request: DockerRunRequest, docker_client=None):
    """Run code in a Docker container and return the result as a dict."""

    if not docker_client:
        docker_client = docker.from_env()

    config = LANGUAGE_CONFIG.get(request.language)
    if not config:
        raise ValueError(f"Unsupported language: {request.language}")

    container = None
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            # Handle Java imports separately
            if request.language == "java":
                imports, clean_code = extract_java_imports_and_methods(request.code)
                wrapped_code = config["wrapper_template"].format(
                    code=clean_code, 
                    imports=imports
                )
            else:
                wrapped_code = config["wrapper_template"].format(code=request.code)

            # Determine filename based on language
            if request.language == "java":
                code_file = os.path.join(temp_dir, "Solution.java")
            else:
                code_file = os.path.join(temp_dir, f"solution{config['file_extension']}")
            
            with open(code_file, "w") as f:
                f.write(wrapped_code)

            # Write input to JSON file (not needed for current templates)
            # All languages now use command line JSON input

            # Build command sequence
            commands = []
            
            # Add compilation step if needed
            if "compile_command" in config:
                compile_cmd = config["compile_command"].format(
                    filename=os.path.basename(code_file)
                )
                commands.append(compile_cmd)
            
            # Add run command
            if request.language == "java":
                run_command = config["run_command"]
            else:
                run_command = config["run_command"].format(
                    filename=os.path.basename(code_file)
                )
            
            # Pass input as command line argument for all languages
            input_json = json.dumps(request.test_input).replace('"', '\\"')
            run_command += f' "{input_json}"'
            
            commands.append(run_command)
            
            # Combine all commands
            full_command = " && ".join(commands)
            
            print(f"Running command: {full_command}")  # Debug output

            # Create and start container
            container = docker_client.containers.run(
                config["image"],
                command=f"/bin/sh -c '{full_command}'",
                volumes={temp_dir: {"bind": "/code", "mode": "rw"}},  # Changed to rw for compilation
                working_dir="/code",
                detach=True,
                mem_limit="256m",  # Increased for compilation
                nano_cpus=1000000000,  # Increased for compilation
                remove=False,
            )

            # Wait for container to finish
            try:
                result = container.wait(timeout=request.timeout)
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
    from backend.models.submission import DockerRunRequest

    test_request = DockerRunRequest(
        code="""def solution(nums, target):\n    lookup = {}\n    for i, num in enumerate(nums):\n        if target - num in lookup:\n            return [lookup[target - num], i]\n        lookup[num] = i""",
        language="python",
        test_input={"nums": [2, 7, 11, 15], "target": 9},
        timeout=5,
    )

    result = run_code_in_docker(test_request)
    print(json.dumps(result, indent=2))
