import os
import json
import docker
import threading
import uuid
import time
from typing import Dict, Any, Optional

# Import Pydantic models
from backend.models.questions import DockerRunRequest
from backend.code_testing.language_config import LANGUAGE_CONFIG
from backend.code_testing.runners.java_runner import JavaRunner
from backend.code_testing.runners.cpp_runner import CppRunner
from backend.code_testing.runners.python_runner import PythonRunner
from backend.code_testing.runners.javascript_runner import JavaScriptRunner

# Language to runner class mapping
LANGUAGE_RUNNERS = {
    "java": JavaRunner,
    "cpp": CppRunner,
    "python": PythonRunner,
    "javascript": JavaScriptRunner,
}

# Timeout configuration - tiered system
EXECUTION_TIMEOUT = 8  # seconds - for user code execution
SETUP_TIMEOUT = 10  # seconds - for compilation, file ops, cache checks


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

        # Allocate more resources for Java containers due to compilation overhead
        cpu_allocation = (
            1000000000 if language == "java" else 300000000
        )  # 1.0 vs 0.3 CPU cores

        container = docker_client.containers.run(
            config["image"],
            command=startup_cmd,
            name=container_name,
            detach=True,
            mem_limit=config.get("mem_limit", "128m"),
            nano_cpus=cpu_allocation,
            network_mode="none",
            security_opt=["no-new-privileges:true"],
            working_dir="/tmp",
            remove=False,
        )

        print(
            f"🐛 [DOCKER DEBUG] Created new {language} container: {container.id[:12]}"
        )

        # For Java containers, copy CompilationServer.java and wait for server to start
        if language == "java":
            try:
                import os
                import time

                # Copy CompilationServer.java to container
                server_path = os.path.join(
                    os.path.dirname(__file__), "CompilationServer.java"
                )
                with open(server_path, "r") as f:
                    server_code = f.read()

                import base64

                encoded_server = base64.b64encode(server_code.encode("utf-8")).decode(
                    "ascii"
                )
                copy_result = container.exec_run(
                    f"timeout {SETUP_TIMEOUT} sh -c 'echo {encoded_server} | base64 -d > /tmp/CompilationServer.java'",
                    workdir="/tmp",
                )

                if copy_result.exit_code != 0:
                    print(
                        f"❌ [DOCKER DEBUG] Failed to copy CompilationServer.java: {copy_result.output.decode()}"
                    )
                else:
                    print(
                        f"🐛 [DOCKER DEBUG] CompilationServer.java copied to container"
                    )

                    # Check if CompilationServer compiles
                    print(f"🔧 [DOCKER DEBUG] Testing CompilationServer compilation...")
                    compile_test = container.exec_run(
                        f"timeout {SETUP_TIMEOUT} javac -cp /tmp CompilationServer.java",
                        workdir="/tmp",
                    )
                    if compile_test.exit_code != 0:
                        print(
                            f"❌ [DOCKER DEBUG] CompilationServer.java failed to compile: {compile_test.output.decode()}"
                        )
                    else:
                        print(
                            f"✅ [DOCKER DEBUG] CompilationServer.java compiled successfully"
                        )

                    # Note: Skip execution test to avoid port conflicts since container already runs the server

                    # Wait for compilation server to start (up to 2 minutes)
                    print(
                        f"🔧 [DOCKER DEBUG] Waiting for CompilationServer to start..."
                    )
                    for i in range(240):  # 240 * 0.5s = 120s timeout (2 minutes)
                        try:
                            # Progress indicator every 10 seconds
                            if i % 20 == 0:
                                elapsed = i * 0.5
                                print(
                                    f"🔧 [DOCKER DEBUG] Detection progress: {elapsed:.1f}s elapsed, still searching..."
                                )

                            # Method 1: Try TCP connection test (simpler and more reliable)
                            tcp_test = container.exec_run(
                                "timeout 1 bash -c 'exec 3<>/dev/tcp/localhost/8901; echo \"test\" >&3; exec 3<&-; exec 3>&-'",
                                workdir="/tmp",
                            )
                            if tcp_test.exit_code == 0:
                                print(
                                    f"🔥 [DOCKER DEBUG] TCP connection to port 8901 successful!"
                                )

                                # Verify server is ready via logs
                                logs = container.logs(tail=20).decode("utf-8")
                                if "Server listening on port 8901" in logs:
                                    print(
                                        f"✅ [DOCKER DEBUG] CompilationServer is ready!"
                                    )
                                    container._java_compilation_server_ready = True
                                    break
                                else:
                                    print(
                                        f"🔧 [DOCKER DEBUG] TCP works but server not ready yet"
                                    )

                            # Method 2: Use /proc filesystem as fallback
                            proc_list = container.exec_run(
                                "ls /proc/ | grep -E '^[0-9]+$'", workdir="/tmp"
                            )
                            if proc_list.exit_code == 0:
                                proc_ids = [
                                    p.strip() for p in proc_list.output.decode().split()
                                ]

                                if i % 40 == 0:  # Every 20 seconds
                                    print(
                                        f"🔧 [DOCKER DEBUG] Found {len(proc_ids)} processes to check"
                                    )

                                for proc_id in proc_ids:
                                    cmdline_check = container.exec_run(
                                        f"cat /proc/{proc_id}/cmdline", workdir="/tmp"
                                    )
                                    if cmdline_check.exit_code == 0:
                                        cmdline = cmdline_check.output.decode()
                                        if "CompilationServer" in cmdline:
                                            print(
                                                f"🔥 [DOCKER DEBUG] Found CompilationServer process {proc_id} with cmdline: {cmdline}"
                                            )

                                            # Verify server is ready via logs
                                            logs = container.logs(tail=20).decode(
                                                "utf-8"
                                            )
                                            if "Server listening on port 8901" in logs:
                                                print(
                                                    f"✅ [DOCKER DEBUG] CompilationServer is ready!"
                                                )
                                                container._java_compilation_server_ready = (
                                                    True
                                                )
                                                break
                                            else:
                                                print(
                                                    f"🔧 [DOCKER DEBUG] Process found but server not ready yet, logs: {logs[-200:]}"
                                                )

                                if (
                                    hasattr(container, "_java_compilation_server_ready")
                                    and container._java_compilation_server_ready
                                ):
                                    break
                        except Exception as e:
                            if i % 40 == 0:  # Every 20 seconds
                                print(
                                    f"🔧 [DOCKER DEBUG] Detection attempt {i} failed: {e}"
                                )
                        time.sleep(0.5)
                    else:
                        print(
                            f"❌ [DOCKER DEBUG] Java compilation server failed to start within 2 minutes"
                        )
                        # Print recent container logs for debugging
                        try:
                            logs = container.logs(tail=20).decode("utf-8")
                            print(f"🔧 [DOCKER DEBUG] Recent container logs:\n{logs}")
                        except:
                            print(
                                f"🔧 [DOCKER DEBUG] Could not retrieve container logs"
                            )

            except Exception as e:
                print(
                    f"❌ [DOCKER DEBUG] Error setting up Java compilation server: {e}"
                )

        _persistent_containers[container_name] = container
        return container


def run_code_in_docker(
    request: DockerRunRequest, docker_client=None, use_fast_runner=None, submission_id=None, cleanup=True
):
    """Run code using persistent containers and modular language runners."""
    start_time = time.time()
    print(f"🐛 [DOCKER DEBUG] Starting {request.language} execution")
    print(f"🐛 [DOCKER DEBUG] Function name: {request.function_name}")
    if submission_id:
        print(f"🐛 [DOCKER DEBUG] Using provided submission ID: {submission_id}")

    submission_dir = None  # Track submission directory for cleanup
    try:
        config = LANGUAGE_CONFIG.get(request.language)
        if not config:
            raise ValueError(f"Unsupported language: {request.language}")

        # Get persistent container
        container_start = time.time()
        container = get_persistent_container(request.language)
        container_time = (time.time() - container_start) * 1000
        print(f"🐛 [DOCKER DEBUG] Getting container took {container_time:.0f}ms")

        # Get language-specific runner class
        if request.language not in LANGUAGE_RUNNERS:
            raise ValueError(f"Unsupported language: {request.language}")
        
        runner_class = LANGUAGE_RUNNERS[request.language]
        
        # Use provided submission ID or generate unique one
        if submission_id is None:
            submission_id = str(uuid.uuid4())[:8]
        
        # Create unique submission directory
        submission_dir = runner_class.create_submission_directory(container, submission_id)
        
        # Prepare code with language-specific wrapper/harness
        wrapped_code = runner_class.prepare_code(request)
        print(f"� [DOCKER DEBUG] Wrapped code length: {len(wrapped_code)}")
        
        # Get unique filename
        filename = runner_class.get_filename(request)
        file_path = f"{submission_dir}/{filename}"
        
        print(f"🐛 [DOCKER DEBUG] Using submission directory: {submission_dir}")
        print(f"🐛 [DOCKER DEBUG] Using filename: {filename}")

        # Write code to container
        file_start = time.time()
        runner_class.write_code_file(container, file_path, wrapped_code)
        file_time = (time.time() - file_start) * 1000
        print(f"🐛 [DOCKER DEBUG] File creation took {file_time:.0f}ms")

        # Compile if needed
        compile_start = time.time()
        compilation_result = runner_class.compile(container, request, file_path, wrapped_code)
        compile_time = (time.time() - compile_start) * 1000
        print(f"🐛 [DOCKER DEBUG] Compilation took {compile_time:.0f}ms")
        
        if not compilation_result["success"]:
            return {
                "success": False,
                "output": None,
                "execution_time": (time.time() - start_time) * 1000,
                "error": compilation_result.get("error", "Compilation failed"),
            }

        # Get run command
        run_command = runner_class.get_run_command(request, file_path, compilation_result)
        print(f"🐛 [DOCKER DEBUG] Run command: {run_command}")

        # Execute the command
        exec_start = time.time()
        exec_result = container.exec_run(
            f"timeout {EXECUTION_TIMEOUT} sh -c '{run_command}'", workdir="/tmp"
        )

        exec_time = (time.time() - exec_start) * 1000
        execution_time = (time.time() - start_time) * 1000
        print(f"🐛 [DOCKER DEBUG] Command execution took {exec_time:.0f}ms, total time {execution_time:.0f}ms")

        # Handle timeout error (exit code 124 from shell timeout command)
        if exec_result.exit_code == 124:
            return {
                "success": False,
                "output": None,
                "execution_time": EXECUTION_TIMEOUT * 1000,  # Convert to milliseconds
                "error": f"Code execution timed out after {EXECUTION_TIMEOUT} seconds. Your solution may have an infinite loop or be too slow.",
            }

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
    finally:
        # Clean up submission directory (only if cleanup=True)
        if cleanup and submission_dir and 'container' in locals():
            try:
                cleanup_result = container.exec_run(
                    f"timeout 5 rm -rf {submission_dir}",
                    workdir="/tmp"
                )
                if cleanup_result.exit_code == 0:
                    print(f"🧹 [CLEANUP] Removed submission directory: {submission_dir}")
                else:
                    print(f"⚠️ [CLEANUP] Failed to remove {submission_dir}: {cleanup_result.output.decode()}")
            except Exception as cleanup_error:
                print(f"❌ [CLEANUP] Error cleaning up {submission_dir}: {cleanup_error}")


def cleanup_submission_directory(language: str, submission_id: str):
    """Manually clean up a submission directory."""
    try:
        container = get_persistent_container(language)
        submission_dir = f"/tmp/submission_{submission_id}"
        
        cleanup_result = container.exec_run(
            f"timeout 5 rm -rf {submission_dir}",
            workdir="/tmp"
        )
        if cleanup_result.exit_code == 0:
            print(f"🧹 [CLEANUP] Manually removed submission directory: {submission_dir}")
            return True
        else:
            print(f"⚠️ [CLEANUP] Failed to remove {submission_dir}: {cleanup_result.output.decode()}")
            return False
    except Exception as cleanup_error:
        print(f"❌ [CLEANUP] Error cleaning up {submission_dir}: {cleanup_error}")
        return False


def run_cpp_batch_in_docker(code: str, test_inputs: list, timeout: int, function_name: str, question_name: str = None):
    """Run C++ code in batch - compile once, execute multiple test cases in the same submission directory."""
    from backend.models.questions import DockerRunRequest
    
    start_time = time.time()
    print(f"🐛 [DOCKER DEBUG] Starting C++ batch execution for {len(test_inputs)} test cases")
    print(f"🐛 [DOCKER DEBUG] Function name: {function_name}")

    submission_dir = None
    container = None
    results = []
    
    try:
        config = LANGUAGE_CONFIG.get("cpp")
        if not config:
            raise ValueError(f"Unsupported language: cpp")

        # Get persistent container
        container_start = time.time()
        container = get_persistent_container("cpp")
        container_time = (time.time() - container_start) * 1000
        print(f"🐛 [DOCKER DEBUG] Getting container took {container_time:.0f}ms")

        # Get language-specific runner class
        runner_class = LANGUAGE_RUNNERS["cpp"]
        
        # Generate unique submission ID for this batch
        submission_id = str(uuid.uuid4())[:8]
        
        # Create unique submission directory (only once for the entire batch)
        submission_dir = runner_class.create_submission_directory(container, submission_id)
        print(f"🐛 [DOCKER DEBUG] Created batch submission directory: {submission_dir}")
        
        # Use first test case to prepare and compile the code
        if not test_inputs:
            return []
            
        first_request = DockerRunRequest(
            code=code,
            language="cpp",
            test_input=test_inputs[0],
            timeout=timeout,
            function_name=function_name,
            question_name=question_name,
        )
        
        # Prepare code with language-specific wrapper/harness (only once)
        wrapped_code = runner_class.prepare_code(first_request)
        print(f"🐛 [DOCKER DEBUG] Wrapped code length: {len(wrapped_code)}")
        
        # Get unique filename
        filename = runner_class.get_filename(first_request)
        file_path = f"{submission_dir}/{filename}"
        
        # Write code to container (only once)
        file_start = time.time()
        runner_class.write_code_file(container, file_path, wrapped_code)
        file_time = (time.time() - file_start) * 1000
        print(f"🐛 [DOCKER DEBUG] File creation took {file_time:.0f}ms")

        # Compile the code (only once)
        compile_start = time.time()
        compilation_result = runner_class.compile(container, first_request, file_path, wrapped_code)
        compile_time = (time.time() - compile_start) * 1000
        print(f"🐛 [DOCKER DEBUG] One-time compilation took {compile_time:.0f}ms")
        
        if not compilation_result["success"]:
            # If compilation fails, return failure for all test cases
            compilation_error = compilation_result.get("error", "Compilation failed")
            for test_input in test_inputs:
                results.append({
                    "success": False,
                    "output": None,
                    "execution_time": (time.time() - start_time) * 1000,
                    "error": compilation_error,
                })
            return results

        # Now run each test case using the compiled binary
        for i, test_input in enumerate(test_inputs):
            test_start = time.time()
            print(f"🐛 [DOCKER DEBUG] Running test case {i+1}/{len(test_inputs)}")
            
            # Create a temporary request for this test case
            test_request = DockerRunRequest(
                code=code,
                language="cpp",
                test_input=test_input,
                timeout=timeout,
                function_name=function_name,
                question_name=question_name,
            )
            
            # Get run command for this specific test case
            run_command = runner_class.get_run_command(test_request, file_path, compilation_result)
            print(f"🐛 [DOCKER DEBUG] Test {i+1} run command: {run_command}")

            # Execute the command
            exec_start = time.time()
            exec_result = container.exec_run(
                f"timeout {EXECUTION_TIMEOUT} sh -c '{run_command}'", workdir="/tmp"
            )

            exec_time = (time.time() - exec_start) * 1000
            test_total_time = (time.time() - test_start) * 1000
            print(f"🐛 [DOCKER DEBUG] Test {i+1} execution took {exec_time:.0f}ms, total test time {test_total_time:.0f}ms")

            # Handle timeout error (exit code 124 from shell timeout command)
            if exec_result.exit_code == 124:
                results.append({
                    "success": False,
                    "output": None,
                    "execution_time": EXECUTION_TIMEOUT * 1000,  # Convert to milliseconds
                    "error": f"Code execution timed out after {EXECUTION_TIMEOUT} seconds. Your solution may have an infinite loop or be too slow.",
                })
                continue

            if exec_result.exit_code == 0:
                try:
                    logs = exec_result.output.decode("utf-8")

                    # Find JSON output line
                    print(f"🐛 [DOCKER DEBUG] Test {i+1} raw logs: {logs}")
                    output_lines = [
                        line.strip() for line in logs.strip().split("\n") if line.strip()
                    ]

                    found_result = False
                    for line in reversed(output_lines):
                        try:
                            output_data = json.loads(line)
                            print(f"🐛 [DOCKER DEBUG] Test {i+1} parsed JSON: {output_data}")
                            if isinstance(output_data, dict) and "result" in output_data:
                                results.append({
                                    "success": True,
                                    "output": output_data.get("result"),
                                    "execution_time": output_data.get("execution_time", test_total_time),
                                    "error": output_data.get("error"),
                                })
                                found_result = True
                                break
                        except json.JSONDecodeError:
                            continue

                    if not found_result:
                        # No valid JSON found
                        results.append({
                            "success": False,
                            "output": None,
                            "execution_time": test_total_time,
                            "error": f"No valid JSON output found. Raw output: {logs[:200]}...",
                        })

                except Exception as e:
                    results.append({
                        "success": False,
                        "output": None,
                        "execution_time": test_total_time,
                        "error": f"Error parsing output: {str(e)}",
                    })
            else:
                # Execution failed
                error_output = exec_result.output.decode("utf-8") if exec_result.output else "Unknown error"
                results.append({
                    "success": False,
                    "output": None,
                    "execution_time": test_total_time,
                    "error": f"Execution failed (exit code {exec_result.exit_code}): {error_output}",
                })

        batch_total_time = (time.time() - start_time) * 1000
        print(f"🐛 [DOCKER DEBUG] Batch execution completed in {batch_total_time:.0f}ms for {len(test_inputs)} test cases")
        return results

    except Exception as e:
        print(f"❌ [DOCKER DEBUG] Error in batch execution: {e}")
        # Return error for all test cases
        error_results = []
        for test_input in test_inputs:
            error_results.append({
                "success": False,
                "output": None,
                "execution_time": (time.time() - start_time) * 1000,
                "error": f"Batch execution error: {str(e)}",
            })
        return error_results
    
    finally:
        # Clean up submission directory
        if container and submission_dir:
            try:
                cleanup_start = time.time()
                container.exec_run(f"rm -rf {submission_dir}", workdir="/tmp")
                cleanup_time = (time.time() - cleanup_start) * 1000
                print(f"🐛 [DOCKER DEBUG] Cleanup took {cleanup_time:.0f}ms")
            except Exception as e:
                print(f"❌ [CLEANUP] Error removing submission directory {submission_dir}: {e}")


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


def cleanup_old_submissions():
    """Clean up any leftover submission directories from all containers."""
    global _persistent_containers
    
    with _container_lock:
        for container_name, container in _persistent_containers.items():
            try:
                # Find all submission directories
                find_result = container.exec_run(
                    "find /tmp -maxdepth 1 -name 'submission_*' -type d",
                    workdir="/tmp"
                )
                
                if find_result.exit_code == 0 and find_result.output:
                    directories = find_result.output.decode().strip().split('\n')
                    directories = [d for d in directories if d.strip()]
                    
                    if directories:
                        print(f"🧹 [CLEANUP] Found {len(directories)} old submission directories in {container_name}")
                        
                        # Remove all old submission directories
                        cleanup_result = container.exec_run(
                            "rm -rf /tmp/submission_*",
                            workdir="/tmp"
                        )
                        
                        if cleanup_result.exit_code == 0:
                            print(f"✅ [CLEANUP] Cleaned up all old submissions in {container_name}")
                        else:
                            print(f"❌ [CLEANUP] Failed to clean up {container_name}: {cleanup_result.output.decode()}")
                    else:
                        print(f"✅ [CLEANUP] No old submissions found in {container_name}")
                        
            except Exception as e:
                print(f"❌ [CLEANUP] Error cleaning up {container_name}: {e}")


# Export cleanup function for use in __init__.py
cleanup_containers = cleanup_persistent_containers


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
