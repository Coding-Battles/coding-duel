#!/usr/bin/env python3
"""
Test script to verify missing-number performance with new Java batch runner.
"""
import time
import json
import sys
import os

# Add backend to path
sys.path.append('/Users/andriysapeha/Documents/coding_duel/coding-duel')

from backend.code_testing.java_batch_runner import run_java_batch

def test_missing_number_performance():
    """Test missing-number question with minimal wrapper."""
    
    # Sample Java solution for missing-number
    java_code = """
class Solution {
    public int missingNumber(int[] nums) {
        int n = nums.length;
        int expectedSum = n * (n + 1) / 2;
        int actualSum = 0;
        for (int num : nums) {
            actualSum += num;
        }
        return expectedSum - actualSum;
    }
}
"""
    
    # Load test cases for missing-number
    test_cases = [
        {"input": {"nums": [3, 0, 1]}},
        {"input": {"nums": [0, 1]}},
        {"input": {"nums": [9, 6, 4, 2, 3, 5, 7, 0, 1]}},
        {"input": {"nums": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 51]}},
        {"input": {"nums": [1]}}
    ]
    
    print("Testing missing-number with new minimal Java batch runner...")
    print(f"Test cases: {len(test_cases)}")
    print(f"Java code length: {len(java_code)} characters")
    
    # Run the batch execution
    start_time = time.time()
    results = run_java_batch(
        code=java_code,
        test_cases=test_cases,
        timeout=10,
        function_name="missingNumber",
        question_name="missing-number"
    )
    total_time = (time.time() - start_time) * 1000
    
    print(f"\n🚀 TOTAL EXECUTION TIME: {total_time:.0f}ms")
    
    # Display results
    print(f"\nResults ({len(results)} test cases):")
    expected_outputs = [2, 2, 8, 50, 0]
    
    for i, (result, expected) in enumerate(zip(results, expected_outputs)):
        status = "✅ PASS" if result.get("success") and result.get("output") == expected else "❌ FAIL"
        exec_time = result.get("execution_time", 0)
        output = result.get("output")
        error = result.get("error")
        
        print(f"  Test {i+1}: {status} | Output: {output} (expected: {expected}) | Time: {exec_time:.2f}ms")
        if error:
            print(f"    Error: {error}")
    
    # Performance analysis
    successful_results = [r for r in results if r.get("success")]
    if successful_results:
        avg_exec_time = sum(r.get("execution_time", 0) for r in successful_results) / len(successful_results)
        print(f"\n📊 Performance Summary:")
        print(f"  - Total time: {total_time:.0f}ms")
        print(f"  - Average per test case: {avg_exec_time:.2f}ms")
        print(f"  - Successful test cases: {len(successful_results)}/{len(results)}")
        
        if total_time < 1000:  # Less than 1 second
            print(f"  - ✅ Performance restored! (target: <1000ms)")
        else:
            print(f"  - ❌ Still slow (target: <1000ms)")
    
    return results

if __name__ == "__main__":
    test_missing_number_performance()