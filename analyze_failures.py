#!/usr/bin/env python3
"""
Static analysis of code structure to identify fixes needed for Cypress failures.
This analyzes the code without running the server.
"""

import os
import json
import re
from pathlib import Path


def analyze_questions_structure():
    """Analyze the questions.json structure"""
    print("🔍 ANALYZING QUESTIONS STRUCTURE")
    print("=" * 50)

    questions_path = "backend/data/questions.json"
    if os.path.exists(questions_path):
        with open(questions_path, "r") as f:
            data = json.load(f)

        # Extract all questions from all difficulty levels
        all_questions = []
        if "questions" in data:
            for difficulty in data["questions"].values():
                if isinstance(difficulty, list):
                    all_questions.extend(difficulty)

        print(f"✅ Found {len(all_questions)} questions in questions.json")

        # Check for edit-distance
        edit_distance_found = any(
            q.get("slug") == "edit-distance" for q in all_questions
        )
        print(
            f"{'✅' if edit_distance_found else '❌'} edit-distance {'found' if edit_distance_found else 'missing'}"
        )

        # Check for regular-expression-matching (should be removed)
        regex_found = any(
            q.get("slug") == "regular-expression-matching" for q in all_questions
        )
        print(
            f"{'❌' if regex_found else '✅'} regular-expression-matching {'still present (should be removed)' if regex_found else 'properly removed'}"
        )

        return all_questions
    else:
        print("❌ questions.json not found")
        return []


def analyze_question_data():
    """Analyze individual question data files"""
    print("\n🔍 ANALYZING QUESTION DATA FILES")
    print("=" * 50)

    data_dir = "backend/data/question-data"
    if not os.path.exists(data_dir):
        print("❌ question-data directory not found")
        return

    # Check edit-distance.json
    edit_distance_path = f"{data_dir}/edit-distance.json"
    if os.path.exists(edit_distance_path):
        with open(edit_distance_path, "r") as f:
            edit_data = json.load(f)
        print("✅ edit-distance.json exists")
        print(f"   Method: {edit_data.get('methodName', 'N/A')}")
        print(f"   Return type: {edit_data.get('returnType', 'N/A')}")
        print(f"   Parameters: {len(edit_data.get('parameters', []))}")
    else:
        print("❌ edit-distance.json missing")

    # Check if regular-expression-matching.json still exists (should be removed)
    regex_path = f"{data_dir}/regular-expression-matching.json"
    if os.path.exists(regex_path):
        print("❌ regular-expression-matching.json still exists (should be removed)")
    else:
        print("✅ regular-expression-matching.json properly removed")


def analyze_test_data():
    """Analyze test data files"""
    print("\n🔍 ANALYZING TEST DATA FILES")
    print("=" * 50)

    test_dir = "backend/data/tests"
    if not os.path.exists(test_dir):
        print("❌ tests directory not found")
        return

    # Check edit-distance tests
    edit_test_path = f"{test_dir}/edit-distance.json"
    if os.path.exists(edit_test_path):
        with open(edit_test_path, "r") as f:
            test_data = json.load(f)
        print("✅ edit-distance test data exists")
        if isinstance(test_data, list):
            print(f"   Test cases: {len(test_data)}")
        else:
            print(f"   Test cases: {len(test_data.get('testCases', []))}")
    else:
        print("❌ edit-distance test data missing")


def analyze_java_wrapper():
    """Analyze Java wrapper parameter patterns"""
    print("\n🔍 ANALYZING JAVA WRAPPER PATTERNS")
    print("=" * 50)

    docker_runner_path = "backend/code_testing/docker_runner.py"
    if not os.path.exists(docker_runner_path):
        print("❌ docker_runner.py not found")
        return

    with open(docker_runner_path, "r") as f:
        content = f.read()

    # Check for parameter patterns
    patterns_to_check = [
        (
            '{"a": "...", "b": "..."}',
            r'json\.contains\("\\\"a\\\""\).*json\.contains\("\\\"b\\\""\)',
        ),
        ('{"intervals": [...]}', r'json\.contains\("\\\"intervals\\\""\)'),
        (
            '{"l1": [...], "l2": [...]}',
            r'json\.contains\("\\\"l1\\\""\).*json\.contains\("\\\"l2\\\""\)',
        ),
        (
            '{"p": [...], "q": [...]}',
            r'json\.contains\("\\\"p\\\""\).*json\.contains\("\\\"q\\\""\)',
        ),
        (
            '{"word1": "...", "word2": "..."}',
            r'json\.contains\("\\\"word1\\\""\).*json\.contains\("\\\"word2\\\""\)',
        ),
    ]

    for pattern_desc, pattern_regex in patterns_to_check:
        if re.search(pattern_regex, content, re.DOTALL):
            print(f"✅ {pattern_desc} pattern found")
        else:
            print(f"❌ {pattern_desc} pattern missing")

    # Check for helper methods
    helper_methods = [
        ("extractIntArrayArray", "for 2D arrays"),
        ("arrayToListNode", "for ListNode conversion"),
        ("arrayToTreeNode", "for TreeNode conversion"),
    ]

    for method_name, description in helper_methods:
        if f"private static.*{method_name}" in content:
            print(f"✅ {method_name} method found ({description})")
        else:
            print(f"❌ {method_name} method missing ({description})")

    # Check for class definitions
    class_definitions = [
        ("class TreeNode", "TreeNode class"),
        ("class ListNode", "ListNode class"),
    ]

    for class_pattern, description in class_definitions:
        if class_pattern in content:
            print(f"✅ {description} found")
        else:
            print(f"❌ {description} missing")


def analyze_cpp_harnesses():
    """Analyze C++ harness files"""
    print("\n🔍 ANALYZING C++ HARNESS FILES")
    print("=" * 50)

    harness_dir = "backend/code_testing/cpp_harnesses"
    if not os.path.exists(harness_dir):
        print("❌ cpp_harnesses directory not found")
        return

    # Check for specific harness files that were mentioned in failures
    harness_files = [
        "edit-distance.cpp",
        "add-binary.cpp",
        "merge-intervals.cpp",
        "valid-anagram.cpp",
        "palindrome-number.cpp",
        "same-tree.cpp",
        "maximum-depth-of-binary-tree.cpp",
    ]

    for harness_file in harness_files:
        harness_path = f"{harness_dir}/{harness_file}"
        if os.path.exists(harness_path):
            print(f"✅ {harness_file} harness exists")
        else:
            print(f"❌ {harness_file} harness missing")


def analyze_function_mappings():
    """Analyze function name mappings in docker_runner.py"""
    print("\n🔍 ANALYZING FUNCTION MAPPINGS")
    print("=" * 50)

    docker_runner_path = "backend/code_testing/docker_runner.py"
    if not os.path.exists(docker_runner_path):
        print("❌ docker_runner.py not found")
        return

    with open(docker_runner_path, "r") as f:
        content = f.read()

    # Check for function mappings
    mappings_to_check = [
        ("minDistance", "edit-distance"),
        ("addTwoNumbers", "add-two-numbers"),
        ("addBinary", "add-binary"),
        ("merge", "merge-intervals"),
        ("isAnagram", "valid-anagram"),
        ("isPalindrome", "palindrome-number"),
        ("isSameTree", "same-tree"),
        ("maxDepth", "maximum-depth-of-binary-tree"),
    ]

    for func_name, problem_id in mappings_to_check:
        if f'"{func_name}"' in content and f'"{problem_id}"' in content:
            print(f"✅ {func_name} -> {problem_id} mapping found")
        else:
            print(f"❌ {func_name} -> {problem_id} mapping missing")


def analyze_solution_files():
    """Analyze solution files for edit-distance"""
    print("\n🔍 ANALYZING SOLUTION FILES")
    print("=" * 50)

    solutions_dir = "backend/test-solutions"
    if not os.path.exists(solutions_dir):
        print("❌ test-solutions directory not found")
        return

    languages = ["py", "js", "java", "cpp"]
    for lang in languages:
        solution_path = f"{solutions_dir}/edit-distance.{lang}"
        if os.path.exists(solution_path):
            with open(solution_path, "r") as f:
                content = f.read().strip()
            print(f"✅ edit-distance.{lang} exists ({len(content)} chars)")

            # Check if it contains the expected method name
            if lang == "py" and "def minDistance" in content:
                print(f"   ✅ Contains minDistance method")
            elif lang == "js" and "function minDistance" in content:
                print(f"   ✅ Contains minDistance function")
            elif lang == "java" and "public int minDistance" in content:
                print(f"   ✅ Contains minDistance method")
            elif lang == "cpp" and "int minDistance" in content:
                print(f"   ✅ Contains minDistance function")
            else:
                print(f"   ❌ Missing or incorrect method signature")
        else:
            print(f"❌ edit-distance.{lang} missing")


def main():
    """Run all analyses"""
    print("🔧 STATIC CODE ANALYSIS FOR CYPRESS FAILURES")
    print("=" * 60)
    print("Analyzing code structure without running server...")

    os.chdir("/Users/andriysapeha/Documents/coding_duel/coding-duel")

    analyze_questions_structure()
    analyze_question_data()
    analyze_test_data()
    analyze_java_wrapper()
    analyze_cpp_harnesses()
    analyze_function_mappings()
    analyze_solution_files()

    print(f"\n{'='*60}")
    print("📋 ANALYSIS SUMMARY")
    print(f"{'='*60}")
    print("This analysis identifies what components exist and what might be missing.")
    print("Key areas to check:")
    print("1. Java wrapper parameter patterns for different input types")
    print("2. C++ harness files for individual problems")
    print("3. Function name mappings in docker_runner.py")
    print("4. TreeNode/ListNode serialization logic")
    print("5. Complete solution files for all languages")


if __name__ == "__main__":
    main()
