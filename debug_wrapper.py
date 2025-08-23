#!/usr/bin/env python3

import sys
import os

sys.path.append("/Users/andriysapeha/Documents/coding_duel/coding-duel")

from backend.code_testing.docker_runner import generate_java_wrapper

code = """class Solution {
    public String alienOrder(String[] words) {
        return "test";
    }
}"""

wrapper = generate_java_wrapper("alienOrder", code)
print("=== GENERATED JAVA WRAPPER ===")
print(wrapper)
