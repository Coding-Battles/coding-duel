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

# Global game states - will be managed from main.py
game_states: Dict[str, GameState] = {}

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

@router.post("/{game_id}/run-all-tests", response_model=CodeTestResult)
async def run_all_tests(game_id: str, request: RunTestCasesRequest):
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
                complexity_response = await analyze_time_complexity_ai(request.code)
                complexity = complexity_response if complexity_response else "N/A"
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

def set_dependencies(db, socketio_instance, game_states_dict):
    """Set dependencies from main.py"""
    global database, sio, game_states
    database = db
    sio = socketio_instance
    game_states = game_states_dict