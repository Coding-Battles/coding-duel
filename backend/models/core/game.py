"""
Game-related Pydantic models
Centralized models for game state, matchmaking, and game flow data structures
"""

from pydantic import BaseModel, Field
from typing import Dict, Set, Optional, List
from datetime import datetime
from enum import Enum
from .user import PlayerInfo, CustomUser, OpponentData, TestResultsData, GameParticipant


class GameStatus(str, Enum):
    WAITING = "waiting"
    IN_PROGRESS = "in_progress"
    FINISHED = "finished"
    CANCELLED = "cancelled"


class DifficultyLevel(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class DifficultyState(BaseModel):
    easy: bool
    medium: bool
    hard: bool


class GameState(BaseModel):
    game_id: str
    players: Dict[str, PlayerInfo] = Field(default_factory=dict)
    finished_players: Set[str] = Field(default_factory=set)
    created_at: datetime = Field(default_factory=datetime.now)
    question_name: str = ""
    
    # Player assignments
    player1: str = ""
    player2: str = ""
    
    # Legacy code storage
    player1_code: str = ""
    player2_code: str = ""
    player1_code_timestamp: Optional[float] = None
    player2_code_timestamp: Optional[float] = None
    
    # Language-aware code storage
    player_codes: Dict[str, Dict[str, str]] = Field(default_factory=dict)  # {player_id: {language: code}}
    player_code_timestamps: Dict[str, Dict[str, float]] = Field(default_factory=dict)  # {player_id: {language: timestamp}}
    current_languages: Dict[str, str] = Field(default_factory=dict)  # {player_id: current_language}
    
    # Game timing
    game_start_time: Optional[float] = None
    players_joined: Set[str] = Field(default_factory=set)
    
    # Winner tracking for "first to solve wins" game mode
    winner_id: Optional[str] = None
    game_end_time: Optional[float] = None
    game_end_reason: str = ""  # "first_win", "timeout", "disconnection", etc.
    
    # Starter code for comparison
    starter_codes: Dict[str, str] = Field(default_factory=dict)  # {language: code}

    class Config:
        # Allow arbitrary types for Set fields
        arbitrary_types_allowed = True
    
    # Business logic methods
    def is_player_finished(self, player_id: str) -> bool:
        return player_id in self.finished_players

    def mark_player_finished(self, player_id: str):
        self.finished_players.add(player_id)

    def get_unfinished_players(self) -> Set[str]:
        return set(self.players.keys()) - self.finished_players

    def all_players_finished(self) -> bool:
        return len(self.finished_players) == len(self.players)

    def get_player_name(self, player_id: str) -> Optional[str]:
        if player_id in self.players:
            return self.players[player_id].name
        return None

    def get_opponent_id(self, player_id: str) -> Optional[str]:
        """Get opponent ID for a given player. Works with both player1/player2 fields and players dict."""
        # Method 1: Use player1/player2 fields if they're set
        if self.player1 and self.player2:
            if player_id == self.player1:
                return self.player2
            elif player_id == self.player2:
                return self.player1
        
        # Method 2: Use players dictionary as fallback
        player_ids = list(self.players.keys())
        if len(player_ids) == 2 and player_id in player_ids:
            return player_ids[0] if player_ids[1] == player_id else player_ids[1]
        
        return None

    def set_winner(self, winner_id: str, reason: str = "first_win"):
        """Set the winner and end the game immediately."""
        import time
        self.winner_id = winner_id
        self.game_end_time = time.time()
        self.game_end_reason = reason
        # Mark winner as finished
        self.mark_player_finished(winner_id)

    def is_game_ended(self) -> bool:
        """Check if the game has ended."""
        return self.winner_id is not None

    def get_loser_id(self) -> Optional[str]:
        """Get the loser's ID (opponent of winner)."""
        if self.winner_id:
            return self.get_opponent_id(self.winner_id)
        return None


class PlayerGameState(BaseModel):
    id: str
    name: str
    status: GameStatus
    created_at: datetime
    last_update: datetime
    current_code: Optional[str] = None
    submitted_code: Optional[str] = None
    language: str
    test_results: Optional[Dict] = None
    final_stats: Optional[TestResultsData] = None


class GameUpdate(BaseModel):
    game_id: str
    player_id: str
    event_type: str
    data: Dict
    timestamp: datetime


class MatchFoundData(BaseModel):
    game_id: str
    opponent_Name: str
    opponentImageURL: Optional[str] = None
    question_name: str


class MatchFoundResponse(BaseModel):
    game_id: str
    opponent_id: str
    opponent_name: str
    opponent_image_url: Optional[str] = None
    question_name: str


class QueueStatus(BaseModel):
    in_queue: bool
    selected_difficulties: DifficultyState
    estimated_wait_time: Optional[int] = None
    queue_position: Optional[int] = None


class QueueStatusResponse(BaseModel):
    in_queue: bool
    position: int
    estimated_wait_time: int


class GameHistoryItem(BaseModel):
    game_id: int
    participants: List[GameParticipant]
    user_won: bool
    result: str = Field(..., pattern="^(won|lost|tie)$")
    user_time: int
    opponent_best_time: int


class EmojiRequest(BaseModel):
    emoji: str
    player1: str