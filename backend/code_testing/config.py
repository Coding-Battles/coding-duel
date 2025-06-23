"""
Configuration for code testing module.
"""
import os

# Performance settings
USE_PERSISTENT_CONTAINERS = os.getenv("USE_PERSISTENT_CONTAINERS", "true").lower() == "true"  # Enabled by default for 50x speed improvement
# To disable persistent containers: export USE_PERSISTENT_CONTAINERS=false
CONTAINER_STARTUP_TIMEOUT = int(os.getenv("CONTAINER_STARTUP_TIMEOUT", "30"))  # seconds
CONTAINER_HEALTH_CHECK_INTERVAL = int(os.getenv("CONTAINER_HEALTH_CHECK_INTERVAL", "60"))  # seconds

# Security settings
ENABLE_NETWORK_ACCESS = os.getenv("ENABLE_NETWORK_ACCESS", "false").lower() == "true"
EXECUTION_TIMEOUT = int(os.getenv("EXECUTION_TIMEOUT", "10"))  # seconds

# Resource limits (optimized for persistent containers)
JAVA_MEMORY_LIMIT = os.getenv("JAVA_MEMORY_LIMIT", "128m")
PYTHON_MEMORY_LIMIT = os.getenv("PYTHON_MEMORY_LIMIT", "64m")
CPP_MEMORY_LIMIT = os.getenv("CPP_MEMORY_LIMIT", "128m")
NODE_MEMORY_LIMIT = os.getenv("NODE_MEMORY_LIMIT", "64m")
DEFAULT_CPU_LIMIT = int(os.getenv("DEFAULT_CPU_LIMIT", "500000000"))  # 0.5 CPU core

# Debug settings
DEBUG_CONTAINER_LOGS = os.getenv("DEBUG_CONTAINER_LOGS", "false").lower() == "true"