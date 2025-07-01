"""
Matchmaking event handlers for Socket.IO.
"""
import logging
from pydantic import ValidationError
from ..services.matchmaking_service import matchmaking_service, MatchFoundResponse

logger = logging.getLogger(__name__)


def register_events(sio):
    """Register matchmaking events with the Socket.IO server."""
    
    @sio.event
    async def join_queue(sid, data):
        """Handle player joining the matchmaking queue."""
        try:
            # Add player to queue
            player = matchmaking_service.add_player_to_queue(data, sid)
            logger.info(f"Player {player.name} joined queue. Total players: {len(matchmaking_service.waiting_players)}")
            
            # Try to create a match
            match_result = matchmaking_service.try_create_match()
            
            if match_result:
                player1, player2, game_id = match_result
                
                # Send match found to both players
                match_response1 = MatchFoundResponse(
                    game_id=game_id,
                    opponent=player2.name,
                    question_name="two-sum"  # TODO: Dynamic question selection
                )
                await sio.emit("match_found", match_response1.model_dump(), room=player1.sid)
                
                match_response2 = MatchFoundResponse(
                    game_id=game_id,
                    opponent=player1.name,
                    question_name="two-sum"
                )
                await sio.emit("match_found", match_response2.model_dump(), room=player2.sid)
                
                logger.info(f"Match created: {player1.name} vs {player2.name} (Game: {game_id})")
            else:
                # Send queue status
                queue_status = matchmaking_service.get_queue_status()
                await sio.emit("queue_status", queue_status.model_dump(), room=sid)
                
        except ValidationError as e:
            logger.error(f"Validation error in join_queue: {e}")
            await sio.emit("error", {"message": "Invalid player data"}, room=sid)
        except Exception as e:
            logger.error(f"Unexpected error in join_queue: {e}")
            await sio.emit("error", {"message": "Internal server error"}, room=sid)
    
    @sio.event
    async def leave_queue(sid, data=None):
        """Handle player leaving the matchmaking queue."""
        try:
            removed = matchmaking_service.remove_player_from_queue(sid)
            if removed:
                logger.info(f"Player with sid {sid} left the queue. Remaining: {len(matchmaking_service.waiting_players)}")
                await sio.emit("queue_left", {"status": "success"}, room=sid)
            else:
                await sio.emit("queue_left", {"status": "not_in_queue"}, room=sid)
                
        except Exception as e:
            logger.error(f"Error in leave_queue: {e}")
            await sio.emit("error", {"message": "Failed to leave queue"}, room=sid)
    
    @sio.event
    async def get_queue_status(sid, data=None):
        """Get current queue status."""
        try:
            queue_status = matchmaking_service.get_queue_status()
            await sio.emit("queue_status", queue_status.model_dump(), room=sid)
        except Exception as e:
            logger.error(f"Error getting queue status: {e}")
            await sio.emit("error", {"message": "Failed to get queue status"}, room=sid)