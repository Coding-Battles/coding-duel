"""
API request and response Pydantic models
Centralized models for HTTP API data structures
"""

from pydantic import BaseModel
from typing import List, Dict, Optional, Any
from .user import TestResultsData, GameParticipant, UserStats
from .question import QuestionData
from .game import GameHistoryItem


# API Request models
class CreateGameRequest(BaseModel):
    player_ids: List[str]
    question_name: str


class UpdateGameRequest(BaseModel):
    player_id: str
    code: Optional[str] = None
    language: Optional[str] = None
    status: Optional[str] = None


class SubmitCodeRequest(BaseModel):
    player_id: str
    code: str
    language: str


class JoinQueueRequest(BaseModel):
    player_id: str
    player_name: str
    question_name: str
    anonymous: bool
    image_url: Optional[str] = None
    selected_difficulties: Dict[str, bool]


# API Response models
class CreateGameResponse(BaseModel):
    game_id: str
    status: str
    message: str


class GameStatusResponse(BaseModel):
    game_id: str
    status: str
    players: List[Any]
    created_at: str
    updated_at: str


class SubmitCodeResponse(BaseModel):
    success: bool
    message: str
    test_results: Optional[TestResultsData] = None


class QueueStatusResponse(BaseModel):
    in_queue: bool
    position: int
    estimated_wait_time: int


class GameHistoryResponse(BaseModel):
    games: List[GameParticipant]
    total_count: int


class UserStatsResponse(BaseModel):
    user_id: str
    stats: UserStats


class QuestionListResponse(BaseModel):
    questions: List[QuestionData]
    total_count: int


class QuestionDetailsResponse(BaseModel):
    question: QuestionData


# Generic API response wrapper
class ApiResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Any] = None
    error: Optional[str] = None


# API error response
class ApiError(BaseModel):
    success: bool = False
    message: str
    error: str
    code: Optional[int] = None


# Pagination parameters
class PaginationParams(BaseModel):
    page: Optional[int] = None
    limit: Optional[int] = None
    offset: Optional[int] = None


# Common query parameters
class QueryParams(PaginationParams):
    search: Optional[str] = None
    sort_by: Optional[str] = None
    sort_order: Optional[str] = None
    filter: Optional[Dict[str, Any]] = None