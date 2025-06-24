# This file marks the code_testing directory as a Python package.
"""
Code testing module with fast Docker-based execution.
"""
import atexit


def _cleanup():
    """Cleanup function to shutdown Docker containers on exit."""
    try:
        from backend.code_testing.docker_runner import cleanup_containers

        cleanup_containers()
    except:
        pass


# Register cleanup function
atexit.register(_cleanup)
