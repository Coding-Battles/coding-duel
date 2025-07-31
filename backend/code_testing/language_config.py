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

# Common algorithm imports
from collections import deque, defaultdict, Counter, OrderedDict
import heapq
import itertools
import bisect
from functools import lru_cache, reduce
import math
import re

# User code starts here
{code}
# User code ends here

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(json.dumps({{"result": "Missing arguments: expected method name and input data", "execution_time": 0}}))
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
            
            # Special handling for first-bad-version problem
            if function_name == 'firstBadVersion':
                # Extract n and bad from input data
                n = input_data.get('n')
                bad = input_data.get('bad')
                
                # Create isBadVersion function based on the bad parameter
                def isBadVersion(version):
                    return version >= bad
                
                # Inject isBadVersion into the global namespace so Solution can use it
                globals()['isBadVersion'] = isBadVersion
                
                # Call firstBadVersion with only n parameter
                result = solution_method(n)
            else:
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
    console.log(JSON.stringify({{result: "Missing arguments: expected method name and input data", execution_time: 0}}));
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
        
        // Special handling for first-bad-version problem
        if (functionName === 'firstBadVersion') {{
            const n = inputData.n;
            const bad = inputData.bad;
            
            // Create isBadVersion function based on the bad parameter
            global.isBadVersion = function(version) {{
                return version >= bad;
            }};
            
            // Call firstBadVersion with only n parameter
            result = solutionInstance[functionName](n);
        }} else {{
            result = solutionInstance[functionName](...Object.values(inputData));
        }}
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
        "image": "frolvlad/alpine-gxx",
        "file_extension": ".cpp",
        "compile_command": "g++ -std=c++17 -o solution {filename}",
        "run_command": "./solution",
        "mem_limit": "256m",
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

// Global isBadVersion API for first-bad-version problem
int globalBadVersion = 0;

bool isBadVersion(int version) {{
    return version >= globalBadVersion;
}}

string vectorToString(const vector<int>& vec) {{
    string result = "[";
    for (size_t i = 0; i < vec.size(); i++) {{
        result += to_string(vec[i]);
        if (i < vec.size() - 1) result += ",";
    }}
    result += "]";
    return result;
}}

string intToString(int value) {{
    return to_string(value);
}}

// User code starts here
{code}
// User code ends here

int main(int argc, char* argv[]) {{
    if (argc < 3) {{
        cout << "{{\\"result\\": \\"Missing arguments: expected method name and input data\\", \\"execution_time\\": 0}}" << endl;
        return 1;
    }}
    
    string methodName = argv[1];
    string inputJson = argv[2];
    auto start = chrono::high_resolution_clock::now();
    
    try {{
        JSONParser parser(inputJson);
        auto inputData = parser.parseObject();
        
        Solution sol;
        
        // Special handling for first-bad-version problem
        if (methodName == "firstBadVersion") {{
            vector<int> nVec = inputData["n"];
            vector<int> badVec = inputData["bad"];
            int n = nVec.empty() ? 0 : nVec[0];
            int bad = badVec.empty() ? 0 : badVec[0];
            
            // Set up isBadVersion API
            globalBadVersion = bad;
            
            // Call firstBadVersion with only n parameter
            int result = sol.firstBadVersion(n);
            
            auto end = chrono::high_resolution_clock::now();
            auto duration = chrono::duration_cast<chrono::microseconds>(end - start);
            double executionTime = duration.count() / 1000.0;
            
            cout << "{{\\"result\\": " << result << ", \\"execution_time\\": " << executionTime << "}}" << endl;
        }} else {{
            // Generic method invocation for other problems
            vector<int> result;
            
            if (methodName == "solution") {{
                // Call solution function with standard two parameters
                vector<int> nums = inputData["nums"];
                vector<int> targetVec = inputData["target"];
                int target = targetVec.empty() ? 0 : targetVec[0];
                
                result = sol.solution(nums, target);
                
                auto end = chrono::high_resolution_clock::now();
                auto duration = chrono::duration_cast<chrono::microseconds>(end - start);
                double executionTime = duration.count() / 1000.0;
                
                cout << "{{\\"result\\": " << vectorToString(result) << ", \\"execution_time\\": " << executionTime << "}}" << endl;
            }} else {{
                throw runtime_error("Unsupported method: " + methodName + ". Only 'solution' and 'firstBadVersion' are supported.");
            }}
        }}
        
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
        "compile_command": "javac -Xlint:none Main.java",
        "run_command": "java -Xms8m -Xmx64m -XX:+UseSerialGC Main",
        "mem_limit": "512m",
        "wrapper_template": """
import java.util.*;
import java.lang.reflect.*;

{code}

// Static isBadVersion API for first-bad-version problem
class VersionControl {{
    private static int badVersion = 0;
    
    public static void setBadVersion(int bad) {{
        badVersion = bad;
    }}
    
    public static boolean isBadVersion(int version) {{
        return version >= badVersion;
    }}
}}

class Main {{
    public static void main(String[] args) {{
        if (args.length < 2) {{
            System.out.println("{{\\\"result\\\": \\\"Missing arguments: expected method name and input data\\\", \\\"execution_time\\\": 0}}");
            return;
        }}
        
        String methodName = args[0];
        String inputJson = args[1];
        long startTime = System.nanoTime();
        
        try {{
            Solution sol = new Solution();
            Object result = null;
            
            // Special handling for first-bad-version problem
            if ("firstBadVersion".equals(methodName)) {{
                int n = extractIntValue(inputJson, "n");
                int bad = extractIntValue(inputJson, "bad");
                
                VersionControl.setBadVersion(bad);
                
                Method method = Solution.class.getMethod("firstBadVersion", int.class);
                result = method.invoke(sol, n);
            }} else {{
                // Find method by name only (like Python does)
                Method targetMethod = null;
                Method[] methods = Solution.class.getMethods();
                for (Method method : methods) {{
                    if (method.getName().equals(methodName)) {{
                        targetMethod = method;
                        break;
                    }}
                }}
                
                if (targetMethod == null) {{
                    throw new RuntimeException("Method " + methodName + " not found in Solution class");
                }}
                
                // Extract parameters in JSON key order (like Python's list(input_data.values()))
                Object[] params = extractParametersInJsonOrder(inputJson);
                
                result = targetMethod.invoke(sol, params);
            }}
            
            long endTime = System.nanoTime();
            double executionTime = (endTime - startTime) / 1_000_000.0;
            
            // Format output based on result type
            if (result instanceof int[]) {{
                int[] intArrayResult = (int[]) result;
                System.out.print("{{\\\"result\\\": [");
                for (int i = 0; i < intArrayResult.length; i++) {{
                    System.out.print(intArrayResult[i]);
                    if (i < intArrayResult.length - 1) System.out.print(",");
                }}
                System.out.println("], \\\"execution_time\\\": " + executionTime + "}}");
            }} else if (result instanceof Integer) {{
                System.out.println("{{\\\"result\\\": " + result + ", \\\"execution_time\\\": " + executionTime + "}}");
            }} else if (result instanceof Boolean) {{
                System.out.println("{{\\\"result\\\": " + result + ", \\\"execution_time\\\": " + executionTime + "}}");
            }} else if (result instanceof String) {{
                System.out.println("{{\\\"result\\\": \\\"" + result.toString().replace("\\"", "\\\\\\"") + "\\\", \\\"execution_time\\\": " + executionTime + "}}");
            }} else {{
                System.out.println("{{\\\"result\\\": \\\"" + String.valueOf(result).replace("\\"", "\\\\\\"") + "\\\", \\\"execution_time\\\": " + executionTime + "}}");
            }}
            
        }} catch (Exception e) {{
            long endTime = System.nanoTime();
            double executionTime = (endTime - startTime) / 1_000_000.0;
            System.out.println("{{\\\"result\\\": \\\"" + e.getMessage().replace("\\"", "\\\\\\"") + "\\\", \\\"execution_time\\\": " + executionTime + "}}");
        }}
    }}
    
    // Simple JSON parsing helpers
    private static int extractIntValue(String json, String key) {{
        String pattern = "\\"" + key + "\\"\\\\s*:\\\\s*(-?\\\\d+)";
        java.util.regex.Pattern p = java.util.regex.Pattern.compile(pattern);
        java.util.regex.Matcher m = p.matcher(json);
        if (m.find()) {{
            return Integer.parseInt(m.group(1));
        }}
        throw new RuntimeException("Could not find key: " + key);
    }}
    
    private static int[] extractIntArray(String json, String key) {{
        String pattern = "\\"" + key + "\\"\\\\s*:\\\\s*\\\\[(.*?)\\\\]";
        java.util.regex.Pattern p = java.util.regex.Pattern.compile(pattern);
        java.util.regex.Matcher m = p.matcher(json);
        if (m.find()) {{
            String arrayContent = m.group(1).trim();
            if (arrayContent.isEmpty()) {{
                return new int[0];
            }}
            String[] parts = arrayContent.split(",");
            int[] result = new int[parts.length];
            for (int i = 0; i < parts.length; i++) {{
                result[i] = Integer.parseInt(parts[i].trim());
            }}
            return result;
        }}
        throw new RuntimeException("Could not find array key: " + key);
    }}
    
    private static String extractStringValue(String json, String key) {{
        String pattern = "\\"" + key + "\\"\\\\s*:\\\\s*\\"(.*?)\\"";
        java.util.regex.Pattern p = java.util.regex.Pattern.compile(pattern);
        java.util.regex.Matcher m = p.matcher(json);
        if (m.find()) {{
            return m.group(1);
        }}
        throw new RuntimeException("Could not find string key: " + key);
    }}
    
    private static String[] extractStringArray(String json, String key) {{
        String pattern = "\\"" + key + "\\"\\\\s*:\\\\s*\\\\[(.*?)\\\\]";
        java.util.regex.Pattern p = java.util.regex.Pattern.compile(pattern);
        java.util.regex.Matcher m = p.matcher(json);
        if (m.find()) {{
            String arrayContent = m.group(1).trim();
            if (arrayContent.isEmpty()) {{
                return new String[0];
            }}
            String[] parts = arrayContent.split(",");
            String[] result = new String[parts.length];
            for (int i = 0; i < parts.length; i++) {{
                String trimmed = parts[i].trim();
                if (trimmed.startsWith("\\"") && trimmed.endsWith("\\"")) {{
                    result[i] = trimmed.substring(1, trimmed.length() - 1);
                }} else {{
                    result[i] = trimmed;
                }}
            }}
            return result;
        }}
        throw new RuntimeException("Could not find string array key: " + key);
    }}
    
    private static Object[] extractParametersInJsonOrder(String json) {{
        // Extract JSON values in order (like Python's list(input_data.values()))
        java.util.List<Object> params = new java.util.ArrayList<>();
        
        // Parse JSON manually to extract key-value pairs in order
        String cleanJson = json.trim();
        if (cleanJson.startsWith("{{") && cleanJson.endsWith("}}")) {{
            cleanJson = cleanJson.substring(1, cleanJson.length() - 1);
        }}
        
        // Split by commas (simple approach for well-formed JSON)
        String[] parts = cleanJson.split(",");
        
        for (String part : parts) {{
            part = part.trim();
            if (part.contains(":")) {{
                String[] keyValue = part.split(":", 2);
                if (keyValue.length == 2) {{
                    String key = keyValue[0].trim().replaceAll("^\\\"|\\\"$", "");
                    String value = keyValue[1].trim();
                    
                    try {{
                        // Try to extract this parameter by key
                        if (value.startsWith("[")) {{
                            // Array parameter
                            if (value.contains("\\\"")) {{
                                // String array - convert to List<String> for Java
                                String[] stringArray = extractStringArray(json, key);
                                java.util.List<String> stringList = java.util.Arrays.asList(stringArray);
                                params.add(stringList);
                            }} else {{
                                params.add(extractIntArray(json, key));
                            }}
                        }} else if (value.startsWith("\\\"")) {{
                            // String parameter
                            params.add(extractStringValue(json, key));
                        }} else if (value.equals("true") || value.equals("false")) {{
                            // Boolean parameter
                            params.add(Boolean.parseBoolean(value));
                        }} else {{
                            // Integer parameter
                            params.add(extractIntValue(json, key));
                        }}
                    }} catch (Exception e) {{
                        // Skip if extraction fails
                    }}
                }}
            }}
        }}
        
        return params.toArray();
    }}
}}""",
    },
}