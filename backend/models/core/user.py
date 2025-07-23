"""
User-related Pydantic models
Centralized models for user, player, and profile data structures
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum


class PlayerStatus(str, Enum):
    WAITING = "waiting"
    TYPING = "typing"
    RUNNING = "running" 
    IDLE = "idle"
    SUBMITTED = "submitted"


class BaseUser(BaseModel):
    id: str
    name: Optional[str] = None
    email: Optional[str] = None


class CustomUser(BaseUser):
    username: Optional[str] = None
    image: Optional[str] = None
    selectedPfp: Optional[int] = None
    anonymous: Optional[bool] = None
    game_ids: Optional[List[int]] = None


class TestCase(BaseModel):
    input: Dict[str, Any]
    expected_output: str
    actual_output: str
    passed: bool
    error: Optional[str] = None
    execution_time: float


class TestResultsData(BaseModel):
    success: bool
    test_results: List[TestCase]
    total_passed: int
    total_failed: int
    error: Optional[str] = None
    message: str
    code: str
    player_name: Optional[str] = None
    opponent_id: str
    complexity: Optional[str] = None
    implement_time: Optional[int] = None
    final_time: Optional[int] = None


class PlayerInfo(BaseModel):
    id: str
    sid: str  # Socket ID
    name: str
    anonymous: bool = True
    image_url: Optional[str] = None
    game_stats: Optional[TestResultsData] = None


class Player(BaseModel):
    id: str
    name: str
    status: PlayerStatus
    code: Optional[str] = None
    language: Optional[str] = None
    last_update: Optional[int] = None
    submitted: Optional[bool] = None
    submit_time: Optional[int] = None


class OpponentData(BaseModel):
    id: Optional[str] = None
    name: Optional[str] = None
    image_url: Optional[str] = None
    status: Optional[str] = None
    timesRan: Optional[int] = None
    timeElapsed: Optional[str] = None
    wins: Optional[int] = None


class GameParticipant(BaseModel):
    id: Optional[int] = None
    question_name: str
    difficulty: str
    game_id: int
    player_name: str
    player_code: str
    implement_time: int
    time_complexity: str
    final_time: int
    user_id: str


class UserStats(BaseModel):
    totalSolved: int
    easySolved: int
    mediumSolved: int
    hardSolved: int
    totalSubmissions: int
    acceptanceRate: float
    ranking: int
    streak: int