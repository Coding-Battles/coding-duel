"""
Game service for managing active game sessions and real-time events.
"""
import time
from typing import Dict, Any, Optional, List
from pydantic import BaseModel
from enum import Enum

from backend.sockets.events import game


class GameStatus(str, Enum):
    ACTIVE = "active"
    FINISHED = "finished"
    ABANDONED = "abandoned"


class PlayerStatus(str, Enum):
    TYPING = "typing"
    RUNNING = "running"
    SUBMITTED = "submitted"
    IDLE = "idle"


class GameUpdate(BaseModel):
    game_id: str
    player_id: str
    event_type: str
    data: Dict[str, Any]
    timestamp: float


class PlayerGameState(BaseModel):
    player_id: str
    code: str
    status: PlayerStatus
    last_run_count: int
    submission_time: Optional[float] = None


class GameState(BaseModel):
    game_id: str
    question_name: str
    players: Dict[str, PlayerGameState]
    status: GameStatus
    created_at: float
    started_at: Optional[float] = None
    finished_at: Optional[float] = None
    winner: Optional[str] = None


class GameService:
    """Service for managing active game sessions."""
    
    def __init__(self):
        self.active_games: Dict[str, GameState] = {}
        self.game_updates: Dict[str, List[GameUpdate]] = {}
        self.game_states: Dict[str, game.GameState] = {}

    def set_dependencies(game_states_param=None):

        game_states = game_states_param
    
    def create_game(self, game_id: str, question_name: str, players: List[Dict[str, Any]]) -> GameState:
        """Create a new game session."""
        player_states = {}
        for player in players:
            player_states[player["id"]] = PlayerGameState(
                player_id=player["id"],
                code="",
                status=PlayerStatus.IDLE,
                last_run_count=0
            )
        
        game_state = GameState(
            game_id=game_id,
            question_name=question_name,
            players=player_states,
            status=GameStatus.ACTIVE,
            created_at=time.time(),
            started_at=time.time()
        )
        
        self.active_games[game_id] = game_state
        self.game_updates[game_id] = []
        
        return game_state
    
    def get_game(self, game_id: str) -> Optional[GameState]:
        """Get game state by ID."""
        return self.active_games.get(game_id)
    
    def update_player_code(self, game_id: str, player_id: str, code: str) -> bool:
        """Update a player's code in real-time."""
        game = self.active_games.get(game_id)
        if not game or player_id not in game.players:
            return False
        
        game.players[player_id].code = code
        game.players[player_id].status = PlayerStatus.TYPING
        
        # Add update event
        self._add_game_update(game_id, player_id, "code_update", {"code": code})
        
        return True
    
    def update_player_status(self, game_id: str, player_id: str, status: PlayerStatus, data: Dict[str, Any] = None) -> bool:
        """Update a player's status."""
        game = self.active_games.get(game_id)
        if not game or player_id not in game.players:
            return False
        
        game.players[player_id].status = status
        
        if status == PlayerStatus.RUNNING:
            game.players[player_id].last_run_count += 1
        elif status == PlayerStatus.SUBMITTED:
            game.players[player_id].submission_time = time.time()
        
        # Add update event
        self._add_game_update(game_id, player_id, "status_update", {
            "status": status,
            "data": data or {}
        })
        
        return True
    
    def submit_solution(self, game_id: str, player_id: str, submission_data: Dict[str, Any]) -> bool:
        """Handle player solution submission."""
        game = self.active_games.get(game_id)
        if not game or player_id not in game.players:
            return False
        
        game.players[player_id].status = PlayerStatus.SUBMITTED
        game.players[player_id].submission_time = time.time()
        
        # Check if this is the first successful submission
        if not game.winner and submission_data.get("success", False):
            game.winner = player_id
            game.status = GameStatus.FINISHED
            game.finished_at = time.time()
        
        # Add submission event
        self._add_game_update(game_id, player_id, "solution_submitted", submission_data)
        
        return True
    
    def end_game(self, game_id: str, reason: str = "completed") -> bool:
        """End a game session."""
        game = self.active_games.get(game_id)
        if not game:
            return False
        
        if reason == "abandoned":
            game.status = GameStatus.ABANDONED
        else:
            game.status = GameStatus.FINISHED
        
        game.finished_at = time.time()
        
        # Add game end event
        self._add_game_update(game_id, "system", "game_ended", {"reason": reason})
        
        return True
    
    def get_opponent_code(self, game_id: str, player_id: str, delay_seconds: int = 30) -> Optional[str]:
        """Get opponent's code with delay (for game mechanic)."""
        game = self.active_games.get(game_id)
        if not game:
            return None
        
        # Find opponent
        opponent_id = None
        for pid in game.players.keys():
            if pid != player_id:
                opponent_id = pid
                break
        
        if not opponent_id:
            return None
        
        # Check if enough time has passed (delay mechanic)
        current_time = time.time()
        opponent_updates = [
            update for update in self.game_updates.get(game_id, [])
            if update.player_id == opponent_id and update.event_type == "code_update"
        ]
        
        if opponent_updates:
            latest_update = max(opponent_updates, key=lambda x: x.timestamp)
            if current_time - latest_update.timestamp >= delay_seconds:
                return game.players[opponent_id].code
        
        return None
    
    def get_game_updates(self, game_id: str, since: Optional[float] = None) -> List[GameUpdate]:
        """Get game updates since a specific timestamp."""
        updates = self.game_updates.get(game_id, [])
        if since:
            updates = [update for update in updates if update.timestamp > since]
        return updates
    
    def _add_game_update(self, game_id: str, player_id: str, event_type: str, data: Dict[str, Any]):
        """Add a game update event."""
        update = GameUpdate(
            game_id=game_id,
            player_id=player_id,
            event_type=event_type,
            data=data,
            timestamp=time.time()
        )
        
        if game_id not in self.game_updates:
            self.game_updates[game_id] = []
        
        self.game_updates[game_id].append(update)
        
        # Keep only last 100 updates per game to prevent memory bloat
        if len(self.game_updates[game_id]) > 100:
            self.game_updates[game_id] = self.game_updates[game_id][-100:]


# Global instance
game_service = GameService()