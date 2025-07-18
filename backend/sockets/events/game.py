"""
Game event handlers for Socket.IO.
"""
import logging
from ..services.game_service import game_service, PlayerStatus
from ..services.matchmaking_service import matchmaking_service
from typing import Dict
from backend.api import game

logger = logging.getLogger(__name__)

game_states: Dict[str, game.GameState] = {}
sio_instance = None

def set_dependencies(game_states_param=None):
    global game_states
    game_states = game_states_param
    game_service.set_dependencies(game_states_param)

def register_events(sio):
    """Register game events with the Socket.IO server."""

    global sio_instance
    sio_instance = sio
    
    @sio.event
    async def join_game(sid, data):
        """Handle player joining a game."""
        try:
            game_id = data.get("game_id")
            player_id = data.get("player_id")
            
            if not game_id or not player_id:
                await sio.emit("error", {"message": "Missing game_id or player_id"}, room=sid)
                return
            
            # Get game info from matchmaking service
            game_info = matchmaking_service.get_game_info(game_id)
            if not game_info:
                await sio.emit("error", {"message": "Game not found"}, room=sid)
                return
            
            # Create game in game service if it doesn't exist
            game_state = game_service.get_game(game_id)
            if not game_state:
                game_state = game_service.create_game(
                    game_id=game_id,
                    question_name=game_info["question_name"],
                    players=game_info["players"]
                )
            
            # Join the game room
            await sio.enter_room(sid, game_id)
            
            # Send game state to player
            await sio.emit("game_joined", {
                "game_id": game_id,
                "game_state": game_state.model_dump()
            }, room=sid)
            
            logger.info(f"Player {player_id} joined game {game_id}")
            
        except Exception as e:
            logger.error(f"Error in join_game: {e}")
            await sio.emit("error", {"message": "Failed to join game"}, room=sid)
    
    @sio.event
    async def code_update(sid, data):
        """Handle real-time code updates."""
        try:
            game_id = data.get("game_id")
            player_id = data.get("player_id")
            code = data.get("code", "")
            
            if not game_id or not player_id:
                await sio.emit("error", {"message": "Missing game_id or player_id"}, room=sid)
                return
            
            # Update code in game service
            success = game_service.update_player_code(game_id, player_id, code)
            if not success:
                await sio.emit("error", {"message": "Failed to update code"}, room=sid)
                return
            
            # Broadcast code update to game room (opponents will see it with delay)
            await sio.emit("player_code_updated", {
                "player_id": player_id,
                "timestamp": game_service.get_game_updates(game_id)[-1].timestamp
            }, room=game_id, skip_sid=sid)
            
        except Exception as e:
            logger.error(f"Error in code_update: {e}")
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
            
            if not game_id or not player_id:
                await sio.emit("error", {"message": "Missing game_id or player_id"}, room=sid)
                return
            
            # Get opponent's code with 30-second delay
            opponent_code = game_service.get_opponent_code(game_id, player_id, delay_seconds=30)
            
            await sio.emit("opponent_code", {
                "code": opponent_code,
                "available": opponent_code is not None
            }, room=sid)
            
        except Exception as e:
            logger.error(f"Error in get_opponent_code: {e}")
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
