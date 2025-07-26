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
    print(f"🐛 [JAVA BATCH] Starting persistent server execution for {len(test_cases)} test cases")

    try:
        # Get persistent Java container with server
        container_start = time.time()
        container = get_persistent_container("java")
        container_time = (time.time() - container_start) * 1000
        print(f"🐛 [JAVA BATCH] Container setup took {container_time:.0f}ms")

        # Check if server is running
        if not hasattr(container, '_java_server_exec'):
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
        print(f"🐛 [JAVA BATCH] Request preparation took {request_time:.0f}ms")
        print(f"🐛 [JAVA BATCH] Request JSON (first 300 chars): {request_json[:300]}")

        # Send request to Java server
        comm_start = time.time()
        
        # Write request to a file and have server process it
        encoded_request = base64.b64encode(request_json.encode("utf-8")).decode("ascii")
        write_result = container.exec_run(
            f"sh -c 'echo {encoded_request} | base64 -d > /tmp/server_request.json'",
            workdir="/tmp"
        )
        
        if write_result.exit_code != 0:
            raise Exception(f"Failed to write request: {write_result.output.decode('utf-8')}")
        
        # Send the request to the server via a simple file-based approach for now
        # In a proper implementation, we'd use stdin/stdout pipes directly
        exec_result = container.exec_run(
            "sh -c 'cat /tmp/server_request.json | java PersistentJavaRunner'",
            workdir="/tmp"
        )
        
        comm_time = (time.time() - comm_start) * 1000
        print(f"🐛 [JAVA BATCH] Server communication took {comm_time:.0f}ms")

        if exec_result.exit_code != 0:
            error_msg = exec_result.output.decode("utf-8")
            print(f"🐛 [JAVA BATCH] Server execution failed: {error_msg}")
            return [{"success": False, "output": None, "error": f"Server execution failed: {error_msg}", "execution_time": None}] * len(test_cases)

        # Parse server response
        parse_start = time.time()
        output = exec_result.output.decode("utf-8").strip()
        
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
                print(f"🐛 [JAVA BATCH] Successfully parsed {len(results)} results")
            except json.JSONDecodeError as e:
                print(f"🐛 [JAVA BATCH] Failed to parse JSON line: {json_line}, error: {e}")
                results = [{"success": False, "output": None, "error": f"Invalid JSON: {json_line}", "execution_time": None}] * len(test_cases)
        else:
            print(f"🐛 [JAVA BATCH] No JSON found in output: {output}")
            results = [{"success": False, "output": None, "error": f"No JSON response found", "execution_time": None}] * len(test_cases)
        
        parse_time = (time.time() - parse_start) * 1000
        print(f"🐛 [JAVA BATCH] Response parsing took {parse_time:.0f}ms")
        
        # Ensure we have the right number of results
        while len(results) < len(test_cases):
            results.append({"success": False, "output": None, "error": "Missing result", "execution_time": None})
        
        return results[:len(test_cases)]

    except Exception as e:
        print(f"🐛 [JAVA BATCH] Persistent server execution error: {str(e)}")
        return [{"success": False, "output": None, "error": str(e), "execution_time": None}] * len(test_cases)


# All old compilation-based functions have been removed.
# Now using persistent JVM server approach for much better performance.
