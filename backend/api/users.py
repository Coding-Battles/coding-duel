from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from backend.services.user_service import (
    is_username_taken,
    get_next_available_username,
    generate_ai_username,
    get_instant_username
)

router = APIRouter()

class UsernameRequest(BaseModel):
    username: str

class GenerateUsernameRequest(BaseModel):
    count: Optional[int] = 1

@router.post("/users/check-username")
async def check_username(request: UsernameRequest):
    """Check if a username is available."""
    is_taken = await is_username_taken(request.username)
    return {"username": request.username, "available": not is_taken}

@router.post("/users/available-username")
async def get_available_username(request: UsernameRequest):
    """Get the next available username (adds numbers if needed)."""
    available = await get_next_available_username(request.username)
    return {"requested": request.username, "available": available}

@router.post("/users/generate-username")
async def generate_username(request: GenerateUsernameRequest = GenerateUsernameRequest()):
    """Generate creative usernames using AI."""
    if request.count == 1:
        # Use instant pool for single username requests
        instant_username = await get_instant_username()
        return {"usernames": [instant_username], "count": 1}
    else:
        # Use regular generation for multiple usernames
        ai_usernames = await generate_ai_username(request.count)
        return {"usernames": ai_usernames, "count": len(ai_usernames)}