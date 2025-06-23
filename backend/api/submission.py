from fastapi import FastAPI, HTTPException
from typing import List, Optional, Dict, Any
from contextlib import asynccontextmanager
from groq import Groq
import os
import docker
import tempfile
import asyncio
from concurrent.futures import ThreadPoolExecutor
import json
import logging
from dotenv import load_dotenv
from backend.code_testing.ai_complexity_analyzer import analyze_time_complexity_ai
from backend.code_testing.docker_runner import (
    run_code_in_docker,
    cleanup_persistent_containers,
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
        
        logger.info("✅ Persistent containers ready! Code execution will now be sub-second.")
        
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
    import time
    start_time = time.time()
    logger.info(f"🐛 [DEBUG] Starting /run-test-cases for {request.language} - {request.question_name}")
    
    if not docker_available:
        raise HTTPException(
            status_code=503,
            detail="Docker is not available. Please install and start Docker Desktop.",
        )

    try:
        step_time = time.time()
        if request.language not in LANGUAGE_CONFIG:
            raise HTTPException(
                status_code=400, detail=f"Unsupported language: {request.language}"
            )
        logger.info(f"🐛 [DEBUG] Language validation took {(time.time() - step_time)*1000:.0f}ms")

        # Load test cases from JSON file based on question name
        step_time = time.time()
        test_file_path = f"backend/tests/{request.question_name}.json"
        logger.info(f"🐛 [DEBUG] Looking for test file: {test_file_path}")
        try:
            with open(test_file_path, "r") as f:
                test_cases = json.load(f)
            logger.info(f"🐛 [DEBUG] Test file loading took {(time.time() - step_time)*1000:.0f}ms, found {len(test_cases)} test cases")
        except FileNotFoundError:
            logger.error(f"🐛 [DEBUG] Test file not found: {test_file_path}")
            raise HTTPException(
                status_code=404,
                detail=f"Test file not found for question: {request.question_name}",
            )

        test_results = []
        total_passed = 0
        total_failed = 0

        logger.info(f"🐛 [DEBUG] Starting execution of {len(test_cases)} test cases")
        
        # For Java and C++, batch execute all test cases to avoid compilation overhead
        if request.language == "java":
            try:
                batch_start_time = time.time()
                logger.info(f"🐛 [DEBUG] Using batch execution for Java")
                
                # Import the batch runner
                from backend.code_testing.java_batch_runner import run_java_batch
                
                batch_results = run_java_batch(request.code, test_cases, request.timeout)
                batch_time = (time.time() - batch_start_time) * 1000
                logger.info(f"🐛 [DEBUG] Java batch execution took {batch_time:.0f}ms for {len(test_cases)} test cases")
                
                # Process batch results
                for i, (test_case, result) in enumerate(zip(test_cases, batch_results)):
                    expected = test_case["expected"]
                    actual_output = result.get("output")
                    
                    if result.get("success", False):
                        passed = check_answer_in_expected(actual_output, expected)
                    else:
                        passed = False
                    
                    test_result = TestCaseResult(
                        input=test_case["input"],
                        expected_output=expected,
                        actual_output=str(actual_output) if actual_output is not None else None,
                        passed=passed,
                        error=result.get("error"),
                        execution_time=result.get("execution_time"),
                    )
                    
                    test_results.append(test_result)
                    
                    if passed:
                        total_passed += 1
                    else:
                        total_failed += 1
                        
            except Exception as e:
                logger.error(f"🐛 [DEBUG] Java batch execution failed: {str(e)}")
                # Fall back to individual execution
                logger.info(f"🐛 [DEBUG] Falling back to individual test case execution")
        
        elif request.language == "cpp":
            try:
                batch_start_time = time.time()
                logger.info(f"🐛 [DEBUG] Using batch execution for C++")
                
                # Import the batch runner
                from backend.code_testing.cpp_batch_runner import run_cpp_batch
                
                batch_results = run_cpp_batch(request.code, test_cases, request.timeout)
                batch_time = (time.time() - batch_start_time) * 1000
                logger.info(f"🐛 [DEBUG] C++ batch execution took {batch_time:.0f}ms for {len(test_cases)} test cases")
                
                # Process batch results
                for i, (test_case, result) in enumerate(zip(test_cases, batch_results)):
                    expected = test_case["expected"]
                    actual_output = result.get("output")
                    
                    if result.get("success", False):
                        passed = check_answer_in_expected(actual_output, expected)
                    else:
                        passed = False
                    
                    test_result = TestCaseResult(
                        input=test_case["input"],
                        expected_output=expected,
                        actual_output=str(actual_output) if actual_output is not None else None,
                        passed=passed,
                        error=result.get("error"),
                        execution_time=result.get("execution_time"),
                    )
                    
                    test_results.append(test_result)
                    
                    if passed:
                        total_passed += 1
                    else:
                        total_failed += 1
                        
            except Exception as e:
                logger.error(f"🐛 [DEBUG] C++ batch execution failed: {str(e)}")
                # Fall back to individual execution
                logger.info(f"🐛 [DEBUG] Falling back to individual test case execution")
                
                # Process batch results
                for i, (test_case, result) in enumerate(zip(test_cases, batch_results)):
                    expected = test_case["expected"]
                    actual_output = result.get("output")
                    
                    if result.get("success", False):
                        passed = check_answer_in_expected(actual_output, expected)
                    else:
                        passed = False
                    
                    test_result = TestCaseResult(
                        input=test_case["input"],
                        expected_output=expected,
                        actual_output=str(actual_output) if actual_output is not None else None,
                        passed=passed,
                        error=result.get("error"),
                        execution_time=result.get("execution_time"),
                    )
                    
                    test_results.append(test_result)
                    
                    if passed:
                        total_passed += 1
                    else:
                        total_failed += 1
                        
            except Exception as e:
                logger.error(f"🐛 [DEBUG] Java batch execution failed: {str(e)}")
                # Fall back to individual execution
                logger.info(f"🐛 [DEBUG] Falling back to individual test case execution")
        
        # For non-Java/C++ languages or fallback, run individual test cases
        if request.language not in ["java", "cpp"] or len(test_results) == 0:
            for i, test_case in enumerate(test_cases):
                logger.info(f"🐛 [DEBUG] Running test case {i+1}/{len(test_cases)}")
                try:
                    # Run the code in docker using run_code_in_docker
                    docker_start_time = time.time()
                    docker_result = run_code_in_docker(
                        DockerRunRequest(
                            code=request.code,
                            language=request.language,
                            test_input=test_case["input"],
                            timeout=request.timeout,
                        )
                    )
                    docker_time = (time.time() - docker_start_time) * 1000
                    logger.info(f"🐛 [DEBUG] Docker execution took {docker_time:.0f}ms for test case {i+1}")

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

        total_time = (time.time() - start_time) * 1000
        logger.info(f"🐛 [DEBUG] Total /run-test-cases execution time: {total_time:.0f}ms")
        
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
        total_time = (time.time() - start_time) * 1000
        logger.error(f"🐛 [DEBUG] Exception in /run-test-cases after {total_time:.0f}ms: {str(e)}")
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


@app.post("/debug-run")
async def debug_run():
    """Quick debug endpoint to test persistent containers directly."""
    import time
    start_time = time.time()
    logger.info("🐛 [DEBUG] Starting debug-run test")
    
    try:
        # Simple test for each language
        test_request = DockerRunRequest(
            code='def solution(nums, target):\n    return [0, 1]',
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
            "error": result.get("error")
        }
        
    except Exception as e:
        total_time = (time.time() - start_time) * 1000
        logger.error(f"🐛 [DEBUG] debug-run failed after {total_time:.0f}ms: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "total_time_ms": total_time
        }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
