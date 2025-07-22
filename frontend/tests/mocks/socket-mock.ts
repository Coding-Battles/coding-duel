import { vi } from 'vitest';
import type { Socket } from 'socket.io-client';

// Type definitions for socket events
interface SocketEvents {
  connect: () => void;
  disconnect: () => void;
  connected: (data: { status: string; sid: string }) => void;
  match_found: (data: any) => void;
  game_joined: (data: { game_id: string; start_time?: number }) => void;
  game_start: (data: { game_id: string; start_time: number }) => void;
  opponent_code_update: (data: { code: string; language: string; player_id: string }) => void;
  opponent_submitted: (data: any) => void;
  game_completed: (data: any) => void;
  emoji_received: (data: { emoji: string; from: string }) => void;
}

// Mock socket implementation
export class MockSocket {
  private eventHandlers: Map<string, Function[]> = new Map();
  private isConnected: boolean = false;
  private mockGameId: string = 'mock-game-123';
  private mockPlayerId: string = 'mock-player-123';
  
  // Socket connection methods
  connect = vi.fn(() => {
    this.isConnected = true;
    this.emit('connect');
    setTimeout(() => {
      this.emit('connected', { status: 'connected', sid: this.id });
    }, 100);
  });

  disconnect = vi.fn(() => {
    this.isConnected = false;
    this.emit('disconnect');
  });

  get connected(): boolean {
    return this.isConnected;
  }

  get id(): string {
    return 'mock-socket-id';
  }

  // Event handling methods
  on = vi.fn(<K extends keyof SocketEvents>(event: K, handler: SocketEvents[K]) => {
    if (!this.eventHandlers.has(event)) {
      this.eventHandlers.set(event, []);
    }
    this.eventHandlers.get(event)!.push(handler);
  });

  off = vi.fn((event: string, handler?: Function) => {
    if (handler) {
      const handlers = this.eventHandlers.get(event);
      if (handlers) {
        const index = handlers.indexOf(handler);
        if (index !== -1) {
          handlers.splice(index, 1);
        }
      }
    } else {
      this.eventHandlers.delete(event);
    }
  });

  emit = vi.fn((event: string, data?: any) => {
    const handlers = this.eventHandlers.get(event);
    if (handlers) {
      handlers.forEach(handler => handler(data));
    }
  });

  // Game simulation methods
  simulateMatchFound(opponent: any, questionName: string) {
    setTimeout(() => {
      this.emit('match_found', {
        game_id: this.mockGameId,
        opponent_id: 'opponent-123',
        opponent_name: opponent.name || 'Test Opponent',
        opponent_image_url: opponent.image_url || 'https://via.placeholder.com/150',
        question_name: questionName
      });
    }, 1000);
  }

  simulateGameJoin(startTime?: number) {
    setTimeout(() => {
      this.emit('game_joined', {
        game_id: this.mockGameId,
        start_time: startTime
      });
    }, 500);
  }

  simulateGameStart() {
    setTimeout(() => {
      this.emit('game_start', {
        game_id: this.mockGameId,
        start_time: Date.now() / 1000
      });
    }, 2000);
  }

  simulateOpponentCodeUpdate(code: string, language: string) {
    setTimeout(() => {
      this.emit('opponent_code_update', {
        code,
        language,
        player_id: 'opponent-123'
      });
    }, Math.random() * 5000 + 1000); // Random delay between 1-6 seconds
  }

  simulateOpponentSubmission(success: boolean = false) {
    setTimeout(() => {
      this.emit('opponent_submitted', {
        player_name: 'Test Opponent',
        success,
        total_passed: success ? 12 : Math.floor(Math.random() * 8),
        total_failed: success ? 0 : Math.ceil(Math.random() * 4),
        complexity: success ? 'O(n)' : 'O(n²)',
        implement_time: 150,
        final_time: success ? 50 : 100,
        message: success ? 'Opponent passed all tests!' : 'Opponent had some failures',
        opponent_id: 'opponent-123'
      });
    }, Math.random() * 10000 + 2000); // Random delay between 2-12 seconds
  }

  simulateGameCompletion(userWon: boolean, reason: string = 'first_win') {
    setTimeout(() => {
      this.emit('game_completed', {
        message: userWon ? 'You won the game!' : 'Opponent won the game!',
        winner_id: userWon ? this.mockPlayerId : 'opponent-123',
        winner_name: userWon ? 'Test User' : 'Test Opponent',
        loser_id: userWon ? 'opponent-123' : this.mockPlayerId,
        loser_name: userWon ? 'Test Opponent' : 'Test User',
        game_end_reason: reason,
        game_end_time: Date.now() / 1000,
        winner_stats: {
          player_name: userWon ? 'Test User' : 'Test Opponent',
          implement_time: 120,
          complexity: 'O(n)',
          final_time: 80,
          success: true
        }
      });
    }, 1000);
  }

  simulateEmojiReceived(emoji: string, from: string) {
    setTimeout(() => {
      this.emit('emoji_received', {
        emoji,
        from
      });
    }, 500);
  }

  simulateDisconnection() {
    setTimeout(() => {
      this.emit('game_completed', {
        message: 'You won! Opponent disconnected.',
        winner_id: this.mockPlayerId,
        winner_name: 'Test User',
        loser_id: 'opponent-123',
        loser_name: 'Test Opponent',
        game_end_reason: 'disconnection',
        game_end_time: Date.now() / 1000,
        winner_stats: {
          player_name: 'Test User',
          success: true
        }
      });
    }, Math.random() * 5000 + 2000);
  }

  // Utility methods for testing
  clearAllEventHandlers() {
    this.eventHandlers.clear();
  }

  getEventHandlers(event: string) {
    return this.eventHandlers.get(event) || [];
  }

  hasEventHandler(event: string): boolean {
    return this.eventHandlers.has(event) && this.eventHandlers.get(event)!.length > 0;
  }
}

// Factory function to create mock socket instances
export function createMockSocket(): MockSocket {
  return new MockSocket();
}

// Mock the socket.io-client module
export const mockSocketIO = vi.fn(() => createMockSocket());

// Export mock for better-auth client
export const mockAuth = {
  useSession: vi.fn(() => ({
    data: {
      user: {
        id: 'mock-user-123',
        name: 'Test User',
        email: 'test@example.com',
        image: 'https://via.placeholder.com/150'
      }
    }
  }))
};

export default MockSocket;