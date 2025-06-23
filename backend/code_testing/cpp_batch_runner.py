"""
C++ batch runner for executing multiple test cases efficiently.
Compiles once and runs multiple test cases to avoid compilation overhead.
"""
import json
import time
import base64
from typing import List, Dict, Any
from backend.code_testing.docker_runner import get_persistent_container
from backend.code_testing.language_config import LANGUAGE_CONFIG

def run_cpp_batch(code: str, test_cases: List[Dict], timeout: int = 10) -> List[Dict[str, Any]]:
    """
    Run C++ code against multiple test cases efficiently.
    Compiles once, then runs all test cases in the same binary.
    
    Args:
        code: C++ code to execute
        test_cases: List of test cases with 'input' field
        timeout: Timeout in seconds
        
    Returns:
        List of results, one per test case
    """
    print(f"🐛 [CPP BATCH] Starting batch execution for {len(test_cases)} test cases")
    
    try:
        # Get persistent C++ container
        container = get_persistent_container("cpp")
        config = LANGUAGE_CONFIG["cpp"]
        
        # Create optimized C++ wrapper for batch execution
        batch_wrapper = create_batch_cpp_wrapper(code, test_cases)
        print(f"🐛 [CPP BATCH] Generated wrapper length: {len(batch_wrapper)} characters")
        
        # Write code to container
        encoded_code = base64.b64encode(batch_wrapper.encode('utf-8')).decode('ascii')
        create_result = container.exec_run(
            f"sh -c 'echo {encoded_code} | base64 -d > /tmp/BatchSolution.cpp'",
            workdir="/tmp"
        )
        
        if create_result.exit_code != 0:
            raise Exception(f"Failed to create batch file: {create_result.output.decode('utf-8')}")
        
        # Compile once with optimization
        compile_start = time.time()
        compile_result = container.exec_run(
            "g++ -std=c++17 -O2 -o BatchSolution BatchSolution.cpp",
            workdir="/tmp"
        )
        compile_time = (time.time() - compile_start) * 1000
        print(f"🐛 [CPP BATCH] Compilation took {compile_time:.0f}ms")
        
        if compile_result.exit_code != 0:
            error_msg = compile_result.output.decode('utf-8')
            print(f"🐛 [CPP BATCH] Compilation failed: {error_msg}")
            
            # For debugging: show a snippet of the generated code
            lines = batch_wrapper.split('\n')
            print(f"🐛 [CPP BATCH] Generated code snippet (lines around error):")
            for i, line in enumerate(lines[300:310], 301):  # Show lines around where error typically occurs
                print(f"  {i}: {line}")
            
            # Return error for all test cases
            return [{"success": False, "output": None, "error": f"Compilation failed: {error_msg}", "execution_time": None}] * len(test_cases)
        
        # Execute all test cases in one binary run
        exec_start = time.time()
        exec_result = container.exec_run(
            "./BatchSolution",
            workdir="/tmp"
        )
        exec_time = (time.time() - exec_start) * 1000
        print(f"🐛 [CPP BATCH] Execution took {exec_time:.0f}ms")
        
        if exec_result.exit_code != 0:
            error_msg = exec_result.output.decode('utf-8')
            print(f"🐛 [CPP BATCH] Execution failed: {error_msg}")
            return [{"success": False, "output": None, "error": f"Execution failed: {error_msg}", "execution_time": None}] * len(test_cases)
        
        # Parse results
        output = exec_result.output.decode('utf-8')
        return parse_batch_results(output, len(test_cases))
        
    except Exception as e:
        print(f"🐛 [CPP BATCH] Batch execution error: {str(e)}")
        return [{"success": False, "output": None, "error": str(e), "execution_time": None}] * len(test_cases)


def create_batch_cpp_wrapper(user_code: str, test_cases: List[Dict]) -> str:
    """Create C++ wrapper that runs multiple test cases."""
    
    # Encode test cases as JSON strings with proper C++ escaping
    test_cases_json = []
    for test_case in test_cases:
        json_str = json.dumps(test_case["input"])
        # Escape quotes and backslashes for C++ string literals
        escaped_json = json_str.replace('\\', '\\\\').replace('"', '\\"')
        test_cases_json.append(escaped_json)
    
    test_cases_array = ",\n        ".join(f'"{tc}"' for tc in test_cases_json)
    
    wrapper = f"""
#include <iostream>
#include <string>
#include <vector>
#include <map>
#include <set>
#include <unordered_map>
#include <unordered_set>
#include <algorithm>
#include <chrono>
#include <sstream>
#include <climits>
#include <cmath>
#include <queue>
#include <stack>
#include <deque>
#include <list>
#include <functional>
using namespace std;

// JSON parsing helpers
class JSONParser {{
private:
    string json;
    size_t pos = 0;
    
    void skipWhitespace() {{
        while (pos < json.length() && isspace(json[pos])) pos++;
    }}
    
    int parseInt() {{
        string numStr;
        if (json[pos] == '-') {{
            numStr += json[pos++];
        }}
        while (pos < json.length() && isdigit(json[pos])) {{
            numStr += json[pos++];
        }}
        return stoi(numStr);
    }}
    
    vector<int> parseIntArray() {{
        if (json[pos] != '[') throw runtime_error("Expected array");
        pos++;
        vector<int> result;
        skipWhitespace();
        
        if (json[pos] == ']') {{
            pos++;
            return result;
        }}
        
        while (true) {{
            skipWhitespace();
            result.push_back(parseInt());
            skipWhitespace();
            
            if (json[pos] == ']') {{
                pos++;
                break;
            }} else if (json[pos] == ',') {{
                pos++;
            }} else {{
                throw runtime_error("Expected ',' or ']'");
            }}
        }}
        return result;
    }}
    
public:
    JSONParser(const string& jsonStr) : json(jsonStr) {{}}
    
    map<string, vector<int>> parseObject() {{
        map<string, vector<int>> result;
        if (json[pos] != '{{') throw runtime_error("Expected object");
        pos++;
        skipWhitespace();
        
        if (json[pos] == '}}') {{
            pos++;
            return result;
        }}
        
        while (true) {{
            skipWhitespace();
            
            // Parse key
            if (json[pos] != '"') throw runtime_error("Expected string key");
            pos++;
            string key;
            while (pos < json.length() && json[pos] != '"') {{
                key += json[pos++];
            }}
            pos++; // skip closing quote
            
            skipWhitespace();
            if (json[pos] != ':') throw runtime_error("Expected ':'");
            pos++;
            skipWhitespace();
            
            vector<int> value;
            if (json[pos] == '[') {{
                // Parse array
                value = parseIntArray();
            }} else {{
                // Parse single integer
                value.push_back(parseInt());
            }}
            result[key] = value;
            skipWhitespace();
            
            if (json[pos] == '}}') {{
                pos++;
                break;
            }} else if (json[pos] == ',') {{
                pos++;
            }} else {{
                throw runtime_error("Expected ',' or '}}'");
            }}
        }}
        return result;
    }}
}};

string vectorToString(const vector<int>& vec) {{
    string result = "[";
    for (size_t i = 0; i < vec.size(); i++) {{
        result += to_string(vec[i]);
        if (i < vec.size() - 1) result += ",";
    }}
    result += "]";
    return result;
}}

// User code starts here
{user_code}
// User code ends here

int main() {{
    string testInputs[] = {{
        {test_cases_array}
    }};
    
    int numTests = sizeof(testInputs) / sizeof(testInputs[0]);
    
    for (int i = 0; i < numTests; i++) {{
        try {{
            auto start = chrono::high_resolution_clock::now();
            
            JSONParser parser(testInputs[i]);
            auto inputData = parser.parseObject();
            
            vector<int> nums = inputData["nums"];
            vector<int> targetVec = inputData["target"];
            int target = targetVec.empty() ? 0 : targetVec[0];
            
            // Call solution
            Solution sol;
            vector<int> result = sol.solution(nums, target);
            
            auto end = chrono::high_resolution_clock::now();
            auto duration = chrono::duration_cast<chrono::microseconds>(end - start);
            double executionTime = duration.count() / 1000.0;
            
            cout << "{{\\"success\\": true, \\"output\\": " << vectorToString(result) << ", \\"execution_time\\": " << executionTime << "}}" << endl;
            
        }} catch (const exception& e) {{
            cout << "{{\\"success\\": false, \\"output\\": null, \\"error\\": \\"" << e.what() << "\\", \\"execution_time\\": null}}" << endl;
        }}
    }}
    
    return 0;
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
                print(f"🐛 [CPP BATCH] Failed to parse result line: {line}, error: {e}")
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