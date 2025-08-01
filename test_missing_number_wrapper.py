#!/usr/bin/env python3

# Test to examine the exact C++ wrapper generated for missingNumber
from backend.code_testing.docker_runner import generate_cpp_method_specific_wrapper

code = '''class Solution {
public:
    int missingNumber(vector<int>& nums) {
        int n = nums.size();
        long expectedSum = (long)n * (n + 1) / 2;
        long actualSum = 0;
        for (int num : nums) {
            actualSum += num;
        }
        return (int)(expectedSum - actualSum);
    }
};'''

wrapper = generate_cpp_method_specific_wrapper(code, "missingNumber")

print("=== GENERATED C++ WRAPPER FOR missingNumber ===")
print(wrapper)
print("=== END ===")

# Also examine just the method-specific code
from backend.code_testing.docker_runner import get_method_specific_code
method_code = get_method_specific_code("missingNumber")
print("\n=== METHOD-SPECIFIC CODE ===") 
print(method_code)
print("=== END ===")