"""
Game event handlers for Socket.IO.
"""
import logging
import time
from ..services.game_service import game_service, PlayerStatus
from ..services.matchmaking_service import matchmaking_service
from typing import Dict
from backend.api import game

logger = logging.getLogger(__name__)

game_states: Dict[str, game.GameState] = {}
# Timer management for delayed opponent code emission
code_timers: Dict[str, Dict[str, any]] = {}  # game_id -> {player_id -> timer_handle}

def set_dependencies(game_states_param=None):
    global game_states
    game_states = game_states_param
    logger.info(f"🔧 [SYNC DEBUG] Socket events received game_states id: {id(game_states_param)}")
    game_service.set_dependencies(game_states_param)

def is_starter_code(code: str, language: str, game_state) -> bool:
    """Check if the provided code matches the starter code for the language."""
    if not game_state.starter_codes:
        return False
    
    starter_code = game_state.starter_codes.get(language, "")
    # Strip whitespace for comparison to handle minor formatting differences
    return code.strip() == starter_code.strip()

async def schedule_delayed_code_emission(sio, game_id: str, player_id: str, code: str, language: str):
    """Schedule delayed emission of player code to opponent after 30 seconds."""
    import asyncio
    
    # Initialize game timers if not exists
    if game_id not in code_timers:
        code_timers[game_id] = {}
    
    # Cancel existing timer for this player
    if player_id in code_timers[game_id]:
        try:
            code_timers[game_id][player_id].cancel()
            logger.info(f"🚀 [PUSH DEBUG] Cancelled existing timer for player {player_id}")
        except:
            pass
    
    async def emit_delayed_code():
        """Emit code to opponent after delay."""
        try:
            await asyncio.sleep(30)  # 30-second delay
            
            # Verify game still exists
            if game_id not in game_states:
                logger.warning(f"🚀 [PUSH DEBUG] Game {game_id} no longer exists, skipping emission")
                return
            
            game_state = game_states[game_id]
            
            # Determine opponent
            opponent_id = None
            if player_id == game_state.player1:
                opponent_id = game_state.player2
            elif player_id == game_state.player2:
                opponent_id = game_state.player1
            
            if not opponent_id or opponent_id not in game_state.players:
                logger.warning(f"🚀 [PUSH DEBUG] Opponent not found for player {player_id}")
                return
            
            # Get opponent's socket ID
            opponent_sid = game_state.players[opponent_id].sid
            
            logger.info(f"🚀 [PUSH DEBUG] Emitting delayed code from {player_id} to opponent {opponent_id} (sid: {opponent_sid})")
            
            # Emit code to opponent (no language filtering - always show code)
            await sio.emit("opponent_code_ready", {
                "code": code,
                "from_player": player_id,
                "language": language,
                "timestamp": time.time()
            }, room=opponent_sid)
            
            logger.info(f"🚀 [PUSH DEBUG] Successfully emitted delayed code to opponent")
            
        except asyncio.CancelledError:
            logger.info(f"🚀 [PUSH DEBUG] Timer cancelled for player {player_id}")
        except Exception as e:
            logger.error(f"🚀 [PUSH DEBUG] Error emitting delayed code: {e}")
        finally:
            # Clean up timer reference
            if game_id in code_timers and player_id in code_timers[game_id]:
                del code_timers[game_id][player_id]
    
    # Create and store new timer
    timer = asyncio.create_task(emit_delayed_code())
    code_timers[game_id][player_id] = timer
    
    logger.info(f"🚀 [PUSH DEBUG] Scheduled delayed code emission for player {player_id} in 30 seconds")

async def schedule_delayed_language_change(sio, game_id: str, player_id: str, language: str):
    """Schedule delayed language change broadcast after 30 seconds."""
    import asyncio
    
    # Initialize game timers if not exists
    if game_id not in code_timers:
        code_timers[game_id] = {}
    
    # Use special key for language change timers
    timer_key = f"{player_id}_lang"
    
    # Cancel existing language change timer for this player
    if timer_key in code_timers[game_id]:
        try:
            code_timers[game_id][timer_key].cancel()
            logger.info(f"🚀 [LANG DEBUG] Cancelled existing language change timer for player {player_id}")
        except:
            pass
    
    async def emit_delayed_language_change():
        """Emit language change to opponent after delay."""
        try:
            await asyncio.sleep(30)  # 30-second delay
            
            # Verify game still exists
            if game_id not in game_states:
                logger.warning(f"🚀 [LANG DEBUG] Game {game_id} no longer exists, skipping language change broadcast")
                return
            
            game_state = game_states[game_id]
            
            # Update the actual current language (now that delay has passed)
            game_state.current_languages[player_id] = language
            
            logger.info(f"🚀 [LANG DEBUG] Broadcasting delayed language change for player {player_id} to {language}")
            
            # Broadcast language change to all players in game
            await sio.emit("player_language_changed", {
                "player_id": player_id,
                "language": language,
                "immediate": False
            }, room=game_id)
            
            logger.info(f"🚀 [LANG DEBUG] Successfully broadcasted delayed language change")
            
        except asyncio.CancelledError:
            logger.info(f"🚀 [LANG DEBUG] Language change timer cancelled for player {player_id}")
        except Exception as e:
            logger.error(f"🚀 [LANG DEBUG] Error broadcasting delayed language change: {e}")
        finally:
            # Clean up timer reference
            if game_id in code_timers and timer_key in code_timers[game_id]:
                del code_timers[game_id][timer_key]
    
    # Create and store new timer
    timer = asyncio.create_task(emit_delayed_language_change())
    code_timers[game_id][timer_key] = timer
    
    logger.info(f"🚀 [LANG DEBUG] Scheduled delayed language change for player {player_id} to {language} in 30 seconds")

def register_events(sio):
    """Register game events with the Socket.IO server."""

    @sio.event
    async def join_game(sid, data):
        """Handle player joining a game."""
        try:
            game_id = data.get("game_id")
            player_id = data.get("player_id")
            
            logger.info(f"🚀 [JOIN DEBUG] join_game called for game {game_id} by player {player_id} with sid {sid}")
            
            if not game_id or not player_id:
                logger.error(f"🚀 [JOIN DEBUG] Missing parameters: game_id={game_id}, player_id={player_id}")
                await sio.emit("error", {"message": "Missing game_id or player_id"}, room=sid)
                return
            
            # Get game info from matchmaking service
            logger.info(f"🚀 [JOIN DEBUG] Getting game info from matchmaking service...")
            game_info = matchmaking_service.get_game_info(game_id)
            if not game_info:
                logger.error(f"🚀 [JOIN DEBUG] Game {game_id} not found in matchmaking service")
                await sio.emit("error", {"message": "Game not found"}, room=sid)
                return
            
            logger.info(f"🚀 [JOIN DEBUG] Game info found: {game_info}")
            
            # Create game in game service if it doesn't exist
            logger.info(f"🚀 [JOIN DEBUG] Checking if game exists in game service...")
            game_state = game_service.get_game(game_id)
            if not game_state:
                logger.info(f"🚀 [JOIN DEBUG] Creating new game in game service...")
                
                # Convert Dict[str, PlayerInfo] to List[Dict[str, Any]] for game service
                players_list = [
                    {
                        "id": player_info.id,
                        "name": player_info.name,
                        "anonymous": player_info.anonymous,
                        "sid": player_info.sid
                    }
                    for player_info in game_info.players.values()
                ]
                logger.info(f"🚀 [JOIN DEBUG] Converted players dict to list: {players_list}")
                
                game_state = game_service.create_game(
                    game_id=game_id,
                    question_name=game_info.question_name,
                    players=players_list
                )
                logger.info(f"🚀 [JOIN DEBUG] Game created successfully")
                
                # Fetch and store starter codes for this question
                logger.info(f"🚀 [STARTER DEBUG] Fetching starter codes for question: {game_info.question_name}")
                try:
                    import aiohttp
                    import json
                    async with aiohttp.ClientSession() as session:
                        # Get the API base URL from environment or use default
                        import os
                        api_base = os.getenv("API_BASE_URL", "http://localhost:8000")
                        url = f"{api_base}/get-question/{game_info.question_name}"
                        logger.info(f"🚀 [STARTER DEBUG] Fetching from: {url}")
                        
                        async with session.get(url) as response:
                            if response.status == 200:
                                question_data = await response.json()
                                starter_code = question_data.get("starter_code", {})
                                
                                # Store starter codes in game state
                                if game_id in game_states:
                                    game_states[game_id].starter_codes = starter_code
                                    logger.info(f"🚀 [STARTER DEBUG] Stored starter codes: {list(starter_code.keys())}")
                                else:
                                    logger.warning(f"🚀 [STARTER DEBUG] Game {game_id} not found in game_states for starter code storage")
                            else:
                                logger.error(f"🚀 [STARTER DEBUG] Failed to fetch question data: {response.status}")
                except Exception as e:
                    logger.error(f"🚀 [STARTER DEBUG] Error fetching starter codes: {e}")
            else:
                logger.info(f"🚀 [JOIN DEBUG] Game already exists in game service")
            
            # Join the game room
            logger.info(f"🚀 [JOIN DEBUG] Adding player to game room {game_id}...")
            await sio.enter_room(sid, game_id)
            logger.info(f"🚀 [JOIN DEBUG] Player added to room successfully")
            
            # Track player joining for game start synchronization
            if game_id in game_states:
                game_states[game_id].players_joined.add(player_id)
                logger.info(f"🚀 [TIMER DEBUG] Player {player_id} joined. Players joined: {len(game_states[game_id].players_joined)}/2")
                
                # Check if both players have joined to start the game
                if len(game_states[game_id].players_joined) == 2 and game_states[game_id].game_start_time is None:
                    import time
                    game_states[game_id].game_start_time = time.time()
                    logger.info(f"🚀 [TIMER DEBUG] Game {game_id} starting! Start time: {game_states[game_id].game_start_time}")
                    
                    # Emit game_start event to all players in the game
                    await sio.emit("game_start", {
                        "game_id": game_id,
                        "start_time": game_states[game_id].game_start_time
                    }, room=game_id)
                    logger.info(f"🚀 [TIMER DEBUG] Emitted game_start event to room {game_id}")
            
            # Send game state to player
            logger.info(f"🚀 [JOIN DEBUG] Sending game_joined event...")
            await sio.emit("game_joined", {
                "game_id": game_id,
                "game_state": game_state.model_dump() if game_state else None,
                "start_time": game_states[game_id].game_start_time if game_id in game_states else None
            }, room=sid)
            
            logger.info(f"🚀 [JOIN DEBUG] Player {player_id} successfully joined game {game_id}")
            
        except Exception as e:
            logger.error(f"🚀 [JOIN DEBUG] Error in join_game: {e}")
            logger.error(f"🚀 [JOIN DEBUG] Exception type: {type(e).__name__}")
            logger.error(f"🚀 [JOIN DEBUG] Exception args: {e.args}")
            await sio.emit("error", {"message": "Failed to join game"}, room=sid)
    
    @sio.event
    async def code_update(sid, data):
        """Handle real-time code updates with language awareness."""
        try:
            game_id = data.get("game_id")
            player_id = data.get("player_id")
            code = data.get("code", "")
            language = data.get("language", "python")  # Default to python if not specified
            
            logger.info(f"🚀 [LANG DEBUG] code_update called for game {game_id} by player {player_id}, language: {language}, code length: {len(code)}")
            
            if not game_id or not player_id:
                logger.error(f"🚀 [LANG DEBUG] Missing parameters: game_id={game_id}, player_id={player_id}")
                await sio.emit("error", {"message": "Missing game_id or player_id"}, room=sid)
                return
            
            # Update code in game_states (same storage as emoji system)
            logger.info(f"🚀 [CODE UPDATE DEBUG] Updating code in game_states...")
            logger.info(f"🚀 [CODE UPDATE DEBUG] Available game_states keys: {list(game_states.keys())}")
            
            if game_id not in game_states:
                logger.error(f"🚀 [CODE UPDATE DEBUG] Game {game_id} not found in game_states")
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
                logger.info(f"🚀 [LANG DEBUG] Player {player_id} changed language from {old_language} to {language}")
                
                # Check if we're in the first 30 seconds of the game
                game_time = time.time() - game_state.game_start_time if game_state.game_start_time else 0
                if game_time < 30:
                    logger.info(f"🚀 [LANG DEBUG] Language change allowed immediately (game_time: {game_time}s)")
                    # Immediately broadcast language change
                    await sio.emit("player_language_changed", {
                        "player_id": player_id,
                        "language": language,
                        "immediate": True
                    }, room=game_id, skip_sid=sid)
                else:
                    logger.info(f"🚀 [LANG DEBUG] Language change delayed (game_time: {game_time}s)")
                    # Schedule delayed language change broadcast
                    await schedule_delayed_language_change(sio, game_id, player_id, language)
                    return  # Don't process code update until language change is broadcasted
            
            # Update player's code for current language
            game_state.player_codes[player_id][language] = code
            game_state.player_code_timestamps[player_id][language] = time.time()
            logger.info(f"🚀 [LANG DEBUG] Updated {player_id} code for language {language}, timestamp: {game_state.player_code_timestamps[player_id][language]}")
            
            # Update legacy fields for backward compatibility
            if player_id == game_state.player1:
                game_state.player1_code = code
                game_state.player1_code_timestamp = time.time()
            elif player_id == game_state.player2:
                game_state.player2_code = code
                game_state.player2_code_timestamp = time.time()
            
            logger.info(f"🚀 [LANG DEBUG] Code updated successfully, determining emission timing...")
            
            # Check if we're in the first 30 seconds of the game
            game_time = time.time() - game_state.game_start_time if game_state.game_start_time else 0
            is_early_game = game_time < 30
            is_starter = is_starter_code(code, language, game_state)
            
            # Determine opponent
            opponent_id = None
            if player_id == game_state.player1:
                opponent_id = game_state.player2
            elif player_id == game_state.player2:
                opponent_id = game_state.player1
            
            should_emit_immediately = False
            
            if is_early_game and is_starter:
                # First 30s + starter code = immediate
                logger.info(f"🚀 [LANG DEBUG] Game time {game_time}s < 30s + starter code, emitting immediately")
                should_emit_immediately = True
            elif not is_early_game and language_changed:
                # After 30s + language change = immediate (regardless of starter/modified code)
                logger.info(f"🚀 [LANG DEBUG] Game time {game_time}s >= 30s + language change, emitting immediately")
                should_emit_immediately = True
            elif is_early_game and not is_starter:
                # First 30s + modified code = delayed
                logger.info(f"🚀 [LANG DEBUG] Game time {game_time}s < 30s + modified code, scheduling delayed emission")
                should_emit_immediately = False
            else:
                # After 30s + regular code update = delayed
                logger.info(f"🚀 [LANG DEBUG] Game time {game_time}s >= 30s + regular update, scheduling delayed emission")
                should_emit_immediately = False
            
            if should_emit_immediately and opponent_id and opponent_id in game_state.players:
                # Get opponent's socket ID
                opponent_sid = game_state.players[opponent_id].sid
                
                logger.info(f"🚀 [LANG DEBUG] Emitting code immediately to opponent {opponent_id}")
                # Emit code to opponent immediately (no language filtering)
                await sio.emit("opponent_code_ready", {
                    "code": code,
                    "from_player": player_id,
                    "language": language,
                    "timestamp": time.time()
                }, room=opponent_sid)
            elif not should_emit_immediately:
                # Schedule delayed emission of code to opponent (after 30 seconds)
                await schedule_delayed_code_emission(sio, game_id, player_id, code, language)
            
            # Broadcast code update notification to game room
            await sio.emit("player_code_updated", {
                "player_id": player_id,
                "timestamp": time.time()
            }, room=game_id, skip_sid=sid)
            
            logger.info(f"🚀 [CODE UPDATE DEBUG] Code update broadcast successfully")
            
        except Exception as e:
            logger.error(f"🚀 [CODE UPDATE DEBUG] Error in code_update: {e}")
            logger.error(f"🚀 [CODE UPDATE DEBUG] Exception type: {type(e).__name__}")
            logger.error(f"🚀 [CODE UPDATE DEBUG] Exception args: {e.args}")
            await sio.emit("error", {"message": "Failed to update code"}, room=sid)
    
    @sio.event
    async def player_status_update(sid, data):
        """Handle player status updates (typing, running, etc.)."""
        try:
            game_id = data.get("game_id")
            player_id = data.get("player_id")
            status = data.get("status")
            extra_data = data.get("data", {})
            
            if not game_id or not player_id or not status:
                await sio.emit("error", {"message": "Missing required fields"}, room=sid)
                return
            
            # Update status in game service
            success = game_service.update_player_status(game_id, player_id, PlayerStatus(status), extra_data)
            if not success:
                await sio.emit("error", {"message": "Failed to update status"}, room=sid)
                return
            
            # Broadcast status update to game room
            await sio.emit("player_status_changed", {
                "player_id": player_id,
                "status": status,
                "data": extra_data
            }, room=game_id)
            
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
                await sio.emit("error", {"message": "Missing game_id or player_id"}, room=sid)
                return
            
            # Process submission in game service
            success = game_service.submit_solution(game_id, player_id, submission_data)
            if not success:
                await sio.emit("error", {"message": "Failed to submit solution"}, room=sid)
                return
            
            # Get updated game state
            game_state = game_service.get_game(game_id)
            
            # Broadcast submission to game room
            await sio.emit("solution_submitted", {
                "player_id": player_id,
                "submission": submission_data,
                "game_state": game_state.model_dump() if game_state else None
            }, room=game_id)
            
            # If game is finished, notify players
            if game_state and game_state.status.value == "finished":
                await sio.emit("game_finished", {
                    "winner": game_state.winner,
                    "game_state": game_state.model_dump()
                }, room=game_id)
                
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
                await sio.emit("error", {"message": "Missing game_id or player_id"}, room=sid)
                return
            
            # Leave the game room
            await sio.leave_room(sid, game_id)
            
            # End the game if player abandons
            game_service.end_game(game_id, reason="abandoned")
            
            # Notify remaining players
            await sio.emit("player_left", {
                "player_id": player_id,
                "game_ended": True
            }, room=game_id)
            
            await sio.emit("game_left", {"status": "success"}, room=sid)
            
            logger.info(f"Player {player_id} left game {game_id}")
            
        except Exception as e:
            logger.error(f"Error in leave_game: {e}")
            await sio.emit("error", {"message": "Failed to leave game"}, room=sid)
