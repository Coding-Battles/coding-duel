import os
import json
import docker
import threading
from typing import Dict, Any, Optional

# Import Pydantic models
from backend.models.questions import DockerRunRequest
from backend.code_testing.language_config import LANGUAGE_CONFIG

# Global Docker client and persistent containers
_docker_client = None
_persistent_containers = {}
_container_lock = threading.Lock()


def get_docker_client():
    global _docker_client
    if _docker_client is None:
        _docker_client = docker.from_env()
    return _docker_client


def get_persistent_container(language: str):
    """Get or create a persistent container for the given language."""
    global _persistent_containers

    with _container_lock:
        container_name = f"{language}-runner"

        # Check if container exists and is running
        if container_name in _persistent_containers:
            try:
                container = _persistent_containers[container_name]
                container.reload()
                if container.status == "running":
                    print(
                        f"🐛 [DOCKER DEBUG] Reusing existing {language} container: {container.id[:12]}"
                    )
                    return container
            except Exception as e:
                print(f"🐛 [DOCKER DEBUG] Container {container_name} is dead: {e}")
                # Container is dead, remove from cache
                del _persistent_containers[container_name]

        # Create new persistent container
        print(
            f"🐛 [DOCKER DEBUG] Creating NEW {language} container - this should only happen at startup!"
        )
        config = LANGUAGE_CONFIG.get(language)
        if not config:
            raise ValueError(f"Unsupported language: {language}")

        docker_client = get_docker_client()

        # Remove existing container if it exists
        try:
            old_container = docker_client.containers.get(container_name)
            old_container.remove(force=True)
            print(f"🐛 [DOCKER DEBUG] Removed old {container_name} container")
        except:
            pass

        # Create new container with appropriate startup command
        startup_cmd = config.get("startup_command", "sleep infinity")
        print(
            f"🐛 [DOCKER DEBUG] Starting new {language} container with image {config['image']}"
        )
        print(f"🐛 [DOCKER DEBUG] Startup command: {startup_cmd}")
        
        # For Java, we need to setup the persistent server
        if language == "java" and "persistent_server" in config:
            # Start with sleep first, then setup server
            container = docker_client.containers.run(
                config["image"],
                command="sleep infinity",
                name=container_name,
                detach=True,
                mem_limit=config.get("mem_limit", "128m"),
                nano_cpus=300000000,  # 0.3 CPU core
                network_mode="none",
                security_opt=["no-new-privileges:true"],
                working_dir="/tmp",
                remove=False,
            )
            
            # Setup the persistent Java server
            setup_java_persistent_server(container, config)
        else:
            container = docker_client.containers.run(
                config["image"],
                command=startup_cmd,
                name=container_name,
                detach=True,
                mem_limit=config.get("mem_limit", "128m"),
                nano_cpus=300000000,  # 0.3 CPU core
                network_mode="none",
                security_opt=["no-new-privileges:true"],
                working_dir="/tmp",
                remove=False,
            )

        print(
            f"🐛 [DOCKER DEBUG] Created new {language} container: {container.id[:12]}"
        )
        _persistent_containers[container_name] = container
        return container


def run_code_in_docker(
    request: DockerRunRequest, docker_client=None, use_fast_runner=None
):
    """Run code using persistent containers for fast execution."""
    import time

    start_time = time.time()
    print(f"🐛 [DOCKER DEBUG] Starting {request.language} execution")
    print(f"🐛 [DOCKER DEBUG] Function name: {request.function_name}")
    print(f"🐛 [DOCKER DEBUG] Raw request.function_name: {repr(request.function_name)}")
    print(f"🐛 [DOCKER DEBUG] Request language: {repr(request.language)}")

    try:
        config = LANGUAGE_CONFIG.get(request.language)
        if not config:
            raise ValueError(f"Unsupported language: {request.language}")

        # Get persistent container
        container_start = time.time()
        container = get_persistent_container(request.language)
        container_time = (time.time() - container_start) * 1000
        print(f"🐛 [DOCKER DEBUG] Getting container took {container_time:.0f}ms")

        # Prepare code with wrapper template
        print(f"🐛 [DOCKER DEBUG] About to format wrapper template for {request.language}")
        try:
            # Special processing for Java firstBadVersion to avoid class conflicts
            processed_code = request.code
            additional_imports = ""
            
            if request.language == "java" and request.function_name == "firstBadVersion":
                # Remove "extends VersionControl" from user code if present to avoid conflicts
                processed_code = processed_code.replace("extends VersionControl", "").replace("  {", " {")
                print(f"🐛 [DOCKER DEBUG] Cleaned Java code for firstBadVersion")
            
            wrapped_code = config["wrapper_template"].format(
                code=processed_code, 
                imports=additional_imports,
                function_name=request.function_name
            )
            print(f"🐛 [DOCKER DEBUG] Wrapped code length: {len(wrapped_code)}")
        except Exception as e:
            print(f"🐛 [DOCKER DEBUG] Exception formatting wrapper: {e}")
            raise

        # Determine filename
        if request.language == "java":
            filename = "Solution.java"
        else:
            filename = f"solution{config['file_extension']}"

        # Write code to container using docker exec
        file_start = time.time()
        import base64

        encoded_code = base64.b64encode(wrapped_code.encode("utf-8")).decode("ascii")

        # Create file in container
        create_result = container.exec_run(
            f"sh -c 'echo {encoded_code} | base64 -d > /tmp/{filename}'", workdir="/tmp"
        )
        file_time = (time.time() - file_start) * 1000
        print(f"🐛 [DOCKER DEBUG] File creation took {file_time:.0f}ms")

        if create_result.exit_code != 0:
            return {
                "success": False,
                "output": None,
                "execution_time": (time.time() - start_time) * 1000,
                "error": f"Failed to create file: {create_result.output.decode('utf-8')}",
            }
            
        print(f"🐛 [DOCKER DEBUG] File created successfully, proceeding to build commands...")

        # Build command sequence
        commands = []
        print(f"🐛 [DOCKER DEBUG] Building commands...")

        # Add compilation step if needed
        if "compile_command" in config:
            compile_cmd = config["compile_command"].format(filename=filename)
            commands.append(compile_cmd)
            print(f"🐛 [DOCKER DEBUG] Added compile command: {compile_cmd}")

        # Add run command
        if request.language == "java":
            run_command = config["run_command"]
        else:
            run_command = config["run_command"].format(filename=filename)
        
        print(f"🐛 [DOCKER DEBUG] Base run command: {run_command}")

        # Pass arguments based on language
        print(f"🐛 [DOCKER DEBUG] About to check language condition: {request.language} in ['python', 'javascript', 'java']")
        if request.language in ["python", "javascript", "java"]:
            print(f"🐛 [DOCKER DEBUG] ENTERING PYTHON/JS/JAVA BRANCH")
            # For Python, JavaScript, and Java, pass function name and input as separate arguments
            function_name = getattr(request, 'function_name', 'solution')
            print(f"🐛 [DOCKER DEBUG] Raw function_name from request: {repr(function_name)}")
            print(f"🐛 [DOCKER DEBUG] Type of function_name: {type(function_name)}")
            print(f"🐛 [DOCKER DEBUG] Function name for {request.language}: {function_name}")
            input_json = json.dumps(request.test_input).replace('"', '\\"')
            run_command += f' "{function_name}" "{input_json}"'
            print(f"🐛 [DOCKER DEBUG] Run command after args: {run_command}")
        else:
            # For other languages (C++), pass input as single argument
            input_json = json.dumps(request.test_input).replace('"', '\\"')
            run_command += f' "{input_json}"'

        commands.append(run_command)

        # Execute commands in container
        exec_start = time.time()
        full_command = " && ".join(commands)
        print(f"🐛 [DOCKER DEBUG] Executing: {full_command}")
        print(f"🐛 [DOCKER DEBUG] Request function_name: {getattr(request, 'function_name', 'NOT SET')}")
        import sys
        sys.stdout.flush()

        exec_result = container.exec_run(f"sh -c '{full_command}'", workdir="/tmp")

        exec_time = (time.time() - exec_start) * 1000
        execution_time = (time.time() - start_time) * 1000
        print(
            f"🐛 [DOCKER DEBUG] Command execution took {exec_time:.0f}ms, total time {execution_time:.0f}ms"
        )

        if exec_result.exit_code == 0:
            try:
                logs = exec_result.output.decode("utf-8")

                # Find JSON output line
                print(f"🐛 [DOCKER DEBUG] Raw logs: {logs}")
                output_lines = [
                    line.strip() for line in logs.strip().split("\n") if line.strip()
                ]

                for line in reversed(output_lines):
                    try:
                        output_data = json.loads(line)
                        print(f"🐛 [DOCKER DEBUG] Parsed JSON: {output_data}")
                        if isinstance(output_data, dict) and "result" in output_data:
                            return {
                                "success": True,
                                "output": output_data.get("result"),
                                "execution_time": output_data.get(
                                    "execution_time", execution_time
                                ),
                                "error": output_data.get("error"),
                            }
                    except json.JSONDecodeError:
                        continue

                return {
                    "success": False,
                    "output": None,
                    "execution_time": execution_time,
                    "error": f"Could not parse JSON output. Raw logs: {logs}",
                }

            except Exception as e:
                return {
                    "success": False,
                    "output": None,
                    "execution_time": execution_time,
                    "error": f"Failed to parse output: {str(e)}",
                }
        else:
            logs = exec_result.output.decode("utf-8")
            return {
                "success": False,
                "output": None,
                "execution_time": execution_time,
                "error": f"Execution failed: {logs}",
            }

    except Exception as e:
        execution_time = (time.time() - start_time) * 1000
        print(f"🐛 [DOCKER DEBUG] MAIN EXCEPTION CAUGHT: {str(e)}")
        print(f"🐛 [DOCKER DEBUG] Exception type: {type(e)}")
        import traceback
        print(f"🐛 [DOCKER DEBUG] Traceback: {traceback.format_exc()}")
        return {
            "success": False,
            "output": None,
            "execution_time": execution_time,
            "error": f"Error: {str(e)}",
        }


def cleanup_persistent_containers():
    """Clean up all persistent containers."""
    global _persistent_containers

    with _container_lock:
        for container_name, container in _persistent_containers.items():
            try:
                container.remove(force=True)
                print(f"Cleaned up container: {container_name}")
            except Exception as e:
                print(f"Error cleaning up container {container_name}: {e}")

        _persistent_containers.clear()


def setup_java_persistent_server(container, config):
    """Setup the persistent Java server in the container."""
    import base64
    import os
    
    print("🐛 [DOCKER DEBUG] Setting up Java persistent server")
    
    # Copy PersistentJavaRunner.java to container
    server_file_path = os.path.join(os.path.dirname(__file__), "PersistentJavaRunner.java")
    with open(server_file_path, "r") as f:
        server_code = f.read()
    
    encoded_code = base64.b64encode(server_code.encode("utf-8")).decode("ascii")
    create_result = container.exec_run(
        f"sh -c 'echo {encoded_code} | base64 -d > /tmp/PersistentJavaRunner.java'",
        workdir="/tmp"
    )
    
    if create_result.exit_code != 0:
        raise Exception(f"Failed to copy server code: {create_result.output.decode('utf-8')}")
    
    # Compile the server
    compile_result = container.exec_run(
        config["compile_command"],
        workdir="/tmp"
    )
    
    if compile_result.exit_code != 0:
        error_msg = compile_result.output.decode("utf-8")
        raise Exception(f"Failed to compile Java server: {error_msg}")
    
    # Start the server process in background
    print("🐛 [DOCKER DEBUG] Starting Java server process")
    server_result = container.exec_run(
        config["startup_command"],
        workdir="/tmp",
        detach=True,
        stdin=True,
        stdout=True,
        stderr=True
    )
    
    # Store the exec instance for communication
    container._java_server_exec = server_result
    print("🐛 [DOCKER DEBUG] Java server started successfully")


# Test it
if __name__ == "__main__":
    from backend.models.questions import DockerRunRequest

    test_request = DockerRunRequest(
        code="class Solution { public int[] solution(int[] nums, int target) { for (int i = 0; i < nums.length; i++) { for (int j = i + 1; j < nums.length; j++) { if (nums[i] + nums[j] == target) { return new int[]{i, j}; } } } return new int[]{}; } }",
        language="java",
        test_input={"nums": [2, 7, 11, 15], "target": 9},
        timeout=5,
    )

    result = run_code_in_docker(test_request)
    print(json.dumps(result, indent=2))
