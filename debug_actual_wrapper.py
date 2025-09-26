#!/usr/bin/env python3
"""
Debug the actual wrapper generation to see what's happening
"""
import sys
import os
import tempfile

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), "backend"))

from backend.code_testing.docker_runner import generate_java_wrapper


def debug_actual_wrapper():
    """Debug the actual wrapper generation process"""

    # Use the same user code as in the test
    sample_user_code = """
    class Solution {
        public List<String> wordBreak(String s, List<String> wordDict) {
            List<String> result = new ArrayList<>();
            backtrack(s, wordDict, 0, new ArrayList<>(), result);
            return result;
        }
        
        private void backtrack(String s, List<String> wordDict, int start, List<String> path, List<String> result) {
            if (start == s.length()) {
                result.add(String.join(" ", path));
                return;
            }
            
            for (String word : wordDict) {
                if (start + word.length() <= s.length() && s.substring(start, start + word.length()).equals(word)) {
                    path.add(word);
                    backtrack(s, wordDict, start + word.length(), path, result);
                    path.remove(path.size() - 1);
                }
            }
        }
    }
    """

    print("🧪 Testing actual wrapper generation...")

    try:
        # Generate the wrapper
        wrapper_code = generate_java_wrapper(
            "wordBreak", sample_user_code, "word-break-ii"
        )

        if wrapper_code:
            print("✅ Wrapper generated successfully")

            # Save to a temp file to examine structure
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".java", delete=False
            ) as temp_file:
                temp_file.write(wrapper_code)
                temp_path = temp_file.name

            print(f"📁 Wrapper saved to: {temp_path}")

            # Show key lines around the injection point
            lines = wrapper_code.split("\n")
            print(f"\n📏 Total lines: {len(lines)}")

            # Find where the user's Solution class ends
            solution_start = -1
            solution_end = -1

            for i, line in enumerate(lines):
                if "class Solution {" in line and solution_start == -1:
                    solution_start = i
                if solution_start != -1 and "// Data structure definitions" in line:
                    solution_end = i
                    break

            if solution_start != -1 and solution_end != -1:
                print(
                    f"\n🎯 User Solution class: lines {solution_start+1} to {solution_end}"
                )
                print(
                    f"Showing lines {max(1, solution_start)} to {min(len(lines), solution_end+5)}:"
                )

                for i in range(
                    max(0, solution_start - 2), min(len(lines), solution_end + 5)
                ):
                    marker = ">>>" if i == solution_end else "   "
                    print(f"{marker} {i+1:3}: {lines[i]}")
            else:
                print("❌ Could not find class boundaries")
                print("\n📋 First 50 lines:")
                for i in range(min(50, len(lines))):
                    print(f"{i+1:3}: {lines[i]}")

        else:
            print("❌ Wrapper generation failed")

    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    debug_actual_wrapper()
