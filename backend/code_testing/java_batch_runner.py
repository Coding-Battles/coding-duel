"""
Java batch runner for executing multiple test cases efficiently.
Compiles once and runs multiple test cases to avoid JVM restart overhead.
"""

import json
import time
import base64
from typing import List, Dict, Any
from backend.code_testing.docker_runner import get_persistent_container


def run_java_batch(
    code: str,
    test_cases: List[Dict],
    timeout: int = 10,
    function_name: str = "solution",
    method_signature: Dict = None,
) -> List[Dict[str, Any]]:
    """
    Run Java code against multiple test cases using persistent JVM server.
    Communicates with long-running Java process to avoid JVM startup and compilation overhead.

    Args:
        code: Java code to execute
        test_cases: List of test cases with 'input' field  
        timeout: Timeout in seconds
        function_name: Name of the function to call

    Returns:
        List of results, one per test case
    """
    print(f"|java_batch_runner.py| [JAVA BATCH] Starting persistent server execution for {len(test_cases)} test cases")

    try:
        # Get persistent Java container with server
        container_start = time.time()
        container = get_persistent_container("java")
        container_time = (time.time() - container_start) * 1000
        print(f"🐛 [JAVA BATCH] Container setup took {container_time:.0f}ms")

        # Check if server is ready
        if not hasattr(container, '_java_server_ready') or not container._java_server_ready:
            raise Exception("Java persistent server not available in container")

        # Prepare request for Java server
        request_start = time.time()
        request = {
            "code": code,
            "test_cases": test_cases,
            "function_name": function_name,
            "method_signature": method_signature
        }
        request_json = json.dumps(request)
        request_time = (time.time() - request_start) * 1000
        print(f"|java_batch_runner.py| [JAVA BATCH] Request preparation took {request_time:.0f}ms")
        print(f"|java_batch_runner.py| [JAVA BATCH] Request JSON (first 300 chars): {request_json[:300]}")

        # Send request to Java server - simplified approach for now  
        comm_start = time.time()
        
        # Check if persistent server is available and ready
        if hasattr(container, '_java_server_ready') and container._java_server_ready:
            print(f"|java_batch_runner.py| [JAVA BATCH] Using persistent server (PID: {container._java_server_pid})")
            use_persistent = True
        else:
            print(f"|java_batch_runner.py| [JAVA BATCH] Persistent server not ready, falling back to direct execution")
            use_persistent = False
        
        if use_persistent:
            # Use TRUE persistent server via socket connection
            print(f"|java_batch_runner.py| [JAVA BATCH] Sending request to persistent server via socket...")
            
            try:
                # Send JSON request via socket using bash TCP redirect 
                # (since nc/netcat is not available in minimal containers)
                print(f"|java_batch_runner.py| [JAVA BATCH] Sending request via bash TCP redirect...")
                
                # Create a temporary script to handle the socket communication
                comm_script = f'''#!/bin/bash
exec 3<>/dev/tcp/localhost/8899
echo '{request_json}' >&3
cat <&3
exec 3<&-
exec 3>&-
'''
                
                # Write the script to container
                script_encoded = base64.b64encode(comm_script.encode()).decode()
                script_create = container.exec_run(
                    f"sh -c 'echo {script_encoded} | base64 -d > /tmp/socket_comm.sh && chmod +x /tmp/socket_comm.sh'",
                    workdir="/tmp"
                )
                
                if script_create.exit_code != 0:
                    print(f"🐛 [JAVA BATCH] Failed to create communication script")
                    use_persistent = False
                else:
                    # Execute the communication script
                    socket_send = container.exec_run(
                        "timeout 10 bash /tmp/socket_comm.sh",
                        workdir="/tmp"
                    )
                    
                    if socket_send.exit_code != 0 and socket_send.exit_code != 124:  # 124 = timeout
                        print(f"|java_batch_runner.py| [JAVA BATCH] Failed to send via socket: {socket_send.output.decode('utf-8')}")
                        use_persistent = False
                    else:
                        output = socket_send.output.decode("utf-8").strip()
                        if output and output != "timeout: failed to run command" and not output.startswith("bash:"):
                            print(f"|java_batch_runner.py| [JAVA BATCH] Got response from persistent server: {len(output)} chars")
                        else:
                            print(f"|java_batch_runner.py| [JAVA BATCH] No valid response from persistent server, falling back")
                            print(f"|java_batch_runner.py| [JAVA BATCH] Output was: {output}")
                            use_persistent = False
                        
            except Exception as e:
                print(f"|java_batch_runner.py| [JAVA BATCH] Persistent server communication error: {str(e)}")
                use_persistent = False
        
        if not use_persistent:
            # Fallback to single test case execution using the docker_runner
            print(f"|java_batch_runner.py| [JAVA BATCH] Using single test case fallback...")
            from backend.code_testing.docker_runner import run_code_in_docker
            from backend.models.questions import DockerRunRequest
            
            results = []
            for test_case in test_cases:
                request = DockerRunRequest(
                    code=code,
                    language="java",
                    test_input=test_case["input"],
                    timeout=timeout,
                    function_name=function_name
                )
                
                result = run_code_in_docker(request)
                results.append({
                    "success": result.get("success", False),
                    "output": result.get("output"),
                    "execution_time": result.get("execution_time"),
                    "error": result.get("error")
                })
            
            return results
        
        comm_time = (time.time() - comm_start) * 1000
        if use_persistent:
            print(f"|java_batch_runner.py| [JAVA BATCH] Persistent server communication took {comm_time:.0f}ms")
        else:
            print(f"|java_batch_runner.py| [JAVA BATCH] Fallback communication took {comm_time:.0f}ms")

        # Parse server response
        parse_start = time.time()
        # output variable is already set above in both branches
        
        # Extract JSON from mixed stderr/stdout output
        # Look for the last line that looks like JSON (starts with [ or {)
        json_line = None
        for line in reversed(output.split('\n')):
            line = line.strip()
            if line.startswith('[') or line.startswith('{'):
                json_line = line
                break
        
        if json_line:
            try:
                results = json.loads(json_line)
                if not isinstance(results, list):
                    results = [results]  # Single result case
                print(f"|java_batch_runner.py| [JAVA BATCH] Successfully parsed {len(results)} results")
            except json.JSONDecodeError as e:
                print(f"|java_batch_runner.py| [JAVA BATCH] Failed to parse JSON line: {json_line}, error: {e}")
                results = [{"success": False, "output": None, "error": f"Invalid JSON: {json_line}", "execution_time": None}] * len(test_cases)
        else:
            print(f"|java_batch_runner.py| [JAVA BATCH] No JSON found in output: {output}")
            results = [{"success": False, "output": None, "error": f"No JSON response found", "execution_time": None}] * len(test_cases)
        
        parse_time = (time.time() - parse_start) * 1000
        print(f"|java_batch_runner.py| [JAVA BATCH] Response parsing took {parse_time:.0f}ms")
        
        # Ensure we have the right number of results
        while len(results) < len(test_cases):
            results.append({"success": False, "output": None, "error": "Missing result", "execution_time": None})
        
        return results[:len(test_cases)]

    except Exception as e:
        print(f"|java_batch_runner.py| [JAVA BATCH] Persistent server execution error: {str(e)}")
        return [{"success": False, "output": None, "error": str(e), "execution_time": None}] * len(test_cases)


# All old compilation-based functions have been removed.
# Now using persistent JVM server approach for much better performance.
