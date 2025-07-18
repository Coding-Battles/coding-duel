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
        
        # TODO: Handle disconnection during active games
        # For now, we'll just log it
        game_states = [
            game_id for game_id, state in matchmaking_service.game_states.items()
            if any(player.sid == sid for player in state.players)
        ]
        
        if game_states:
            logger.warning(f"Client {sid} disconnected during active game(s): {game_states}")
            # TODO: Notify opponent and handle game state
        
        if removed_from_queue:
            logger.info(f"Client {sid} disconnected and removed from queue. Queue size: {len(matchmaking_service.waiting_players)}")
        else:
            logger.info(f"Client {sid} disconnected")