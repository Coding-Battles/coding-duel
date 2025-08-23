#!/usr/bin/env python3

import requests
import json


def test_alien_dictionary_languages():
    """Test alien-dictionary API with all language solutions"""

    languages = {
        "python": "/Users/andriysapeha/Documents/coding_duel/coding-duel/backend/test-solutions/alien-dictionary.py",
        "javascript": "/Users/andriysapeha/Documents/coding_duel/coding-duel/backend/test-solutions/alien-dictionary.js",
        "java": "/Users/andriysapeha/Documents/coding_duel/coding-duel/backend/test-solutions/alien-dictionary.java",
        "cpp": "/Users/andriysapeha/Documents/coding_duel/coding-duel/backend/test-solutions/alien-dictionary.cpp",
    }

    for language, file_path in languages.items():
        print(f"\n{'='*50}")
        print(f"Testing {language.upper()}")
        print(f"{'='*50}")

        try:
            with open(file_path, "r") as f:
                code = f.read()

            payload = {
                "player_id": "test_player",
                "code": code,
                "language": language,
                "question_name": "alien-dictionary",
                "timer": 300,
            }

            response = requests.post(
                "http://localhost:8000/api/alien-dictionary/test-sample",
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
                        print(f"  Expected: '{expected}' (len={len(str(expected))})")
                        print(f"  Actual:   '{actual}' (len={len(str(actual))})")

                        if not passed and expected != actual:
                            print(
                                f"  Expected bytes: {[ord(c) for c in str(expected)]}"
                            )
                            print(f"  Actual bytes:   {[ord(c) for c in str(actual)]}")
            else:
                print(f"Error: {response.text}")

        except FileNotFoundError:
            print(f"❌ Solution file not found: {file_path}")
        except Exception as e:
            print(f"❌ Error: {e}")


if __name__ == "__main__":
    test_alien_dictionary_languages()
