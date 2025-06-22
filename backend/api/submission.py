from fastapi import FastAPI, HTTPException
from typing import List, Optional, Dict, Any
from groq import Groq
import os
import docker
import tempfile
import asyncio
from concurrent.futures import ThreadPoolExecutor
import json
from dotenv import load_dotenv
from backend.code_testing.ai_complexity_analyzer import analyze_time_complexity_ai
from backend.code_testing.docker_runner import (
    run_code_in_docker,
)
from fastapi import Body
from backend.models.submission import (
    TimeComplexity,
    TimeComplexityResponse,
    TestCaseResult,
    RunTestCasesRequest,
    RunTestCasesResponse,
    DockerRunRequest,
)
from backend.code_testing.language_config import LANGUAGE_CONFIG

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

# FastAPI application
app = FastAPI()

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


def normalize_answer(answer):
    """Normalize answer to handle different formats (list vs string)."""
    if isinstance(answer, str):
        # Handle string format like "[0, 1]"
        try:
            import ast

            return ast.literal_eval(answer)
        except:
            return answer
    return answer


def check_answer_in_expected(actual, expected_list):
    """Check if the actual answer matches any of the expected answers."""
    actual_normalized = normalize_answer(actual)

    # If expected is a single answer (old format), convert to list
    if not isinstance(expected_list[0], list):
        expected_list = [expected_list]

    for expected in expected_list:
        if actual_normalized == expected:
            return True

    return False


@app.post("/run-test-cases", response_model=RunTestCasesResponse)
async def run_test_cases(request: RunTestCasesRequest):
    """Execute code with test cases loaded from file based on question name."""
    if not docker_available:
        raise HTTPException(
            status_code=503,
            detail="Docker is not available. Please install and start Docker Desktop.",
        )

    try:
        if request.language not in LANGUAGE_CONFIG:
            raise HTTPException(
                status_code=400, detail=f"Unsupported language: {request.language}"
            )

        # Load test cases from JSON file based on question name
        test_file_path = f"backend/tests/{request.question_name}.json"
        try:
            with open(test_file_path, "r") as f:
                test_cases = json.load(f)
        except FileNotFoundError:
            raise HTTPException(
                status_code=404,
                detail=f"Test file not found for question: {request.question_name}",
            )

        test_results = []
        total_passed = 0
        total_failed = 0

        for test_case in test_cases:
            try:
                # Run the code in docker using run_code_in_docker
                docker_result = run_code_in_docker(
                    DockerRunRequest(
                        code=request.code,
                        language=request.language,
                        test_input=test_case["input"],
                        timeout=request.timeout,
                    )
                )

                # Parse the result
                expected = test_case["expected"]
                actual_output = docker_result.get("output")

                # Check if actual output matches any of the expected answers
                if docker_result.get("success", False):
                    passed = check_answer_in_expected(actual_output, expected)
                else:
                    passed = False

                test_result = TestCaseResult(
                    input=test_case["input"],
                    expected_output=expected,
                    actual_output=(
                        str(actual_output) if actual_output is not None else None
                    ),
                    passed=passed,
                    error=docker_result.get("error"),
                    execution_time=docker_result.get("execution_time"),
                )

                test_results.append(test_result)

                if passed:
                    total_passed += 1
                else:
                    total_failed += 1

            except Exception as e:
                # Handle individual test case failure
                test_result = TestCaseResult(
                    input=test_case["input"],
                    expected_output=test_case["expected"],
                    actual_output=None,
                    passed=False,
                    error=str(e),
                    execution_time=None,
                )
                test_results.append(test_result)
                total_failed += 1

        return RunTestCasesResponse(
            success=total_failed == 0,
            test_results=test_results,
            total_passed=total_passed,
            total_failed=total_failed,
            error=None,
        )

    except HTTPException:
        raise
    except Exception as e:
        return RunTestCasesResponse(
            success=False,
            test_results=[],
            total_passed=0,
            total_failed=0,
            error=f"Error executing code: {str(e)}",
        )


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


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
