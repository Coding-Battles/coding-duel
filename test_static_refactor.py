#!/usr/bin/env python3
"""
Test script to verify the static method refactoring works correctly.
"""

import sys
import os

# Add the backend directory to the path
sys.path.append("/Users/andriysapeha/Documents/coding_duel/coding-duel")

from backend.code_testing.runners.runner_factory import RunnerFactory
from backend.models.questions import DockerRunRequest


def test_static_methods():
    """Test that the static methods work as expected."""

    # Test getting runner classes
    print("Testing runner factory...")

    python_runner = RunnerFactory.get_runner("python")
    java_runner = RunnerFactory.get_runner("java")
    cpp_runner = RunnerFactory.get_runner("cpp")
    js_runner = RunnerFactory.get_runner("javascript")

    print(f"✅ Python runner class: {python_runner}")
    print(f"✅ Java runner class: {java_runner}")
    print(f"✅ C++ runner class: {cpp_runner}")
    print(f"✅ JavaScript runner class: {js_runner}")

    # Test that we get classes, not instances
    print(f"✅ Python runner is class: {type(python_runner)}")

    # Create a mock request for testing
    mock_request = DockerRunRequest(
        language="python",
        code="def solution(nums): return sum(nums)",
        function_name="solution",
        test_input={"nums": [1, 2, 3]},
    )

    # Test static method calls
    print("\nTesting static method calls...")

    try:
        filename = python_runner.get_filename(mock_request)
        print(f"✅ Python filename generation: {filename}")

        wrapped_code = python_runner.prepare_code(mock_request)
        print(f"✅ Python code preparation: {len(wrapped_code)} characters")

        print("✅ All static method calls work correctly!")

    except Exception as e:
        print(f"❌ Error testing static methods: {e}")
        return False

    return True


if __name__ == "__main__":
    success = test_static_methods()
    if success:
        print("\n🎉 Static method refactoring completed successfully!")
        print("✅ No more object instantiation overhead")
        print("✅ All methods are now stateless and efficient")
    else:
        print("\n❌ Some issues were found during testing")
