#!/usr/bin/env python3

import requests
import json


def test_edit_distance():
    """Test edit-distance API with all language solutions"""

    languages = {
        "python": "/Users/andriysapeha/Documents/coding_duel/coding-duel/backend/test-solutions/edit-distance.py",
        "javascript": "/Users/andriysapeha/Documents/coding_duel/coding-duel/backend/test-solutions/edit-distance.js",
        "java": "/Users/andriysapeha/Documents/coding_duel/coding-duel/backend/test-solutions/edit-distance.java",
        "cpp": "/Users/andriysapeha/Documents/coding_duel/coding-duel/backend/test-solutions/edit-distance.cpp",
    }

    for language, file_path in languages.items():
        print(f"\n{'='*50}")
        print(f"Testing EDIT DISTANCE - {language.upper()}")
        print(f"{'='*50}")

        try:
            with open(file_path, "r") as f:
                code = f.read()

            payload = {
                "player_id": "test_player",
                "code": code,
                "language": language,
                "question_name": "edit-distance",
                "timer": 300,
            }

            response = requests.post(
                "http://localhost:8000/api/edit-distance/test-sample",
                json=payload,
                timeout=30,
            )

            print(f"Response status: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                print(f"Success: {result.get('success', False)}")
                print(f"Total passed: {result.get('total_passed', 0)}")
                print(f"Total failed: {result.get('total_failed', 0)}")

                if result.get("test_results"):
                    for i, test in enumerate(result["test_results"]):
                        expected = test.get("expected_output", "N/A")
                        actual = test.get("actual_output", "N/A")
                        passed = test.get("passed", False)

                        print(f"\nTest {i+1}: {'✅' if passed else '❌'}")
                        print(f"  Input: {test.get('input', 'N/A')}")
                        print(f"  Expected: {expected}")
                        print(f"  Actual:   {actual}")

                        if test.get("error"):
                            print(f"  Error: {test['error']}")
            else:
                print(f"Error: {response.text}")

        except FileNotFoundError:
            print(f"❌ Solution file not found: {file_path}")
        except Exception as e:
            print(f"❌ Error: {e}")


if __name__ == "__main__":
    test_edit_distance()
