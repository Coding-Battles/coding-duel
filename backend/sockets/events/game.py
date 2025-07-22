"""
Game event handlers for Socket.IO.
"""

import logging
import time
from ..services.game_service import game_service
from ..services.matchmaking_service import matchmaking_service
from typing import Dict
from backend.models.core import GameState, PlayerStatus

logger = logging.getLogger(__name__)

game_states: Dict[str, GameState] = {}
# Timer management for delayed opponent code emission
code_timers: Dict[str, Dict[str, any]] = {}  # game_id -> {player_id -> timer_handle}
code_timer_start_times: Dict[str, Dict[str, float]] = {}  # game_id -> {player_id -> start_time}


def set_dependencies(game_states_param=None):
    global game_states
    game_states = game_states_param
    logger.info(
        f"🔧 [SYNC DEBUG] Socket events received game_states id: {id(game_states_param)}"
    )
    game_service.set_dependencies(game_states_param)


async def schedule_delayed_code_emission(
    sio, game_id: str, player_id: str, code: str, language: str
):
    """Schedule delayed emission of player code to opponent with smart debouncing."""
    import asyncio

    # Initialize game timers if not exists
    if game_id not in code_timers:
        code_timers[game_id] = {}
    if game_id not in code_timer_start_times:
        code_timer_start_times[game_id] = {}

    current_time = time.time()
    
    # Smart timer cancellation logic
    should_cancel_existing = False
    if player_id in code_timers[game_id]:
        existing_start_time = code_timer_start_times[game_id].get(player_id, 0)
        time_since_start = current_time - existing_start_time
        
        # Only cancel if timer has been running for less than 3 seconds
        # Or if it's been running for more than 45 seconds (fallback protection)
        if time_since_start < 3.0:
            should_cancel_existing = True
            logger.info(
                f"🚀 [CODE DEBUG] Cancelling recent timer for player {player_id} (running for {time_since_start:.1f}s)"
            )
        elif time_since_start > 45.0:
            should_cancel_existing = True
            logger.info(
                f"🚀 [CODE DEBUG] Cancelling stale timer for player {player_id} (running for {time_since_start:.1f}s)"
            )
        else:
            logger.info(
                f"🚀 [CODE DEBUG] Keeping existing timer for player {player_id} (running for {time_since_start:.1f}s)"
            )
            return  # Let the existing timer complete

    if should_cancel_existing:
        try:
            code_timers[game_id][player_id].cancel()
        except:
            pass

    async def emit_delayed_code():
        """Emit code to opponent after delay."""
        start_time = code_timer_start_times[game_id][player_id]
        try:
            await asyncio.sleep(30)  # 30-second delay

            # Verify game still exists
            if game_id not in game_states:
                logger.warning(
                    f"🚀 [CODE DEBUG] Game {game_id} no longer exists, skipping emission"
                )
                return

            game_state = game_states[game_id]

            # Use the centralized opponent lookup method
            opponent_id = game_state.get_opponent_id(player_id)
            if not opponent_id or opponent_id not in game_state.players:
                logger.warning(
                    f"🚀 [CODE DEBUG] Opponent not found for player {player_id}. opponent_id: {opponent_id}"
                )
                return

            # Get opponent's socket ID
            opponent_sid = game_state.players[opponent_id].sid

            logger.info(
                f"🚀 [CODE DEBUG] Successfully emitting delayed code from {player_id} to opponent {opponent_id} (sid: {opponent_sid}) after {time.time() - start_time:.1f}s"
            )

            # Emit code to opponent
            await sio.emit(
                "opponent_code_ready",
                {
                    "code": code,
                    "from_player": player_id,
                    "language": language,
                    "timestamp": time.time(),
                    "delay_duration": time.time() - start_time,
                },
                room=opponent_sid,
            )

            logger.info(
                f"🚀 [CODE DEBUG] ✅ Code emission completed successfully for player {player_id}"
            )

        except asyncio.CancelledError:
            elapsed = time.time() - start_time
            logger.info(f"🚀 [CODE DEBUG] ❌ Timer cancelled for player {player_id} after {elapsed:.1f}s")
            raise
        except Exception as e:
            elapsed = time.time() - start_time
            logger.error(f"🚀 [CODE DEBUG] ❌ Error emitting delayed code for player {player_id} after {elapsed:.1f}s: {e}")
        finally:
            # Clean up timer references
            if game_id in code_timers and player_id in code_timers[game_id]:
                del code_timers[game_id][player_id]
            if game_id in code_timer_start_times and player_id in code_timer_start_times[game_id]:
                del code_timer_start_times[game_id][player_id]

    # Store start time and create new timer
    code_timer_start_times[game_id][player_id] = current_time
    timer = asyncio.create_task(emit_delayed_code())
    code_timers[game_id][player_id] = timer

    logger.info(
        f"🚀 [CODE DEBUG] Scheduled delayed code emission for player {player_id} in 30 seconds (debounced)"
    )


def register_events(sio):
    """Register game events with the Socket.IO server."""

    @sio.event
    async def join_game(sid, data):
        """Handle player joining a game."""
        try:
            game_id = data.get("game_id")
            player_id = data.get("player_id")

            logger.info(
                f"🚀 [JOIN DEBUG] join_game called for game {game_id} by player {player_id} with sid {sid}"
            )

            if not game_id or not player_id:
                logger.error(
                    f"🚀 [JOIN DEBUG] Missing parameters: game_id={game_id}, player_id={player_id}"
                )
                await sio.emit(
                    "error", {"message": "Missing game_id or player_id"}, room=sid
                )
                return

            # Get game info from matchmaking service
            logger.info(
                f"🚀 [JOIN DEBUG] Getting game info from matchmaking service..."
            )
            game_info = matchmaking_service.get_game_info(game_id)
            if not game_info:
                logger.error(
                    f"🚀 [JOIN DEBUG] Game {game_id} not found in matchmaking service"
                )
                await sio.emit("error", {"message": "Game not found"}, room=sid)
                return

            logger.info(f"🚀 [JOIN DEBUG] Game info found: {game_info}")

            # Create game in game service if it doesn't exist
            game_state = game_service.get_game(game_id)
            if not game_state:
                logger.info(f"🚀 [JOIN DEBUG] Creating new game in game service...")

                # Convert Dict[str, PlayerInfo] to List[Dict[str, Any]] for game service
                players_list = [
                    {
                        "id": player_info.id,
                        "name": player_info.name,
                        "anonymous": player_info.anonymous,
                        "sid": player_info.sid,
                    }
                    for player_info in game_info.players.values()
                ]
                logger.info(
                    f"🚀 [JOIN DEBUG] Converted players dict to list: {players_list}"
                )

                game_state = game_service.create_game(
                    game_id=game_id,
                    question_name=game_info.question_name,
                    players=players_list,
                )
                logger.info(f"🚀 [JOIN DEBUG] Game created successfully")
            else:
                logger.info(f"🚀 [JOIN DEBUG] Game already exists in game service")

            # Join the game room
            await sio.enter_room(sid, game_id)
            logger.info(f"🚀 [JOIN DEBUG] Player added to room successfully")

            # Track player joining for game start synchronization
            if game_id in game_states:
                game_states[game_id].players_joined.add(player_id)
                logger.info(
                    f"🚀 [TIMER DEBUG] Player {player_id} joined. Players joined: {len(game_states[game_id].players_joined)}/2"
                )

                # Check if both players have joined to start the game
                if (
                    len(game_states[game_id].players_joined) == 2
                    and game_states[game_id].game_start_time is None
                ):
                    import time

                    game_states[game_id].game_start_time = time.time()
                    logger.info(
                        f"🚀 [TIMER DEBUG] Game {game_id} starting! Start time: {game_states[game_id].game_start_time}"
                    )

                    # Emit game_start event to all players in the game
                    await sio.emit(
                        "game_start",
                        {
                            "game_id": game_id,
                            "start_time": game_states[game_id].game_start_time,
                        },
                        room=game_id,
                    )
                    logger.info(
                        f"🚀 [TIMER DEBUG] Emitted game_start event to room {game_id}"
                    )

            # Send game state to player
            logger.info(f"🚀 [JOIN DEBUG] Sending game_joined event...")
            
            # Convert game state to dict with proper JSON serialization for all non-JSON types
            game_state_dict = None
            if game_state:
                game_state_dict = game_state.model_dump()
                # Convert Set fields to lists for JSON serialization
                if 'finished_players' in game_state_dict:
                    game_state_dict['finished_players'] = list(game_state_dict['finished_players'])
                if 'players_joined' in game_state_dict:
                    game_state_dict['players_joined'] = list(game_state_dict['players_joined'])
                # Convert datetime fields to ISO format strings for JSON serialization
                if 'created_at' in game_state_dict and game_state_dict['created_at']:
                    game_state_dict['created_at'] = game_state_dict['created_at'].isoformat()
            
            await sio.emit(
                "game_joined",
                {
                    "game_id": game_id,
                    "game_state": game_state_dict,
                    "start_time": (
                        game_states[game_id].game_start_time
                        if game_id in game_states
                        else None
                    ),
                },
                room=sid,
            )

            logger.info(
                f"🚀 [JOIN DEBUG] Player {player_id} successfully joined game {game_id}"
            )

        except Exception as e:
            import traceback
            logger.error(f"❌ [JOIN DEBUG] Error in join_game: {e}")
            logger.error(f"❌ [JOIN DEBUG] Traceback: {traceback.format_exc()}")
            logger.error(f"❌ [JOIN DEBUG] Game ID: {data.get('game_id')}, Player ID: {data.get('player_id')}")
            await sio.emit("error", {"message": "Failed to join game"}, room=sid)

    @sio.event
    async def code_update(sid, data):
        """Handle real-time code updates with language awareness."""
        try:
            game_id = data.get("game_id")
            player_id = data.get("player_id")
            code = data.get("code", "")
            language = data.get(
                "language", "python"
            )  # Default to python if not specified

            logger.info(
                f"🚀 [LANG DEBUG] code_update called for game {game_id} by player {player_id}, language: {language}, code length: {len(code)}"
            )

            if not game_id or not player_id:
                logger.error(
                    f"🚀 [LANG DEBUG] Missing parameters: game_id={game_id}, player_id={player_id}"
                )
                await sio.emit(
                    "error", {"message": "Missing game_id or player_id"}, room=sid
                )
                return

            # Update code in game_states (same storage as emoji system)
            logger.info(f"🚀 [CODE UPDATE DEBUG] Updating code in game_states...")
            logger.info(
                f"🚀 [CODE UPDATE DEBUG] Available game_states keys: {list(game_states.keys())}"
            )

            if game_id not in game_states:
                logger.error(
                    f"🚀 [CODE UPDATE DEBUG] Game {game_id} not found in game_states"
                )
                await sio.emit("error", {"message": "Game not found"}, room=sid)
                return

            game_state = game_states[game_id]

            # Initialize language-specific storage if needed
            if player_id not in game_state.player_codes:
                game_state.player_codes[player_id] = {}
            if player_id not in game_state.player_code_timestamps:
                game_state.player_code_timestamps[player_id] = {}

            # Update current language for player
            old_language = game_state.current_languages.get(player_id)
            game_state.current_languages[player_id] = language

            # Check if language changed
            language_changed = old_language is not None and old_language != language
            if language_changed:
                logger.info(
                    f"🚀 [CODE DEBUG] Player {player_id} changed language from {old_language} to {language}"
                )
                # Broadcast language change immediately
                await sio.emit(
                    "player_language_changed",
                    {
                        "player_id": player_id,
                        "language": language,
                        "immediate": True,
                    },
                    room=game_id,
                    skip_sid=sid,
                )

            # Update player's code for current language
            game_state.player_codes[player_id][language] = code
            game_state.player_code_timestamps[player_id][language] = time.time()
            logger.info(
                f"🚀 [LANG DEBUG] Updated {player_id} code for language {language}, timestamp: {game_state.player_code_timestamps[player_id][language]}"
            )

            # Update legacy fields for backward compatibility
            if player_id == game_state.player1:
                game_state.player1_code = code
                game_state.player1_code_timestamp = time.time()
            elif player_id == game_state.player2:
                game_state.player2_code = code
                game_state.player2_code_timestamp = time.time()

            logger.info(
                f"🚀 [CODE DEBUG] Code updated successfully, scheduling 30-second delayed emission..."
            )

            # Simple 30-second delay for all code changes
            await schedule_delayed_code_emission(
                sio, game_id, player_id, code, language
            )

            # Broadcast code update notification to game room
            await sio.emit(
                "player_code_updated",
                {"player_id": player_id, "timestamp": time.time()},
                room=game_id,
                skip_sid=sid,
            )

            logger.info(f"🚀 [CODE UPDATE DEBUG] Code update broadcast successfully")

        except Exception as e:
            logger.error(f"Error in code_update: {e}")
            await sio.emit("error", {"message": "Failed to update code"}, room=sid)

    @sio.event
    async def instant_code_update(sid, data):
        """Handle instant code updates that bypass the 30-second delay."""
        try:
            game_id = data.get("game_id")
            player_id = data.get("player_id")
            code = data.get("code", "")
            language = data.get("language", "python")
            reason = data.get("reason", "unknown")

            logger.info(
                f"🚀 [INSTANT DEBUG] instant_code_update called for game {game_id} by player {player_id}, reason: {reason}, language: {language}, code length: {len(code)}"
            )

            if not game_id or not player_id:
                logger.error(
                    f"🚀 [INSTANT DEBUG] Missing parameters: game_id={game_id}, player_id={player_id}"
                )
                await sio.emit(
                    "error", {"message": "Missing game_id or player_id"}, room=sid
                )
                return

            # Update code in game_states
            if game_id not in game_states:
                logger.error(
                    f"🚀 [INSTANT DEBUG] Game {game_id} not found in game_states"
                )
                await sio.emit("error", {"message": "Game not found"}, room=sid)
                return

            game_state = game_states[game_id]

            # Initialize language-specific storage if needed
            if player_id not in game_state.player_codes:
                game_state.player_codes[player_id] = {}
            if player_id not in game_state.player_code_timestamps:
                game_state.player_code_timestamps[player_id] = {}

            # Update current language for player
            game_state.current_languages[player_id] = language

            # Update player's code for current language
            game_state.player_codes[player_id][language] = code
            game_state.player_code_timestamps[player_id][language] = time.time()

            # Update legacy fields for backward compatibility
            if player_id == game_state.player1:
                game_state.player1_code = code
                game_state.player1_code_timestamp = time.time()
            elif player_id == game_state.player2:
                game_state.player2_code = code
                game_state.player2_code_timestamp = time.time()

            # Determine opponent
            opponent_id = None
            if player_id == game_state.player1:
                opponent_id = game_state.player2
            elif player_id == game_state.player2:
                opponent_id = game_state.player1

            logger.info(
                f"🚀 [INSTANT DEBUG] Game state - player1: {game_state.player1}, player2: {game_state.player2}, current player: {player_id}, opponent: {opponent_id}"
            )
            logger.info(
                f"🚀 [INSTANT DEBUG] Players in game_state.players: {list(game_state.players.keys())}"
            )

            # Cancel any existing delayed timer for this player
            if game_id in code_timers and player_id in code_timers[game_id]:
                try:
                    code_timers[game_id][player_id].cancel()
                    logger.info(
                        f"🚀 [INSTANT DEBUG] Cancelled existing delayed timer for player {player_id}"
                    )
                except:
                    pass

            # Emit code to opponent immediately
            if opponent_id and opponent_id in game_state.players:
                opponent_sid = game_state.players[opponent_id].sid

                logger.info(
                    f"🚀 [INSTANT DEBUG] Emitting instant code update to opponent {opponent_id} (sid: {opponent_sid}) (reason: {reason})"
                )

                await sio.emit(
                    "opponent_code_ready",
                    {
                        "code": code,
                        "from_player": player_id,
                        "language": language,
                        "timestamp": time.time(),
                        "instant": True,
                        "reason": reason,
                    },
                    room=opponent_sid,
                )
            else:
                logger.warning(
                    f"🚀 [INSTANT DEBUG] Cannot emit to opponent - opponent_id: {opponent_id}, opponent in players: {opponent_id in game_state.players if opponent_id else False}"
                )

            # Broadcast code update notification to game room
            await sio.emit(
                "player_code_updated",
                {"player_id": player_id, "timestamp": time.time(), "instant": True},
                room=game_id,
                skip_sid=sid,
            )

            logger.info(
                f"🚀 [INSTANT DEBUG] Instant code update broadcast successfully"
            )

        except Exception as e:
            logger.error(f"🚀 [INSTANT DEBUG] Error in instant_code_update: {e}")
            logger.error(f"🚀 [INSTANT DEBUG] Exception type: {type(e).__name__}")
            logger.error(f"🚀 [INSTANT DEBUG] Exception args: {e.args}")
            await sio.emit(
                "error", {"message": "Failed to update code instantly"}, room=sid
            )

    @sio.event
    async def player_status_update(sid, data):
        """Handle player status updates (typing, running, etc.)."""
        try:
            game_id = data.get("game_id")
            player_id = data.get("player_id")
            status = data.get("status")
            extra_data = data.get("data", {})

            if not game_id or not player_id or not status:
                await sio.emit(
                    "error", {"message": "Missing required fields"}, room=sid
                )
                return

            # Update status in game service
            success = game_service.update_player_status(
                game_id, player_id, PlayerStatus(status), extra_data
            )
            if not success:
                await sio.emit(
                    "error", {"message": "Failed to update status"}, room=sid
                )
                return

            # Broadcast status update to game room
            await sio.emit(
                "player_status_changed",
                {"player_id": player_id, "status": status, "data": extra_data},
                room=game_id,
            )

        except Exception as e:
            logger.error(f"Error in player_status_update: {e}")
            await sio.emit("error", {"message": "Failed to update status"}, room=sid)

    @sio.event
    async def submit_solution(sid, data):
        """Handle solution submission."""
        try:
            game_id = data.get("game_id")
            player_id = data.get("player_id")
            submission_data = data.get("submission", {})

            if not game_id or not player_id:
                await sio.emit(
                    "error", {"message": "Missing game_id or player_id"}, room=sid
                )
                return

            # Process submission in game service
            success = game_service.submit_solution(game_id, player_id, submission_data)
            if not success:
                await sio.emit(
                    "error", {"message": "Failed to submit solution"}, room=sid
                )
                return

            # Get updated game state
            game_state = game_service.get_game(game_id)

            # Broadcast submission to game room
            await sio.emit(
                "solution_submitted",
                {
                    "player_id": player_id,
                    "submission": submission_data,
                    "game_state": game_state.model_dump() if game_state else None,
                },
                room=game_id,
            )

            # If game is finished, notify players
            if game_state and game_state.status.value == "finished":
                await sio.emit(
                    "game_finished",
                    {
                        "winner": game_state.winner,
                        "game_state": game_state.model_dump(),
                    },
                    room=game_id,
                )

                # End game in matchmaking service
                matchmaking_service.end_game(game_id)

        except Exception as e:
            logger.error(f"Error in submit_solution: {e}")
            await sio.emit("error", {"message": "Failed to submit solution"}, room=sid)

    @sio.event
    async def leave_game(sid, data):
        """Handle player leaving a game."""
        try:
            game_id = data.get("game_id")
            player_id = data.get("player_id")

            if not game_id or not player_id:
                await sio.emit(
                    "error", {"message": "Missing game_id or player_id"}, room=sid
                )
                return

            # Leave the game room
            await sio.leave_room(sid, game_id)

            # End the game if player abandons
            game_service.end_game(game_id, reason="abandoned")

            # Notify remaining players
            await sio.emit(
                "player_left",
                {"player_id": player_id, "game_ended": True},
                room=game_id,
            )

            await sio.emit("game_left", {"status": "success"}, room=sid)

            logger.info(f"Player {player_id} left game {game_id}")

        except Exception as e:
            logger.error(f"Error in leave_game: {e}")
            await sio.emit("error", {"message": "Failed to leave game"}, room=sid)
