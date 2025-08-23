#!/usr/bin/env python3

import requests
import json


def test_tree_problems():
    """Test tree problems to see what's failing"""

    tree_problems = ["invert-binary-tree", "same-tree"]
    languages = ["python", "javascript", "java", "cpp"]

    for problem in tree_problems:
        print(f"\n{'='*60}")
        print(f"Testing {problem.upper()}")
        print(f"{'='*60}")

        for language in languages:
            try:
                extension = "js" if language == "javascript" else language
                file_path = f"/Users/andriysapeha/Documents/coding_duel/coding-duel/backend/test-solutions/{problem}.{extension}"

                with open(file_path, "r") as f:
                    code = f.read()

                payload = {
                    "player_id": "test_player",
                    "code": code,
                    "language": language,
                    "question_name": problem,
                    "timer": 300,
                }

                response = requests.post(
                    f"http://localhost:8000/api/{problem}/test-sample",
                    json=payload,
                    timeout=30,
                )

                print(f"\n--- {language.upper()} ---")
                print(f"Status: {response.status_code}")

                if response.status_code == 200:
                    result = response.json()
                    print(f"Success: {result.get('success', False)}")
                    print(
                        f"Passed: {result.get('total_passed', 0)}/{result.get('total_passed', 0) + result.get('total_failed', 0)}"
                    )

                    # Show first failure if any
                    if result.get("test_results"):
                        failed = [
                            t
                            for t in result["test_results"]
                            if not t.get("passed", False)
                        ]
                        if failed:
                            print(f"First failure:")
                            print(f"  Input: {failed[0].get('input', 'N/A')}")
                            print(
                                f"  Expected: {failed[0].get('expected_output', 'N/A')}"
                            )
                            print(f"  Actual: {failed[0].get('actual_output', 'N/A')}")
                            if failed[0].get("error"):
                                print(f"  Error: {failed[0]['error']}")
                else:
                    print(f"Error: {response.text}")

            except FileNotFoundError:
                print(f"--- {language.upper()} ---")
                print(f"❌ Solution file not found")
            except Exception as e:
                print(f"--- {language.upper()} ---")
                print(f"❌ Error: {e}")


if __name__ == "__main__":
    test_tree_problems()
