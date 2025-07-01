
from contextlib import asynccontextmanager
from fastapi import FastAPI, UploadFile, HTTPException, File
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import subprocess
from pathlib import Path
import os
from fastapi.middleware.cors import CORSMiddleware
import shutil
import sys
from dotenv import load_dotenv
import databases
from sockets.socket_app import create_socket_asgi_app
from sockets.services.matchmaking_service import matchmaking_service
from api import users
from services.user_service import initialize_username_pool

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
database = databases.Database(DATABASE_URL)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await database.connect()
    # Initialize username pool for instant generation
    await initialize_username_pool()
    yield
    # Shutdown
    await database.disconnect()

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Include API routers
app.include_router(users.router, prefix="/api")


@app.get("/")
def health_check():
    """Health check endpoint."""
    queue_status = matchmaking_service.get_queue_status()
    return {
        "status": "ok", 
        "queue_size": queue_status.queue_size,
        "active_games": len(matchmaking_service.active_games)
    }


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


def run_code_in_docker(
    user_code: str, input_data: str
):  # have to first build image using "docker build -t coderunner ./"
    run_id = str(
        uuid.uuid4()
    )  # creates a unique id for unique folders when running code
    # create a temporary directory for the run
    temp_dir = Path(f"./runs/{run_id}")
    temp_dir.mkdir(parents=True)
    # write user code and input data to files
    (temp_dir / "user_code.py").write_text(user_code)
    (temp_dir / "input.txt").write_text(input_data)

    shutil.copy("./codeRunner.py", temp_dir)

    volume_path = str(temp_dir.absolute()).replace("\\", "/")
    if sys.platform.startswith("win") and volume_path[1] == ":":
        drive_letter = volume_path[0].lower()
        volume_path = f"/{drive_letter}{volume_path[2:]}"

    print(f"Mounting volume: {volume_path}:/app")
    try:
        result = subprocess.run(
            [
                "docker",
                "run",
                "--rm",
                "-v",
                f"{volume_path}:/app",  # Mount the folder
                "--memory",
                "128m",  # Memory limit
                "--cpus",
                "0.5",  # CPU limit
                "--network",
                "none",  # No internet access
                "coderunner",
            ],
            capture_output=True,
            text=True,
            timeout=5,
        )

        output = result.stdout
        error = result.stderr

    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)  # Clean up the temporary directory

    return {"output": output, "error": error}

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

    return {"message": "Image updated", "path": file_path}





if __name__ == "__main__":
    import uvicorn
    
    # Create the combined FastAPI + Socket.IO app
    socket_app = create_socket_asgi_app(app)
    uvicorn.run(socket_app, host="0.0.0.0", port=8000)
