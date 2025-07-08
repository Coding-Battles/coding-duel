from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from pathlib import Path
import subprocess
import uuid
import shutil
import sys
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

class CodeRequest(BaseModel):
    code: str
    input: str

@router.post("/run_code")
async def run_code_endpoint(payload: CodeRequest):
    try:
        user_code = payload.code
        input_data = payload.input

        # Run the code in a Docker container
        result = run_code_in_docker(user_code, input_data)
        return {"output": result.get("output", ""), "error": result.get("error", "")}
    except Exception as e:
        return {"error": str(e)}

def run_code_in_docker(user_code: str, input_data: str):
    """Run code in Docker container - have to first build image using "docker build -t coderunner ./" """
    run_id = str(uuid.uuid4())  # creates a unique id for unique folders when running code
    
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