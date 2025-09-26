#!/usr/bin/env python3

import os
import glob


def fix_all_harness_include_order():
    """Fix the include order in all C++ harness files"""

    harness_pattern = "/Users/andriysapeha/Documents/coding_duel/coding-duel/backend/code_testing/cpp_harnesses/harnesses/*/harness.cpp"
    harness_files = glob.glob(harness_pattern)

    print(f"Found {len(harness_files)} harness files to fix...")

    for harness_file in harness_files:
        problem_name = os.path.basename(os.path.dirname(harness_file))
        print(f"Processing {problem_name}...")

        try:
            with open(harness_file, "r") as f:
                content = f.read()

            # Check if it needs fixing (userfunc.h should be after includes)
            lines = content.split("\n")
            userfunc_line_idx = None
            using_namespace_idx = None

            for i, line in enumerate(lines):
                if '#include "userfunc.h"' in line:
                    userfunc_line_idx = i
                elif line.strip() == "using namespace std;":
                    using_namespace_idx = i
                    break

            if userfunc_line_idx is not None and using_namespace_idx is not None:
                # Check if userfunc.h comes before using namespace (needs fixing)
                if userfunc_line_idx < using_namespace_idx:
                    print(f"  ⚠️  {problem_name}: Fixing include order...")

                    # Remove the userfunc.h line
                    userfunc_line = lines[userfunc_line_idx]
                    lines.pop(userfunc_line_idx)

                    # Adjust using_namespace_idx after removal
                    if using_namespace_idx > userfunc_line_idx:
                        using_namespace_idx -= 1

                    # Insert userfunc.h after "using namespace std;"
                    lines.insert(using_namespace_idx + 1, "")
                    lines.insert(using_namespace_idx + 2, userfunc_line)

                    # Write back
                    with open(harness_file, "w") as f:
                        f.write("\n".join(lines))

                    print(f"  ✅ {problem_name}: Fixed!")
                else:
                    print(f"  ✅ {problem_name}: Already correct")
            else:
                print(
                    f"  ⚠️  {problem_name}: Could not find userfunc.h or using namespace std"
                )

        except Exception as e:
            print(f"  ❌ {problem_name}: Error - {e}")


if __name__ == "__main__":
    fix_all_harness_include_order()
