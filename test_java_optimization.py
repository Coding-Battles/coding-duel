#!/usr/bin/env python3
"""Test script for Java optimization performance."""

import time
import sys
import os

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.code_testing.java_batch_runner import run_java_batch

def test_java_performance():
    """Test the optimized Java batch runner performance."""
    
    # Sample Java code for missingNumber
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
    
    # Test cases for missingNumber
    test_cases = [
        {"input": {"nums": [3, 0, 1]}},
        {"input": {"nums": [0, 1]}},
        {"input": {"nums": [9, 6, 4, 2, 3, 5, 7, 0, 1]}},
    ]
    
    # Mock method signature (like what would come from question data)
    method_signature = {
        "params": [{"name": "nums", "type": "int[]"}],
        "return_type": "int"
    }
    
    print("Testing optimized Java batch runner...")
    print(f"Code length: {len(java_code)} characters")
    print(f"Test cases: {len(test_cases)}")
    
    # Run the test
    start_time = time.time()
    results = run_java_batch(java_code, test_cases, function_name="missingNumber", method_signature=method_signature)
    total_time = (time.time() - start_time) * 1000
    
    # Display results
    print(f"\nTotal execution time: {total_time:.0f}ms")
    print("\nResults:")
    for i, result in enumerate(results):
        print(f"Test {i+1}: {result}")
    
    # Check if all tests succeeded
    success_count = sum(1 for r in results if r.get("success", False))
    print(f"\nSuccess rate: {success_count}/{len(test_cases)}")
    
    if total_time < 1000:  # Less than 1 second
        print("✅ Performance target achieved!")
    else:
        print("❌ Still too slow")

if __name__ == "__main__":
    print("=== First run (container creation) ===")
    test_java_performance()
    
    print("\n=== Second run (should reuse container) ===")
    test_java_performance()
    
    print("\n=== Third run (should reuse container) ===") 
    test_java_performance()