import { vi } from 'vitest';
import type { MockSocket } from './socket-mock';
import type { CustomUser, OpponentData } from '@/shared/types';

// Mock game context data
export interface MockGameContext {
  socket: MockSocket | null;
  gameId: string | null;
  opponent: OpponentData | null;
  user: CustomUser | null;
  isAnonymous: boolean;
  anonymousId: string | null;
  loading: boolean;
}

// Create mock game context
export function createMockGameContext(
  overrides: Partial<MockGameContext> = {}
): MockGameContext {
  const defaultContext: MockGameContext = {
    socket: null,
    gameId: 'mock-game-123',
    opponent: {
      id: 'opponent-123',
      name: 'Test Opponent',
      image_url: 'https://via.placeholder.com/150'
    },
    user: {
      id: 'user-123',
      name: 'Test User',
      email: 'test@example.com',
      image: 'https://via.placeholder.com/150'
    },
    isAnonymous: false,
    anonymousId: null,
    loading: false
  };

  return { ...defaultContext, ...overrides };
}

// Mock game context hook
export const mockUseGameContext = vi.fn(() => createMockGameContext());

// Mock various game states
export const mockGameContexts = {
  // Loading state
  loading: createMockGameContext({
    loading: true,
    socket: null,
    gameId: null,
    opponent: null
  }),

  // Anonymous user
  anonymous: createMockGameContext({
    isAnonymous: true,
    anonymousId: 'anon-123',
    user: null
  }),

  // No opponent yet (waiting in queue)
  waiting: createMockGameContext({
    opponent: null,
    gameId: null
  }),

  // Ready to play (full context)
  ready: createMockGameContext(),

  // Socket disconnected
  disconnected: createMockGameContext({
    socket: null
  })
};

// Mock providers for testing
export const GameContextProviderMock = ({ 
  children, 
  value 
}: { 
  children: React.ReactNode; 
  value?: MockGameContext;
}) => {
  return children;
};

export default mockUseGameContext;