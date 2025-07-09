"""
Matchmaking service for handling player queues and match formation.
"""
import uuid
from typing import List, Optional, Dict, Any
from pydantic import BaseModel


class Player(BaseModel):
    id: str  # Player's custom ID
    name: str
    sid: str  # Socket connection ID
    joined_at: float  # Timestamp when joined queue


class MatchFoundResponse(BaseModel):
    game_id: str
    opponent: str
    question_name: str


class QueueStatusResponse(BaseModel):
    status: str
    queue_size: int


class MatchmakingService:
    """Service for managing player queues and creating matches."""
    
    def __init__(self):
        self.waiting_players: List[Player] = []
        self.active_games: Dict[str, Dict[str, Any]] = {}
    
    def add_player_to_queue(self, player_data: Dict[str, Any], sid: str) -> Player:
        """Add a player to the matchmaking queue."""
        import time
        
        player = Player(
            **player_data,
            sid=sid,
            joined_at=time.time()
        )
        self.waiting_players.append(player)
        return player
    
    def remove_player_from_queue(self, sid: str) -> bool:
        """Remove a player from the queue by socket ID."""
        initial_count = len(self.waiting_players)
        self.waiting_players = [p for p in self.waiting_players if p.sid != sid]
        return len(self.waiting_players) < initial_count
    
    def try_create_match(self) -> Optional[tuple[Player, Player, str]]:
        """Try to create a match if 2+ players are in queue."""
        import time
        
        if len(self.waiting_players) >= 2:
            player1 = self.waiting_players.pop(0)
            player2 = self.waiting_players.pop(0)
            game_id = f"game_{uuid.uuid4().hex[:12]}"
            
            # Store active game
            self.active_games[game_id] = {
                "players": [player1.model_dump(), player2.model_dump()],
                "question_name": "two-sum",  # TODO: Random question selection
                "created_at": time.time(),
                "status": "active"
            }
            
            return player1, player2, game_id
        return None
    
    def get_queue_status(self) -> QueueStatusResponse:
        """Get current queue status."""
        return QueueStatusResponse(
            status="waiting" if self.waiting_players else "empty",
            queue_size=len(self.waiting_players)
        )
    
    def get_game_info(self, game_id: str) -> Optional[Dict[str, Any]]:
        """Get information about an active game."""
        return self.active_games.get(game_id)
    
    def end_game(self, game_id: str) -> bool:
        """End an active game."""
        if game_id in self.active_games:
            del self.active_games[game_id]
            return True
        return False


# Global instance
matchmaking_service = MatchmakingService()