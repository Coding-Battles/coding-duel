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
    if not arr:
        return None
    head = ListNode(arr[0])
    current = head
    for val in arr[1:]:
        current.next = ListNode(val)
        current = current.next
    return head

def listnode_to_list(head):
    result = []
    current = head
    while current:
        result.append(current.val)
        current = current.next
    return result

# User code starts here
{code}
# User code ends here

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(json.dumps({"result": "Missing arguments: expected method name and input data", "execution_time": 0}))
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
            elif function_name == 'addTwoNumbers':
                # Convert input arrays to ListNode objects
                l1_node = list_to_listnode(input_data.get('l1', []))
                l2_node = list_to_listnode(input_data.get('l2', []))
                
                # Call method with ListNode arguments
                result_node = solution_method(l1_node, l2_node)
                
                # Convert result back to array format
                result = listnode_to_list(result_node)
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
        print(json.dumps({
            "result": error,
            "execution_time": execution_time
        }))
    else:
        print(json.dumps({
            "result": result,
            "execution_time": execution_time
        }))
""",
    },
    "javascript": {
        "image": "node:16-alpine",
        "file_extension": ".js",
        "run_command": "node {filename}",
        "mem_limit": "64m",
        "wrapper_template": """
if (process.argv.length < 4) {
    console.log(JSON.stringify({result: "Missing arguments: expected method name and input data", execution_time: 0}));
    process.exit(1);
}

const functionName = process.argv[2];
const inputData = JSON.parse(process.argv[3]);
const startTime = process.hrtime.bigint();

// Helper functions for ListNode conversion (definitions removed to avoid conflicts)

// Helper functions for ListNode conversion
function listToListNode(arr) {
    if (!arr || arr.length === 0) return null;
    
    // Use user-defined ListNode constructor
    const head = new ListNode(arr[0]);
    let current = head;
    for (let i = 1; i < arr.length; i++) {
        current.next = new ListNode(arr[i]);
        current = current.next;
    }
    return head;
}

function listNodeToList(head) {
    const result = [];
    let current = head;
    while (current) {
        result.push(current.val);
        current = current.next;
    }
    return result;
}

// User code starts here
{code}
// User code ends here

let result = null;

// Call the solution method on Solution class
try {
    // Improved detection logic for ES6 classes
    const solutionExists = typeof Solution === 'function';
    let methodExists = false;
    
    if (solutionExists) {
        // Try multiple ways to detect the method
        methodExists = typeof Solution.prototype[functionName] === 'function' ||
                      (Solution.prototype && functionName in Solution.prototype) ||
                      (typeof Solution.prototype.constructor === 'function' && 
                       typeof new Solution()[functionName] === 'function');
    }
    
    if (solutionExists && methodExists) {
        const solutionInstance = new Solution();
        
        // Special handling for first-bad-version problem
        if (functionName === 'firstBadVersion') {
            const n = inputData.n;
            const bad = inputData.bad;
            
            // Create isBadVersion function based on the bad parameter
            global.isBadVersion = function(version) {
                return version >= bad;
            };
            
            // Call firstBadVersion with only n parameter
            result = solutionInstance[functionName](n);
        } else if (functionName === 'addTwoNumbers') {
            // Special handling for ListNode methods
            const l1Node = listToListNode(inputData.l1 || []);
            const l2Node = listToListNode(inputData.l2 || []);
            
            // Call method with ListNode arguments
            const resultNode = solutionInstance[functionName](l1Node, l2Node);
            
            // Convert result back to array format
            result = listNodeToList(resultNode);
        } else {
            result = solutionInstance[functionName](...Object.values(inputData));
        }
    } else {
        if (!solutionExists) {
            result = `Solution class not found. typeof Solution = ${typeof Solution}`;
        } else {
            result = `Method '${functionName}' not found in Solution class. Available methods: ${Object.getOwnPropertyNames(Solution.prototype).join(', ')}`;
        }
    }
} catch (e) {
    result = e.message;
}

const endTime = process.hrtime.bigint();
const executionTime = Number(endTime - startTime) / 1000000;

console.log(JSON.stringify({
    result: result,
    execution_time: executionTime
}));
""",
    },
    "cpp": {
        "image": "frolvlad/alpine-gxx",
        "file_extension": ".cpp",
        "compile_command": "g++ -std=c++17 -o solution {filename}",
        "run_command": "./solution",
        "mem_limit": "256m",
        "startup_command": "sh -c 'sleep infinity'",
        "wrapper_template": "DYNAMIC_GENERATED_WRAPPER",  # This will be replaced by generate_cpp_wrapper()
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
{user_imports}

// ListNode and TreeNode definitions for algorithm problems
class ListNode {
    int val;
    ListNode next;
    ListNode() {}
    ListNode(int val) { this.val = val; }
    ListNode(int val, ListNode next) { this.val = val; this.next = next; }
}

class TreeNode {
    int val;
    TreeNode left;
    TreeNode right;
    TreeNode() {}
    TreeNode(int val) { this.val = val; }
    TreeNode(int val, TreeNode left, TreeNode right) {
        this.val = val;
        this.left = left;
        this.right = right;
    }
}

// Helper methods for ListNode conversion
class ListNodeHelper {
    public static ListNode arrayToListNode(int[] arr) {
        if (arr == null || arr.length == 0) return null;
        
        ListNode head = new ListNode(arr[0]);
        ListNode current = head;
        for (int i = 1; i < arr.length; i++) {
            current.next = new ListNode(arr[i]);
            current = current.next;
        }
        return head;
    }
    
    public static int[] listNodeToArray(ListNode head) {
        List<Integer> result = new ArrayList<>();
        ListNode current = head;
        while (current != null) {
            result.add(current.val);
            current = current.next;
        }
        return result.stream().mapToInt(Integer::intValue).toArray();
    }
}

{code}

// Static isBadVersion API for first-bad-version problem
class VersionControl {
    private static int badVersion = 0;
    
    public static void setBadVersion(int bad) {
        badVersion = bad;
    }
    
    public static boolean isBadVersion(int version) {
        return version >= badVersion;
    }
}

class Main {
    public static void main(String[] args) {
        if (args.length < 2) {
            System.out.println("{\\"result\\": \\"Missing arguments: expected method name and input data\\", \\"execution_time\\": 0}");
            return;
        }
        
        String methodName = args[0];
        String inputJson = args[1];
        long startTime = System.nanoTime();
        
        try {
            Solution sol = new Solution();
            Object result = null;
            
            // Special handling for first-bad-version problem
            if ("firstBadVersion".equals(methodName)) {
                int n = extractIntValue(inputJson, "n");
                int bad = extractIntValue(inputJson, "bad");
                
                VersionControl.setBadVersion(bad);
                
                Method method = Solution.class.getMethod("firstBadVersion", int.class);
                result = method.invoke(sol, n);
            } else if ("addTwoNumbers".equals(methodName)) {
                // Special handling for ListNode methods
                int[] l1Array = extractIntArray(inputJson, "l1");
                int[] l2Array = extractIntArray(inputJson, "l2");
                
                // Convert arrays to ListNode objects
                ListNode l1 = ListNodeHelper.arrayToListNode(l1Array);
                ListNode l2 = ListNodeHelper.arrayToListNode(l2Array);
                
                // Call method with ListNode arguments
                Method method = Solution.class.getMethod("addTwoNumbers", ListNode.class, ListNode.class);
                ListNode resultNode = (ListNode) method.invoke(sol, l1, l2);
                
                // Convert result back to array format
                result = ListNodeHelper.listNodeToArray(resultNode);
            } else {
                // Find method by name only (like Python does)
                Method targetMethod = null;
                Method[] methods = Solution.class.getMethods();
                for (Method method : methods) {
                    if (method.getName().equals(methodName)) {
                        targetMethod = method;
                        break;
                    }
                }
                
                if (targetMethod == null) {
                    throw new RuntimeException("Method " + methodName + " not found in Solution class");
                }
                
                // Extract parameters in JSON key order (like Python's list(input_data.values()))
                Object[] params = extractParametersInJsonOrder(inputJson);
                
                result = targetMethod.invoke(sol, params);
            }
            
            long endTime = System.nanoTime();
            double executionTime = (endTime - startTime) / 1_000_000.0;
            
            // Format output based on result type
            if (result instanceof int[]) {
                int[] intArrayResult = (int[]) result;
                System.out.print("{\\"result\\": [");
                for (int i = 0; i < intArrayResult.length; i++) {
                    System.out.print(intArrayResult[i]);
                    if (i < intArrayResult.length - 1) System.out.print(",");
                }
                System.out.println("], \\"execution_time\\": " + executionTime + "}");
            } else if (result instanceof Integer) {
                System.out.println("{\\"result\\": " + result + ", \\"execution_time\\": " + executionTime + "}");
            } else if (result instanceof Boolean) {
                System.out.println("{\\"result\\": " + result + ", \\"execution_time\\": " + executionTime + "}");
            } else if (result instanceof String) {
                System.out.println("{\\"result\\": \\"" + result.toString().replace("\\"", "\\\\\\"") + "\\", \\"execution_time\\": " + executionTime + "}");
            } else {
                System.out.println("{\\"result\\": \\"" + String.valueOf(result).replace("\\"", "\\\\\\"") + "\\", \\"execution_time\\": " + executionTime + "}");
            }
            
        } catch (Exception e) {
            long endTime = System.nanoTime();
            double executionTime = (endTime - startTime) / 1_000_000.0;
            System.out.println("{\\"result\\": \\"" + e.getMessage().replace("\\"", "\\\\\\"") + "\\", \\"execution_time\\": " + executionTime + "}");
        }
    }
    
    // Simple JSON parsing helpers
    private static int extractIntValue(String json, String key) {
        String pattern = "\\"" + key + "\\"\\\\s*:\\\\s*(-?\\\\d+)";
        java.util.regex.Pattern p = java.util.regex.Pattern.compile(pattern);
        java.util.regex.Matcher m = p.matcher(json);
        if (m.find()) {
            return Integer.parseInt(m.group(1));
        }
        throw new RuntimeException("Could not find key: " + key);
    }
    
    private static int[] extractIntArray(String json, String key) {
        String pattern = "\\"" + key + "\\"\\\\s*:\\\\s*\\\\[(.*?)\\\\]";
        java.util.regex.Pattern p = java.util.regex.Pattern.compile(pattern);
        java.util.regex.Matcher m = p.matcher(json);
        if (m.find()) {
            String arrayContent = m.group(1).trim();
            if (arrayContent.isEmpty()) {
                return new int[0];
            }
            String[] parts = arrayContent.split(",");
            int[] result = new int[parts.length];
            for (int i = 0; i < parts.length; i++) {
                result[i] = Integer.parseInt(parts[i].trim());
            }
            return result;
        }
        throw new RuntimeException("Could not find array key: " + key);
    }
    
    private static String extractStringValue(String json, String key) {
        String pattern = "\\"" + key + "\\"\\\\s*:\\\\s*\\"(.*?)\\"";
        java.util.regex.Pattern p = java.util.regex.Pattern.compile(pattern);
        java.util.regex.Matcher m = p.matcher(json);
        if (m.find()) {
            return m.group(1);
        }
        throw new RuntimeException("Could not find string key: " + key);
    }
    
    private static String[] extractStringArray(String json, String key) {
        String pattern = "\\"" + key + "\\"\\\\s*:\\\\s*\\\\[(.*?)\\\\]";
        java.util.regex.Pattern p = java.util.regex.Pattern.compile(pattern);
        java.util.regex.Matcher m = p.matcher(json);
        if (m.find()) {
            String arrayContent = m.group(1).trim();
            if (arrayContent.isEmpty()) {
                return new String[0];
            }
            String[] parts = arrayContent.split(",");
            String[] result = new String[parts.length];
            for (int i = 0; i < parts.length; i++) {
                String trimmed = parts[i].trim();
                if (trimmed.startsWith("\\"") && trimmed.endsWith("\\"")) {
                    result[i] = trimmed.substring(1, trimmed.length() - 1);
                } else {
                    result[i] = trimmed;
                }
            }
            return result;
        }
        throw new RuntimeException("Could not find string array key: " + key);
    }
    
    private static Object[] extractParametersInJsonOrder(String json) {
        // Extract JSON values in order (like Python's list(input_data.values()))
        java.util.List<Object> params = new java.util.ArrayList<>();
        
        // Parse JSON manually to extract key-value pairs in order
        String cleanJson = json.trim();
        if (cleanJson.startsWith("{") && cleanJson.endsWith("}")) {
            cleanJson = cleanJson.substring(1, cleanJson.length() - 1);
        }
        
        // Split by commas (simple approach for well-formed JSON)
        String[] parts = cleanJson.split(",");
        
        for (String part : parts) {
            part = part.trim();
            if (part.contains(":")) {
                String[] keyValue = part.split(":", 2);
                if (keyValue.length == 2) {
                    String key = keyValue[0].trim().replaceAll("^\\"|\\"$", "");
                    String value = keyValue[1].trim();
                    
                    try {
                        // Try to extract this parameter by key
                        if (value.startsWith("[")) {
                            // Array parameter
                            if (value.contains("\\"")) {
                                // String array - convert to List<String> for Java
                                String[] stringArray = extractStringArray(json, key);
                                java.util.List<String> stringList = java.util.Arrays.asList(stringArray);
                                params.add(stringList);
                            } else {
                                params.add(extractIntArray(json, key));
                            }
                        } else if (value.startsWith("\\"")) {
                            // String parameter
                            params.add(extractStringValue(json, key));
                        } else if (value.equals("true") || value.equals("false")) {
                            // Boolean parameter
                            params.add(Boolean.parseBoolean(value));
                        } else {
                            // Integer parameter
                            params.add(extractIntValue(json, key));
                        }
                    } catch (Exception e) {
                        // Skip if extraction fails
                    }
                }
            }
        }
        
        return params.toArray();
    }
}""",
    },
}