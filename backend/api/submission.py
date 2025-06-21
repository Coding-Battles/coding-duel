from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
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
    execute_code_with_test_cases,
)
from fastapi import Body

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


class TimeComplexity(BaseModel):
    code: str


class TimeComplexityResponse(BaseModel):
    time_complexity: str


class CodeSubmission(BaseModel):
    question_name: str
    code: str
    language: str


class SubmissionResult(BaseModel):
    is_correct: bool
    passed: int
    total: int
    failed_tests: List[Dict[str, Any]]


class TestCaseResult(BaseModel):
    input: Dict[str, Any]
    expected_output: Any
    actual_output: Optional[str]
    passed: bool
    error: Optional[str]
    execution_time: Optional[float]


LANGUAGE_CONFIG = {
    "python": {
        "image": "python:3.9-slim",
        "file_extension": ".py",
        "run_command": "python {filename}",
        "wrapper_template": """
import sys
import json
import time

def main():
    # User code starts here
{code}
    # User code ends here

if __name__ == "__main__":
    input_data = json.loads(sys.argv[1])
    start_time = time.time()
    
    # Create variables from input
    for key, value in input_data.items():
        globals()[key] = value
    
    # Execute the solution function (assuming it's named 'solution' or the first function defined)
    result = None
    for name, obj in globals().items():
        if callable(obj) and not name.startswith('__'):
            result = obj(**input_data)
            break
    
    end_time = time.time()
    execution_time = (end_time - start_time) * 1000
    
    print(json.dumps({
        "result": result,
        "execution_time": execution_time
    }))
""",
    },
    "javascript": {
        "image": "node:16-slim",
        "file_extension": ".js",
        "run_command": "node {filename}",
        "wrapper_template": """
const inputData = JSON.parse(process.argv[2]);
const startTime = process.hrtime.bigint();

// User code starts here
{code}
// User code ends here

const functionNames = Object.keys(global).filter(key => typeof global[key] === 'function');
let result = null;

if (functionNames.length > 0) {{
    const mainFunction = global[functionNames[0]];
    result = mainFunction(...Object.values(inputData));
}}

const endTime = process.hrtime.bigint();
const executionTime = Number(endTime - startTime) / 1000000;

console.log(JSON.stringify({{
    result: result,
    execution_time: executionTime
}}));
""",
    },
}


@app.post("/submit", response_model=SubmissionResult)
async def submit_code(submission: CodeSubmission):
    """Submit code for a specific question and run all tests."""
    if not docker_available:
        raise HTTPException(
            status_code=503,
            detail="Docker is not available. Please install and start Docker Desktop.",
        )

    try:
        # Load test cases from JSON file
        test_file_path = f"backend/tests/{submission.question_name}.json"
        with open(test_file_path, "r") as f:
            test_cases = json.load(f)

        # Run all test cases
        loop = asyncio.get_event_loop()
        tasks = []

        for test_case in test_cases:
            task = loop.run_in_executor(
                executor,
                run_code_in_docker,
                submission.code,
                submission.language,
                test_case["input"],
                5,  # timeout
            )
            tasks.append((task, test_case))

        # Collect results
        passed = 0
        failed = 0
        failed_tests = []

        for task, test_case in tasks:
            result = await task

            expected = test_case["expected"]
            actual = result.get("output")

            if result["success"] and actual == expected:
                passed += 1
            else:
                failed += 1
                failed_tests.append(
                    {
                        "input": test_case["input"],
                        "expected": expected,
                        "actual": actual,
                        "error": result.get("error"),
                    }
                )

        return SubmissionResult(
            is_correct=failed == 0,
            passed=passed,
            total=len(test_cases),
            failed_tests=failed_tests,
        )

    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"Test file not found for question: {submission.question_name}",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error running tests: {str(e)}")


class CodeExecutionRequest(BaseModel):
    code: str
    language: str
    test_cases: List[Dict[str, Any]]
    timeout: Optional[int] = 5


class CodeExecutionResponse(BaseModel):
    success: bool
    test_results: List[TestCaseResult]
    total_passed: int
    total_failed: int
    error: Optional[str]


@app.post("/execute", response_model=CodeExecutionResponse)
async def execute_code(request: CodeExecutionRequest):
    """Execute code with custom test cases."""
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
        # Use the new function from docker_runner
        result = execute_code_with_test_cases(
            code=request.code,
            language=request.language,
            test_cases=request.test_cases,
            timeout=request.timeout or 5,
        )
        return CodeExecutionResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error executing code: {str(e)}")


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


class DockerRunRequest(BaseModel):
    code: str
    language: str
    test_input: dict
    timeout: int = 5


@app.post("/docker-run")
async def docker_run(request: DockerRunRequest = Body(...)):
    """Run code in Docker using the extracted utility."""
    try:
        result = run_code_in_docker(
            code=request.code,
            language=request.language,
            test_input=request.test_input,
            timeout=request.timeout,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
