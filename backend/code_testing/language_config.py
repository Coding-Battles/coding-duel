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

// Simple JSON parsing helpers (no complex parsing needed)
int parseIntValue(const string& json, const string& key) {{
    string searchKey = string(1, 34) + key + string(1, 34) + string(1, 58); // "key":
    size_t pos = json.find(searchKey);
    if (pos == string::npos) return 0;
    
    pos = json.find(":", pos) + 1;
    while (pos < json.length() && isspace(json[pos])) pos++;
    
    string numStr;
    while (pos < json.length() && (isdigit(json[pos]) || json[pos] == '-')) {{
        numStr += json[pos++];
    }}
    return numStr.empty() ? 0 : stoi(numStr);
}}

string parseStringValue(const string& json, const string& key) {{
    string searchKey = string(1, 34) + key + string(1, 34) + string(1, 58) + string(1, 34); // "key":"
    size_t start = json.find(searchKey);
    if (start == string::npos) return "";
    
    start += searchKey.length(); // Skip "key":"
    size_t end = json.find(string(1, 34), start);
    return json.substr(start, end - start);
}}

vector<string> parseStringArrayValue(const string& json, const string& key) {{
    string searchKey = string(1, 34) + key + string(1, 34) + string(1, 58); // "key":
    size_t keyPos = json.find(searchKey);
    if (keyPos == string::npos) return {{}};
    
    size_t start = json.find("[", keyPos);
    if (start == string::npos) return {{}};
    
    start++; // Skip the [
    size_t end = json.find("]", start);
    string arrayStr = json.substr(start, end - start);
    
    vector<string> result;
    if (arrayStr.empty()) return result;
    
    // Parse string array: ["word1","word2","word3"]
    size_t pos = 0;
    while (pos < arrayStr.length()) {{
        size_t quoteStart = arrayStr.find(string(1, 34), pos);
        if (quoteStart == string::npos) break;
        
        size_t quoteEnd = arrayStr.find(string(1, 34), quoteStart + 1);
        if (quoteEnd == string::npos) break;
        
        string word = arrayStr.substr(quoteStart + 1, quoteEnd - quoteStart - 1);
        result.push_back(word);
        pos = quoteEnd + 1;
    }}
    return result;
}}

vector<int> parseArrayValue(const string& json, const string& key) {{
    string searchKey = string(1, 34) + key + string(1, 34) + string(1, 58); // "key":
    size_t keyPos = json.find(searchKey);
    if (keyPos == string::npos) return {{}};
    
    size_t start = json.find("[", keyPos);
    if (start == string::npos) return {{}};
    
    start++; // Skip the [
    size_t end = json.find("]", start);
    string arrayStr = json.substr(start, end - start);
    
    vector<int> result;
    if (arrayStr.empty()) return result;
    
    // Simple parsing: split by comma and convert to int
    stringstream ss(arrayStr);
    string item;
    while (getline(ss, item, ',')) {{
        // Remove whitespace
        item.erase(0, item.find_first_not_of(" \t"));
        item.erase(item.find_last_not_of(" \t") + 1);
        if (!item.empty()) {{
            result.push_back(stoi(item));
        }}
    }}
    return result;
}}

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

// Dynamic parameter extraction (like Java's extractParametersInJsonOrder)
struct JsonParam {{
    string key;
    string valueType; // "int", "string", "array_int", "array_string"
    
    // Union-like storage for different types
    int intVal;
    string stringVal;
    vector<int> intArrayVal;
    vector<string> stringArrayVal;
}};

vector<JsonParam> extractParametersInOrder(const string& json) {{
    vector<JsonParam> params;
    
    // Use existing parsing functions to get known parameters
    // Check for common algorithm parameters in typical order
    
    // Check for beginWord, endWord, wordList (word ladder pattern)
    string beginWord = parseStringValue(json, "beginWord");
    if (!beginWord.empty()) {{
        JsonParam param1;
        param1.key = "beginWord";
        param1.valueType = "string";
        param1.stringVal = beginWord;
        params.push_back(param1);
        
        string endWord = parseStringValue(json, "endWord");
        if (!endWord.empty()) {{
            JsonParam param2;
            param2.key = "endWord";
            param2.valueType = "string";
            param2.stringVal = endWord;
            params.push_back(param2);
            
            vector<string> wordList = parseStringArrayValue(json, "wordList");
            if (!wordList.empty()) {{
                JsonParam param3;
                param3.key = "wordList";
                param3.valueType = "array_string";
                param3.stringArrayVal = wordList;
                params.push_back(param3);
            }}
        }}
        return params;
    }}
    
    // Check for nums, target (two sum pattern)
    vector<int> nums = parseArrayValue(json, "nums");
    if (!nums.empty()) {{
        JsonParam param1;
        param1.key = "nums";
        param1.valueType = "array_int";
        param1.intArrayVal = nums;
        params.push_back(param1);
        
        int target = parseIntValue(json, "target");
        if (target != 0 || json.find(string(1, 34) + "target" + string(1, 34) + ":0") != string::npos) {{
            JsonParam param2;
            param2.key = "target";
            param2.valueType = "int";
            param2.intVal = target;
            params.push_back(param2);
        }}
        return params;
    }}
    
    // Check for single string parameter (valid parentheses pattern)
    string s = parseStringValue(json, "s");
    if (!s.empty()) {{
        JsonParam param;
        param.key = "s";
        param.valueType = "string";
        param.stringVal = s;
        params.push_back(param);
        return params;
    }}
    
    return params;
}}

// User code starts here
{code}
// User code ends here


int main(int argc, char* argv[]) {{
    if (argc < 3) {{
        cout << string(1, 123) << string(1, 34) << "result" << string(1, 34) << ": " << string(1, 34) << "Missing arguments" << string(1, 34) << ", " << string(1, 34) << "execution_time" << string(1, 34) << ": 0" << string(1, 125) << endl;
        return 1;
    }}
    
    string methodName = argv[1];
    string inputJson = argv[2];
    auto start = chrono::high_resolution_clock::now();
    
    try {{
        Solution sol;
        
        // Extract parameters dynamically from JSON (like Java does)
        vector<JsonParam> params = extractParametersInOrder(inputJson);
        
        auto end = chrono::high_resolution_clock::now();
        auto duration = chrono::duration_cast<chrono::microseconds>(end - start);
        double executionTime = duration.count() / 1000.0;
        
        // Dynamic method dispatch - only call the method specified by methodName
        string result;
        
        if (methodName == "twoSum") {{
            if (params.size() >= 2 && params[0].valueType == "array_int" && params[1].valueType == "int") {{
                vector<int> nums = params[0].intArrayVal;
                int target = params[1].intVal;
                vector<int> methodResult = sol.twoSum(nums, target);
                result = vectorToString(methodResult);
            }} else {{
                result = string(1, 34) + "Invalid parameters for twoSum" + string(1, 34);
            }}
        }} else if (methodName == "ladderLength") {{
            if (params.size() >= 3 && params[0].valueType == "string" && params[1].valueType == "string" && params[2].valueType == "array_string") {{
                string beginWord = params[0].stringVal;
                string endWord = params[1].stringVal;
                vector<string> wordList = params[2].stringArrayVal;
                int methodResult = sol.ladderLength(beginWord, endWord, wordList);
                result = to_string(methodResult);
            }} else {{
                result = string(1, 34) + "Invalid parameters for ladderLength" + string(1, 34);
            }}
        }} else if (methodName == "missingNumber") {{
            if (params.size() >= 1 && params[0].valueType == "array_int") {{
                vector<int> nums = params[0].intArrayVal;
                int methodResult = sol.missingNumber(nums);
                result = to_string(methodResult);
            }} else {{
                result = string(1, 34) + "Invalid parameters for missingNumber" + string(1, 34);
            }}
        }} else if (methodName == "isValid") {{
            if (params.size() >= 1 && params[0].valueType == "string") {{
                string s = params[0].stringVal;
                bool methodResult = sol.isValid(s);
                result = methodResult ? "true" : "false";
            }} else {{
                result = string(1, 34) + "Invalid parameters for isValid" + string(1, 34);
            }}
        }} else {{
            result = string(1, 34) + "Method " + methodName + " not supported" + string(1, 34);
        }}
        
        // Output result in JSON format
        cout << string(1, 123) << string(1, 34) << "result" << string(1, 34) << ": " << result << ", " << string(1, 34) << "execution_time" << string(1, 34) << ": " << executionTime << string(1, 125) << endl;
        
    }} catch (const exception& e) {{
        auto end = chrono::high_resolution_clock::now();
        auto duration = chrono::duration_cast<chrono::microseconds>(end - start);
        double executionTime = duration.count() / 1000.0;
        
        cout << string(1, 123) << string(1, 34) << "result" << string(1, 34) << ": " << string(1, 34) << e.what() << string(1, 34) << ", " << string(1, 34) << "execution_time" << string(1, 34) << ": " << executionTime << string(1, 125) << endl;
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
        "startup_command": "sh -c 'javac /tmp/CompilationServer.java && java -cp /tmp CompilationServer'",
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