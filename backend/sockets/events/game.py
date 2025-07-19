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

def set_dependencies(game_states_param=None):
    global game_states
    game_states = game_states_param
    game_service.set_dependencies(game_states_param)

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
                game_state = game_service.create_game(
                    game_id=game_id,
                    question_name=game_info.question_name,
                    players=game_info.players
                )
                logger.info(f"🚀 [JOIN DEBUG] Game created successfully")
            else:
                logger.info(f"🚀 [JOIN DEBUG] Game already exists in game service")
            
            # Join the game room
            logger.info(f"🚀 [JOIN DEBUG] Adding player to game room {game_id}...")
            await sio.enter_room(sid, game_id)
            logger.info(f"🚀 [JOIN DEBUG] Player added to room successfully")
            
            # Send game state to player
            logger.info(f"🚀 [JOIN DEBUG] Sending game_joined event...")
            await sio.emit("game_joined", {
                "game_id": game_id,
                "game_state": game_state.model_dump()
            }, room=sid)
            
            logger.info(f"🚀 [JOIN DEBUG] Player {player_id} successfully joined game {game_id}")
            
        except Exception as e:
            logger.error(f"🚀 [JOIN DEBUG] Error in join_game: {e}")
            logger.error(f"🚀 [JOIN DEBUG] Exception type: {type(e).__name__}")
            logger.error(f"🚀 [JOIN DEBUG] Exception args: {e.args}")
            await sio.emit("error", {"message": "Failed to join game"}, room=sid)
    
    @sio.event
    async def code_update(sid, data):
        """Handle real-time code updates."""
        try:
            game_id = data.get("game_id")
            player_id = data.get("player_id")
            code = data.get("code", "")
            
            logger.info(f"🚀 [CODE UPDATE DEBUG] code_update called for game {game_id} by player {player_id}, code length: {len(code)}")
            
            if not game_id or not player_id:
                logger.error(f"🚀 [CODE UPDATE DEBUG] Missing parameters: game_id={game_id}, player_id={player_id}")
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
            
            # Update player's code and timestamp
            if player_id == game_state.player1:
                game_state.player1_code = code
                game_state.player1_code_timestamp = time.time()
                logger.info(f"🚀 [CODE UPDATE DEBUG] Updated player1 code, timestamp: {game_state.player1_code_timestamp}")
            elif player_id == game_state.player2:
                game_state.player2_code = code
                game_state.player2_code_timestamp = time.time()
                logger.info(f"🚀 [CODE UPDATE DEBUG] Updated player2 code, timestamp: {game_state.player2_code_timestamp}")
            else:
                logger.error(f"🚀 [CODE UPDATE DEBUG] Player {player_id} not found in game")
                await sio.emit("error", {"message": "Player not found in game"}, room=sid)
                return
            
            logger.info(f"🚀 [CODE UPDATE DEBUG] Code updated successfully, broadcasting to room...")
            
            # Broadcast code update to game room (opponents will see it with delay)
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
    async def get_opponent_code(sid, data):
        """Get opponent's code with delay."""
        try:
            game_id = data.get("game_id")
            player_id = data.get("player_id")
            
            logger.info(f"🚀 [CODE DEBUG] get_opponent_code called for game {game_id} by player {player_id}")
            
            if not game_id or not player_id:
                logger.error(f"🚀 [CODE DEBUG] Missing parameters: game_id={game_id}, player_id={player_id}")
                await sio.emit("error", {"message": "Missing game_id or player_id"}, room=sid)
                return
            
            # Get opponent's code using game_states (same storage as emoji system)
            logger.info(f"🚀 [CODE DEBUG] Looking for game in game_states...")
            logger.info(f"🚀 [CODE DEBUG] Available game_states keys: {list(game_states.keys())}")
            
            if game_id not in game_states:
                logger.error(f"🚀 [CODE DEBUG] Game {game_id} not found in game_states")
                await sio.emit("opponent_code", {
                    "code": None,
                    "available": False
                }, room=sid)
                return
            
            game_state = game_states[game_id]
            logger.info(f"🚀 [CODE DEBUG] Found game state for {game_id}")
            
            # Determine opponent and get their code with 30-second delay
            opponent_code = None
            opponent_code_timestamp = None
            
            if player_id == game_state.player1:
                # Current player is player1, get player2's code
                opponent_code = game_state.player2_code
                opponent_code_timestamp = getattr(game_state, 'player2_code_timestamp', None)
                logger.info(f"🚀 [CODE DEBUG] Player1 requesting player2 code, timestamp: {opponent_code_timestamp}")
            elif player_id == game_state.player2:
                # Current player is player2, get player1's code
                opponent_code = game_state.player1_code
                opponent_code_timestamp = getattr(game_state, 'player1_code_timestamp', None)
                logger.info(f"🚀 [CODE DEBUG] Player2 requesting player1 code, timestamp: {opponent_code_timestamp}")
            else:
                logger.error(f"🚀 [CODE DEBUG] Player {player_id} not found in game")
                await sio.emit("opponent_code", {
                    "code": None,
                    "available": False
                }, room=sid)
                return
            
            # Check if 30-second delay has passed
            current_time = time.time()
            delay_seconds = 30
            
            if opponent_code and opponent_code_timestamp:
                time_diff = current_time - opponent_code_timestamp
                logger.info(f"🚀 [CODE DEBUG] Time difference: {time_diff}s, required delay: {delay_seconds}s")
                
                if time_diff >= delay_seconds:
                    logger.info(f"🚀 [CODE DEBUG] Delay passed, returning opponent code (length: {len(opponent_code)})")
                    await sio.emit("opponent_code", {
                        "code": opponent_code,
                        "available": True
                    }, room=sid)
                else:
                    logger.info(f"🚀 [CODE DEBUG] Delay not yet passed, returning no code")
                    await sio.emit("opponent_code", {
                        "code": None,
                        "available": False
                    }, room=sid)
            else:
                logger.info(f"🚀 [CODE DEBUG] No opponent code available yet")
                await sio.emit("opponent_code", {
                    "code": None,
                    "available": False
                }, room=sid)
            
            logger.info(f"🚀 [CODE DEBUG] Emitted opponent_code event to room {sid}")
            
        except Exception as e:
            logger.error(f"🚀 [CODE DEBUG] Error in get_opponent_code: {e}")
            logger.error(f"🚀 [CODE DEBUG] Exception type: {type(e).__name__}")
            logger.error(f"🚀 [CODE DEBUG] Exception args: {e.args}")
            await sio.emit("error", {"message": "Failed to get opponent code"}, room=sid)
    
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
