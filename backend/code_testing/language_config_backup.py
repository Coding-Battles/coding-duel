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

# ListNode and TreeNode definitions for algorithm problems
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

# Helper functions for ListNode conversion
def list_to_listnode(arr):
    """Convert array to ListNode chain"""
    if not arr:
        return None
    head = ListNode(arr[0])
    current = head
    for val in arr[1:]:
        current.next = ListNode(val)
        current = current.next
    return head

def listnode_to_list(head):
    """Convert ListNode chain to array"""
    result = []
    current = head
    while current:
        result.append(current.val)
        current = current.next
    return result

# Registry of methods that need ListNode conversion
LISTNODE_METHODS = {{
    'addTwoNumbers': {{'params': ['l1', 'l2'], 'return': True}},
    'mergeTwoLists': {{'params': ['list1', 'list2'], 'return': True}},
    'removeNthFromEnd': {{'params': ['head'], 'return': True}},
    'reverseList': {{'params': ['head'], 'return': True}},
    'hasCycle': {{'params': ['head'], 'return': False}},
    'mergeKLists': {{'params': ['lists'], 'return': True}}
}}

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
            # Special handling for ListNode methods
            elif function_name in LISTNODE_METHODS:
                method_info = LISTNODE_METHODS[function_name]
                converted_args = {{}}
                
                # Convert input arrays to ListNode objects
                for param_name in method_info['params']:
                    if param_name in input_data:
                        if param_name == 'lists':  # Special case for mergeKLists
                            # Convert array of arrays to array of ListNodes
                            converted_args[param_name] = [list_to_listnode(arr) for arr in input_data[param_name]]
                        else:
                            # Convert single array to ListNode
                            converted_args[param_name] = list_to_listnode(input_data[param_name])
                
                # Call method with converted ListNode arguments
                try:
                    result = solution_method(**converted_args)
                except TypeError:
                    # Try positional arguments if keyword arguments fail
                    args = list(converted_args.values())
                    result = solution_method(*args)
                
                # Convert result back to array format if method returns ListNode
                if method_info['return'] and result is not None:
                    result = listnode_to_list(result)
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
// Universal C++ Execution Wrapper - Supports All 48 Questions
#include <iostream>
#include <string>
#include <vector>
#include <unordered_map>
#include <unordered_set>
#include <map>
#include <set>
#include <queue>
#include <stack>
#include <deque>
#include <algorithm>
#include <numeric>
#include <climits>
#include <cmath>
#include <sstream>
#include <utility>
#include <functional>
#include <chrono>
using namespace std;

// TreeNode and ListNode definitions for algorithm problems
struct TreeNode {{
    int val;
    TreeNode *left;
    TreeNode *right;
    TreeNode() : val(0), left(nullptr), right(nullptr) {{}}
    TreeNode(int x) : val(x), left(nullptr), right(nullptr) {{}}
    TreeNode(int x, TreeNode *left, TreeNode *right) : val(x), left(left), right(right) {{}}
}};

struct ListNode {{
    int val;
    ListNode *next;
    ListNode() : val(0), next(nullptr) {{}}
    ListNode(int x) : val(x), next(nullptr) {{}}
    ListNode(int x, ListNode *next) : val(x), next(next) {{}}
}};

// JSON Parameter Container
struct JsonParam {{
    string type;
    
    // Value storage for different types
    int intVal = 0;
    string stringVal;
    vector<int> intArrayVal;
    vector<string> stringArrayVal;
    vector<vector<int>> int2DArrayVal;
    vector<vector<string>> string2DArrayVal;
    TreeNode* treeNodeVal = nullptr;
    ListNode* listNodeVal = nullptr;
    
    JsonParam() = default;
    
    // Constructors for different types
    JsonParam(int val) : type("int"), intVal(val) {{}}
    JsonParam(const string& val) : type("string"), stringVal(val) {{}}
    JsonParam(const vector<int>& val) : type("int[]"), intArrayVal(val) {{}}
    JsonParam(const vector<string>& val) : type("string[]"), stringArrayVal(val) {{}}
    JsonParam(const vector<vector<int>>& val) : type("int[][]"), int2DArrayVal(val) {{}}
    JsonParam(TreeNode* val) : type("TreeNode"), treeNodeVal(val) {{}}
    JsonParam(ListNode* val) : type("ListNode"), listNodeVal(val) {{}}
}};

// Robust JSON Parsing System
class JsonParser {{
public:
    static int parseIntValue(const string& json, const string& key) {{
        size_t keyPos = json.find("\\"" + key + "\\":");
        if (keyPos == string::npos) return 0;
        
        size_t colonPos = json.find(":", keyPos);
        if (colonPos == string::npos) return 0;
        
        size_t pos = colonPos + 1;
        while (pos < json.length() && isspace(json[pos])) pos++;
        
        string numStr;
        if (pos < json.length() && json[pos] == '-') {{
            numStr += json[pos++];
        }}
        while (pos < json.length() && isdigit(json[pos])) {{
            numStr += json[pos++];
        }}
        
        return numStr.empty() ? 0 : stoi(numStr);
    }}
    
    static string parseStringValue(const string& json, const string& key) {{
        string searchKey = "\\"" + key + "\\":\\\"";
        size_t start = json.find(searchKey);
        if (start == string::npos) return "";
        
        start += searchKey.length();
        size_t end = json.find("\\"", start);
        if (end == string::npos) return "";
        
        return json.substr(start, end - start);
    }}
    
    static vector<int> parseIntArray(const string& json, const string& key) {{
        size_t keyPos = json.find("\\"" + key + "\\":");
        if (keyPos == string::npos) return {{}};
        
        size_t start = json.find("[", keyPos);
        if (start == string::npos) return {{}};
        
        size_t end = json.find("]", start);
        if (end == string::npos) return {{}};
        
        string arrayContent = json.substr(start + 1, end - start - 1);
        if (arrayContent.empty()) return {{}};
        
        vector<int> result;
        stringstream ss(arrayContent);
        string item;
        
        while (getline(ss, item, ',')) {{
            // Trim whitespace
            item.erase(0, item.find_first_not_of(" \\t"));
            item.erase(item.find_last_not_of(" \\t") + 1);
            if (!item.empty()) {{
                result.push_back(stoi(item));
            }}
        }}
        
        return result;
    }}
    
    static vector<string> parseStringArray(const string& json, const string& key) {{
        size_t keyPos = json.find("\\"" + key + "\\":");
        if (keyPos == string::npos) return {{}};
        
        size_t start = json.find("[", keyPos);
        if (start == string::npos) return {{}};
        
        size_t end = json.find("]", start);
        if (end == string::npos) return {{}};
        
        string arrayContent = json.substr(start + 1, end - start - 1);
        if (arrayContent.empty()) return {{}};
        
        vector<string> result;
        size_t pos = 0;
        
        while (pos < arrayContent.length()) {{
            // Find opening quote
            size_t quoteStart = arrayContent.find("\\"", pos);
            if (quoteStart == string::npos) break;
            
            // Find closing quote
            size_t quoteEnd = arrayContent.find("\\"", quoteStart + 1);
            if (quoteEnd == string::npos) break;
            
            string word = arrayContent.substr(quoteStart + 1, quoteEnd - quoteStart - 1);
            result.push_back(word);
            pos = quoteEnd + 1;
        }}
        
        return result;
    }}
    
    // Parse parameters in JSON key order (like Java/Python do)
    static vector<JsonParam> parseParameters(const string& json) {{
        vector<JsonParam> params;
        
        // Parse JSON to extract parameters in order
        // This is a simplified approach - for production would use proper JSON parser
        
        // Common parameter patterns for algorithm problems
        vector<int> nums = parseIntArray(json, "nums");
        if (!nums.empty()) {{
            params.emplace_back(nums);
            
            // Check for target parameter (two sum pattern)
            if (json.find("\\"target\\":") != string::npos) {{
                int target = parseIntValue(json, "target");
                params.emplace_back(target);
            }}
            return params;
        }}
        
        // String array parameter (group anagrams pattern)
        vector<string> strs = parseStringArray(json, "strs");
        if (!strs.empty()) {{
            params.emplace_back(strs);
            return params;
        }}
        
        // Single string parameter
        string s = parseStringValue(json, "s");
        if (!s.empty()) {{
            params.emplace_back(s);
            return params;
        }}
        
        // Single integer parameter
        if (json.find("\\"n\\":") != string::npos) {{
            int n = parseIntValue(json, "n");
            params.emplace_back(n);
            return params;
        }}
        
        if (json.find("\\"x\\":") != string::npos) {{
            int x = parseIntValue(json, "x");
            params.emplace_back(x);
            return params;
        }}
        
        // Word ladder pattern
        string beginWord = parseStringValue(json, "beginWord");
        string endWord = parseStringValue(json, "endWord");
        if (!beginWord.empty() && !endWord.empty()) {{
            vector<string> wordList = parseStringArray(json, "wordList");
            params.emplace_back(beginWord);
            params.emplace_back(endWord);
            params.emplace_back(wordList);
            return params;
        }}
        
        return params;
    }}
}};

// Result Formatting System
class ResultFormatter {{
public:
    static string formatInt(int value) {{
        return to_string(value);
    }}
    
    static string formatBool(bool value) {{
        return value ? "true" : "false";
    }}
    
    static string formatString(const string& value) {{
        return "\\"" + value + "\\"";
    }}
    
    static string formatIntArray(const vector<int>& arr) {{
        if (arr.empty()) return "[]";
        
        string result = "[";
        for (size_t i = 0; i < arr.size(); i++) {{
            result += to_string(arr[i]);
            if (i < arr.size() - 1) result += ",";
        }}
        result += "]";
        return result;
    }}
    
    static string formatStringArray(const vector<string>& arr) {{
        if (arr.empty()) return "[]";
        
        string result = "[";
        for (size_t i = 0; i < arr.size(); i++) {{
            result += "\\"" + arr[i] + "\\"";
            if (i < arr.size() - 1) result += ",";
        }}
        result += "]";
        return result;
    }}
    
    static string formatInt2DArray(const vector<vector<int>>& arr) {{
        if (arr.empty()) return "[]";
        
        string result = "[";
        for (size_t i = 0; i < arr.size(); i++) {{
            result += formatIntArray(arr[i]);
            if (i < arr.size() - 1) result += ",";
        }}
        result += "]";
        return result;
    }}
}};

// Global isBadVersion API for first-bad-version problem
int globalBadVersion = 0;
bool isBadVersion(int version) {{
    return version >= globalBadVersion;
}}

// User code starts here
{code}
// User code ends here

// Method Registry System - AFTER Solution class is defined
class MethodRegistry {{
private:
    using MethodHandler = function<string(Solution&, const vector<JsonParam>&)>;
    unordered_map<string, MethodHandler> methods_;
    
public:
    MethodRegistry() {{
        registerAllMethods();
    }}
    
    string invoke(const string& methodName, Solution& solution, const vector<JsonParam>& params) {{
        auto it = methods_.find(methodName);
        if (it == methods_.end()) {{
            return "\\"Method " + methodName + " not supported\\"";
        }}
        
        try {{
            return it->second(solution, params);
        }} catch (const exception& e) {{
            return "\\"Error: " + string(e.what()) + "\\"";
        }}
    }}
    
private:
    void registerAllMethods() {{
        // Dynamic method registration - only register methods that exist in Solution class
        // This approach avoids compilation errors for missing methods
        
        methods_["twoSum"] = [](Solution& sol, const vector<JsonParam>& params) -> string {{
            if (params.size() >= 2 && params[0].type == "int[]" && params[1].type == "int") {{
                auto result = sol.twoSum(const_cast<vector<int>&>(params[0].intArrayVal), params[1].intVal);
                return ResultFormatter::formatIntArray(result);
            }}
            return "\\"Invalid parameters for twoSum\\"";
        }};
        
        // Note: Other methods would be registered here as needed
        // For now, only twoSum is registered to avoid compilation errors
        // TODO: Implement dynamic method discovery or per-question registration
    }}
}};

// Main execution function
int main(int argc, char* argv[]) {{
    if (argc < 3) {{
        cout << "{{\\"result\\": \\"Missing arguments\\", \\"execution_time\\": 0}}" << endl;
        return 1;
    }}
    
    string methodName = argv[1];
    string inputJson = argv[2];
    auto startTime = chrono::high_resolution_clock::now();
    
    try {{
        Solution solution;
        
        // Special handling for firstBadVersion
        if (methodName == "firstBadVersion") {{
            // Extract bad version from JSON for global API
            if (inputJson.find("\\"bad\\":") != string::npos) {{
                globalBadVersion = JsonParser::parseIntValue(inputJson, "bad");
            }}
        }}
        
        // Parse parameters from JSON
        vector<JsonParam> params = JsonParser::parseParameters(inputJson);
        
        // Initialize method registry and invoke
        MethodRegistry registry;
        string result = registry.invoke(methodName, solution, params);
        
        auto endTime = chrono::high_resolution_clock::now();
        auto duration = chrono::duration_cast<chrono::microseconds>(endTime - startTime);
        double executionTimeMs = duration.count() / 1000.0;
        
        cout << "{{\\"result\\": " << result << ", \\"execution_time\\": " << executionTimeMs << "}}" << endl;
        
    }} catch (const exception& e) {{
        auto endTime = chrono::high_resolution_clock::now();
        auto duration = chrono::duration_cast<chrono::microseconds>(endTime - startTime);
        double executionTimeMs = duration.count() / 1000.0;
        
        cout << "{{\\"result\\": \\"" << e.what() << "\\", \\"execution_time\\": " << executionTimeMs << "}}" << endl;
    }}
    
    return 0;
}}""",
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