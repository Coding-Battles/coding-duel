# backend/code_testing/language_config.py

LANGUAGE_CONFIG = {
    "python": {
        "image": "python:3.9-alpine",
        "file_extension": ".py",
        "run_command": "python {filename}",
        "mem_limit": "64m",
        "wrapper_template": """
import sys
import json
import time

# User code starts here
{code}
# User code ends here

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(json.dumps({{"result": "Missing arguments: function_name and input_data", "execution_time": 0}}))
        sys.exit(1)
        
    function_name = sys.argv[1]
    input_data = json.loads(sys.argv[2])
    start_time = time.time()
    
    result = None
    error = None
    
    try:
        # Look for Solution class
        if 'Solution' in globals() and hasattr(globals()['Solution'], function_name):
            solution_instance = globals()['Solution']()
            solution_method = getattr(solution_instance, function_name)
            
            # Call the method with the input data as arguments
            # Try both ways: as keyword arguments and as positional arguments
            try:
                result = solution_method(**input_data)
            except TypeError:
                # If keyword arguments don't work, try positional arguments
                # This handles cases where the method expects (nums, target) instead of (nums=..., target=...)
                args = list(input_data.values())
                result = solution_method(*args)
        else:
            error = f"No Solution class found or method '{function_name}' not found in Solution class"
            
    except Exception as e:
        error = str(e)
    
    end_time = time.time()
    execution_time = (end_time - start_time) * 1000
    
    if error:
        print(json.dumps({{
            "result": error,
            "execution_time": execution_time
        }}))
    else:
        print(json.dumps({{
            "result": result,
            "execution_time": execution_time
        }}))
""",
    },
    "javascript": {
        "image": "node:16-alpine",
        "file_extension": ".js",
        "run_command": "node {filename}",
        "mem_limit": "64m",
        "wrapper_template": """
if (process.argv.length < 4) {{
    console.log(JSON.stringify({{result: "Missing arguments: function_name and input_data", execution_time: 0}}));
    process.exit(1);
}}

const functionName = process.argv[2];
const inputData = JSON.parse(process.argv[3]);
const startTime = process.hrtime.bigint();

// User code starts here
{code}
// User code ends here

let result = null;

// Call the solution method on Solution class
try {{
    if (typeof Solution === 'function' && typeof Solution.prototype[functionName] === 'function') {{
        const solutionInstance = new Solution();
        result = solutionInstance[functionName](...Object.values(inputData));
    }} else {{
        result = `No Solution class found or method '${{functionName}}' not found in Solution class`;
    }}
}} catch (e) {{
    result = e.message;
}}

const endTime = process.hrtime.bigint();
const executionTime = Number(endTime - startTime) / 1000000;

console.log(JSON.stringify({{
    result: result,
    execution_time: executionTime
}}));
""",
    },
    "cpp": {
        "image": "frolvlad/alpine-gcc",
        "file_extension": ".cpp",
        "compile_command": "g++ -std=c++17 -O2 -o solution {filename}",
        "run_command": "./solution",
        "mem_limit": "128m",
        "wrapper_template": """
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
    
    string parseString() {{
        if (json[pos] != '"') throw runtime_error("Expected string");
        pos++; // skip opening quote
        string result;
        while (pos < json.length() && json[pos] != '"') {{
            if (json[pos] == '\\\\') {{
                pos++;
                if (pos >= json.length()) throw runtime_error("Unterminated string");
                switch (json[pos]) {{
                    case '"': result += '"'; break;
                    case '\\\\': result += '\\\\'; break;
                    case '/': result += '/'; break;
                    case 'b': result += '\\b'; break;
                    case 'f': result += '\\f'; break;
                    case 'n': result += '\\n'; break;
                    case 'r': result += '\\r'; break;
                    case 't': result += '\\t'; break;
                    default: result += json[pos]; break;
                }}
            }} else {{
                result += json[pos];
            }}
            pos++;
        }}
        if (pos >= json.length()) throw runtime_error("Unterminated string");
        pos++; // skip closing quote
        return result;
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
            string key = parseString();
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
{code}
// User code ends here

int main(int argc, char* argv[]) {{
    if (argc < 2) {{
        cout << "{{\\"result\\": \\"No input provided\\", \\"execution_time\\": 0}}" << endl;
        return 1;
    }}
    
    auto start = chrono::high_resolution_clock::now();
    
    try {{
        string inputJson = argv[1];
        JSONParser parser(inputJson);
        auto inputData = parser.parseObject();
        
        vector<int> result;
        
        // Call solution function - only accept exact function name "solution"
        // User must implement a function named exactly "solution"
        
        // Call solution function with standard two parameters
        vector<int> nums = inputData["nums"];
        vector<int> targetVec = inputData["target"];
        int target = targetVec.empty() ? 0 : targetVec[0];
        
        // Create Solution instance and call solution method
        Solution sol;
        result = sol.solution(nums, target);
        
        auto end = chrono::high_resolution_clock::now();
        auto duration = chrono::duration_cast<chrono::microseconds>(end - start);
        double executionTime = duration.count() / 1000.0;
        
        cout << "{{\\"result\\": " << vectorToString(result) << ", \\"execution_time\\": " << executionTime << "}}" << endl;
        
    }} catch (const exception& e) {{
        auto end = chrono::high_resolution_clock::now();
        auto duration = chrono::duration_cast<chrono::microseconds>(end - start);
        double executionTime = duration.count() / 1000.0;
        
        cout << "{{\\"result\\": \\"" << e.what() << "\\", \\"execution_time\\": " << executionTime << "}}" << endl;
    }}
    
    return 0;
}}
""",
    },
    "java": {
        "image": "openjdk:11-jdk-slim",
        "file_extension": ".java", 
        "compile_command": "javac -Xlint:none Solution.java",
        "run_command": "java -Xms8m -Xmx32m -XX:+UseSerialGC -XX:TieredStopAtLevel=1 Main",
        "mem_limit": "128m",
        "wrapper_template": """
import java.util.*;
{imports}

{code}

class Main {{
    public static void main(String[] args) {{
        if (args.length == 0) {{
            System.out.println("{{\\\"result\\\": \\\"No input provided\\\", \\\"execution_time\\\": 0}}");
            return;
        }}
        
        long startTime = System.nanoTime();
        
        try {{
            // Parse JSON manually for speed
            String inputJson = args[0];
            String[] nums = null;
            int target = 0;
            
            // Quick JSON parsing for nums and target
            int numsStart = inputJson.indexOf("[");
            int numsEnd = inputJson.indexOf("]");
            if (numsStart != -1 && numsEnd != -1) {{
                String numsStr = inputJson.substring(numsStart + 1, numsEnd);
                if (!numsStr.trim().isEmpty()) {{
                    nums = numsStr.split(",");
                }}
            }}
            
            int targetStart = inputJson.indexOf("target") + 8;
            if (targetStart > 7) {{
                String targetStr = inputJson.substring(targetStart);
                target = Integer.parseInt(targetStr.replaceAll("[^\\\\d-]", ""));
            }}
            
            // Convert to int array
            int[] numArray = new int[nums != null ? nums.length : 0];
            if (nums != null) {{
                for (int i = 0; i < nums.length; i++) {{
                    numArray[i] = Integer.parseInt(nums[i].trim());
                }}
            }}
            
            // Call solution
            Solution sol = new Solution();
            int[] result = sol.solution(numArray, target);
            
            long endTime = System.nanoTime();
            double executionTime = (endTime - startTime) / 1_000_000.0;
            
            // Output result
            System.out.print("{{\\\"result\\\": [");
            for (int i = 0; i < result.length; i++) {{
                System.out.print(result[i]);
                if (i < result.length - 1) System.out.print(",");
            }}
            System.out.println("], \\\"execution_time\\\": " + executionTime + "}}");
            
        }} catch (Exception e) {{
            long endTime = System.nanoTime();
            double executionTime = (endTime - startTime) / 1_000_000.0;
            System.out.println("{{\\\"result\\\": \\\"" + e.getMessage().replace("\\"", "\\\\\\"") + "\\\", \\\"execution_time\\\": " + executionTime + "}}");
        }}
    }}
}}""",
    },
}