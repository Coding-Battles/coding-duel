#!/usr/bin/env python3

import os
import glob
import re


def extract_data_structures_from_userfunc():
    """Extract common data structures from all userfunc.h files and add them to harnesses"""

    # Standard data structures used across problems
    standard_data_structures = """
// Standard LeetCode data structures
struct ListNode {
    int val;
    ListNode *next;
    ListNode() : val(0), next(nullptr) {}
    ListNode(int x) : val(x), next(nullptr) {}
    ListNode(int x, ListNode *next) : val(x), next(next) {}
};

struct TreeNode {
    int val;
    TreeNode *left;
    TreeNode *right;
    TreeNode() : val(0), left(nullptr), right(nullptr) {}
    TreeNode(int x) : val(x), left(nullptr), right(nullptr) {}
    TreeNode(int x, TreeNode *left, TreeNode *right) : val(x), left(left), right(right) {}
};
"""

    harness_pattern = "/Users/andriysapeha/Documents/coding_duel/coding-duel/backend/code_testing/cpp_harnesses/harnesses/*/harness.cpp"
    harness_files = glob.glob(harness_pattern)

    print(f"Found {len(harness_files)} harness files to update...")

    for harness_file in harness_files:
        problem_name = os.path.basename(os.path.dirname(harness_file))
        userfunc_path = os.path.join(os.path.dirname(harness_file), "userfunc.h")

        print(f"Processing {problem_name}...")

        # Add data structures to ALL harnesses for maximum compatibility
        needs_data_structures = True

        if not needs_data_structures:
            print(
                f"  ⚠️  {problem_name}: Adding data structures anyway for compatibility"
            )
            needs_data_structures = True

        try:
            with open(harness_file, "r") as f:
                harness_content = f.read()

            # Check if data structures are already added
            if (
                "struct ListNode" in harness_content
                or "struct TreeNode" in harness_content
            ):
                print(f"  ✅ {problem_name}: Data structures already present")
                continue

            # Find the position to insert data structures (after using namespace std;)
            lines = harness_content.split("\n")
            insert_position = None

            for i, line in enumerate(lines):
                if line.strip() == "using namespace std;":
                    insert_position = i + 1
                    break

            if insert_position is None:
                print(f"  ❌ {problem_name}: Could not find 'using namespace std;'")
                continue

            # Insert data structures
            data_structure_lines = standard_data_structures.strip().split("\n")
            for j, ds_line in enumerate(data_structure_lines):
                lines.insert(insert_position + j, ds_line)

            # Write back
            with open(harness_file, "w") as f:
                f.write("\n".join(lines))

            print(f"  ✅ {problem_name}: Added data structures")

        except Exception as e:
            print(f"  ❌ {problem_name}: Error - {e}")


def update_userfunc_files():
    """Clean userfunc.h files to only contain the class definition"""

    harness_pattern = "/Users/andriysapeha/Documents/coding_duel/coding-duel/backend/code_testing/cpp_harnesses/harnesses/*/userfunc.h"
    userfunc_files = glob.glob(harness_pattern)

    print(f"\nCleaning {len(userfunc_files)} userfunc.h files...")

    for userfunc_file in userfunc_files:
        problem_name = os.path.basename(os.path.dirname(userfunc_file))

        try:
            with open(userfunc_file, "r") as f:
                content = f.read()

            # Remove includes and data structures, keep only class definition
            lines = content.split("\n")
            clean_lines = []
            in_class = False

            for line in lines:
                # Skip includes and pragmas
                if line.strip().startswith("#include") or line.strip().startswith(
                    "#pragma"
                ):
                    continue

                # Skip using namespace
                if line.strip() == "using namespace std;":
                    continue

                # Skip struct definitions
                if line.strip().startswith("struct "):
                    continue

                # Skip lines inside struct definitions
                if any(
                    keyword in line for keyword in ["ListNode", "TreeNode"]
                ) and not line.strip().startswith("class"):
                    continue

                # Keep class definitions and forward declarations
                if (
                    line.strip().startswith("class ")
                    or line.strip().startswith("};")
                    or in_class
                ):
                    in_class = True
                    clean_lines.append(line)
                    if line.strip() == "};":
                        in_class = False
                elif (
                    line.strip()
                    and not any(char in line for char in ["{", "}"])
                    and "Solution" in line
                ):
                    # Forward declarations or function signatures
                    clean_lines.append(line)

            # Write cleaned content
            with open(userfunc_file, "w") as f:
                f.write("\n".join(clean_lines))

            print(f"  ✅ {problem_name}: Cleaned userfunc.h")

        except Exception as e:
            print(f"  ❌ {problem_name}: Error - {e}")


if __name__ == "__main__":
    print("=== Adding data structures to harness files ===")
    extract_data_structures_from_userfunc()

    print("\n=== Cleaning userfunc.h files ===")
    update_userfunc_files()

    print("\n=== Done! ===")
    print(
        "Data structures are now embedded in harness files and will be available when user code is injected."
    )
