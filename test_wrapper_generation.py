#!/usr/bin/env python3
"""
Test script to verify Java wrapper generation works correctly
"""
import sys
import os
import tempfile
import subprocess

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), "backend"))

from backend.code_testing.docker_runner import generate_java_wrapper


def test_wrapper_generation():
    """Test Java wrapper generation with a simple problem"""

    # Test with word-break-ii problem that was causing compilation errors
    problem_id = "word-break-ii"

    # Sample user code for testing
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

    print(f"🧪 Testing wrapper generation for {problem_id}...")

    try:
        # Generate the wrapper with None signature to bypass signature loading
        wrapper_code = generate_java_wrapper("wordBreak", sample_user_code, problem_id)

        print("✅ Wrapper generation completed successfully")
        print(f"📄 Generated wrapper length: {len(wrapper_code)} characters")

        # Write to temporary file for compilation test
        with tempfile.NamedTemporaryFile(mode="w", suffix=".java", delete=False) as f:
            f.write(wrapper_code)
            temp_file = f.name

        print(f"📁 Temporary file created: {temp_file}")

        # Try to compile it
        print("🔨 Testing Java compilation...")
        result = subprocess.run(
            ["javac", temp_file], capture_output=True, text=True, timeout=30
        )

        if result.returncode == 0:
            print("✅ Java compilation successful!")
            # Clean up compiled class file
            class_file = temp_file.replace(".java", ".class")
            if os.path.exists(class_file):
                os.remove(class_file)
        else:
            print("❌ Java compilation failed:")
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)

            # Show problematic lines
            lines = wrapper_code.split("\n")
            print("\n🔍 First 50 lines of generated code:")
            for i, line in enumerate(lines[:50], 1):
                print(f"{i:3d}: {line}")

        # Clean up temp file
        os.remove(temp_file)

        return result.returncode == 0

    except Exception as e:
        print(f"❌ Error during wrapper generation: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_multiple_problems():
    """Test with several different problem types"""
    test_problems = [
        "word-break-ii",
        "two-sum",
        "add-two-numbers",
        "merge-k-sorted-lists",
    ]

    results = {}

    for problem in test_problems:
        print(f"\n{'='*60}")
        print(f"Testing {problem}")
        print("=" * 60)

        success = test_wrapper_generation_for_problem(problem)
        results[problem] = success

        if success:
            print(f"✅ {problem} - SUCCESS")
        else:
            print(f"❌ {problem} - FAILED")

    print(f"\n{'='*60}")
    print("SUMMARY")
    print("=" * 60)

    success_count = sum(results.values())
    total_count = len(results)

    for problem, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{problem:30} {status}")

    print(f"\nOverall: {success_count}/{total_count} tests passed")

    return success_count == total_count


def test_wrapper_generation_for_problem(problem_id):
    """Test wrapper generation for a specific problem"""

    # Sample user codes for different problems
    sample_codes = {
        "word-break-ii": """
        class Solution {
            public List<String> wordBreak(String s, List<String> wordDict) {
                List<String> result = new ArrayList<>();
                return result;
            }
        }
        """,
        "two-sum": """
        class Solution {
            public int[] twoSum(int[] nums, int target) {
                return new int[]{0, 1};
            }
        }
        """,
        "add-two-numbers": """
        class Solution {
            public ListNode addTwoNumbers(ListNode l1, ListNode l2) {
                return new ListNode(0);
            }
        }
        """,
        "merge-k-sorted-lists": """
        class Solution {
            public ListNode mergeKLists(ListNode[] lists) {
                return null;
            }
        }
        """,
    }

    user_code = sample_codes.get(
        problem_id,
        """
    class Solution {
        public int solution() {
            return 0;
        }
    }
    """,
    )

    try:
        wrapper_code = generate_java_wrapper("twoSum", user_code, problem_id)

        # Write to temporary file for compilation test
        with tempfile.NamedTemporaryFile(mode="w", suffix=".java", delete=False) as f:
            f.write(wrapper_code)
            temp_file = f.name

        # Try to compile it
        result = subprocess.run(
            ["javac", temp_file], capture_output=True, text=True, timeout=30
        )

        # Clean up
        if os.path.exists(temp_file):
            os.remove(temp_file)
        class_file = temp_file.replace(".java", ".class")
        if os.path.exists(class_file):
            os.remove(class_file)

        if result.returncode != 0:
            print(f"Compilation errors for {problem_id}:")
            print(result.stderr)

        return result.returncode == 0

    except Exception as e:
        print(f"Error testing {problem_id}: {e}")
        return False


if __name__ == "__main__":
    print("🚀 Starting Java wrapper generation tests...")

    # Test single problem first
    success = test_wrapper_generation()

    if success:
        print("\n🎯 Single test passed, running comprehensive tests...")
        all_success = test_multiple_problems()

        if all_success:
            print("\n🎉 All tests passed! Wrapper generation is working correctly.")
        else:
            print("\n⚠️ Some tests failed. Check the output above for details.")
    else:
        print("\n❌ Basic test failed. Check the implementation.")
