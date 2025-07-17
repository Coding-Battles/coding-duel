from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Set, Optional
import asyncio
from backend.models.questions import (
    RunTestCasesRequest,
    CodeTestResult
)
from backend.services.test_execution_service import TestExecutionService
from backend.code_testing.ai_complexity_analyzer import analyze_time_complexity_ai
from backend.models.questions import TimeComplexity

router = APIRouter()
logger = logging.getLogger(__name__)

# These will be injected from main.py
database = None
sio = None
game_service = None
matchmaking_service = None

@dataclass
class EmojiRequest:
    emoji: str
    player1: str

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

# Game states are now managed by the centralized game_service

def get_player_socket_id(game_id: str, player_id: str) -> Optional[str]:
    """Get player's socket ID from matchmaking service."""
    game_info = matchmaking_service.get_game_info(game_id)
    if not game_info:
        return None
    
    for player in game_info["players"]:
        if player["id"] == player_id:
            return player["sid"]
    return None

def get_player_name(game_id: str, player_id: str) -> Optional[str]:
    """Get player's name from matchmaking service."""
    game_info = matchmaking_service.get_game_info(game_id)
    if not game_info:
        return None
    
    for player in game_info["players"]:
        if player["id"] == player_id:
            return player["name"]
    return None

def get_opponent_id(game_id: str, player_id: str) -> Optional[str]:
    """Get opponent's ID from matchmaking service."""
    game_info = matchmaking_service.get_game_info(game_id)
    if not game_info:
        return None
    
    for player in game_info["players"]:
        if player["id"] != player_id:
            return player["id"]
    return None

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

@router.post("/{game_id}/send-emoji")
async def send_emoji(game_id: str, data: EmojiRequest):
    player1 = data.player1 #id
    emoji = data.emoji
    """Endpoint to send emoji from player to opponent."""
    logger.info(f"🚀 [ENTRY DEBUG] /send-emoji called for game {game_id} by player {player1} with emoji {emoji}")
    game_state = game_service.get_game(game_id)
    if not game_state:
        raise HTTPException(status_code=404, detail="Game not found")
    
    if len(game_state.players) != 2:
        raise HTTPException(status_code=400, detail="Emoji can only be sent in 2-player games")
    
    opponent_id = get_opponent_id(game_id, player1)
    if not opponent_id:
        raise HTTPException(status_code=404, detail="Opponent not found in game")
    
    opponent_sid = get_player_socket_id(game_id, opponent_id)
    if not opponent_sid:
        raise HTTPException(status_code=404, detail="Opponent socket not found")
    
    # Emit emoji to opponent
    await sio.emit("emoji_received", {"emoji": emoji, "from": player1}, room=opponent_sid)
    
    return {"message": "Emoji sent successfully"}

@router.post("/{game_id}/run-all-tests", response_model=CodeTestResult)
async def run_all_tests(game_id: str, request: RunTestCasesRequest):
    print(f"🚀 [ENTRY DEBUG] /run-all-tests called for game {game_id}")
    print(f"🚀 [ENTRY DEBUG] Player ID: {request.player_id}")
    print(f"🚀 [ENTRY DEBUG] Available games: {list(game_service.active_games.keys())}")
    logger.info(f"🚀 [ENTRY DEBUG] /run-all-tests called for game {game_id}")
    logger.info(f"🚀 [ENTRY DEBUG] Player ID: {request.player_id}")
    logger.info(f"🚀 [ENTRY DEBUG] Available games: {list(game_service.active_games.keys())}")
    
    # Check if game exists
    game_state = game_service.get_game(game_id)
    if not game_state:
        logger.error(f"🚀 [ENTRY DEBUG] Game {game_id} not found in game_service")
        raise HTTPException(status_code=404, detail="Game not found")
    player_id = request.player_id

    logger.info(f"🚀 [ENTRY DEBUG] Game found, players in game {game_id}: {game_state.players}")

    # Verify player is in this game
    if player_id not in game_state.players:
        logger.error(f"🚀 [ENTRY DEBUG] Player {player_id} not in game {game_id}")
        raise HTTPException(status_code=403, detail="Player not in this game")
        
    logger.info(f"🚀 [ENTRY DEBUG] Player verified, starting test execution") #need to replace opponent_id with array of ids for multiple players
    try: 
        test_results = TestExecutionService.execute_test_cases(request)

        # Get opponent info
        opponent_id = get_opponent_id(game_id, player_id)
        opponent_player_info = None
        opponent_sid = None

        print(f"🔍 [OPPONENT DEBUG] Player {player_id} finished tests. Opponent ID: {opponent_id}")
        print(f"🔍 [OPPONENT DEBUG] Game state players: {list(game_state.players.keys())}")
        logger.info(f"🔍 [OPPONENT DEBUG] Player {player_id} finished tests. Opponent ID: {opponent_id}")
        logger.info(f"🔍 [OPPONENT DEBUG] Game state players: {list(game_state.players.keys())}")

        complexity = "N/A"

        if(test_results.success):
            # Submit solution to game service
            submission_data = {
                "success": True,
                "code": request.code,
                "timer": request.timer,
                "test_results": test_results.test_results
            }
            game_service.submit_solution(game_id, player_id, submission_data)
            
            if opponent_id:
                # Emit to opponent only (don't expose full test results)
                player_name = get_player_name(game_id, player_id)
                opponent_sid = get_player_socket_id(game_id, opponent_id)
                logger.info(f"🔍 [OPPONENT DEBUG] SUCCESS: Player {player_name} (ID: {player_id}) passed all tests")
                logger.info(f"🔍 [OPPONENT DEBUG] SUCCESS: Opponent SID: {opponent_sid}")
                
                complexity_response = analyze_time_complexity_ai(request.code)
                complexity = complexity_response if complexity_response else "N/A"
                logger.info(f"🔍 [OPPONENT DEBUG] SUCCESS: Complexity analysis: {complexity}")

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
                
                # Game stats are now handled by the game service
                print(f"🔍 [OPPONENT DEBUG] SUCCESS: About to emit 'opponent_submitted' to room {opponent_sid}")
                logger.info(f"🔍 [OPPONENT DEBUG] SUCCESS: About to emit 'opponent_submitted' to room {opponent_sid}")
                await sio.emit(
                    "opponent_submitted", 
                    test_result.model_dump(), 
                    room=opponent_sid
                )
                print(f"🔍 [OPPONENT DEBUG] SUCCESS: Successfully emitted 'opponent_submitted' event")
                logger.info(f"🔍 [OPPONENT DEBUG] SUCCESS: Successfully emitted 'opponent_submitted' event")
                
                logger.info(f"✅ Notified opponent {opponent_id} that {player_id} finished with success")
        else:
            logger.warning(f"{test_results.total_passed} out of {test_results.total_passed + test_results.total_failed} test cases passed.")
            # Emit to opponent only (don't expose full test results)
            if opponent_id:
                opponent_player_name = get_player_name(game_id, opponent_id)
                opponent_sid = get_player_socket_id(game_id, opponent_id)
                logger.info(f"🔍 [OPPONENT DEBUG] PARTIAL: Player {player_id} passed {test_results.total_passed}/{test_results.total_passed + test_results.total_failed} tests")
                logger.info(f"🔍 [OPPONENT DEBUG] PARTIAL: Opponent SID: {opponent_sid}")
            
            logger.info(f"🔍 [OPPONENT DEBUG] PARTIAL: About to emit 'opponent_submitted' to room {opponent_sid}")
            await sio.emit(
                "opponent_submitted", 
                CodeTestResult(
                    message=f"Your opponents code has passed {test_results.total_passed} out of {test_results.total_passed + test_results.total_failed} test cases.",
                    code=request.code,
                    opponent_id=player_id,
                    success=test_results.success,
                    player_name=opponent_player_name,
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
            logger.info(f"🔍 [OPPONENT DEBUG] PARTIAL: Successfully emitted 'opponent_submitted' event")
            
            logger.info(f"⚠️ Notified opponent {opponent_id} that {player_id} finished with partial success")

        # If all players finished, emit game completion
        updated_game_state = game_service.get_game(game_id)
        if updated_game_state and updated_game_state.status.value == "finished":
            # Create player info for save_game_to_history
            player_infos = []
            game_info = matchmaking_service.get_game_info(game_id)
            if game_info:
                for player_data in game_info["players"]:
                    player_info = PlayerInfo(
                        id=player_data["id"],
                        sid=player_data["sid"],
                        name=player_data["name"],
                        anonymous=player_data.get("anonymous", True)
                    )
                    player_infos.append(player_info)
            
            await save_game_to_history(player_infos)
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
            player_name= get_player_name(game_id, player_id),
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

def set_dependencies(db, socketio_instance, game_service_instance, matchmaking_service_instance):
    """Set dependencies from main.py"""
    global database, sio, game_service, matchmaking_service
    database = db
    sio = socketio_instance
    game_service = game_service_instance
    matchmaking_service = matchmaking_service_instance