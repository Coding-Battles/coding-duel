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

// ListNode definition for wrapper functionality
function ListNode(val, next) {
    this.val = (val===undefined ? 0 : val);
    this.next = (next===undefined ? null : next);
}

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
        "compile_command": "javac -Xlint:none Solution.java",
        "run_command": "java -Xms8m -Xmx64m -XX:+UseSerialGC Solution",
        "mem_limit": "512m",
        "startup_command": "sh -c 'javac /tmp/CompilationServer.java && java -cp /tmp CompilationServer'",
        "wrapper_template": "JAVA_DYNAMIC_WRAPPER_INJECTION",
    },
}