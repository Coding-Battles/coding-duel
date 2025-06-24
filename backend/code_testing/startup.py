#!/usr/bin/env python3
"""
Startup script to initialize persistent containers for fast code execution.
Run this once when your server starts to pre-pull images and warm up containers.
"""
import docker
import time
import logging
from backend.code_testing.language_config import LANGUAGE_CONFIG

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def pull_all_images():
    """Pre-pull all required Docker images."""
    client = docker.from_env()

    logger.info("Pre-pulling Docker images for fast execution...")

    for language, config in LANGUAGE_CONFIG.items():
        image = config["image"]
        logger.info(f"Pulling {image} for {language}...")

        try:
            start_time = time.time()
            client.images.pull(image)
            pull_time = time.time() - start_time
            logger.info(f"✅ Pulled {image} in {pull_time:.1f}s")
        except Exception as e:
            logger.error(f"❌ Failed to pull {image}: {e}")


def warm_up_containers():
    """Create initial containers to warm up the system."""
    from backend.code_testing.docker_runner import get_persistent_container

    logger.info("Warming up persistent containers...")

    for language in LANGUAGE_CONFIG.keys():
        try:
            start_time = time.time()
            container = get_persistent_container(language)
            warmup_time = time.time() - start_time

            # Test container is responsive
            result = container.exec_run("echo 'warmup test'")
            if result.exit_code == 0:
                logger.info(f"✅ {language} container ready in {warmup_time:.1f}s")
            else:
                logger.warning(f"⚠️ {language} container unresponsive")

        except Exception as e:
            logger.error(f"❌ Failed to warm up {language} container: {e}")


def test_execution():
    """Test execution with each language to verify everything works."""
    from backend.models.questions import DockerRunRequest
    from backend.code_testing.docker_runner import run_code_in_docker

    logger.info("Testing code execution...")

    test_cases = {
        "python": {
            "code": "def solution(nums, target):\n    return [0, 1]",
            "test_input": {"nums": [2, 7], "target": 9},
        },
        "java": {
            "code": "class Solution { public int[] solution(int[] nums, int target) { return new int[]{0, 1}; } }",
            "test_input": {"nums": [2, 7], "target": 9},
        },
        "javascript": {
            "code": "function solution(nums, target) { return [0, 1]; }",
            "test_input": {"nums": [2, 7], "target": 9},
        },
        "cpp": {
            "code": "vector<int> solution(vector<int> nums, int target) { return {0, 1}; }",
            "test_input": {"nums": [2, 7], "target": 9},
        },
    }

    for language, test_data in test_cases.items():
        try:
            request = DockerRunRequest(
                code=test_data["code"],
                language=language,
                test_input=test_data["test_input"],
                timeout=5,
            )

            start_time = time.time()
            result = run_code_in_docker(request)
            execution_time = time.time() - start_time

            if result.get("success"):
                logger.info(f"✅ {language} test passed in {execution_time:.3f}s")
            else:
                logger.warning(f"⚠️ {language} test failed: {result.get('error')}")

        except Exception as e:
            logger.error(f"❌ {language} test error: {e}")


def main():
    """Main startup sequence."""
    logger.info("🚀 Starting code execution system initialization...")

    start_time = time.time()

    # Step 1: Pull all images
    pull_all_images()

    # Step 2: Create and warm up containers
    warm_up_containers()

    # Step 3: Test execution
    test_execution()

    total_time = time.time() - start_time
    logger.info(f"🎉 Initialization complete in {total_time:.1f}s")
    logger.info("System ready for sub-second code execution!")


if __name__ == "__main__":
    main()
