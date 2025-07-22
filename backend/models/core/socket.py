"""
Socket.IO event Pydantic models
Centralized models for real-time communication data structures
"""

from pydantic import BaseModel
from typing import Dict, Optional, Any
from .user import TestResultsData
from .game import GameState, DifficultyState


# Socket event payloads
class JoinGameData(BaseModel):
    game_id: str
    player_id: str


class CodeUpdateData(BaseModel):
    game_id: str
    player_id: str
    code: str
    language: str


class InstantCodeUpdateData(CodeUpdateData):
    reason: str


class PlayerStatusUpdateData(BaseModel):
    game_id: str
    player_id: str
    status: str
    data: Optional[Dict[str, Any]] = None


class SubmitSolutionData(BaseModel):
    game_id: str
    player_id: str
    submission: TestResultsData


class LeaveGameData(BaseModel):
    game_id: str
    player_id: str


class JoinQueueData(BaseModel):
    player_id: str
    player_name: str
    question_name: str
    anonymous: bool
    image_url: Optional[str] = None
    selected_difficulties: DifficultyState


class LeaveQueueData(BaseModel):
    player_id: str


# Socket event responses
class GameJoinedResponse(BaseModel):
    game_id: str
    game_state: Optional[GameState] = None
    start_time: Optional[float] = None


class GameStartResponse(BaseModel):
    game_id: str
    start_time: float


class OpponentCodeReadyResponse(BaseModel):
    code: str
    from_player: str
    language: str
    timestamp: float
    instant: Optional[bool] = None
    reason: Optional[str] = None


class PlayerCodeUpdatedResponse(BaseModel):
    player_id: str
    timestamp: float
    instant: Optional[bool] = None


class PlayerLanguageChangedResponse(BaseModel):
    player_id: str
    language: str
    immediate: bool


class PlayerStatusChangedResponse(BaseModel):
    player_id: str
    status: str
    data: Optional[Dict[str, Any]] = None


class SolutionSubmittedResponse(BaseModel):
    player_id: str
    submission: TestResultsData
    game_state: Optional[GameState] = None


class GameFinishedResponse(BaseModel):
    winner: str
    game_state: GameState


class PlayerLeftResponse(BaseModel):
    player_id: str
    game_ended: bool


class ErrorResponse(BaseModel):
    message: str