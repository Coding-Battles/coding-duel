from fastapi import FastAPI, HTTPException
from typing import List, Optional, Dict, Any
from contextlib import asynccontextmanager
from groq import Groq
import os
import docker
import asyncio
from concurrent.futures import ThreadPoolExecutor
import logging
import json
from pathlib import Path
from dotenv import load_dotenv
from backend.code_testing.ai_complexity_analyzer import analyze_time_complexity_ai
from backend.code_testing.docker_runner import (
    run_code_in_docker,
    cleanup_persistent_containers,
)
from fastapi import Body
from backend.models.questions import (
    TimeComplexity,
    TimeComplexityResponse,
    RunTestCasesRequest,
    RunTestCasesResponse,
    DockerRunRequest,
    QuestionData,
)
from backend.services.test_execution_service import TestExecutionService

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
# Try multiple possible locations
from pathlib import Path

# Find .env file
env_path = Path(".env")
if not env_path.exists():
    # Try parent directory
    env_path = Path("../.env")
    if not env_path.exists():
        # Try backend directory
        env_path = Path("backend/.env")

if env_path.exists():
    load_dotenv(env_path)
    print(f"Loaded .env from: {env_path.absolute()}")
else:
    print("WARNING: .env file not found!")
    load_dotenv()  # Try to load from system environment


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Manage the lifespan of the FastAPI application."""
    # Startup
    logger.info("🚀 Initializing persistent containers for fast code execution...")

    try:
        # Import initialization functions
        from backend.code_testing.startup import pull_all_images, warm_up_containers

        # Run initialization in thread pool to avoid blocking
        loop = asyncio.get_event_loop()

        # Pre-pull all images
        logger.info("📦 Pre-pulling Docker images...")
        await loop.run_in_executor(executor, pull_all_images)

        # Warm up containers
        logger.info("🔥 Warming up persistent containers...")
        await loop.run_in_executor(executor, warm_up_containers)

        logger.info(
            "✅ Persistent containers ready! Code execution will now be sub-second."
        )

    except Exception as e:
        logger.error(f"❌ Failed to initialize persistent containers: {e}")
        logger.warning("⚠️ Falling back to traditional Docker execution (slower)")

    yield  # Application runs here

    # Shutdown
    logger.info("🧹 Cleaning up persistent containers...")

    try:
        cleanup_persistent_containers()
        logger.info("✅ Containers cleaned up successfully")
    except Exception as e:
        logger.error(f"❌ Error during container cleanup: {e}")


# FastAPI application with lifespan management
app = FastAPI(lifespan=lifespan)


# Debug: Check if API key is loaded
groq_api_key = os.getenv("GROQ_API_KEY")
if not groq_api_key:
    print("WARNING: GROQ_API_KEY not found in environment variables")
else:
    print(f"GROQ API key loaded: {groq_api_key[:8]}...{groq_api_key[-4:]}")

client = Groq(api_key=groq_api_key)

# Initialize Docker client with error handling
try:
    docker_client = docker.from_env()
    docker_available = True
    print("Docker connected successfully")
except docker.errors.DockerException as e:
    docker_available = False
    print(f"Warning: Docker not available - {e}")
    print("Code execution features will not work without Docker")

executor = ThreadPoolExecutor(max_workers=5)


@app.post("/run-test-cases", response_model=RunTestCasesResponse)
async def run_test_cases(request: RunTestCasesRequest):
    """Execute code with test cases loaded from file based on question name."""
    if not docker_available:
        raise HTTPException(
            status_code=503,
            detail="Docker is not available. Please install and start Docker Desktop.",
        )

    try:
        return TestExecutionService.execute_test_cases(request)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in /run-test-cases: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.post("/analyze-complexity", response_model=TimeComplexityResponse)
async def analyze_time_complexity(request: TimeComplexity):
    """Analyze the time complexity of the provided code."""
    try:
        time_complexity = analyze_time_complexity_ai(request.code)
        return TimeComplexityResponse(time_complexity=time_complexity)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """Check if the service is healthy and Docker is available."""
    return {
        "status": "healthy",
        "docker_available": docker_available,
        "docker_status": "connected" if docker_available else "not connected",
    }


@app.post("/docker-run")
async def docker_run(request: DockerRunRequest = Body(...)):
    """Run code in Docker using the extracted utility."""
    try:
        result = run_code_in_docker(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/debug-run")
async def debug_run():
    """Quick debug endpoint to test persistent containers directly."""
    import time

    start_time = time.time()
    logger.info("🐛 [DEBUG] Starting debug-run test")

    try:
        # Simple test for each language
        test_request = DockerRunRequest(
            code="def solution(nums, target):\n    return [0, 1]",
            language="python",
            test_input={"nums": [2, 7], "target": 9},
            timeout=5,
        )

        result = run_code_in_docker(test_request)
        total_time = (time.time() - start_time) * 1000

        logger.info(f"🐛 [DEBUG] debug-run completed in {total_time:.0f}ms")

        return {
            "success": result.get("success"),
            "output": result.get("output"),
            "execution_time": result.get("execution_time"),
            "total_time_ms": total_time,
            "error": result.get("error"),
        }

    except Exception as e:
        total_time = (time.time() - start_time) * 1000
        logger.error(f"🐛 [DEBUG] debug-run failed after {total_time:.0f}ms: {str(e)}")
        return {"success": False, "error": str(e), "total_time_ms": total_time}


@app.get("/get-question/{question_name}", response_model=QuestionData)
async def get_question(question_name: str):
    """Get question data by question name from the question-data directory."""
    try:
        # Construct file path
        question_file_path = Path(f"backend/data/question-data/{question_name}.json")

        # Check if file exists
        if not question_file_path.exists():
            raise HTTPException(
                status_code=404, detail=f"Question '{question_name}' not found"
            )

        # Read and parse JSON file
        with open(question_file_path, "r", encoding="utf-8") as file:
            question_data = json.load(file)

        return QuestionData(**question_data)

    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in question file {question_name}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Invalid question data format for '{question_name}'",
        )
    except Exception as e:
        logger.error(f"Error loading question {question_name}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error loading question '{question_name}'",
        )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
