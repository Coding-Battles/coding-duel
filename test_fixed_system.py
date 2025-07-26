#!/usr/bin/env python3

import sys
sys.path.append('.')

from backend.code_testing.java_batch_runner import run_java_batch
from backend.code_testing.docker_runner import get_persistent_container
import json
import time

def test_container_persistence():
    print("Testing container persistence...")
    
    # First, get the container (should create it)
    print("🔧 Getting initial container...")
    container1 = get_persistent_container('java')
    container1_id = container1.id
    print(f"✅ Container 1 ID: {container1_id[:12]}")
    
    # Wait a moment
    time.sleep(2)
    
    # Get container again (should reuse existing)
    print("🔧 Getting container again...")
    container2 = get_persistent_container('java')
    container2_id = container2.id
    print(f"✅ Container 2 ID: {container2_id[:12]}")
    
    if container1_id == container2_id:
        print("✅ SUCCESS: Container persistence is working!")
        return True
    else:
        print("❌ FAILED: Containers are different (not persistent)")
        return False

def test_missing_number():
    print("\nTesting missingNumber problem...")
    
    # Test cases for missingNumber
    test_cases = [
        {'input': {'nums': [3, 0, 1]}},  # Expected: 2
        {'input': {'nums': [0, 1]}},     # Expected: 2  
        {'input': {'nums': [9, 6, 4, 2, 3, 5, 7, 0, 1]}} # Expected: 8
    ]
    
    # Java code for missingNumber
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
    
    try:
        print("🚀 Running missingNumber batch execution...")
        start_time = time.time()
        
        results = run_java_batch(
            code=java_code,
            test_cases=test_cases,
            function_name='missingNumber'
        )
        
        execution_time = time.time() - start_time
        print(f"⏱️ Total execution time: {execution_time:.2f} seconds")
        
        print("📊 Results:")
        for i, result in enumerate(results):
            expected = [2, 2, 8][i]
            actual = result.get('output')
            success = result.get('success', False)
            print(f"  Test {i+1}: Expected {expected}, Got {actual}, Success: {success}")
        
        # Check if all tests passed with correct results
        expected_results = [2, 2, 8]
        all_correct = True
        
        for i, result in enumerate(results):
            if not result.get('success', False) or result.get('output') != expected_results[i]:
                all_correct = False
                break
        
        if all_correct:
            print("✅ SUCCESS: All missingNumber tests passed with correct results!")
            return True, execution_time
        else:
            print("❌ FAILED: Some tests failed or incorrect results")
            return False, execution_time
            
    except Exception as e:
        print(f"❌ Execution failed: {e}")
        return False, 0

def main():
    print("🧪 Testing Fixed Java Execution System")
    print("=" * 50)
    
    # Test 1: Container persistence
    persistence_ok = test_container_persistence()
    
    # Test 2: missingNumber problem
    missing_number_ok, execution_time = test_missing_number()
    
    print("\n" + "=" * 50)
    print("📋 FINAL RESULTS:")
    print(f"✅ Container persistence: {'PASS' if persistence_ok else 'FAIL'}")
    print(f"✅ missingNumber execution: {'PASS' if missing_number_ok else 'FAIL'}")
    
    if missing_number_ok:
        print(f"⚡ Execution time: {execution_time:.2f}s")
        if execution_time < 5:
            print("🎉 FAST EXECUTION: Sub-5-second performance achieved!")
        else:
            print("⚠️ SLOW EXECUTION: Still taking too long")
    
    if persistence_ok and missing_number_ok:
        print("\n🎉 SUCCESS: All issues have been resolved!")
        print("✅ Container lifecycle fixed")
        print("✅ Dynamic method signatures working") 
        print("✅ JSON parsing implemented")
        print("✅ missingNumber problem solved correctly")
        return True
    else:
        print("\n❌ Some issues remain to be fixed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)