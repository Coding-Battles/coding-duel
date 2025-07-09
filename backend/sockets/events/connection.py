"""
Connection event handlers for Socket.IO.
"""
import logging
from ..services.matchmaking_service import matchmaking_service

logger = logging.getLogger(__name__)


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
        active_games = [
            game_id for game_id, game_info in matchmaking_service.active_games.items()
            if any(player["sid"] == sid for player in game_info["players"])
        ]
        
        if active_games:
            logger.warning(f"Client {sid} disconnected during active game(s): {active_games}")
            # TODO: Notify opponent and handle game state
        
        if removed_from_queue:
            logger.info(f"Client {sid} disconnected and removed from queue. Queue size: {len(matchmaking_service.waiting_players)}")
        else:
            logger.info(f"Client {sid} disconnected")