# backend/code_testing/language_config.py

LANGUAGE_CONFIG = {
    "python": {
        "image": "python:3.9-slim",
        "file_extension": ".py",
        "run_command": "python {filename}",
        "wrapper_template": """
import sys
import json
import time

# User code starts here
{code}
# User code ends here

if __name__ == "__main__":
    input_data = json.loads(sys.argv[1])
    start_time = time.time()
    
    # Find the solution function
    result = None
    error = None
    
    try:
        # Look for solution function - only accept exact name "solution"
        solution_func = None
        
        if 'solution' in globals() and callable(globals()['solution']):
            solution_func = globals()['solution']
        
        if solution_func:
            # Call the function with the input data as arguments
            # Try both ways: as keyword arguments and as positional arguments
            try:
                result = solution_func(**input_data)
            except TypeError:
                # If keyword arguments don't work, try positional arguments
                # This handles cases where the function expects (nums, target) instead of (nums=..., target=...)
                args = list(input_data.values())
                result = solution_func(*args)
        else:
            error = "No solution function found"
            
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
        "image": "node:16-slim",
        "file_extension": ".js",
        "run_command": "node {filename}",
        "wrapper_template": """
const inputData = JSON.parse(process.argv[2]);
const startTime = process.hrtime.bigint();

// User code starts here
{code}
// User code ends here

let result = null;

// Call the solution function
try {{
    if (typeof solution === 'function') {{
        result = solution(...Object.values(inputData));
    }} else {{
        result = "No solution function found";
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
        "image": "gcc:9",
        "file_extension": ".cpp",
        "compile_command": "g++ -std=c++17 -o solution {filename}",
        "run_command": "./solution",
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
            if (json[pos] == '\\') {{
                pos++;
                if (pos >= json.length()) throw runtime_error("Unterminated string");
                switch (json[pos]) {{
                    case '"': result += '"'; break;
                    case '\\': result += '\\'; break;
                    case '/': result += '/'; break;
                    case 'b': result += '\b'; break;
                    case 'f': result += '\f'; break;
                    case 'n': result += '\n'; break;
                    case 'r': result += '\r'; break;
                    case 't': result += '\t'; break;
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
            
            vector<int> value = parseIntArray();
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
        
        // Call solution function based on input pattern
        if (inputData.count("nums") && inputData.count("target")) {{
            // Two parameter pattern (e.g., Two Sum)
            vector<int> nums = inputData["nums"];
            int target = inputData["target"][0]; // target is usually a single value
            result = solution(nums, target);
        }} else if (inputData.count("nums")) {{
            // Single array input
            vector<int> nums = inputData["nums"];
            result = solution(nums);
        }}
        
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
        "compile_command": "javac Solution.java",
        "run_command": "java Main",
        "wrapper_template": """
import java.util.*;
import java.lang.reflect.Method;
{imports}

{code}

class Main {{
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
    
    public static String resultToJson(Object result, double executionTime) {{
        String resultStr;
        if (result instanceof int[]) {{
            resultStr = arrayToString((int[])result);
        }} else if (result instanceof String) {{
            resultStr = "\\\"" + result + "\\\"";
        }} else {{
            resultStr = String.valueOf(result);
        }}
        return "{{\\\"result\\\": " + resultStr + ", \\\"execution_time\\\": " + executionTime + "}}";
    }}
    
    public static Map<String, Object> parseInput(String jsonStr) {{
        Map<String, Object> data = new HashMap<>();
        
        // Remove outer braces and whitespace
        jsonStr = jsonStr.trim();
        if (jsonStr.startsWith("{{")) jsonStr = jsonStr.substring(1);
        if (jsonStr.endsWith("}}")) jsonStr = jsonStr.substring(0, jsonStr.length() - 1);
        
        // Split by commas, but respect nested structures
        List<String> parts = new ArrayList<>();
        int braceCount = 0;
        int bracketCount = 0;
        boolean inQuotes = false;
        StringBuilder current = new StringBuilder();
        
        for (int i = 0; i < jsonStr.length(); i++) {{
            char c = jsonStr.charAt(i);
            
            if (c == '\"' && (i == 0 || jsonStr.charAt(i-1) != '\\\\')) {{
                inQuotes = !inQuotes;
            }}
            
            if (!inQuotes) {{
                if (c == '{{') braceCount++;
                else if (c == '}}') braceCount--;
                else if (c == '[') bracketCount++;
                else if (c == ']') bracketCount--;
                else if (c == ',' && braceCount == 0 && bracketCount == 0) {{
                    parts.add(current.toString().trim());
                    current = new StringBuilder();
                    continue;
                }}
            }}
            
            current.append(c);
        }}
        parts.add(current.toString().trim());
        
        for (String part : parts) {{
            part = part.trim();
            if (part.isEmpty()) continue;
            
            String[] keyValue = part.split(":", 2);
            if (keyValue.length != 2) continue;
            
            String key = keyValue[0].trim().replaceAll("\\\"", "");
            String value = keyValue[1].trim();
            
            if (key.equals("nums") && value.startsWith("[") && value.endsWith("]")) {{
                // Parse array
                String arrayContent = value.substring(1, value.length() - 1).trim();
                if (arrayContent.isEmpty()) {{
                    data.put("nums", new int[0]);
                }} else {{
                    String[] numStrs = arrayContent.split(",");
                    int[] nums = new int[numStrs.length];
                    for (int i = 0; i < numStrs.length; i++) {{
                        nums[i] = Integer.parseInt(numStrs[i].trim());
                    }}
                    data.put("nums", nums);
                }}
            }} else if (key.equals("target")) {{
                data.put("target", Integer.parseInt(value));
            }} else if (key.equals("s") && value.startsWith("\\\"") && value.endsWith("\\\"")) {{
                data.put("s", value.substring(1, value.length() - 1));
            }}
        }}
        
        return data;
    }}
    
    public static void main(String[] args) {{
        if (args.length == 0) {{
            System.out.println("{{\\\"result\\\": \\\"No input provided\\\", \\\"execution_time\\\": 0}}");
            return;
        }}
        
        long startTime = System.nanoTime();
        
        try {{
            String inputJson = args[0];
            Map<String, Object> inputData = parseInput(inputJson);
            
            Object result = null;
            String error = null;
            
            // Create solution instance
            Solution solutionInstance = new Solution();
            
            // Try to find and call solution method
            int[] nums = (int[]) inputData.get("nums");
            Integer target = (Integer) inputData.get("target");
            String s = (String) inputData.get("s");
            
            Method solutionMethod = null;
            Object[] methodArgs = null;
            
            // Debug: List all available methods
            Method[] allMethods = solutionInstance.getClass().getDeclaredMethods();
            System.err.println("DEBUG: Available methods in Solution class:");
            for (Method m : allMethods) {{
                System.err.println("  " + m.getName() + " with parameters: " + java.util.Arrays.toString(m.getParameterTypes()));
            }}
            
            // Find method using reflection - only accept exact method name "solution"
            try {{
                if (nums != null && target != null) {{
                    // Two parameter method - only accept "solution"
                    try {{
                        solutionMethod = solutionInstance.getClass().getDeclaredMethod("solution", int[].class, int.class);
                        solutionMethod.setAccessible(true);
                        methodArgs = new Object[]{{nums, target}};
                    }} catch (NoSuchMethodException e) {{
                        error = "Method 'solution' with signature (int[], int) not found";
                    }}
                }} else if (nums != null) {{
                    // Single array parameter - only accept "solution"
                    try {{
                        solutionMethod = solutionInstance.getClass().getDeclaredMethod("solution", int[].class);
                        solutionMethod.setAccessible(true);
                        methodArgs = new Object[]{{nums}};
                    }} catch (NoSuchMethodException e) {{
                        error = "Method 'solution' with signature (int[]) not found";
                    }}
                }} else if (s != null) {{
                    // String parameter - only accept "solution"
                    try {{
                        solutionMethod = solutionInstance.getClass().getDeclaredMethod("solution", String.class);
                        solutionMethod.setAccessible(true);
                        methodArgs = new Object[]{{s}};
                    }} catch (NoSuchMethodException e) {{
                        error = "Method 'solution' with signature (String) not found";
                    }}
                }} else {{
                    error = "No suitable input parameters found";
                }}
                
                if (solutionMethod != null && error == null) {{
                    result = solutionMethod.invoke(solutionInstance, methodArgs);
                }} else if (error == null) {{
                    error = "No solution method found with matching signature";
                }}
            }} catch (Exception e) {{
                error = "Error calling solution method: " + e.getMessage();
            }}
            
            if (error != null) {{
                result = error;
            }}
            
            long endTime = System.nanoTime();
            double executionTime = (endTime - startTime) / 1_000_000.0;
            
            System.out.println(resultToJson(result, executionTime));
            
        }} catch (Exception e) {{
            long endTime = System.nanoTime();
            double executionTime = (endTime - startTime) / 1_000_000.0;
            
            System.out.println("{{\\\"result\\\": \\\"" + e.getMessage().replace("\\"", "\\\\\\"") + "\\\", \\\"execution_time\\\": " + executionTime + "}}");
        }}
    }}
}}
""",
    },
}
