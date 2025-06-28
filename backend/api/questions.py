from fastapi import FastAPI, HTTPException, Body, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from typing import List, Optional, Dict, Any
from contextlib import asynccontextmanager
import socketio
from groq import Groq
import os
import docker
import asyncio
from concurrent.futures import ThreadPoolExecutor
import logging
import json
from pathlib import Path
from dotenv import load_dotenv
import databases
from pydantic import BaseModel, ValidationError
import uuid
import shutil
import random
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Set


#--------------CLASSES AND MODELS--------------#

@dataclass
class GameState:
    game_id: str
    players: Dict[str, str] = field(default_factory=dict)  # player_id -> sid mapping
    finished_players: Set[str] = field(default_factory=set)  # player_ids who finished
    created_at: datetime = field(default_factory=datetime.now)
    question_name: str = ""
    
    def is_player_finished(self, player_id: str) -> bool:
        return player_id in self.finished_players
    
    def mark_player_finished(self, player_id: str):
        self.finished_players.add(player_id)
    
    def get_unfinished_players(self) -> Set[str]:
        return set(self.players.keys()) - self.finished_players
    
    def all_players_finished(self) -> bool:
        return len(self.finished_players) == len(self.players)
    
    def get_opponent_id(self, player_id: str) -> Optional[str]:
        """Get the opponent's player ID"""
        player_ids = list(self.players.keys())
        if len(player_ids) == 2 and player_id in player_ids:
            return player_ids[0] if player_ids[1] == player_id else player_ids[1]
        return None

class Player(BaseModel):
    id: str  # This is the player's custom ID
    name: str
    imageURL: str
    sid: str  # This is the socket connection ID



class MatchFoundResponse(BaseModel):
    game_id: str
    opponent_Name: str
    opponentImageURL: Optional[str] = None
    question_name: str


class QueueStatusResponse(BaseModel):
    status: str
    queue_size: int
#--------------CLASSES AND MODELS END--------------#


# Load environment variables early before any usage
env_path = Path(".env")
if not env_path.exists():
    env_path = Path("../.env")
    if not env_path.exists():
        env_path = Path("backend/.env")

if env_path.exists():
    load_dotenv(dotenv_path=env_path)
    print(f"Loaded .env from: {env_path.absolute()}")
else:
    print("WARNING: .env file not found! Attempting to load from system environment")
    load_dotenv()

# Now it’s safe to use environment variables
groq_api_key = os.getenv("GROQ_API_KEY")
if not groq_api_key:
    print("WARNING: GROQ_API_KEY not found in environment variables")
else:
    print(f"GROQ API key loaded: {groq_api_key[:8]}...{groq_api_key[-4:]}")

# Import after env is loaded
from backend.code_testing.ai_complexity_analyzer import analyze_time_complexity_ai
from backend.code_testing.docker_runner import (
    run_code_in_docker,
    cleanup_persistent_containers,
)
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

@asynccontextmanager
async def lifespan(_app: FastAPI):
    logger.info("🚀 Initializing persistent containers for fast code execution...")
    try:
        from backend.code_testing.startup import pull_all_images, warm_up_containers
        loop = asyncio.get_event_loop()
        logger.info("📦 Pre-pulling Docker images...")
        await loop.run_in_executor(executor, pull_all_images)
        logger.info("🔥 Warming up persistent containers...")
        await loop.run_in_executor(executor, warm_up_containers)
        logger.info("✅ Persistent containers ready! Code execution will now be sub-second.")
    except Exception as e:
        logger.error(f"❌ Failed to initialize persistent containers: {e}")
        logger.warning("⚠️ Falling back to traditional Docker execution (slower)")

    yield

    logger.info("🧹 Cleaning up persistent containers...")
    try:
        cleanup_persistent_containers()
        logger.info("✅ Containers cleaned up successfully")
    except Exception as e:
        logger.error(f"❌ Error during container cleanup: {e}")

app = FastAPI(lifespan=lifespan)

#-------------#SOCKET SETUP#-------------#
DATABASE_URL = os.getenv("DATABASE_URL")
database = databases.Database(DATABASE_URL)
waiting_players: list[Player] = []
game_states: Dict[str, GameState] = {}  # game_id -> GameState
player_to_game: Dict[str, str] = {}  # player_id -> game_id mapping


sio = socketio.AsyncServer(
    cors_allowed_origins="*",
    async_mode='asgi'
)

socket_app = socketio.ASGIApp(sio, app)

@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

@app.get("/", response_model=QueueStatusResponse)
def health_check():
    return QueueStatusResponse(status="ok", queue_size=len(waiting_players))

@sio.event
async def ping(sid, data):
    await sio.emit("pong", {"timestamp": time.time()}, room=sid)

@sio.event
async def connect(sid, environ):
    logger.info(f"Client {sid} connected")


@sio.event
async def disconnect(sid):
    global waiting_players
    # Remove player from queue if they disconnect
    waiting_players = [p for p in waiting_players if p.sid != sid]

    # Remove player from game if they disconnect
    player_id_to_remove = None
    game_id_to_update = None
    
    for player_id, game_id in player_to_game.items():
        if game_id in game_states and game_states[game_id].players.get(player_id) == sid:
            player_id_to_remove = player_id
            game_id_to_update = game_id
            break
    
    if player_id_to_remove and game_id_to_update:
        # Notify opponent that player disconnected
        game_state = game_states[game_id_to_update]
        opponent_id = game_state.get_opponent_id(player_id_to_remove)
        
        if opponent_id and opponent_id in game_state.players:
            opponent_sid = game_state.players[opponent_id]
            await sio.emit(
                "opponent_disconnected", 
                {"message": "Your opponent has disconnected"}, 
                room=opponent_sid
            )
        
        # Clean up mappings
        del player_to_game[player_id_to_remove]
        if game_id_to_update in game_states:
            del game_states[game_id_to_update]
    
    logger.info(f"Client {sid} disconnected. Queue size: {len(waiting_players)}")
    logger.info(f"Client {sid} disconnected. Queue size: {len(waiting_players)}")

@sio.event
async def join_queue(sid, data):
    try:
        # Create player with both custom ID and socket ID
        player_data = {**data, "sid": sid}
        player = Player(**player_data)
        waiting_players.append(player)
        logger.info(
            f"Player {player.name} joined the queue. Total players in queue: {len(waiting_players)}"
        )

        # Check if we can form a match
        if len(waiting_players) >= 2:
            logger.info("🔍 pair found")
            player1 = waiting_players.pop(0)  # First player
            player2 = waiting_players.pop(0)  # Second player (current player)

            game_id = f"game_{uuid.uuid4().hex[:12]}"

            with open("backend/data/questions.json", 'r') as f:
                data = json.load(f)

            # Randomly select a question from the available questions
            question = random.choice(data["questions"])
            question_name = question["title"]  # → 'two-sum'

            # Create game state
            game_state = GameState(
                game_id=game_id,
                players={
                    player1.id: player1.id,
                    player2.id: player2.id
                },
                question_name=question_name
            )
            game_states[game_id] = game_state
            
            # Map players to game
            player_to_game[player1.id] = game_id
            player_to_game[player2.id] = game_id

            # Send match notification to both players using their socket IDs
            match_response1 = MatchFoundResponse(
                game_id=game_id, 
                opponent_Name=player2.name, 
                opponentImageURL=player2.imageURL, 
                question_name=question_name
            )
            await sio.emit("match_found", match_response1.model_dump(), room=player1.sid)

            match_response2 = MatchFoundResponse(
                game_id=game_id, 
                opponent_Name=player1.name, 
                opponentImageURL=player1.imageURL, 
                question_name=question_name
            )
            await sio.emit("match_found", match_response2.model_dump(), room=player2.sid)

            logger.info(f"Match found: {player1.name} vs {player2.name} in game {game_id}")

            # After match is found
            await sio.enter_room(player1.sid, game_id)
            await sio.enter_room(player2.sid, game_id)
        else:
            status_response = QueueStatusResponse(
                status="waiting", queue_size=len(waiting_players)
            )
            await sio.emit("queue_status", status_response.model_dump(), room=sid)

    except ValidationError as e:
        print(f"Validation error: {e}")
        await sio.emit("error", {"message": "Invalid data"}, room=sid)


app.mount("/uploads", StaticFiles(directory="backend/uploads"), name="uploads")
#-------------#SOCKET end#-------------#


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/{game_id}/run-all-tests", response_model=RunTestCasesResponse)
async def run_all_tests(game_id: str, request: RunTestCasesRequest):
    if not docker_available:
        raise HTTPException(status_code=503, detail="Docker is not available.")
    # Check if game exists
    if game_id not in game_states:
        raise HTTPException(status_code=404, detail="Game not found")
    
    game_state = game_states[game_id]
    player_id = request.player_id

    logger.info(f"players in game {game_id}: {game_state.players}")

    # Verify player is in this game
    if player_id not in game_state.players:
        raise HTTPException(status_code=403, detail="Player not in this game")
    try: 
        results = TestExecutionService.execute_test_cases(request)

        # Get opponent info
        opponent_id = game_state.get_opponent_id(player_id)


        if(results.success):
            game_state.mark_player_finished(player_id)
            
            if opponent_id:
                # Emit to opponent only (don't expose full test results)
                opponent_sid = game_state.players[opponent_id]
                await sio.emit(
                    "opponent_submitted", 
                    {
                        "message": "Your opponent has finished their tests!",
                        "opponent_id": player_id,
                        "status": results.success,
                        "total_tests": results.total_passed + results.total_failed if hasattr(results, 'total_failed') else None
                    }, 
                    room=opponent_sid
                )
                
                logger.info(f"Notified opponent {opponent_id} that {player_id} finished")
        else:
            logger.warning(f"{results.total_passed} out of {results.total_passed + results.total_failed} test cases passed.")
            # Emit to opponent only (don't expose full test results)
            opponent_sid = game_state.players[opponent_id]
            await sio.emit(
                "opponent_submitted", 
                {
                    "message": f"Your opponents code has passed {results.total_passed} out of {results.total_passed + results.total_failed} test cases.",
                    "opponent_id": player_id,
                    "status": results.success,
                    "total_tests": results.total_passed + results.total_failed if hasattr(results, 'total_failed') else None
                }, 
                room=opponent_sid
            )
            
            logger.info(f"Notified opponent {opponent_id} that {player_id} finished")

        # If all players finished, emit game completion
        if game_state.all_players_finished():
            await sio.emit(
                "game_completed",
                {"message": "All players have finished!"},
                room=game_id
            )
            logger.info(f"Game {game_id} completed - all players finished")

        if results.success:
            logger.info(f"All {results.total_passed} test cases passed successfully for player {player_id}.")
        else:
            total_failed = getattr(results, 'total_failed', 0)
            logger.warning(f"{results.total_passed} out of {results.total_passed + total_failed} test cases passed for player {player_id}.")

        return results
    
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in /run-all-tests: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/run-sample-tests", response_model=RunTestCasesResponse)
async def run_sample_tests(request: RunTestCasesRequest):
    if not docker_available:
        raise HTTPException(status_code=503, detail="Docker is not available.")
    try:
        return TestExecutionService.execute_sample_test_cases(request)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in /run-sample-tests: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/analyze-complexity", response_model=TimeComplexityResponse)
async def analyze_time_complexity(request: TimeComplexity):
    try:
        time_complexity = analyze_time_complexity_ai(request.code)
        return TimeComplexityResponse(time_complexity=time_complexity)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "docker_available": docker_available,
        "docker_status": "connected" if docker_available else "not connected",
    }

@app.post("/docker-run")
async def docker_run(request: DockerRunRequest = Body(...)):
    try:
        result = run_code_in_docker(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/debug-run")
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

@app.get("/get-question/{question_name}", response_model=QuestionData)
async def get_question(question_name: str):
    try:
        question_file_path = Path(f"backend/data/question-data/{question_name}.json")
        if not question_file_path.exists():
            raise HTTPException(status_code=404, detail=f"Question '{question_name}' not found")
        with open(question_file_path, "r", encoding="utf-8") as file:
            question_data = json.load(file)
        return QuestionData(**question_data)
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in question file {question_name}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Invalid question data format for '{question_name}'")
    except Exception as e:
        logger.error(f"Error loading question {question_name}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error loading question '{question_name}'")

@app.post("/image/{player_id}")
async def change_image(player_id: str, image: UploadFile = File(...)):
    # Save file
    os.makedirs("uploads", exist_ok=True)
    filename = f"player_{player_id}_{image.filename}"
    file_path = f"uploads/{filename}"
    public_url = f"http://localhost:8000/uploads/{filename}"

    with open(file_path, "wb") as f:
        shutil.copyfileobj(image.file, f)

    # Update DB using raw SQL
    query = 'UPDATE "user" SET image = :image_url WHERE id = :id'
    values = {"image_url": public_url, "id": player_id}
    await database.execute(query=query, values=values)

    return {"message": "Image updated", "path": file_path}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.api.questions:app", host="0.0.0.0", port=8000)
