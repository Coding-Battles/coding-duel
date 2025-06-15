from fastapi import FastAPI
import socketio
from pydantic import BaseModel, Field, ValidationError
from typing import Optional

# Create FastAPI app
app = FastAPI()

# Create Socket.IO server
sio = socketio.AsyncServer(
    cors_allowed_origins="*",
    async_mode='asgi'
)

# Combine them
socket_app = socketio.ASGIApp(sio, app)

# Pydantic models
class JoinQueueData(BaseModel):
    ## If logged in
    auth_token: Optional[str] = None 
    ## If not logged in
    user_name: Optional[str] = Field(None, min_length=1, max_length=20)
    

class Player(BaseModel):
    id: str
    user_name: str
    wins: int = 0
    losses: int = 0

class MatchFoundResponse(BaseModel):
    game_id: str
    opponent_user_name: str

class QueueStatusResponse(BaseModel):
    status: str
    queue_size: int

# Simple in-memory queue
waiting_players: list[Player] = []

@app.get("/", response_model=QueueStatusResponse)
def health_check():
    return QueueStatusResponse(status="ok", queue_size=len(waiting_players))

@app.get("")

@sio.event
async def join_queue(sid, data):
    try:
        # Validate incoming data
        queue_data = JoinQueueData(**data)
        
        # Create player with validated data
        player_user_name = queue_data.user_name
        player = Player(id=sid, user_name=player_user_name)
        
        waiting_players.append(player)
        
        print(f"{player.user_name} joined queue. Queue size: {len(waiting_players)}")
        
        # Check for match
        if len(waiting_players) >= 2:
            player1 = waiting_players.pop(0)
            player2 = waiting_players.pop(0)
            
            game_id = f"game_{player1.id[:6]}_{player2.id[:6]}"
            
            # Create validated responses
            match1 = MatchFoundResponse(game_id=game_id, opponent=player2.user_name)
            match2 = MatchFoundResponse(game_id=game_id, opponent=player1.user_name)
            
            # Notify both players
            await sio.emit('match_found', match1.dict(), room=player1.id)
            await sio.emit('match_found', match2.dict(), room=player2.id)
            
            print(f"Match found: {player1.user_name} vs {player2.user_name}")
            
    except ValidationError as e:
        # Send validation error back to client
        await sio.emit('error', {
            'message': 'Invalid data',
            'details': e.errors()
        }, room=sid)
        print(f"Validation error for {sid}: {e.errors()}")
    except Exception as e:
        # Handle other errors
        await sio.emit('error', {
            'message': 'Server error',
            'details': str(e)
        }, room=sid)
        print(f"Error in join_queue: {e}")

@sio.event
async def disconnect(sid):
    # Remove player from queue if they disconnect
    global waiting_players
    waiting_players = [p for p in waiting_players if p.id != sid]
    print(f"Player {sid} disconnected. Queue size: {len(waiting_players)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(socket_app, host="0.0.0.0", port=8000)