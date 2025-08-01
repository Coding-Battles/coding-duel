#!/usr/bin/env python3

# Simple test to see what C++ wrapper generates
from backend.code_testing.language_config import LANGUAGE_CONFIG

code = '''class Solution {
public:
    vector<int> twoSum(vector<int>& nums, int target) {
        return {0, 1};
    }
};'''

wrapper = LANGUAGE_CONFIG['cpp']['wrapper_template'].format(code=code)

print("=== GENERATED C++ WRAPPER ===")
print(wrapper)
print("=== END ===")