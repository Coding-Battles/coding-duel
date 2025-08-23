#!/usr/bin/env python3

import requests
import json


def test_alien_dictionary_cpp_full():
    """Test alien-dictionary API with C++ solution - FULL TESTS"""

    # Test with the C++ solution
    with open(
        "/Users/andriysapeha/Documents/coding_duel/coding-duel/backend/test-solutions/alien-dictionary.cpp",
        "r",
    ) as f:
        cpp_code = f.read()

    payload = {
        "player_id": "test_player",
        "code": cpp_code,
        "language": "cpp",
        "question_name": "alien-dictionary",
        "timer": 300,
    }

    try:
        # Test FULL submission
        response = requests.post(
            "http://localhost:8000/api/alien-dictionary/submit",
            json=payload,
            timeout=60,
        )

        print(f"Response status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Success: {result.get('success', False)}")
            print(f"Total passed: {result.get('total_passed', 0)}")
            print(f"Total failed: {result.get('total_failed', 0)}")

            if result.get("test_results"):
                # Show failed tests
                failed_tests = [
                    test
                    for test in result["test_results"]
                    if not test.get("passed", False)
                ]
                if failed_tests:
                    print(f"\n🚨 Found {len(failed_tests)} failed tests:")
                    for i, test in enumerate(failed_tests[:5]):  # Show first 5 failures
                        print(f"\n--- Failed Test {i+1} ---")
                        print(f"Input: {test.get('input', 'N/A')}")
                        print(f"Expected: '{test.get('expected_output', 'N/A')}'")
                        print(f"Actual: '{test.get('actual_output', 'N/A')}'")
                        if test.get("error"):
                            print(f"Error: {test['error']}")
                else:
                    print("✅ All tests passed!")
        else:
            print(f"Response: {response.text}")

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    test_alien_dictionary_cpp_full()
