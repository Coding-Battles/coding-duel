#!/usr/bin/env python3

import os
import glob


def find_missing_harnesses():
    """Find which C++ harnesses are missing by comparing frontend test solutions with backend harnesses"""

    # Get all frontend test solutions
    frontend_pattern = "/Users/andriysapeha/Documents/coding_duel/coding-duel/frontend/cypress/test-solutions/*.cpp"
    frontend_files = glob.glob(frontend_pattern)

    # Extract problem names from frontend
    frontend_problems = set()
    for file_path in frontend_files:
        problem_name = os.path.basename(file_path).replace(".cpp", "")
        frontend_problems.add(problem_name)

    # Get all backend harnesses
    backend_pattern = "/Users/andriysapeha/Documents/coding_duel/coding-duel/backend/code_testing/cpp_harnesses/harnesses/*/harness.cpp"
    backend_files = glob.glob(backend_pattern)

    # Extract problem names from backend
    backend_problems = set()
    for file_path in backend_files:
        problem_name = os.path.basename(os.path.dirname(file_path))
        backend_problems.add(problem_name)

    # Find missing harnesses
    missing_harnesses = frontend_problems - backend_problems
    extra_harnesses = backend_problems - frontend_problems

    print(f"Frontend problems: {len(frontend_problems)}")
    print(f"Backend harnesses: {len(backend_problems)}")
    print()

    if missing_harnesses:
        print(f"❌ Missing harnesses ({len(missing_harnesses)}):")
        for problem in sorted(missing_harnesses):
            print(f"   - {problem}")
        print()
    else:
        print("✅ All frontend problems have corresponding harnesses!")
        print()

    if extra_harnesses:
        print(
            f"📋 Extra harnesses (no frontend test solution) ({len(extra_harnesses)}):"
        )
        for problem in sorted(extra_harnesses):
            print(f"   - {problem}")
        print()

    return sorted(missing_harnesses)


def create_missing_harnesses(missing_problems):
    """Create harness files for missing problems"""

    if not missing_problems:
        print("No missing harnesses to create!")
        return

    print(f"Creating {len(missing_problems)} missing harnesses...")

    # Template harness content
    harness_template = """// Comprehensive standard library includes for portability
#include <iostream>
#include <string>
#include <vector>
#include <unordered_map>
#include <unordered_set>
#include <map>
#include <set>
#include <queue>
#include <stack>
#include <deque>
#include <list>
#include <algorithm>
#include <numeric>
#include <climits>
#include <cmath>
#include <sstream>
#include <utility>
#include <chrono>
#include <functional>
#include <iomanip>
#include <bitset>
#include <array>
#include <memory>
#include <iterator>
#include <random>
using namespace std;

// Standard LeetCode data structures
struct ListNode {{
    int val;
    ListNode *next;
    ListNode() : val(0), next(nullptr) {{}}
    ListNode(int x) : val(x), next(nullptr) {{}}
    ListNode(int x, ListNode *next) : val(x), next(next) {{}}
}};

struct TreeNode {{
    int val;
    TreeNode *left;
    TreeNode *right;
    TreeNode() : val(0), left(nullptr), right(nullptr) {{}}
    TreeNode(int x) : val(x), left(nullptr), right(nullptr) {{}}
    TreeNode(int x, TreeNode *left, TreeNode *right) : val(x), left(left), right(right) {{}}
}};

#include "userfunc.h"

// TODO: Implement problem-specific parsing and main function for {problem_name}
// This is a placeholder harness - needs to be customized for the specific problem

int main(int argc, char* argv[]) {{
    try {{
        // Read input from stdin
        string input;
        getline(cin, input);
        
        // TODO: Parse input according to problem requirements
        // TODO: Call Solution method
        // TODO: Format output
        
        Solution solution;
        
        // Placeholder output
        cout << "{{\\"result\\": \\"TODO: Implement {problem_name} harness\\", \\"execution_time\\": 0.01}}" << endl;
        
    }} catch (const exception& e) {{
        cout << "{{\\"result\\": \\"Error: " << e.what() << "\\", \\"execution_time\\": 0.01}}" << endl;
    }}
    
    return 0;
}}
"""

    userfunc_template = """class Solution {{
public:
    // TODO: Add method signature for {problem_name}
}};
"""

    for problem in missing_problems:
        # Create directory
        harness_dir = f"/Users/andriysapeha/Documents/coding_duel/coding-duel/backend/code_testing/cpp_harnesses/harnesses/{problem}"
        os.makedirs(harness_dir, exist_ok=True)

        # Create harness.cpp
        harness_path = os.path.join(harness_dir, "harness.cpp")
        with open(harness_path, "w") as f:
            f.write(harness_template.format(problem_name=problem))

        # Create userfunc.h
        userfunc_path = os.path.join(harness_dir, "userfunc.h")
        with open(userfunc_path, "w") as f:
            f.write(userfunc_template.format(problem_name=problem))

        print(f"✅ Created harness for {problem}")


if __name__ == "__main__":
    print("=== Finding Missing C++ Harnesses ===")
    missing = find_missing_harnesses()

    if missing:
        print("=== Creating Missing Harnesses ===")
        create_missing_harnesses(missing)
        print()
        print("⚠️  Note: The created harnesses are templates and need to be")
        print("   customized with proper input parsing and method calls")
        print("   for each specific problem.")
    else:
        print("🎉 All harnesses are present!")
