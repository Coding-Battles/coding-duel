from fastapi import FastAPI, HTTPException, Body, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from typing import List, Optional, Dict, Any
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



class Player(BaseModel):
    id: str  # This is the player's custom ID
    name: str
    imageURL: str
    easy: bool
    medium: bool
    hard: bool
    anonymous: bool = True  # Whether the player is anonymous or not
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
)
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

@dataclass
class PlayerInfo:
    id: str
    sid: str
    name: str
    anonymous: bool = True
    game_stats: Optional[CodeTestResult] = field(default_factory=lambda: CodeTestResult(
        message="",
        code="",
        player_name="",
        opponent_id="",
        success=False,
        test_results=[],
        total_passed=0,
        total_failed=0,
        error="",
        complexity="",
        implement_time=0,
        final_time=20000
    ))

@dataclass
class GameState:
    game_id: str
    players: Dict[str, PlayerInfo] = field(default_factory=dict)  # player_id -> PlayerInfo
    finished_players: Set[str] = field(default_factory=set)
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
    
    def get_player_name(self, player_id: str) -> Optional[str]:
        if player_id in self.players:
            return self.players[player_id].name
        return None

    def get_opponent_id(self, player_id: str) -> Optional[str]:
        player_ids = list(self.players.keys())
        if len(player_ids) == 2 and player_id in player_ids:
            return player_ids[0] if player_ids[1] == player_id else player_ids[1]
        return None

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

async def startup_event():
    # Startup - database connection only (containers managed by main.py)
    logger.info("🚀 Starting questions app...")
    
    try:
        logger.info("📊 Connecting to database...")
        await database.connect()
        logger.info("✅ Database connected successfully")
    except Exception as e:
        logger.error(f"❌ Failed to connect to database: {e}")
        raise

async def shutdown_event():
    # Shutdown - database disconnection only (containers managed by main.py)
    try:
        logger.info("📊 Disconnecting from database...")
        await database.disconnect()
        logger.info("✅ Database disconnected successfully")
    except Exception as e:
        logger.error(f"❌ Error during database disconnect: {e}")

app = FastAPI()

# Add startup and shutdown events
app.add_event_handler("startup", startup_event)
app.add_event_handler("shutdown", shutdown_event)

#-------------#SOCKET SETUP#-------------#
DATABASE_URL = os.getenv("DATABASE_URL")
database = databases.Database(DATABASE_URL)
waiting_players_easy: list[Player] = []
waiting_players_medium: list[Player] = []
waiting_players_hard: list[Player] = []
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
    return QueueStatusResponse(status="ok", queue_size=max(len(waiting_players_easy), len(waiting_players_medium), len(waiting_players_hard)))

@sio.event
async def ping(sid, data):
    await sio.emit("pong", {"timestamp": time.time()}, room=sid)

@sio.event
async def connect(sid, environ):
    logger.info(f"Client {sid} connected")


@sio.event
async def disconnect(sid):
    global waiting_players_easy
    global waiting_players_medium
    global waiting_players_hard
    # Remove player from queue if they disconnect
    waiting_players_easy = [p for p in waiting_players_easy if p.sid != sid]
    waiting_players_medium = [p for p in waiting_players_medium if p.sid != sid]
    waiting_players_hard = [p for p in waiting_players_hard if p.sid != sid]

    # Remove player from game if they disconnect
    player_id_to_remove = None
    game_id_to_update = None
    
    for player_id, game_id in player_to_game.items():
        if game_id in game_states:
            game_state = game_states[game_id]
            if player_id in game_state.players and game_state.players[player_id].sid == sid:
                player_id_to_remove = player_id
                game_id_to_update = game_id
                break
    
    if player_id_to_remove and game_id_to_update:
        # Notify opponent that player disconnected
        game_state = game_states[game_id_to_update]
        opponent_id = game_state.get_opponent_id(player_id_to_remove)
        
        if opponent_id and opponent_id in game_state.players:
            opponent_sid = game_state.players[opponent_id].sid
            await sio.emit(
                "opponent_disconnected", 
                {"message": "Your opponent has disconnected"}, 
                room=opponent_sid
            )
        
        # Clean up mappings
        del player_to_game[player_id_to_remove]
        if game_id_to_update in game_states:
            del game_states[game_id_to_update]
    
    logger.info(f"Client {sid} disconnected. Queue size: {len(waiting_players_easy) + len(waiting_players_medium) + len(waiting_players_hard)}")
    logger.info(f"Client {sid} disconnected. Queue size: easy={len(waiting_players_easy)}, medium={len(waiting_players_medium)}, hard={len(waiting_players_hard)}")

@sio.event
async def join_queue(sid, data):
    try:
        # Create player with both custom ID and socket ID
        player_data = {**data, "sid": sid}
        player = Player(**player_data)
        if player.easy:
            waiting_players_easy.append(player)
        if player.medium:
            waiting_players_medium.append(player)
        if player.hard:
            waiting_players_hard.append(player)

        logger.info(
            f"Player {player.name} joined the queue. Total players in queue: easy={len(waiting_players_easy)}, medium={len(waiting_players_medium)}, hard={len(waiting_players_hard)}"
        )

        difficulties = []
        difficulties_identifier = []

        if(len(waiting_players_easy) >= 2):
            difficulties.append(waiting_players_easy)
            difficulties_identifier.append("easy")
        if(len(waiting_players_medium) >= 2):
            difficulties.append(waiting_players_medium)
            difficulties_identifier.append("medium")
        if(len(waiting_players_hard) >= 2):
            difficulties.append(waiting_players_hard)
            difficulties_identifier.append("hard")

        with open("backend/data/questions.json", 'r') as f:
            data = json.load(f)

        logger.info(data["questions"].keys())



        # Check if we can form a match
        if len(difficulties) > 0:
            logger.info("🔍 pair found")
            rand_num = random.randint(0, len(difficulties) - 1)
            difficulty_player_list = difficulties[rand_num]
            difficulty_identifier = difficulties_identifier[rand_num]


            player1 = difficulty_player_list.pop(0)  # First player (current player)
            player2 = difficulty_player_list.pop(0)  # Second player (opponent)

            logger.info(f"Pairing players: {player1.name} vs {player2.name} in difficulty {difficulty_identifier}")

            # Remove players from waiting lists
            if player1 in waiting_players_easy:
                waiting_players_easy.remove(player1)
            if player2 in waiting_players_easy:
                waiting_players_easy.remove(player2)
            if player1 in waiting_players_medium:
                waiting_players_medium.remove(player1)
            if player2 in waiting_players_medium:
                waiting_players_medium.remove(player2)
            if player1 in waiting_players_hard:
                waiting_players_hard.remove(player1)
            if player2 in waiting_players_hard:
                waiting_players_hard.remove(player2)

            game_id = f"game_{uuid.uuid4().hex[:12]}"
            with open("backend/data/questions.json", 'r') as f:
                data = json.load(f)

            logger.info("difficulty_identifier:", difficulty_identifier)
            logger.info("keys available:", list(data["questions"].keys()))
            logger.info("selected list:", data["questions"][difficulty_identifier])

            # Randomly select a question from the available questions
            question = random.choice(data["questions"][difficulty_identifier])

            question_name = question["slug"]  # Use slug for both loading files and URLs
            question_slug = question["slug"]  # Use slug for URLs
            question_title = question["title"]  # Human-readable title for display

            logger.info(f"player1: {player1.name} vs player2: {player2.name} with question: {question_name}")

            # Create game state
            game_state = GameState(
                game_id=game_id,
                players={
                    player1.id: PlayerInfo(id=player1.id, name=player1.name, sid=player1.sid, anonymous=player1.anonymous),
                    player2.id: PlayerInfo(id=player2.id, name=player2.name, sid=player2.sid, anonymous=player2.anonymous)
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
                question_name=question_slug  # Send slug for URL navigation
            )
            await sio.emit("match_found", match_response1.model_dump(), room=player1.sid)

            match_response2 = MatchFoundResponse(
                game_id=game_id, 
                opponent_Name=player1.name, 
                opponentImageURL=player1.imageURL, 
                question_name=question_slug  # Send slug for URL navigation
            )
            await sio.emit("match_found", match_response2.model_dump(), room=player2.sid)

            logger.info(f"Match found: {player1.name} vs {player2.name} in game {game_id}")

            # After match is found
            await sio.enter_room(player1.sid, game_id)
            await sio.enter_room(player2.sid, game_id)
        else:
            status_response = QueueStatusResponse(
                status="waiting", queue_size=len(max(len(waiting_players_easy), len(waiting_players_medium), len(waiting_players_hard)))
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

@app.post("/{game_id}/run-all-tests", response_model=CodeTestResult)
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
        test_results = TestExecutionService.execute_test_cases(request)

        # Get opponent info
        opponent_id = game_state.get_opponent_id(player_id)
        opponent_player_info = None
        opponent_sid = None

        complexity = "N/A"

        if(test_results.success):
            game_state.mark_player_finished(player_id)
            
            if opponent_id:
                # Emit to opponent only (don't expose full test results)
                player_name = game_state.get_player_name(player_id)
                opponent_sid = game_state.players[opponent_id].sid
                complexity = await analyze_time_complexity(TimeComplexity(code=request.code))
                complexity = complexity.time_complexity if complexity and hasattr(complexity, 'time_complexity') else "N/A"
                logger.info(f"Player {player_name} finished tests with complexity {complexity}, notifying opponent sid {opponent_sid}")

                test_result = CodeTestResult(
                        message="Your opponent has finished their tests!",
                        code=request.code,
                        player_name=player_name,
                        opponent_id=player_id,
                        success=test_results.success,
                        test_results= test_results.test_results,
                        error=None,
                        total_passed= test_results.total_passed,
                        total_failed= test_results.total_failed if hasattr(test_results, 'total_failed') else 0,
                        complexity=complexity,
                        implement_time=request.timer,
                        final_time= get_score(complexity, request.timer),
                    )
                
                game_state.players[player_id].game_stats = test_result
                await sio.emit(
                    "opponent_submitted", 
                    test_result.model_dump(), 
                    room=opponent_sid
                )
                
                logger.info(f"Notified opponent {opponent_id} that {player_id} finished")
        else:
            logger.warning(f"{test_results.total_passed} out of {test_results.total_passed + test_results.total_failed} test cases passed.")
            # Emit to opponent only (don't expose full test results)
            if opponent_id:
                opponent_player_info = game_state.players[opponent_id]
                opponent_sid = opponent_player_info.sid
            
            await sio.emit(
                "opponent_submitted", 
                CodeTestResult(
                    message=f"Your opponents code has passed {test_results.total_passed} out of {test_results.total_passed + test_results.total_failed} test cases.",
                    code=request.code,
                    opponent_id=player_id,
                    success=test_results.success,
                    player_name=opponent_player_info.name,
                    test_results=test_results.test_results,
                    error=None,
                    total_passed=test_results.total_passed,
                    total_failed=test_results.total_failed if hasattr(test_results, 'total_failed') else 0,
                    complexity=complexity,
                    implement_time=request.timer,
                    final_time= 0  # No final time if tests failed,
                ).model_dump(), 
                room=opponent_sid
            )
            
            logger.info(f"Notified opponent {opponent_id} that {player_id} finished")

        # If all players finished, emit game completion
        if game_state.all_players_finished():
            await save_game_to_history(
                list(game_state.players.values())
            )
            await sio.emit(
                "game_completed",
                {"message": "All players have finished!"},
                room=game_id
            )
            logger.info(f"Game {game_id} completed - all players finished")

        if test_results.success:
            logger.info(f"All {test_results.total_passed} test cases passed successfully for player {player_id}.")
        else:
            total_failed = getattr(test_results, 'total_failed', 0)
            logger.warning(f"{test_results.total_passed} out of {test_results.total_passed + total_failed} test cases passed for player {player_id}.")

        logger.info(f"Complexity analysis for player {player_id}: {complexity} timer {request.timer}ms")
        finalTime = get_score(complexity, request.timer)
        logger.info(f"Final time for player {player_id} is {finalTime}ms based on complexity {complexity} and implementation time {request.timer}ms")

        results = CodeTestResult(
            message="Test execution completed",
            code=request.code,
            opponent_id=opponent_id,
            player_name= game_state.get_player_name(player_id),
            success=test_results.success,
            test_results=test_results.test_results,
            total_passed=test_results.total_passed,
            total_failed=test_results.total_failed if hasattr(test_results, 'total_failed') else 0,
            error=test_results.error,
            complexity= complexity,  # Complexity will be sent separately to opponent
            implement_time=request.timer,
            final_time= finalTime
        )

        return results
    
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in /run-all-tests: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    
async def save_game_to_history(players: List[PlayerInfo]):
    """Save game history to the database."""
    try:
        logger.info(f"Saving game history with {len(players)} players")

        game_query = "INSERT INTO games DEFAULT VALUES RETURNING id"
        result = await database.fetch_one(query=game_query)

        db_game_id = None

        if result:
            db_game_id = result["id"]  # Access the returned ID
            logger.info(f"Game history saved with DB ID: {db_game_id}")
        else:
            raise Exception("Failed to insert game record")
        
        participant_query = """
        INSERT INTO game_participants (game_id, player_name, player_code, 
                                    implement_time, time_complexity, final_time, user_id)
        VALUES (:game_id, :player_name, :player_code, :implement_time, 
                :time_complexity, :final_time, :user_id)
        """

        store_game_id_query = """
            UPDATE "user" 
            SET game_ids = array_append(COALESCE(game_ids, ARRAY[]::INTEGER[]), :game_id)
            WHERE id = :user_id;
        """

        for player in players:
            logger.info(f"Saving stats for player {player.name} in game {db_game_id}")
            player_stats = player.game_stats
            if player_stats:
                values = {
                    "game_id": db_game_id,
                    "player_name": player.name,
                    "player_code": player_stats.code,
                    "implement_time": player_stats.implement_time,
                    "time_complexity": player_stats.complexity,
                    "final_time": player_stats.final_time,
                    "user_id": player.id
                }
                await database.execute(query=participant_query, values=values)
            if(not player.anonymous):
                logger.info(f"Storing game ID {db_game_id} for player {player.id}")
                try:
                    values = {
                        "game_id": db_game_id,
                        "user_id": player.id
                    }
                    await database.execute(
                        query=store_game_id_query,
                        values=values
                    )
                except Exception as e:
                    logger.error(f"Error storing game ID {db_game_id} for player {player.id}: {str(e)}")
                


    
    except Exception as e:
        logger.error(f"Database error while saving game history: {str(e)}")


    
def get_score(timeComplexity: str, implementTime: int) -> int:
    """Convert time complexity string to a score."""
    timeReduction = 0
    if "O(1)" in timeComplexity:
        timeReduction = 100
    elif "O(log n)" in timeComplexity:
        timeReduction = 90
    elif "O(n)" in timeComplexity:
        timeReduction = 80
    elif "O(n log n)" in timeComplexity:
        timeReduction = 70
    elif "O(n^2)" in timeComplexity:
        timeReduction = 60
    else:
        timeReduction = 50

    return implementTime - timeReduction

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

def get_file_name_from_slug(slug: str) -> str:
    """Return slug as file name since they are now the same."""
    return slug

@app.get("/get-question/{question_slug}", response_model=QuestionData)
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
    
@app.get("/user/{user_id}/game-history")
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
