"""
Connection event handlers for Socket.IO.
"""
import datetime
import logging
from ..services.matchmaking_service import matchmaking_service
from typing import Dict
from backend.api import game
from backend.global_variables import games

logger = logging.getLogger(__name__)

game_states: Dict[str, game.GameState] = {}

def set_dependencies(game_states_param=None):
    global game_states
    game_states = game_states_param

def remove_lp_from_player(player_id: str, difficulty: str, lp_change: int):
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


def register_events(sio):
    """Register connection events with the Socket.IO server."""
    
    @sio.event
    async def connect(sid, environ):
        """Handle client connection."""
        logger.info(f"Client {sid} connected")
        await sio.emit("connected", {"status": "connected", "sid": sid}, room=sid)
    
    @sio.event
    async def disconnect(sid, reason=None):
        try:
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
                    time_elapsed_since_start = datetime.datetime.now() - game_state.created_at

                    if time_elapsed_since_start > datetime.timedelta(seconds=120) or len(game_state.finished_players) > 0:
                        # Award win to remaining player
                        opponent_id = game_state.get_opponent_id(disconnected_player_id)
                        if opponent_id:
                            logger.info(f"🔌 [DISCONNECT] Player {disconnected_player_id} disconnected from game {game_id} - awarding win to {opponent_id}")
                            game_state.set_winner(opponent_id, "disconnection")
                            logger.info(f"players: {list(game_state.players.values())}")
                            await game.save_game_to_history(
                                players=list(game_state.players.values()),
                                winner_id=opponent_id,
                                question_name=game_state.question_name,
                                difficulty=game_state.difficulty
                            )

                            # Send game end event to remaining player
                            opponent_name = game_state.get_player_name(opponent_id)
                            disconnected_name = game_state.get_player_name(disconnected_player_id)

                            (winner_lp_gain, loser_lp_loss) = games.get_lp_changes()

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
                                },
                                "lp_loss": loser_lp_loss,
                                "lp_gain": winner_lp_gain
                            }
                            
                            await sio.emit("game_completed", game_end_data, room=game_id)
                            logger.info(f"🏆 Game {game_id} ended due to disconnection - {opponent_name} wins!")

                            await game.cleanup_game_state(game_id)

                    else: # Less than 2 minutes and no finished players, do not award win
                        opponent_id = game_state.get_opponent_id(disconnected_player_id)
                        opponent_name = game_state.get_player_name(opponent_id) if opponent_id else "Unknown"
                        disconnected_name = game_state.get_player_name(disconnected_player_id)

                        logger.info("opponent disconnected too early to award win")
                        game_end_data = {
                            "message": f"Opponent {opponent_name} disconnected too early. No winner awarded.",
                            "winner_id": opponent_id,
                            "winner_name": opponent_name,
                            "loser_id": disconnected_player_id,
                            "loser_name": disconnected_name,
                            "game_end_reason": "disconnection",
                            "game_end_time": game_state.game_end_time,
                            "winner_stats": {
                                "player_name": "no winner",
                                "success": True
                            },
                            "lp_loss": 0,
                            "lp_gain": 0
                        }

                        (lp_gain, loser_lp_loss) = games.get_lp_changes()
                        remove_lp_from_player(disconnected_player_id, game_state.difficulty, loser_lp_loss)  
                        await sio.emit("game_completed", game_end_data, room=game_id)
                
                #remove game state after handling disconnection
                matchmaking_service.end_game(game_id)
            
            if removed_from_queue:
                logger.info(f"Client {sid} disconnected and removed from queue")
            else:
                logger.info(f"Client {sid} disconnected")
        except Exception as e:
            logger.error(f"Error during disconnect handling for {sid}: {e}")
            