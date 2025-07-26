#!/usr/bin/env python3

import sys
sys.path.append('.')
import json

# Create the exact JSON that would be sent to the Java server
test_cases = [
    {'input': {'nums': [3, 0, 1]}},
    {'input': {'nums': [0, 1]}},     
    {'input': {'nums': [9, 6, 4, 2, 3, 5, 7, 0, 1]}}
]

java_code = '''
class Solution {
    public int missingNumber(int[] nums) {
        int n = nums.length;
        long expectedSum = (long)n * (n + 1) / 2;
        long actualSum = 0;
        for (int num : nums) {
            actualSum += num;
        }
        return (int)(expectedSum - actualSum);
    }
}
'''

request = {
    "code": java_code,
    "test_cases": test_cases,
    "function_name": "missingNumber",
    "method_signature": {"params": [{"name": "nums", "type": "int[]"}], "return_type": "int"}
}

request_json = json.dumps(request)

print("Full JSON request:")
print(request_json)
print(f"\nJSON length: {len(request_json)}")

print("\nTesting our parsing logic...")

# Simulate the Java parsing
def test_parse_test_cases(json_str):
    print(f"Input: {json_str[:300]}...")
    
    # Look for test cases (updated pattern)
    start_idx = json_str.find('"test_cases":')
    if start_idx == -1:
        print("❌ No test_cases found")
        return []
    
    print(f"✅ Found test_cases at index {start_idx}")
    
    # Find array bounds
    array_start = json_str.find('[', start_idx) + 1
    
    # Find matching bracket
    depth = 0
    array_end = -1
    for i in range(array_start - 1, len(json_str)):
        if json_str[i] == '[':
            depth += 1
        elif json_str[i] == ']':
            depth -= 1
            if depth == 0:
                array_end = i
                break
    
    if array_end == -1:
        print("❌ Could not find array end")
        return []
    
    array_content = json_str[array_start:array_end]
    print(f"✅ Array content: {array_content[:200]}...")
    
    # Count test cases by counting {"input": occurrences
    count = array_content.count('{"input":')
    print(f"✅ Found {count} test cases in array")
    
    return count

count = test_parse_test_cases(request_json)
print(f"\nExpected: 3 test cases")
print(f"Parsed: {count} test cases")

if count == 3:
    print("✅ JSON parsing logic should work")
else:
    print("❌ JSON parsing logic needs fixing")