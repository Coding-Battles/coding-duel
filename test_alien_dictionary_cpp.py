#!/usr/bin/env python3

import requests
import json


def test_alien_dictionary_cpp():
    """Test alien-dictionary API with C++ solution"""

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
                    print(f"\n--- Test {i+1} ---")
                    print(f"Input: {test.get('input', 'N/A')}")
                    print(f"Expected: {test.get('expected_output', 'N/A')}")
                    print(f"Actual: {test.get('actual_output', 'N/A')}")
                    print(f"Passed: {'✅' if test.get('passed', False) else '❌'}")
                    if test.get("error"):
                        print(f"Error: {test['error']}")
        else:
            print(f"Response: {response.text}")

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    test_alien_dictionary_cpp()
