"""
Java batch runner for executing multiple test cases efficiently.
Compiles once and runs multiple test cases to avoid JVM restart overhead.
"""
import json
import time
import base64
from typing import List, Dict, Any
from backend.code_testing.docker_runner import get_persistent_container
from backend.code_testing.language_config import LANGUAGE_CONFIG

def run_java_batch(code: str, test_cases: List[Dict], timeout: int = 10) -> List[Dict[str, Any]]:
    """
    Run Java code against multiple test cases efficiently.
    Compiles once, then runs all test cases in the same JVM.
    
    Args:
        code: Java code to execute
        test_cases: List of test cases with 'input' field
        timeout: Timeout in seconds
        
    Returns:
        List of results, one per test case
    """
    print(f"🐛 [JAVA BATCH] Starting batch execution for {len(test_cases)} test cases")
    
    try:
        # Get persistent Java container
        container = get_persistent_container("java")
        config = LANGUAGE_CONFIG["java"]
        
        # Create optimized Java wrapper for batch execution
        batch_wrapper = create_batch_java_wrapper(code, test_cases)
        print(f"🐛 [JAVA BATCH] Generated wrapper length: {len(batch_wrapper)} characters")
        
        # Write code to container
        encoded_code = base64.b64encode(batch_wrapper.encode('utf-8')).decode('ascii')
        create_result = container.exec_run(
            f"sh -c 'echo {encoded_code} | base64 -d > /tmp/BatchSolution.java'",
            workdir="/tmp"
        )
        
        if create_result.exit_code != 0:
            raise Exception(f"Failed to create batch file: {create_result.output.decode('utf-8')}")
        
        # Compile once
        compile_start = time.time()
        compile_result = container.exec_run(
            "javac -Xlint:none BatchSolution.java",
            workdir="/tmp"
        )
        compile_time = (time.time() - compile_start) * 1000
        print(f"🐛 [JAVA BATCH] Compilation took {compile_time:.0f}ms")
        
        if compile_result.exit_code != 0:
            error_msg = compile_result.output.decode('utf-8')
            print(f"🐛 [JAVA BATCH] Compilation failed: {error_msg}")
            
            # For debugging: show a snippet of the generated code
            lines = batch_wrapper.split('\n')
            print(f"🐛 [JAVA BATCH] Generated code snippet (lines around error):")
            for i, line in enumerate(lines[80:90], 81):  # Show lines around where error typically occurs
                print(f"  {i}: {line}")
            
            # Return error for all test cases
            return [{"success": False, "output": None, "error": f"Compilation failed: {error_msg}", "execution_time": None}] * len(test_cases)
        
        # Execute all test cases in one JVM run
        exec_start = time.time()
        exec_result = container.exec_run(
            "java -Xms16m -Xmx64m -XX:+UseSerialGC -XX:TieredStopAtLevel=1 BatchSolution",
            workdir="/tmp"
        )
        exec_time = (time.time() - exec_start) * 1000
        print(f"🐛 [JAVA BATCH] Execution took {exec_time:.0f}ms")
        
        if exec_result.exit_code != 0:
            error_msg = exec_result.output.decode('utf-8')
            print(f"🐛 [JAVA BATCH] Execution failed: {error_msg}")
            return [{"success": False, "output": None, "error": f"Execution failed: {error_msg}", "execution_time": None}] * len(test_cases)
        
        # Parse results
        output = exec_result.output.decode('utf-8')
        return parse_batch_results(output, len(test_cases))
        
    except Exception as e:
        print(f"🐛 [JAVA BATCH] Batch execution error: {str(e)}")
        return [{"success": False, "output": None, "error": str(e), "execution_time": None}] * len(test_cases)


def create_batch_java_wrapper(user_code: str, test_cases: List[Dict]) -> str:
    """Create Java wrapper that runs multiple test cases."""
    
    # Encode test cases as JSON strings with proper Java escaping
    test_cases_json = []
    for test_case in test_cases:
        json_str = json.dumps(test_case["input"])
        # Escape quotes for Java string literals
        escaped_json = json_str.replace('"', '\\"')
        test_cases_json.append(escaped_json)
    
    test_cases_array = ", ".join(f'"{tc}"' for tc in test_cases_json)
    
    wrapper = f"""
import java.util.*;

{user_code}

class BatchSolution {{
    public static String arrayToString(int[] arr) {{
        if (arr == null) return "null";
        StringBuilder sb = new StringBuilder();
        sb.append("[");
        for (int i = 0; i < arr.length; i++) {{
            sb.append(arr[i]);
            if (i < arr.length - 1) sb.append(",");
        }}
        sb.append("]");
        return sb.toString();
    }}
    
    public static Map<String, Object> parseInput(String jsonStr) {{
        Map<String, Object> data = new HashMap<>();
        
        // Remove outer braces and whitespace
        jsonStr = jsonStr.trim();
        if (jsonStr.startsWith("{{")) jsonStr = jsonStr.substring(1);
        if (jsonStr.endsWith("}}")) jsonStr = jsonStr.substring(0, jsonStr.length() - 1);
        
        // Parse nums array
        int numsStart = jsonStr.indexOf("[");
        int numsEnd = jsonStr.indexOf("]");
        if (numsStart != -1 && numsEnd != -1) {{
            String numsStr = jsonStr.substring(numsStart + 1, numsEnd);
            if (!numsStr.trim().isEmpty()) {{
                String[] numStrs = numsStr.split(",");
                int[] nums = new int[numStrs.length];
                for (int i = 0; i < numStrs.length; i++) {{
                    nums[i] = Integer.parseInt(numStrs[i].trim());
                }}
                data.put("nums", nums);
            }}
        }}
        
        // Parse target
        int targetStart = jsonStr.indexOf("target") + 8;
        if (targetStart > 7) {{
            String targetStr = jsonStr.substring(targetStart);
            int target = Integer.parseInt(targetStr.replaceAll("[^\\\\d-]", ""));
            data.put("target", target);
        }}
        
        return data;
    }}
    
    public static void main(String[] args) {{
        String[] testInputs = {{{test_cases_array}}};
        Solution solutionInstance = new Solution();
        
        for (int i = 0; i < testInputs.length; i++) {{
            try {{
                long startTime = System.nanoTime();
                
                Map<String, Object> inputData = parseInput(testInputs[i]);
                int[] nums = (int[]) inputData.get("nums");
                Integer target = (Integer) inputData.get("target");
                
                int[] result = solutionInstance.solution(nums, target);
                
                long endTime = System.nanoTime();
                double executionTime = (endTime - startTime) / 1_000_000.0;
                
                System.out.println("{{\\\"success\\\": true, \\\"output\\\": " + arrayToString(result) + ", \\\"execution_time\\\": " + executionTime + "}}");
                
            }} catch (Exception e) {{
                System.out.println("{{\\\"success\\\": false, \\\"output\\\": null, \\\"error\\\": \\\"" + e.getMessage().replace("\\"", "\\\\\\"") + "\\\", \\\"execution_time\\\": null}}");
            }}
        }}
    }}
}}
"""
    return wrapper


def parse_batch_results(output: str, expected_count: int) -> List[Dict[str, Any]]:
    """Parse the JSON results from batch execution."""
    results = []
    lines = output.strip().split('\n')
    
    for line in lines:
        line = line.strip()
        if line and line.startswith('{'):
            try:
                result = json.loads(line)
                results.append(result)
            except json.JSONDecodeError as e:
                print(f"🐛 [JAVA BATCH] Failed to parse result line: {line}, error: {e}")
                results.append({
                    "success": False,
                    "output": None,
                    "error": f"Failed to parse result: {line}",
                    "execution_time": None
                })
    
    # Ensure we have the right number of results
    while len(results) < expected_count:
        results.append({
            "success": False,
            "output": None,
            "error": "Missing result",
            "execution_time": None
        })
    
    return results[:expected_count]