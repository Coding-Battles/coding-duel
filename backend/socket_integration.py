import socketio
import logging
import json
import random
import time
import uuid
from typing import List, Dict
from pydantic import BaseModel, ValidationError
from backend.api.game import PlayerInfo, GameState

logger = logging.getLogger(__name__)

class Player(BaseModel):
    id: str  # This is the player's custom ID
    name: str
    imageURL: str
    anonymous: bool = True  # Whether the player is anonymous or not
    sid: str  # This is the socket connection ID

class MatchFoundResponse(BaseModel):
    game_id: str
    opponent_Name: str
    opponentImageURL: str | None = None
    question_name: str

class QueueStatusResponse(BaseModel):
    status: str
    queue_size: int

def setup_socket_events(sio: socketio.AsyncServer, database, game_states: Dict[str, GameState], player_to_game: Dict[str, str]):
    """Set up socket events matching the functionality from questions.py"""
    
    waiting_players: List[Player] = []

    @sio.event
    async def ping(sid, data):
        await sio.emit("pong", {"timestamp": time.time()}, room=sid)

    @sio.event
    async def connect(sid, environ):
        logger.info(f"Client {sid} connected")

    @sio.event
    async def disconnect(sid):
        nonlocal waiting_players
        # Remove player from queue if they disconnect
        waiting_players = [p for p in waiting_players if p.sid != sid]

        # Remove player from game if they disconnect
        player_id_to_remove = None
        game_id_to_update = None
        
        for player_id, game_id in player_to_game.items():
            if game_id in game_states:
                game_state = game_states[game_id]
                if player_id in game_state.players and game_state.players[player_id].sid == sid:
                    player_id_to_remove = player_id
                    game_id_to_update = game_id
                    break
        
        if player_id_to_remove and game_id_to_update:
            # Notify opponent that player disconnected
            game_state = game_states[game_id_to_update]
            opponent_id = game_state.get_opponent_id(player_id_to_remove)
            
            if opponent_id and opponent_id in game_state.players:
                opponent_sid = game_state.players[opponent_id].sid
                await sio.emit(
                    "opponent_disconnected", 
                    {"message": "Your opponent has disconnected"}, 
                    room=opponent_sid
                )
            
            # Clean up mappings
            del player_to_game[player_id_to_remove]
            if game_id_to_update in game_states:
                del game_states[game_id_to_update]
        
        logger.info(f"Client {sid} disconnected. Queue size: {len(waiting_players)}")

    @sio.event
    async def join_queue(sid, data):
        nonlocal waiting_players
        try:
            # Create player with both custom ID and socket ID
            player_data = {**data, "sid": sid}
            player = Player(**player_data)
            waiting_players.append(player)
            logger.info(
                f"Player {player.name} joined the queue. Total players in queue: {len(waiting_players)}"
            )

            # Check if we can form a match
            if len(waiting_players) >= 2:
                logger.info("🔍 pair found")
                player1 = waiting_players.pop(0)  # First player
                player2 = waiting_players.pop(0)  # Second player (current player)

                game_id = f"game_{uuid.uuid4().hex[:12]}"

                with open("backend/data/questions.json", 'r') as f:
                    data = json.load(f)

                # Randomly select a question from the available questions
                question = random.choice(data["questions"])
                question_name = question["slug"]  # Use slug for both loading files and URLs
                question_slug = question["slug"]  # Use slug for URLs
                question_title = question["title"]  # Human-readable title for display

                logger.info(f"player1: {player1.name} vs player2: {player2.name} with question: {question_name}")

                # Create game state
                game_state = GameState(
                    game_id=game_id,
                    players={
                        player1.id: PlayerInfo(id=player1.id, name=player1.name, sid=player1.sid, anonymous=player1.anonymous),
                        player2.id: PlayerInfo(id=player2.id, name=player2.name, sid=player2.sid, anonymous=player2.anonymous)
                    },
                    question_name=question_name
                )

                game_states[game_id] = game_state
                
                # Map players to game
                player_to_game[player1.id] = game_id
                player_to_game[player2.id] = game_id

                # Send match notification to both players using their socket IDs
                match_response1 = MatchFoundResponse(
                    game_id=game_id, 
                    opponent_Name=player2.name, 
                    opponentImageURL=player2.imageURL, 
                    question_name=question_slug  # Send slug for URL navigation
                )
                await sio.emit("match_found", match_response1.model_dump(), room=player1.sid)

                match_response2 = MatchFoundResponse(
                    game_id=game_id, 
                    opponent_Name=player1.name, 
                    opponentImageURL=player1.imageURL, 
                    question_name=question_slug  # Send slug for URL navigation
                )
                await sio.emit("match_found", match_response2.model_dump(), room=player2.sid)

                logger.info(f"Match found: {player1.name} vs {player2.name} in game {game_id}")

                # After match is found
                await sio.enter_room(player1.sid, game_id)
                await sio.enter_room(player2.sid, game_id)
            else:
                status_response = QueueStatusResponse(
                    status="waiting", queue_size=len(waiting_players)
                )
                await sio.emit("queue_status", status_response.model_dump(), room=sid)

        except ValidationError as e:
            print(f"Validation error: {e}")
            await sio.emit("error", {"message": "Invalid data"}, room=sid)

    return sio