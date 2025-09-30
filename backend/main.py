from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import socketio
import os
import docker
import asyncio
from concurrent.futures import ThreadPoolExecutor
import logging
import shutil
from pathlib import Path
from dotenv import load_dotenv
import databases
from typing import Dict
from dataclasses import dataclass, field
from datetime import datetime
from typing import Set
from backend.sockets.events import matchmaking, connection
from backend.sockets.events import game as socket_game_events
from pathlib import Path


# Load environment variables early
env_path = Path(".env")
if not env_path.exists():
    env_path = Path("../.env")
    if not env_path.exists():
        env_path = Path("backend/.env")

if env_path.exists():
    load_dotenv(dotenv_path=env_path)
    print(f"Loaded .env from: {env_path.absolute()}")
else:
    print("WARNING: .env file not found! Attempting to load from system environment")
    load_dotenv()


# Import API routers after loading env
from backend.api import users
from backend.api import questions_router
from backend.api import code
from backend.api import game
from backend.models.core import GameState

# Import socket functionality
from backend.sockets.socket_app import create_socket_app

# Import services
from backend.services.user_service import initialize_username_pool

# Import models for socket functionality
from backend.models.questions import CodeTestResult


# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
# Silence engineio.server and socketio.server INFO logs
logging.getLogger("engineio.server").setLevel(logging.ERROR)
logging.getLogger("socketio.server").setLevel(logging.ERROR)

# Initialize Docker client with error handling
try:
    docker_client = docker.from_env()
    docker_available = True
    print("Docker connected successfully")
except docker.errors.DockerException as e:
    docker_available = False
    print(f"Warning: Docker not available - {e}")
    print("Code execution features will not work without Docker")

executor = ThreadPoolExecutor(max_workers=5)

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL")
database = databases.Database(DATABASE_URL)

# Game state storage
game_states: Dict[str, GameState] = {}
player_to_game: Dict[str, str] = {}


@asynccontextmanager
async def lifespan(_app: FastAPI):
    # Startup
    logger.info("🚀 Starting application...")

    # Connect to database first
    try:
        logger.info("|main.py| Connecting to database...")
        await database.connect()
        logger.info("|main.py| Database connected successfully")
    except Exception as e:
        logger.error(f"❌ Failed to connect to database: {e}")
        raise

    # Initialize username pool for instant generation
    try:
        await initialize_username_pool()
        logger.info("|main.py| Username pool initialized")
    except Exception as e:
        logger.error(f"❌ Failed to initialize username pool: {e}")

    # Initialize persistent containers for fast code execution
    logger.info("|main.py| Initializing persistent containers for fast code execution...")
    try:
        from backend.code_testing.startup import pull_all_images, warm_up_containers

        loop = asyncio.get_event_loop()
        logger.info("|main.py| Pre-pulling Docker images...")
        await loop.run_in_executor(executor, pull_all_images)
        logger.info("|main.py| Warming up persistent containers...")
        await loop.run_in_executor(executor, warm_up_containers)
        logger.info(
            "|main.py|✅ Persistent containers ready! Code execution will now be sub-second."
        )
    except Exception as e:
        logger.error(f"❌ Failed to initialize persistent containers: {e}")
        logger.warning("|main.py| Falling back to traditional Docker execution (slower)")

    yield

    # Shutdown
    logger.info("🧹 Cleaning up persistent containers...")
    try:
        from backend.code_testing.docker_runner import cleanup_persistent_containers

        cleanup_persistent_containers()
        logger.info("|main.py| Containers cleaned up successfully")
    except Exception as e:
        logger.error(f"❌ Error during container cleanup: {e}")

    try:
        await database.disconnect()
        logger.info("|main.py| Database disconnected successfully")
    except Exception as e:
        logger.error(f"❌ Error disconnecting database: {e}")


# Create FastAPI app
app = FastAPI(lifespan=lifespan)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Set up database dependencies for routers
questions_router.set_database(database)

# Set dependencies for socket events BEFORE creating socket app
logger.info(
    f"|main.py| [SYNC DEBUG] Setting dependencies with game_states id: {id(game_states)}"
)
matchmaking.set_dependencies(game_states)
connection.set_dependencies(game_states)
socket_game_events.set_dependencies(game_states)
# Note: game API module will be set after sio is created

# Include API routers
app.include_router(users.router, prefix="/api")
app.include_router(questions_router.router, prefix="/api")
app.include_router(code.router, prefix="/api")
app.include_router(game.router, prefix="/api")


# Create Socket.IO server with CORS and better connection settings
sio = create_socket_app(database, game_states, app)

# Now set the socket instance for game router
game.set_dependencies(database, sio, game_states)

# Create combined ASGI app
socket_app = socketio.ASGIApp(sio, app)

# Database connection is handled by lifespan context manager


# Image upload endpoint
@app.post("/image/{player_id}")
async def change_image(player_id: str, image: UploadFile = File(...)):
    # Save file
    os.makedirs("uploads", exist_ok=True)
    filename = f"player_{player_id}_{image.filename}"
    file_path = f"uploads/{filename}"
    public_url = f"http://localhost:8000/uploads/{filename}"

    with open(file_path, "wb") as f:
        shutil.copyfileobj(image.file, f)

    # Update DB using raw SQL
    query = 'UPDATE "user" SET image = :image_url WHERE id = :id'
    values = {"image_url": public_url, "id": player_id}
    await database.execute(query=query, values=values)

    return {"message": "Image updated", "path": public_url}


# Health check endpoint
@app.get("/")
def health_check():
    return {
        "status": "ok",
        "docker_available": docker_available,
        "services": ["users", "questions", "code", "game", "socket"],
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("backend.main:socket_app", host="0.0.0.0", port=8000, reload=True)
