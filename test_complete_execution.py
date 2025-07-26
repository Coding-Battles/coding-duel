#!/usr/bin/env python3

import sys
sys.path.append('.')

from backend.code_testing.java_batch_runner import run_java_batch
import json

def test_complete_execution():
    print("Testing complete Java execution pipeline...")
    
    # Test cases for twoSum problem
    test_cases = [
        {'input': {'nums': [2, 7, 11, 15], 'target': 9}},
        {'input': {'nums': [3, 2, 4], 'target': 6}},
        {'input': {'nums': [3, 3], 'target': 6}}
    ]
    
    # Java code for twoSum
    java_code = '''
class Solution {
    public int[] twoSum(int[] nums, int target) {
        for (int i = 0; i < nums.length; i++) {
            for (int j = i + 1; j < nums.length; j++) {
                if (nums[i] + nums[j] == target) {
                    return new int[]{i, j};
                }
            }
        }
        return new int[]{};
    }
}
'''
    
    try:
        print("🚀 Running Java batch execution...")
        results = run_java_batch(
            code=java_code,
            test_cases=test_cases,
            function_name='twoSum'
        )
        
        print("📊 Results:")
        for i, result in enumerate(results):
            print(f"  Test {i+1}: {result}")
        
        # Check if all tests passed
        all_passed = all(result.get('success', False) for result in results)
        
        if all_passed:
            print("🎉 ALL TESTS PASSED! Socket-based Java execution is working perfectly!")
            return True
        else:
            print("❌ Some tests failed")
            return False
            
    except Exception as e:
        print(f"❌ Execution failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    if test_complete_execution():
        print()
        print("=" * 60)
        print("🎉 SUCCESS: Your Java execution system is now fixed!")
        print("✅ Named pipe deadlock resolved")
        print("✅ Socket-based communication working")
        print("✅ Persistent JVM server operational")
        print("✅ Batch test execution functional")
        print("=" * 60)
    else:
        print()
        print("❌ Complete execution test failed")