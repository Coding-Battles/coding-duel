#!/usr/bin/env python3
"""
Test Java wrapper code generation without Docker.
"""

import sys
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent / 'backend'))

from code_testing.language_config import LANGUAGE_CONFIG

def test_java_wrapper():
    """Test that our simplified Java wrapper generates correct code."""
    
    java_code = """
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
"""

    config = LANGUAGE_CONFIG["java"]
    wrapped_code = config["wrapper_template"].format(
        code=java_code.strip(),
        function_name="twoSum"
    )
    
    print("🧪 Generated Java wrapper code:")
    print("=" * 60)
    print(wrapped_code)
    print("=" * 60)
    
    # Check for key elements
    checks = [
        ("Main class present", "class Main" in wrapped_code),
        ("Strategy 1 (nums, target)", "int[].class, int.class" in wrapped_code),
        ("Strategy 2 (nums only)", 'getMethod(methodName, int[].class)' in wrapped_code),
        ("Strategy 3 (int n)", 'getMethod(methodName, int.class)' in wrapped_code),
        ("No signature complexity", "{signature}" not in wrapped_code),
        ("User code embedded", "twoSum" in wrapped_code),
        ("JSON parsing helpers", "extractIntArray" in wrapped_code),
        ("VersionControl API", "isBadVersion" in wrapped_code),
    ]
    
    print("\n🔍 Validation checks:")
    all_passed = True
    for check_name, passed in checks:
        status = "✅" if passed else "❌"
        print(f"  {status} {check_name}")
        if not passed:
            all_passed = False
    
    if all_passed:
        print("\n🎉 All checks passed! Java wrapper looks good.")
    else:
        print("\n⚠️  Some checks failed. Review the wrapper code.")
    
    print(f"\n📊 Wrapper code length: {len(wrapped_code)} characters")
    print(f"📊 Much simpler than before!")

if __name__ == "__main__":
    test_java_wrapper()