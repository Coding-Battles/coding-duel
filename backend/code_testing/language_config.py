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

# Helper functions for TreeNode conversion
def array_to_treenode(arr):
    if not arr or arr[0] is None:
        return None
    
    root = TreeNode(arr[0])
    queue = deque([root])
    i = 1
    
    while queue and i < len(arr):
        current = queue.popleft()
        
        # Left child
        if i < len(arr) and arr[i] is not None:
            current.left = TreeNode(arr[i])
            queue.append(current.left)
        i += 1
        
        # Right child
        if i < len(arr) and arr[i] is not None:
            current.right = TreeNode(arr[i])
            queue.append(current.right)
        i += 1
    
    return root

def treenode_to_array(root):
    if not root:
        return []
    
    result = []
    queue = deque([root])
    
    while queue:
        node = queue.popleft()
        if node:
            result.append(node.val)
            queue.append(node.left)
            queue.append(node.right)
        else:
            result.append(None)
    
    # Remove trailing None values
    while result and result[-1] is None:
        result.pop()
    
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
            elif function_name == 'mergeTwoLists':
                # Convert input arrays to ListNode objects
                list1_node = list_to_listnode(input_data.get('list1', []))
                list2_node = list_to_listnode(input_data.get('list2', []))
                
                # Call method with ListNode arguments
                result_node = solution_method(list1_node, list2_node)
                
                # Convert result back to array format
                result = listnode_to_list(result_node)
            # Special handling for TreeNode methods
            elif function_name == 'invertTree':
                # Convert input array to TreeNode object
                root_node = array_to_treenode(input_data.get('root', []))
                
                # Call method with TreeNode argument and convert result back
                result_node = solution_method(root_node)
                
                # Convert result TreeNode back to array format
                if result_node is None:
                    result = []
                else:
                    # Convert TreeNode to level-order array
                    result = treenode_to_array(result_node)
            elif function_name == 'isSameTree':
                # Convert input arrays to TreeNode objects
                p_node = array_to_treenode(input_data.get('p', []))
                q_node = array_to_treenode(input_data.get('q', []))
                
                # Call method with TreeNode arguments
                result = solution_method(p_node, q_node)
            elif function_name == 'maxDepth' or 'root' in input_data:
                # Convert input array to TreeNode object
                root_node = array_to_treenode(input_data.get('root', []))
                
                # Call method with TreeNode argument
                result = solution_method(root_node)
            # Special handling for rotate method which modifies matrix in place
            elif function_name == 'rotate':
                # Extract matrix from input data
                matrix = input_data.get('matrix', [])
                
                # Call rotate method (modifies matrix in place)
                solution_method(matrix)
                
                # Return the modified matrix
                result = matrix
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

// TreeNode definition for binary tree problems
function TreeNode(val, left, right) {
    this.val = (val===undefined ? 0 : val);
    this.left = (left===undefined ? null : left);
    this.right = (right===undefined ? null : right);
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

// Helper functions for TreeNode conversion
function arrayToTreeNode(arr) {
    if (!arr || arr.length === 0 || arr[0] === null) return null;
    
    const root = new TreeNode(arr[0]);
    const queue = [root];
    let i = 1;
    
    while (queue.length > 0 && i < arr.length) {
        const current = queue.shift();
        
        // Left child
        if (i < arr.length && arr[i] !== null) {
            current.left = new TreeNode(arr[i]);
            queue.push(current.left);
        }
        i++;
        
        // Right child
        if (i < arr.length && arr[i] !== null) {
            current.right = new TreeNode(arr[i]);
            queue.push(current.right);
        }
        i++;
    }
    
    return root;
}

function treeNodeToArray(root) {
    if (!root) return [];
    
    const result = [];
    const queue = [root];
    
    while (queue.length > 0) {
        const node = queue.shift();
        
        if (node) {
            result.push(node.val);
            queue.push(node.left);
            queue.push(node.right);
        } else {
            result.push(null);
        }
    }
    
    // Remove trailing nulls
    while (result.length > 0 && result[result.length - 1] === null) {
        result.pop();
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
        } else if (functionName === 'addTwoNumbers' || functionName === 'mergeTwoLists') {
            // Special handling for ListNode methods
            const list1Data = inputData.list1 || inputData.l1 || [];
            const list2Data = inputData.list2 || inputData.l2 || [];
            const l1Node = listToListNode(list1Data);
            const l2Node = listToListNode(list2Data);
            
            // Call method with ListNode arguments
            const resultNode = solutionInstance[functionName](l1Node, l2Node);
            
            // Convert result back to array format
            result = listNodeToList(resultNode);
        } else if (functionName === 'invertTree') {
            // Special handling for invertTree - convert result back to array
            const rootNode = arrayToTreeNode(inputData.root || []);
            
            // Call method with TreeNode argument
            const resultNode = solutionInstance[functionName](rootNode);
            
            // Convert TreeNode result back to array format
            result = treeNodeToArray(resultNode);
        } else if (functionName === 'isSameTree') {
            // Special handling for isSameTree - takes two TreeNode parameters
            const pNode = arrayToTreeNode(inputData.p || []);
            const qNode = arrayToTreeNode(inputData.q || []);
            
            // Call method with TreeNode arguments
            result = solutionInstance[functionName](pNode, qNode);
        } else if (functionName === 'maxDepth' || inputData.root !== undefined) {
            // Special handling for TreeNode methods
            const rootNode = arrayToTreeNode(inputData.root || []);
            
            // Call method with TreeNode argument
            result = solutionInstance[functionName](rootNode);
        } else if (functionName === 'rotate') {
            // Special handling for rotate method which modifies matrix in place
            const matrix = inputData.matrix || [];
            
            // Call rotate method (modifies matrix in place)
            solutionInstance[functionName](matrix);
            
            // Return the modified matrix
            result = matrix;
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
        "run_command": "java -Xms8m -Xmx64m -XX:+UseSerialGC HarnessMain",
        "mem_limit": "512m",
        "startup_command": "sh -c 'javac /tmp/CompilationServer.java && java -cp /tmp CompilationServer'",
        "wrapper_template": "JAVA_HARNESS_SYSTEM",
    },
}
