import threading
from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
import logging
import asyncio
from backend.global_variables import games

from backend.models.core import (
    RunTestCasesRequest, 
    CodeTestResult,
    TimeComplexity,
    PlayerInfo,
    GameState,
    EmojiRequest
)
from backend.services.test_execution_service import TestExecutionService
from backend.code_testing.ai_complexity_analyzer import analyze_time_complexity_ai

router = APIRouter()
logger = logging.getLogger(__name__)

# These will be injected from main.py
database = None
sio = None




# Note: GameState now comes from centralized models
# We can extend it with additional methods if needed


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


async def save_game_to_history(players: List[PlayerInfo], difficulty: str, question_name: str = "Unknown", winner_id: str = None):
    """Save game history to the database."""
    try:
        logger.info(f"Saving game history with {len(players)} players and difficulty {difficulty}")

        game_query = """INSERT INTO games (question_name, difficulty)
            VALUES (:question_name, :difficulty)
            RETURNING id;
            """
        values = {
            "question_name": question_name if players else "Unknown",
            "difficulty": difficulty
        }
        result = await database.fetch_one(query=game_query, values=values)

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

        difficulty_column = {
        "easy": "easyLP",
        "medium": "mediumLP",
        "hard": "hardLP"
        }[difficulty]

        update_user_lp_query = f"""
            UPDATE "user"
            SET {difficulty_column} = {difficulty_column} + :lp_gain
            WHERE id = :user_id;
        """


        for player in players:
            logger.info(f"Saving stats for player {player.name} in game {db_game_id}")
            player_stats = player.game_stats
            logger.info(f"Player stats: {player_stats}")
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
                logger.info(f"Executing game participants query with values: {values}")
                await database.execute(query=participant_query, values=values)
            else: #in the case the game finished by time or disconnection player.game_stats will be empty
                time = 0
                if(player.id == winner_id):
                    time = -100
                else:
                    time = 100
                values = {
                    "game_id": db_game_id,
                    "player_name": player.name,
                    "player_code": "N/A",
                    "implement_time": 0,
                    "time_complexity": "N/A",
                    "final_time": time,
                    "user_id": player.id
                }
                logger.info(f"Executing game participants query with empty values: {values}")
                await database.execute(query=participant_query, values=values)
            if not player.anonymous:
                logger.info(f"Storing game ID {db_game_id} for player {player.id}")
                try:
                    values = {"game_id": db_game_id, "user_id": player.id}
                    await database.execute(query=store_game_id_query, values=values)

                    (winner_lp_gain, loser_lp_loss) = games.get_lp_changes()

                    lp_gain = 0
                    if player.id == winner_id:
                        lp_gain = winner_lp_gain
                    else:
                        lp_gain = -loser_lp_loss

                    values = {"lp_gain": lp_gain, "user_id": player.id}
                    await database.execute(query=update_user_lp_query, values=values)

                except Exception as e:
                    logger.error(
                        f"Error storing game ID {db_game_id} for player {player.id}: {str(e)}"
                    )

    except Exception as e:
        logger.error(f"Database error while saving game history: {str(e)}")

def set_game_end_timer(game_id: str):
    easy_timer = 60
    medium_timer = 180
    hard_timer = 300
    timer_duration = None
    game_state = game_states.get(game_id)
    def delayed_task():
        if game_state and not game_state.all_players_finished():
            logger.info(f"Game {game_id} ended due to taking too much time")
            winner_id = game_state.get_finished_players().pop() if game_state.get_finished_players() else None
            game_state.set_winner(winner_id, reason="Time Limit Exceeded")

            opponent_id = game_state.get_opponent_id(winner_id)
            if opponent_id:
                # Return an empty CodeTestResult if opponent did not finish
                test_result = CodeTestResult(
                    message="Last player did not finish in time.",
                    code="",
                    player_name=game_state.get_player_name(opponent_id),
                    player_id=opponent_id,
                    success=False,
                    test_results=[],
                    error=None,
                    total_passed=0,
                    total_failed=0,
                    complexity="N/A",
                    implement_time=0,
                    final_time=0,
                )
                game_state.players[opponent_id].game_stats = test_result
                save_game_to_history(list(game_state.players.values()), game_state.difficulty, game_state.question_name, game_state.winner_id)

                winner_name = game_state.get_player_name(game_state.winner_id)
                loser_id = opponent_id
                loser_name = game_state.get_player_name(loser_id) if loser_id else "error"

                (winner_lp_gain, loser_lp_loss) = games.get_lp_changes()

                game_end_data = {
                "message": f"{winner_name} won the game!",
                "winner_id": game_state.winner_id,
                "winner_name": winner_name,
                "loser_id": loser_id,
                "loser_name": loser_name,
                    "game_end_reason": "Time Limit Exceeded",
                "lp_loss": loser_lp_loss,
                "lp_gain": winner_lp_gain
                }
                
                sio.emit("game_completed", game_end_data, room=game_id)

    if game_state:
        if game_state.difficulty == "easy":
            timer_duration = easy_timer
        elif game_state.difficulty == "medium":
            timer_duration = medium_timer
        elif game_state.difficulty == "hard":
            timer_duration = hard_timer
        else:
            logger.warning(f"Unknown game difficulty: {game_state.difficulty}")

    if timer_duration:
        timer = threading.Timer(timer_duration, delayed_task)
        timer.start()


@router.post("/{game_id}/send-emoji")
async def send_emoji(game_id: str, data: EmojiRequest):
    logger.info(
        f"🚀 [ENTRY DEBUG] /send-emoji called for game {game_id} by player {data.player1} with emoji {data.emoji}"
    )
    player1 = data.player1  # id
    emoji = data.emoji
    """Endpoint to send emoji from player to opponent."""
    logger.info(
        f"🚀 [ENTRY DEBUG] /send-emoji called for game {game_id} by player {player1} with emoji {emoji}"
    )
    if game_id not in game_states:
        raise HTTPException(status_code=404, detail="Game not found")

    game_state = game_states[game_id]
    players = list(game_state.players.values())

    if len(players) != 2:
        raise HTTPException(
            status_code=400, detail="Emoji can only be sent in 2-player games"
        )

    opponent_id = game_state.get_opponent_id(player1)
    if (opponent_id is None) or (opponent_id not in game_state.players):
        raise HTTPException(status_code=404, detail="Opponent not found in game")

    opponent_sid = game_state.players[opponent_id].sid

    # Emit emoji to opponent
    await sio.emit(
        "emoji_received", {"emoji": emoji, "from": player1}, room=opponent_sid
    )

    return {"message": "Emoji sent successfully"}


@router.post("/{game_id}/run-all-tests", response_model=CodeTestResult)
async def run_all_tests(game_id: str, request: RunTestCasesRequest):
    print(f"gameStates: {game_states}")
    print(f"🚀 [ENTRY DEBUG] /run-all-tests called for game {game_id}")
    print(f"🚀 [ENTRY DEBUG] Player ID: {request.player_id}")
    print(f"🚀 [ENTRY DEBUG] Available games: {list(game_states.keys())}")
    logger.info(f"🚀 [ENTRY DEBUG] /run-all-tests called for game {game_id}")
    logger.info(f"🚀 [ENTRY DEBUG] Player ID: {request.player_id}")
    logger.info(f"🚀 [ENTRY DEBUG] Available games: {list(game_states.keys())}")

    # Check if game exists
    if game_id not in game_states:
        logger.error(f"🚀 [ENTRY DEBUG] Game {game_id} not found in game_states")
        raise HTTPException(status_code=404, detail="Game not found")

    game_state = game_states[game_id]
    player_id = request.player_id

    logger.info(
        f"🚀 [ENTRY DEBUG] Game found, players in game {game_id}: {game_state.players}"
    )
    logger.info(
        f"🚀 [ENTRY DEBUG] difficulty {game_state.difficulty} question-name {game_state.question_name}"
    )

    # Verify player is in this game
    if player_id not in game_state.players:
        logger.error(f"🚀 [ENTRY DEBUG] Player {player_id} not in game {game_id}")
        raise HTTPException(status_code=403, detail="Player not in this game")

    logger.info(
        f"🚀 [ENTRY DEBUG] Player verified, starting test execution"
    )  # need to replace opponent_id with array of ids for multiple players
    try:
        test_results = TestExecutionService.execute_test_cases(request)

        # Get opponent info
        opponent_id = game_state.get_opponent_id(player_id)
        opponent_player_info = None
        opponent_sid = None

        print(
            f"🔍 [OPPONENT DEBUG] Player {player_id} finished tests. Opponent ID: {opponent_id}"
        )
        print(
            f"🔍 [OPPONENT DEBUG] Game state players: {list(game_state.players.keys())}"
        )
        logger.info(
            f"🔍 [OPPONENT DEBUG] Player {player_id} finished tests. Opponent ID: {opponent_id}"
        )
        logger.info(
            f"🔍 [OPPONENT DEBUG] Game state players: {list(game_state.players.keys())}"
        )

        complexity = "N/A"

        if test_results.success:
            game_state.mark_player_finished(player_id)

            if not game_state.all_players_finished():
                set_game_end_timer(game_id)  # Set a timer for game end if not all players finished

            if opponent_id:
                # Emit to opponent only (don't expose full test results)
                player_name = game_state.get_player_name(player_id)
                opponent_sid = game_state.players[opponent_id].sid
                logger.info(
                    f"🔍 [OPPONENT DEBUG] SUCCESS: Player {player_name} (ID: {player_id}) passed all tests"
                )
                logger.info(
                    f"🔍 [OPPONENT DEBUG] SUCCESS: Opponent SID: {opponent_sid}"
                )

                complexity_response = analyze_time_complexity_ai(request.code)
                complexity = complexity_response if complexity_response else "N/A"
                logger.info(
                    f"🔍 [OPPONENT DEBUG] SUCCESS: Complexity analysis: {complexity}"
                )

                test_result = None

                try:
                    # Convert TestCaseResult objects to dictionaries
                    test_results_as_dicts = []
                    for result in test_results.test_results:
                        if hasattr(result, '__dict__'):
                            test_results_as_dicts.append(result.__dict__)
                        elif hasattr(result, 'model_dump'):  # If it's a Pydantic model
                            test_results_as_dicts.append(result.model_dump())
                        else:
                            # Fallback: convert to dict manually
                            test_results_as_dicts.append({
                                'input': getattr(result, 'input', {}),
                                'expected_output': getattr(result, 'expected_output', []),
                                'actual_output': getattr(result, 'actual_output', ''),
                                'passed': getattr(result, 'passed', False),
                                'error': getattr(result, 'error', None),
                                'execution_time': getattr(result, 'execution_time', 0)
                            })

                    test_result = CodeTestResult(
                        message="Your opponent has finished their tests!",
                        code=request.code,
                        player_name=player_name,
                        player_id=player_id,
                        success=test_results.success,
                        test_results=test_results_as_dicts,  # Use the converted dictionaries
                        error=None,
                        total_passed=test_results.total_passed,
                        total_failed=(
                            test_results.total_failed
                            if hasattr(test_results, "total_failed")
                            else 0
                        ),
                        complexity=complexity,
                        implement_time=int(request.timer),
                        final_time=int(get_score(complexity, request.timer)),
                    )
                    logger.info("✅ CodeTestResult created successfully")
                except ValueError as e:
                    logger.error(f"❌ ValueError in CodeTestResult: {e}")
                    raise

                game_state.players[player_id].game_stats = test_result
                print(
                    f"🔍 [OPPONENT DEBUG] SUCCESS: About to emit 'opponent_submitted' to room {opponent_sid}"
                )
                logger.info(
                    f"🔍 [OPPONENT DEBUG] SUCCESS: About to emit 'opponent_submitted' to room {opponent_sid}"
                )
                await sio.emit(
                    "opponent_submitted", test_result.model_dump(), room=opponent_sid
                )
                print(
                    f"🔍 [OPPONENT DEBUG] SUCCESS: Successfully emitted 'opponent_submitted' event"
                )
                logger.info(
                    f"🔍 [OPPONENT DEBUG] SUCCESS: Successfully emitted 'opponent_submitted' event"
                )

                logger.info(
                    f"✅ Notified opponent {opponent_id} that {player_id} finished with success"
                )
        else:
            logger.warning(
                f"{test_results.total_passed} out of {test_results.total_passed + test_results.total_failed} test cases passed."
            )
            # Emit to opponent only (don't expose full test results)
            if opponent_id:
                opponent_player_info = game_state.players[opponent_id]
                opponent_sid = opponent_player_info.sid
                logger.info(
                    f"🔍 [OPPONENT DEBUG] PARTIAL: Player {player_id} passed {test_results.total_passed}/{test_results.total_passed + test_results.total_failed} tests"
                )
                logger.info(
                    f"🔍 [OPPONENT DEBUG] PARTIAL: Opponent SID: {opponent_sid}"
                )

            logger.info(
                f"🔍 [OPPONENT DEBUG] PARTIAL: About to emit 'opponent_submitted' to room {opponent_sid}"
            )
            test_results.message = "Opponent has finished their tests with partial success"
            await sio.emit(
                "opponent_submitted",
                test_results.model_dump(),
                room=opponent_sid,
            )
            logger.info(
                f"🔍 [OPPONENT DEBUG] PARTIAL: Successfully emitted 'opponent_submitted' event"
            )

            logger.info(
                f"⚠️ Notified opponent {opponent_id} that {player_id} finished with partial success"
            )

        # If game has ended (first player won), emit game completion immediately
        if game_state.all_players_finished():
            opponent_id = game_state.get_opponent_id(player_id)
            if game_state.players[player_id].game_stats.final_time < game_state.players[opponent_id].game_stats.final_time:
                game_state.set_winner(player_id, reason="Better Score")
            else:
                game_state.set_winner(opponent_id, reason="Better Score")

            winner_name = game_state.get_player_name(game_state.winner_id)
            loser_id = game_state.get_opponent_id(game_state.winner_id)
            loser_name = game_state.get_player_name(loser_id) if loser_id else "error"

            difficulty = game_state.difficulty if hasattr(game_state, 'difficulty') else "Unknown"
            question_name = game_state.question_name if hasattr(game_state, 'question_name') else "Unknown"
            
            print(f"🏆 [GAME END DEBUG] Game {game_id} ended - Winner: {winner_name} ({game_state.winner_id})")
            
            await save_game_to_history(list(game_state.players.values()), difficulty, question_name, game_state.winner_id)

            (winner_lp_gain, loser_lp_loss) = games.get_lp_changes()

            # Send comprehensive game end event with winner info
            game_end_data = {
                "message": f"{winner_name} won the game!",
                "winner_id": game_state.winner_id,
                "winner_name": winner_name,
                "loser_id": loser_id,
                "loser_name": loser_name,
                "lp_loss": loser_lp_loss,
                "lp_gain": winner_lp_gain,
                "game_end_reason": 'Better Score',
            }
            
            await sio.emit("game_completed", game_end_data, room=game_id)
            logger.info(f"🏆 Game {game_id} completed - {winner_name} won!")

        if test_results.success:
            logger.info(
                f"All {test_results.total_passed} test cases passed successfully for player {player_id}."
            )
        else:
            total_failed = getattr(test_results, "total_failed", 0)
            logger.warning(
                f"{test_results.total_passed} out of {test_results.total_passed + total_failed} test cases passed for player {player_id}."
            )

        logger.info(
            f"Complexity analysis for player {player_id}: {complexity} timer {request.timer}ms"
        )
        finalTime = get_score(complexity, request.timer)
        logger.info(
            f"Final time for player {player_id} is {finalTime}ms based on complexity {complexity} and implementation time {request.timer}ms"
        )

        if(test_results.success):
            test_result.message = "All test cases passed successfully!"
        else:
            test_result.message = "Was not able to pass all test cases"

        return test_result

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
