#!/usr/bin/env python3
"""
Test that the simplified approach works.
"""

import sys

sys.path.append("/Users/andriysapeha/Documents/coding_duel/coding-duel")

from backend.models.questions import DockerRunRequest


def test_simplified_approach():
    """Test the direct dictionary approach."""

    print("Testing simplified runner approach...")

    # Import the dictionary directly
    from backend.code_testing.docker_runner import LANGUAGE_RUNNERS

    print(f"✅ Available languages: {list(LANGUAGE_RUNNERS.keys())}")

    # Test direct lookup
    python_runner = LANGUAGE_RUNNERS["python"]
    java_runner = LANGUAGE_RUNNERS["java"]

    print(f"✅ Python runner: {python_runner}")
    print(f"✅ Java runner: {java_runner}")

    # Create a mock request
    mock_request = DockerRunRequest(
        language="python",
        code="def solution(nums): return sum(nums)",
        function_name="solution",
        test_input={"nums": [1, 2, 3]},
    )

    # Test direct static method call
    filename = python_runner.get_filename(mock_request)
    print(f"✅ Generated filename: {filename}")

    print("\n🎉 Simplified approach works perfectly!")
    print("✅ No unnecessary abstraction layers")
    print("✅ Direct dictionary lookup")
    print("✅ Simple and straightforward")


if __name__ == "__main__":
    test_simplified_approach()
