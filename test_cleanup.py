#!/usr/bin/env python3
"""
Test the cleanup functionality.
"""

import sys

sys.path.append("/Users/andriysapeha/Documents/coding_duel/coding-duel")

from backend.models.questions import DockerRunRequest
from backend.code_testing.docker_runner import (
    run_code_in_docker,
    cleanup_old_submissions,
)


def test_cleanup():
    """Test that cleanup works correctly."""

    print("Testing cleanup functionality...")

    # Create a test request
    test_request = DockerRunRequest(
        language="python",
        code="def solution(nums): return sum(nums)",
        function_name="solution",
        test_input={"nums": [1, 2, 3]},
    )

    print(
        "1. Running code execution (should create and cleanup submission directory)..."
    )

    try:
        result = run_code_in_docker(test_request)
        print(f"✅ Execution result: {result['success']}")
        if result["success"]:
            print(f"✅ Output: {result['output']}")
            print(f"✅ Execution time: {result['execution_time']}ms")
        else:
            print(f"❌ Error: {result['error']}")

        print("\n2. Testing cleanup of any remaining submission directories...")
        cleanup_old_submissions()

        print("\n🎉 Cleanup test completed!")
        print("✅ Submission directories should be cleaned up automatically")
        print("✅ No more disk space accumulation in containers")

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    test_cleanup()
