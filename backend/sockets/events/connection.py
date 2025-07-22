"""
Connection event handlers for Socket.IO.
"""
import logging
from ..services.matchmaking_service import matchmaking_service
from typing import Dict
from backend.api import game

logger = logging.getLogger(__name__)

game_states: Dict[str, game.GameState] = {}

def set_dependencies(game_states_param=None):
    global game_states
    game_states = game_states_param


def register_events(sio):
    """Register connection events with the Socket.IO server."""
    
    @sio.event
    async def connect(sid, environ):
        """Handle client connection."""
        logger.info(f"Client {sid} connected")
        await sio.emit("connected", {"status": "connected", "sid": sid}, room=sid)
    
    @sio.event
    async def disconnect(sid):
        """Handle client disconnection."""
        # Remove player from queue if they disconnect
        removed_from_queue = matchmaking_service.remove_player_from_queue(sid)
        
        # Handle disconnection during active games
        active_games = [
            (game_id, state) for game_id, state in matchmaking_service.game_states.items()
            if any(player.sid == sid for player in state.players.values())
        ]
        
        for game_id, game_state in active_games:
            # Find which player disconnected
            disconnected_player_id = None
            for player_id, player_info in game_state.players.items():
                if player_info.sid == sid:
                    disconnected_player_id = player_id
                    break
            
            if disconnected_player_id and not game_state.is_game_ended():
                # Award win to remaining player
                opponent_id = game_state.get_opponent_id(disconnected_player_id)
                if opponent_id:
                    logger.info(f"🔌 [DISCONNECT] Player {disconnected_player_id} disconnected from game {game_id} - awarding win to {opponent_id}")
                    game_state.set_winner(opponent_id, "disconnection")
                    
                    # Send game end event to remaining player
                    opponent_name = game_state.get_player_name(opponent_id)
                    disconnected_name = game_state.get_player_name(disconnected_player_id)
                    
                    game_end_data = {
                        "message": f"{opponent_name} won! Opponent disconnected.",
                        "winner_id": opponent_id,
                        "winner_name": opponent_name,
                        "loser_id": disconnected_player_id,
                        "loser_name": disconnected_name,
                        "game_end_reason": "disconnection",
                        "game_end_time": game_state.game_end_time,
                        "winner_stats": {
                            "player_name": opponent_name,
                            "success": True
                        }
                    }
                    
                    await sio.emit("game_completed", game_end_data, room=game_id)
                    logger.info(f"🏆 Game {game_id} ended due to disconnection - {opponent_name} wins!")
        
        if removed_from_queue:
            logger.info(f"Client {sid} disconnected and removed from queue")
        else:
            logger.info(f"Client {sid} disconnected")