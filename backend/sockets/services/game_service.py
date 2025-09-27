"""
Game service for managing active game sessions and real-time events.
"""
import time
from typing import Dict, Any, Optional, List
from datetime import datetime

from backend.models.core import (
    GameState, 
    PlayerInfo, 
    PlayerStatus,
    GameStatus,
    GameUpdate
)


class GameService:
    """Service for managing active game sessions."""
    
    def __init__(self):
        self.active_games: Dict[str, GameState] = {}
        self.game_updates: Dict[str, List[GameUpdate]] = {}
        self.game_states: Dict[str, GameState] = {}

    def set_dependencies(self, game_states_param=None):
        self.game_states = game_states_param
    
    def create_game(self, game_id: str, question_name: str, players: List[Dict[str, Any]]) -> GameState:
        """Create a new game session using centralized GameState model."""
        # Create PlayerInfo objects for the centralized GameState
        player_info_dict = {}
        player_ids = []
        
        for player in players:
            player_info = PlayerInfo(
                id=player["id"],
                name=player["name"],
                anonymous=player.get("anonymous", False),
                sid=player.get("sid", "")
            )
            player_info_dict[player["id"]] = player_info
            player_ids.append(player["id"])
        
        # Create the centralized GameState
        game_state = GameState(
            game_id=game_id,
            question_name=question_name,
            players=player_info_dict,
            created_at=datetime.now(),
            # Set player1 and player2 for backward compatibility
            player1=player_ids[0] if len(player_ids) > 0 else "",
            player2=player_ids[1] if len(player_ids) > 1 else "",
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
        
        # The centralized GameState handles code differently - using player_codes dict
        # For now, just mark the player as active
        # Code is handled by the socket events directly
        
        # Add update event
        self._add_game_update(game_id, player_id, "code_update", {"code": code})
        
        return True
    
    def update_player_status(self, game_id: str, player_id: str, status: PlayerStatus, data: Dict[str, Any] = None) -> bool:
        """Update a player's status."""
        game = self.active_games.get(game_id)
        if not game or player_id not in game.players:
            return False
        
        # The centralized GameState doesn't have a direct status field on PlayerInfo
        # Status updates are handled through the socket events
        
        # Add update event
        self._add_game_update(game_id, player_id, "status_update", {
            "status": status.value if hasattr(status, 'value') else str(status),
            "data": data or {}
        })
        
        return True
    
    def submit_solution(self, game_id: str, player_id: str, submission_data: Dict[str, Any]) -> bool:
        """Handle player solution submission."""
        game = self.active_games.get(game_id)
        if not game or player_id not in game.players:
            return False
        
        # Mark player as finished in the centralized GameState
        game.mark_player_finished(player_id)
        
        # Add submission event
        self._add_game_update(game_id, player_id, "solution_submitted", submission_data)
        
        return True
    
    def end_game(self, game_id: str, reason: str = "completed") -> bool:
        """End a game session."""
        game = self.active_games.get(game_id)
        if not game:
            return False
        
        # The centralized GameState doesn't have status/finished_at fields
        # Game ending is handled through the socket events
        
        # Add game end event
        self._add_game_update(game_id, "system", "game_ended", {"reason": reason})
        
        return True
    
    def get_opponent_code(self, game_id: str, player_id: str, delay_seconds: int = 30) -> Optional[str]:
        """Get opponent's code with delay (for game mechanic)."""
        game = self.active_games.get(game_id)
        if not game:
            return None
        
        # Use the centralized GameState's get_opponent_id method
        opponent_id = game.get_opponent_id(player_id)
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
                # Get code from the centralized GameState's player_codes structure
                if opponent_id in game.player_codes:
                    # Return the most recent code (any language)
                    opponent_codes = game.player_codes[opponent_id]
                    if opponent_codes:
                        # Get the current language or any available code
                        current_lang = game.current_languages.get(opponent_id)
                        if current_lang and current_lang in opponent_codes:
                            return opponent_codes[current_lang]
                        else:
                            # Return any available code
                            return next(iter(opponent_codes.values()))
        
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
            timestamp=datetime.now()
        )
        
        if game_id not in self.game_updates:
            self.game_updates[game_id] = []
        
        self.game_updates[game_id].append(update)
        
        # Keep only last 100 updates per game to prevent memory bloat
        if len(self.game_updates[game_id]) > 100:
            self.game_updates[game_id] = self.game_updates[game_id][-100:]

    def set_timer_until_end_of_game(self, game_id: str, seconds: int):
        """Set a timer until the game ends."""
        game = self.active_games.get(game_id)
        if not game:
            return False
        
        # The centralized GameState doesn't have a direct timer field
        # Timer handling is done through socket events
        
        # Add timer event
        self._add_game_update(game_id, "system", "timer_set", {"seconds": seconds})
        
        return True


# Global instance
game_service = GameService()