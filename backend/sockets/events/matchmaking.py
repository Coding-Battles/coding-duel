"""
Matchmaking event handlers for Socket.IO.
"""

import logging
from pydantic import ValidationError
from ..services.matchmaking_service import matchmaking_service, MatchFoundResponse
from typing import Dict
from backend.api import game

logger = logging.getLogger(__name__)

game_states: Dict[str, game.GameState] = {}

def set_dependencies(game_states_param=None):
    global game_states
    game_states = game_states_param
    matchmaking_service.set_dependencies(game_states_param)


def register_events(sio):
    """Register matchmaking events with the Socket.IO server."""

    @sio.event
    async def join_queue(sid, data):
        """Handle player joining the matchmaking queue."""
        try:
            # Add player to queue
            player = matchmaking_service.add_player_to_queue(data, sid)
            total_players = len(matchmaking_service.waiting_players_easy) + len(matchmaking_service.waiting_players_medium) + len(matchmaking_service.waiting_players_hard)
            logger.info(
                f"Player {player.name} joined queue. Total players in queue: easy={len(matchmaking_service.waiting_players_easy)}, medium={len(matchmaking_service.waiting_players_medium)}, hard={len(matchmaking_service.waiting_players_hard)}"
            )

            # Try to create a match
            match_result = matchmaking_service.try_create_match()

            logger.info(f"game_states: {game_states}")

            if match_result:
                player1, player2, game_id, difficulty, question_slug = match_result

                # Send match found to both players
                match_response1 = MatchFoundResponse(
                    game_id=game_id,
                    opponent_Name=player2.name,
                    opponentImageURL=player2.imageURL,
                    question_name=question_slug,
                )
                await sio.emit(
                    "match_found", match_response1.model_dump(), room=player1.sid
                )

                match_response2 = MatchFoundResponse(
                    game_id=game_id, 
                    opponent_Name=player1.name, 
                    opponentImageURL=player1.imageURL,
                    question_name=question_slug
                )
                await sio.emit(
                    "match_found", match_response2.model_dump(), room=player2.sid
                )

                logger.info(
                    f"Match created: {player1.name} vs {player2.name} in {difficulty} difficulty with question {question_slug} (Game: {game_id})"
                )

                # After match is found
                await sio.enter_room(player1.sid, game_id)
                await sio.enter_room(player2.sid, game_id)
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
            logger.info(f"[leave_queue] Called with sid: {sid}")
            # Print all waiting players with their sids and names
            # Log current queue state
            logger.info(
                f"[leave_queue] Current queue sizes - easy: {len(matchmaking_service.waiting_players_easy)}, medium: {len(matchmaking_service.waiting_players_medium)}, hard: {len(matchmaking_service.waiting_players_hard)}"
            )
            
            removed = matchmaking_service.remove_player_from_queue(sid)
            
            logger.info(
                f"[leave_queue] Queue sizes after removal - easy: {len(matchmaking_service.waiting_players_easy)}, medium: {len(matchmaking_service.waiting_players_medium)}, hard: {len(matchmaking_service.waiting_players_hard)}"
            )
            logger.info(f"[leave_queue] Removed: {removed}")
            
            if removed:
                total_remaining = len(matchmaking_service.waiting_players_easy) + len(matchmaking_service.waiting_players_medium) + len(matchmaking_service.waiting_players_hard)
                logger.info(f"Player with sid {sid} left the queue. Total remaining: {total_remaining}")
                await sio.emit("queue_left", {"status": "success"}, room=sid)
            else:
                logger.info(f"[leave_queue] Player with sid {sid} not found in any queue.")
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
