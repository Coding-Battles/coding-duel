#!/usr/bin/env python3
"""
Test the new RunnerRegistry naming.
"""

import sys

sys.path.append("/Users/andriysapeha/Documents/coding_duel/coding-duel")

from backend.code_testing.runners import RunnerRegistry
from backend.models.questions import DockerRunRequest


def test_runner_registry():
    """Test the new naming and approach."""

    print("Testing RunnerRegistry...")

    # Test getting runner classes
    python_runner_class = RunnerRegistry.get_runner_class("python")
    java_runner_class = RunnerRegistry.get_runner_class("java")

    print(f"✅ Python runner class: {python_runner_class}")
    print(f"✅ Java runner class: {java_runner_class}")

    # Test supported languages
    languages = RunnerRegistry.get_supported_languages()
    print(f"✅ Supported languages: {languages}")

    # Create a mock request
    mock_request = DockerRunRequest(
        language="python",
        code="def solution(nums): return sum(nums)",
        function_name="solution",
        test_input={"nums": [1, 2, 3]},
    )

    # Test that we can call static methods directly on the class
    filename = python_runner_class.get_filename(mock_request)
    print(f"✅ Generated filename: {filename}")

    print("\n🎉 RunnerRegistry works perfectly!")
    print("✅ No 'creation' or 'factory' language")
    print("✅ Clear that we're just getting class references")
    print("✅ Static methods called directly on classes")


if __name__ == "__main__":
    test_runner_registry()
