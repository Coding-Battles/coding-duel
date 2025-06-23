# This file marks the code_testing directory as a Python package.
"""
Code testing module with fast container pool execution.
"""
import atexit

def _cleanup():
    """Cleanup function to shutdown container pool and ultra-fast runner on exit."""
    try:
        from backend.code_testing.container_pool import shutdown_pool
        shutdown_pool()
    except:
        pass
    
    try:
        from backend.code_testing.ultra_fast_runner import shutdown_ultra_fast
        shutdown_ultra_fast()
    except:
        pass

# Register cleanup function
atexit.register(_cleanup)
