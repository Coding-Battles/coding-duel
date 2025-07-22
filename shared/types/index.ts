/**
 * Shared types index file
 * Exports all types for easy importing across frontend and backend
 */

// Core types
export * from './core/User';
export * from './core/Game';
export * from './core/Question';
export * from './core/Socket';
export * from './core/API';

// Re-export commonly used interfaces for convenience
export type {
  CustomUser,
  PlayerInfo,
  OpponentData,
  TestResultsData,
  UserStats
} from './core/User';

export type {
  GameState,
  GameContextType,
  MatchFoundData,
  QueueStatus,
  DifficultyState
} from './core/Game';

export type {
  QuestionData,
  TestCase,
  Problem
} from './core/Question';

export type {
  JoinGameData,
  CodeUpdateData,
  InstantCodeUpdateData,
  GameJoinedResponse,
  OpponentCodeReadyResponse
} from './core/Socket';

export type {
  ApiResponse,
  CreateGameRequest,
  SubmitCodeResponse,
  GameHistoryResponse
} from './core/API';