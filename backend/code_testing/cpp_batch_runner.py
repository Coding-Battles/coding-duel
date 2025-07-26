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

def run_cpp_batch(code: str, test_cases: List[Dict], timeout: int = 10, function_name: str = "solution") -> List[Dict[str, Any]]:
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
        batch_wrapper = create_batch_cpp_wrapper(code, test_cases, function_name)
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


def create_batch_cpp_wrapper(user_code: str, test_cases: List[Dict], function_name: str) -> str:
    """Create C++ wrapper that runs multiple test cases."""
    
    # Encode test cases as JSON strings with proper C++ escaping
    test_cases_json = []
    for test_case in test_cases:
        json_str = json.dumps(test_case["input"])
        # Escape quotes and backslashes for C++ string literals
        escaped_json = json_str.replace('\\', '\\\\').replace('"', '\\"')
        test_cases_json.append(escaped_json)
    
    test_cases_array = ",\n        ".join(f'"{tc}"' for tc in test_cases_json)
    
    # Check if this is the firstBadVersion function
    is_first_bad_version = (function_name == "firstBadVersion")
    
    # Function signature mapping for dynamic parameter handling
    def get_function_signature(fn_name):
        """Return parameter info for each function"""
        signatures = {
            "twoSum": {"params": ["nums", "target"], "return_type": "vector<int>"},
            "missingNumber": {"params": ["nums"], "return_type": "int"},
            "singleNumber": {"params": ["nums"], "return_type": "int"},
            "containsDuplicate": {"params": ["nums"], "return_type": "bool"},
            "climbStairs": {"params": ["n"], "return_type": "int"},
            "isPalindrome": {"params": ["x"], "return_type": "bool"},
            "isValid": {"params": ["s"], "return_type": "bool"},
            "moveZeroes": {"params": ["nums"], "return_type": "void"},
            "isAnagram": {"params": ["s", "t"], "return_type": "bool"},
            "isPowerOfTwo": {"params": ["n"], "return_type": "bool"},
            "firstBadVersion": {"params": ["n"], "return_type": "int"},
            # Add more as needed
        }
        return signatures.get(fn_name, {"params": ["nums", "target"], "return_type": "vector<int>"})
    
    signature = get_function_signature(function_name)
    
    # Generate conditional execution logic
    if is_first_bad_version:
        execution_logic = (
            '            vector<int> nVec = inputData["n"];\n'
            '            vector<int> badVec = inputData["bad"];\n'
            '            int n = nVec.empty() ? 0 : nVec[0];\n'
            '            int bad = badVec.empty() ? 0 : badVec[0];\n'
            '            \n'
            '            globalBadVersion = bad;\n'
            '            int intResult = sol.firstBadVersion(n);\n'
            '            \n'
            '            auto end = chrono::high_resolution_clock::now();\n'
            '            auto duration = chrono::duration_cast<chrono::microseconds>(end - start);\n'
            '            double executionTime = duration.count() / 1000.0;\n'
            '            \n'
            '            cout << "{\\"success\\": true, \\"output\\": " << intResult << ", \\"execution_time\\": " << executionTime << "}" << endl;'
        )
    else:
        # Generate dynamic parameter handling based on signature
        params = signature["params"]
        return_type = signature["return_type"]
        
        # Generate parameter extraction code
        param_extractions = []
        param_names = []
        
        for param in params:
            if param == "nums":
                param_extractions.append('            vector<int> nums = inputData["nums"];')
                param_names.append("nums")
            elif param == "target":
                param_extractions.append('            vector<int> targetVec = inputData["target"];')
                param_extractions.append('            int target = targetVec.empty() ? 0 : targetVec[0];')
                param_names.append("target")
            elif param == "n":
                param_extractions.append('            vector<int> nVec = inputData["n"];')
                param_extractions.append('            int n = nVec.empty() ? 0 : nVec[0];')
                param_names.append("n")
            elif param == "x":
                param_extractions.append('            vector<int> xVec = inputData["x"];')
                param_extractions.append('            int x = xVec.empty() ? 0 : xVec[0];')
                param_names.append("x")
            elif param == "s":
                param_extractions.append('            string s = inputData.find("s") != inputData.end() ? inputData["s"][0] : "";')
                param_names.append("s")
            elif param == "t":
                param_extractions.append('            string t = inputData.find("t") != inputData.end() ? inputData["t"][0] : "";')
                param_names.append("t")
        
        param_extraction_code = '\n'.join(param_extractions)
        function_params = ", ".join(param_names)
        
        # Generate result handling based on return type
        if return_type == "vector<int>":
            result_code = f'            vector<int> result = sol.{function_name}({function_params});'
            output_code = 'vectorToString(result)'
        elif return_type == "int":
            result_code = f'            int result = sol.{function_name}({function_params});'
            output_code = 'result'
        elif return_type == "bool":
            result_code = f'            bool result = sol.{function_name}({function_params});'
            output_code = '(result ? "true" : "false")'
        elif return_type == "void":
            result_code = f'            sol.{function_name}({function_params});'
            output_code = '"void"'
        else:
            result_code = f'            auto result = sol.{function_name}({function_params});'
            output_code = 'result'
        
        execution_logic = (
            f'{param_extraction_code}\n'
            '            \n'
            f'{result_code}\n'
            '            \n'
            '            auto end = chrono::high_resolution_clock::now();\n'
            '            auto duration = chrono::duration_cast<chrono::microseconds>(end - start);\n'
            '            double executionTime = duration.count() / 1000.0;\n'
            '            \n'
            f'            cout << "{{\\"success\\": true, \\"output\\": " << {output_code} << ", \\"execution_time\\": " << executionTime << "}}" << endl;'
        )
    
    # Build the wrapper in parts to avoid escaping issues
    includes = """#include <iostream>
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
using namespace std;"""

    json_parser = '''
// JSON parsing helpers
class JSONParser {
private:
    string json;
    size_t pos = 0;
    
    void skipWhitespace() {
        while (pos < json.length() && isspace(json[pos])) pos++;
    }
    
    int parseInt() {
        string numStr;
        if (json[pos] == '-') {
            numStr += json[pos++];
        }
        while (pos < json.length() && isdigit(json[pos])) {
            numStr += json[pos++];
        }
        return stoi(numStr);
    }
    
    vector<int> parseIntArray() {
        if (json[pos] != '[') throw runtime_error("Expected array");
        pos++;
        vector<int> result;
        skipWhitespace();
        
        if (json[pos] == ']') {
            pos++;
            return result;
        }
        
        while (true) {
            skipWhitespace();
            result.push_back(parseInt());
            skipWhitespace();
            
            if (json[pos] == ']') {
                pos++;
                break;
            } else if (json[pos] == ',') {
                pos++;
            } else {
                throw runtime_error("Expected ',' or ']'");
            }
        }
        return result;
    }
    
public:
    JSONParser(const string& jsonStr) : json(jsonStr) {}
    
    map<string, vector<int>> parseObject() {
        map<string, vector<int>> result;
        if (json[pos] != '{') throw runtime_error("Expected object");
        pos++;
        skipWhitespace();
        
        if (json[pos] == '}') {
            pos++;
            return result;
        }
        
        while (true) {
            skipWhitespace();
            
            // Parse key
            if (json[pos] != '"') throw runtime_error("Expected string key");
            pos++;
            string key;
            while (pos < json.length() && json[pos] != '"') {
                key += json[pos++];
            }
            pos++; // skip closing quote
            
            skipWhitespace();
            if (json[pos] != ':') throw runtime_error("Expected ':'");
            pos++;
            skipWhitespace();
            
            vector<int> value;
            if (json[pos] == '[') {
                // Parse array
                value = parseIntArray();
            } else {
                // Parse single integer
                value.push_back(parseInt());
            }
            result[key] = value;
            skipWhitespace();
            
            if (json[pos] == '}') {
                pos++;
                break;
            } else if (json[pos] == ',') {
                pos++;
            } else {
                throw runtime_error("Expected ',' or '}'");
            }
        }
        return result;
    }
};'''

    helpers = '''
// Global isBadVersion API for first-bad-version problem
int globalBadVersion = 0;

bool isBadVersion(int version) {
    return version >= globalBadVersion;
}

string vectorToString(const vector<int>& vec) {
    string result = "[";
    for (size_t i = 0; i < vec.size(); i++) {
        result += to_string(vec[i]);
        if (i < vec.size() - 1) result += ",";
    }
    result += "]";
    return result;
}

string intToString(int value) {
    return to_string(value);
}'''

    main_function = f'''
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
            
            Solution sol;
            {execution_logic}
            
        }} catch (const exception& e) {{
            cout << "{{" + string("\\"success\\": false, \\"output\\": null, \\"error\\": \\"") + e.what() + string("\\", \\"execution_time\\": null}}") << endl;
        }}
    }}
    
    return 0;
}}'''

    wrapper = includes + json_parser + helpers + f"\n\n// User code starts here\n{user_code}\n// User code ends here\n" + main_function
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