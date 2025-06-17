
from fastapi import FastAPI
from pydantic import BaseModel, Field, ValidationError
import socketio
import uuid
import subprocess
from pathlib import Path
import os
from fastapi.middleware.cors import CORSMiddleware
import shutil
import sys

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

sio = socketio.AsyncServer(
    cors_allowed_origins="*",
    async_mode='asgi'
)

socket_app = socketio.ASGIApp(sio, app)

class Player(BaseModel):
    id: str  # This is the player's custom ID
    name: str
    sid: str  # This is the socket connection ID

class MatchFoundResponse(BaseModel):
    game_id: str
    opponent: str

class QueueStatusResponse(BaseModel):
    status: str
    queue_size: int

# Simple in-memory queue
waiting_players: list[Player] = []

@app.get("/", response_model=QueueStatusResponse)
def health_check():
    return QueueStatusResponse(status="ok", queue_size=len(waiting_players))

@sio.event
async def connect(sid, environ):
    print(f"Client {sid} connected")

@sio.event
async def disconnect(sid):
    global waiting_players
    # Remove player from queue if they disconnect
    waiting_players = [p for p in waiting_players if p.sid != sid]
    print(f"Client {sid} disconnected. Queue size: {len(waiting_players)}")

@sio.event
async def join_queue(sid, data):
    try:
        # Create player with both custom ID and socket ID
        player_data = {**data, 'sid': sid}
        player = Player(**player_data)
        waiting_players.append(player)
        print(f"Player {player.name} joined the queue. Total players in queue: {len(waiting_players)}")
        
        # Check if we can form a match
        if len(waiting_players) >= 2:
            player1 = waiting_players.pop(0)  # First player
            player2 = waiting_players.pop(0)  # Second player (current player)
            
            game_id = f"game_{uuid.uuid4().hex[:12]}"
            
            # Send match notification to both players using their socket IDs
            match_response1 = MatchFoundResponse(game_id=game_id, opponent=player2.name)
            await sio.emit('match_found', match_response1.model_dump(), room=player1.sid)
            
            match_response2 = MatchFoundResponse(game_id=game_id, opponent=player1.name)
            await sio.emit('match_found', match_response2.model_dump(), room=player2.sid)
            
            print(f"Match found: {player1.name} vs {player2.name} in game {game_id}")
        else:
            status_response = QueueStatusResponse(status="waiting", queue_size=len(waiting_players))
            await sio.emit('queue_status', status_response.model_dump(), room=sid)
            
    except ValidationError as e:
        print(f"Validation error: {e}")
        await sio.emit('error', {'message': 'Invalid data'}, room=sid)

class CodeRequest(BaseModel):
    code: str
    input: str

@app.post("/run_code")
async def run_code_enpoint(payload: CodeRequest):
    try:
        user_code = payload.code
        input_data = payload.input
        
        # Run the code in a Docker container
        result = run_code_in_docker(user_code, input_data)
        return {"output": result.get("output", ""), "error": result.get("error", "")}
    except Exception as e:
        return {"error": str(e)}

def run_code_in_docker(user_code: str, input_data:str): #have to first build image using "docker build -t coderunner ./"
    run_id = str(uuid.uuid4()) #creates a unique id for unique folders when running code
    #create a temporary directory for the run
    temp_dir = Path(f"./runs/{run_id}")
    temp_dir.mkdir(parents=True)
    #write user code and input data to files
    (temp_dir / "user_code.py").write_text(user_code)
    (temp_dir / "input.txt").write_text(input_data)

    shutil.copy("./codeRunner.py", temp_dir)

    volume_path = str(temp_dir.absolute()).replace("\\", "/")
    if sys.platform.startswith("win") and volume_path[1] == ':':
        drive_letter = volume_path[0].lower()
        volume_path = f"/{drive_letter}{volume_path[2:]}"

    print(f"Mounting volume: {volume_path}:/app")
    try:
        result = subprocess.run([
            "docker", "run", "--rm",
            "-v", f"{volume_path}:/app",  # Mount the folder
            "--memory", "128m",  # Memory limit
            "--cpus", "0.5",     # CPU limit
            "--network", "none", # No internet access
            "coderunner"
        ], capture_output=True, text=True, timeout=5)

        output = result.stdout
        error = result.stderr

    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)  # Clean up the temporary directory

    return {"output": output, "error": error}



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(socket_app, host="0.0.0.0", port=8000)