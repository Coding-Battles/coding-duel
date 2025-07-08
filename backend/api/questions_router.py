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
    QuestionData,
    CodeTestResult
)
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
        
        if not results:
            return {"message": "No game history found for this user."}

        return [dict(result) for result in results]
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
    logger.info("🔋 [DEBUG] Starting debug-run test")
    try:
        test_request = DockerRunRequest(
            code="def solution(nums, target):\n    return [0, 1]",
            language="python",
            test_input={"nums": [2, 7], "target": 9},
            timeout=5,
        )
        result = run_code_in_docker(test_request)
        total_time = (time.time() - start_time) * 1000
        logger.info(f"🔋 [DEBUG] debug-run completed in {total_time:.0f}ms")
        return {
            "success": result.get("success"),
            "output": result.get("output"),
            "execution_time": result.get("execution_time"),
            "total_time_ms": total_time,
            "error": result.get("error"),
        }
    except Exception as e:
        total_time = (time.time() - start_time) * 1000
        logger.error(f"🔋 [DEBUG] debug-run failed after {total_time:.0f}ms: {str(e)}")
        return {"success": False, "error": str(e), "total_time_ms": total_time}

@router.post("/image/{player_id}")
async def change_image(player_id: str, image: UploadFile = File(...)):
    # Save file
    os.makedirs("backend/uploads", exist_ok=True)
    filename = f"player_{player_id}_{image.filename}"
    file_path = f"backend/uploads/{filename}"
    public_url = f"http://localhost:8000/uploads/{filename}"

    with open(file_path, "wb") as f:
        shutil.copyfileobj(image.file, f)

    # Update DB using raw SQL
    query = 'UPDATE "user" SET image = :image_url WHERE id = :id'
    values = {"image_url": public_url, "id": player_id}
    await database.execute(query=query, values=values)

    return {"message": "Image updated", "path": file_path}

def set_database(db):
    """Set the database instance from main.py"""
    global database
    database = db