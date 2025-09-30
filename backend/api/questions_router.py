from fastapi import APIRouter, HTTPException, Body, UploadFile, File
from typing import List, Optional, Dict, Any
import json
from pathlib import Path
import logging
import shutil
import os
import databases
from backend.models.questions import (
    TimeComplexity,
    TimeComplexityResponse,
    RunTestCasesRequest,
    RunTestCasesResponse,
    DockerRunRequest,
    CodeTestResult
)
from backend.models.core.question import QuestionData
from backend.services.test_execution_service import TestExecutionService
from backend.code_testing.ai_complexity_analyzer import analyze_time_complexity_ai
from backend.code_testing.docker_runner import run_code_in_docker

router = APIRouter()
logger = logging.getLogger(__name__)

# This will be injected from main.py
database = None

def get_file_name_from_slug(slug: str) -> str:
    """Return slug as file name since they are now the same."""
    return slug

@router.get("/questions")
async def get_all_questions():
    """Get all available questions organized by difficulty."""
    try:
        questions_file_path = Path("backend/data/questions.json")
        
        if not questions_file_path.exists():
            raise HTTPException(status_code=404, detail="Questions data not found")
            
        with open(questions_file_path, "r", encoding="utf-8") as file:
            questions_data = json.load(file)
        return questions_data
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in questions file: {str(e)}")
        raise HTTPException(status_code=500, detail="Invalid questions data format")
    except Exception as e:
        logger.error(f"Error loading questions: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error loading questions")

@router.get("/get-question/{question_slug}", response_model=QuestionData)
async def get_question(question_slug: str):
    try:
        # Map slug to file_name
        file_name = get_file_name_from_slug(question_slug)
        question_file_path = Path(f"backend/data/question-data/{file_name}.json")
        
        if not question_file_path.exists():
            raise HTTPException(status_code=404, detail=f"Question '{question_slug}' not found")
        with open(question_file_path, "r", encoding="utf-8") as file:
            question_data = json.load(file)
        return QuestionData(**question_data)
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in question file {question_slug}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Invalid question data format for '{question_slug}'")
    except Exception as e:
        logger.error(f"Error loading question {question_slug}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error loading question '{question_slug}'")

@router.get("/user/{user_id}/game-history")
async def get_user_game_history(user_id: str):
    try:
        query = """
            SELECT g.id AS game_id,
                    g.question_name as question_name,
                     g.difficulty as difficulty,
                    gp.user_id,
                   g.created_at,
                   gp.player_name,
                   gp.implement_time,
                   gp.time_complexity,
                   gp.final_time,
                     gp.player_code
            FROM "user" u
            CROSS JOIN LATERAL unnest(u.game_ids) AS user_game_id
            JOIN games g ON g.id = user_game_id
            JOIN game_participants gp ON gp.game_id = g.id
            WHERE u.id = :user_id
            ORDER BY g.created_at DESC
        """
        values = {"user_id": user_id}
        results = await database.fetch_all(query=query, values=values)
        
        results_list = [dict(result) for result in results]
        
        return {
            "games": results_list,
            "total_count": len(results_list)
        }
    except Exception as e:
        logger.error(f"Error fetching game history for user {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/run-sample-tests", response_model=RunTestCasesResponse)
async def run_sample_tests(request: RunTestCasesRequest):
    try:
        return TestExecutionService.execute_sample_test_cases(request)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in /run-sample-tests: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/{question_slug}/test", response_model=RunTestCasesResponse)
async def test_question(question_slug: str, request: RunTestCasesRequest):
    """Test individual question with either sample tests or full test suite."""
    try:
        # Override question_name with the slug from URL
        request.question_name = question_slug
        
        # Check if this is a sample test request (first 3 tests only)
        # This can be determined by a query parameter or request field
        return TestExecutionService.execute_test_cases(request)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in /test-question: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/{question_slug}/test-sample", response_model=RunTestCasesResponse)
async def test_question_sample(question_slug: str, request: RunTestCasesRequest):
    """Test individual question with sample tests only (first 3 test cases)."""
    try:
        # Override question_name with the slug from URL
        request.question_name = question_slug
        
        return TestExecutionService.execute_sample_test_cases(request)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in /test-question-sample: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/analyze-complexity", response_model=TimeComplexityResponse)
async def analyze_time_complexity(request: TimeComplexity):
    try:
        time_complexity = analyze_time_complexity_ai(request.code)
        return TimeComplexityResponse(time_complexity=time_complexity)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check():
    # Docker availability check would need to be imported from main
    return {
        "status": "healthy",
        "docker_available": True,  # This should be passed from main
        "docker_status": "connected",
    }

@router.post("/docker-run")
async def docker_run(request: DockerRunRequest = Body(...)):
    try:
        result = run_code_in_docker(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/debug-run")
async def debug_run():
    import time
    start_time = time.time()
    logger.info("|api/questions_router| [DEBUG] Starting debug-run test")
    try:
        test_request = DockerRunRequest(
            code="def solution(nums, target):\n    return [0, 1]",
            language="python",
            test_input={"nums": [2, 7], "target": 9},
            timeout=5,
        )
        result = run_code_in_docker(test_request)
        total_time = (time.time() - start_time) * 1000
        logger.info(f"|api/questions_router| [DEBUG] debug-run completed in {total_time:.0f}ms")
        return {
            "success": result.get("success"),
            "output": result.get("output"),
            "execution_time": result.get("execution_time"),
            "total_time_ms": total_time,
            "error": result.get("error"),
        }
    except Exception as e:
        total_time = (time.time() - start_time) * 1000
        logger.error(f"|api/questions_router| [DEBUG] debug-run failed after {total_time:.0f}ms: {str(e)}")
        return {"success": False, "error": str(e), "total_time_ms": total_time}


def set_database(db):
    """Set the database instance from main.py"""
    global database
    database = db