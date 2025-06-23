#!/usr/bin/env python3
"""
Quick test to verify persistent container performance.
"""
import sys
import time
import json
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from backend.models.submission import DockerRunRequest
from backend.code_testing.docker_runner import run_code_in_docker

def test_java_speed():
    """Test Java execution speed with persistent containers."""
    
    java_code = '''
class Solution {
    public int[] solution(int[] nums, int target) {
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
    
    request = DockerRunRequest(
        code=java_code,
        language="java",
        test_input={"nums": [2, 7, 11, 15], "target": 9},
        timeout=10,
    )
    
    print("🧪 Testing Java execution speed...")
    
    # Test multiple runs to show persistent container benefit
    times = []
    for i in range(3):
        print(f"Run {i+1}...")
        start_time = time.time()
        result = run_code_in_docker(request)
        execution_time = time.time() - start_time
        times.append(execution_time)
        
        print(f"  Success: {result.get('success', False)}")
        print(f"  Output: {result.get('output')}")
        print(f"  Total time: {execution_time:.3f}s")
        print(f"  Reported time: {result.get('execution_time', 0):.0f}ms")
        
        if result.get('error'):
            print(f"  Error: {result.get('error')}")
        print()
    
    avg_time = sum(times) / len(times)
    print(f"📊 Average execution time: {avg_time:.3f}s")
    
    if avg_time < 1.0:
        print("🎉 SUCCESS: Sub-second execution achieved!")
    elif avg_time < 5.0:
        print("✅ GOOD: Much faster than before")
    else:
        print("⚠️ SLOW: Still needs optimization")

if __name__ == "__main__":
    test_java_speed()