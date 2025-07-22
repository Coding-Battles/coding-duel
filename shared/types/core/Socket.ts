/**
 * Socket.IO event interfaces and types
 * Consolidates all real-time communication data structures
 */

import { PlayerInfo, OpponentData, TestResultsData } from './User';
import { GameState, DifficultyState } from './Game';
import { QuestionData } from './Question';

// Socket event payloads
export interface JoinGameData {
  game_id: string;
  player_id: string;
}

export interface CodeUpdateData {
  game_id: string;
  player_id: string;
  code: string;
  language: string;
}

export interface InstantCodeUpdateData extends CodeUpdateData {
  reason: string;
}

export interface PlayerStatusUpdateData {
  game_id: string;
  player_id: string;
  status: string;
  data?: Record<string, any>;
}

export interface SubmitSolutionData {
  game_id: string;
  player_id: string;
  submission: TestResultsData;
}

export interface LeaveGameData {
  game_id: string;
  player_id: string;
}

export interface JoinQueueData {
  player_id: string;
  player_name: string;
  question_name: string;
  anonymous: boolean;
  image_url?: string;
  selected_difficulties: DifficultyState;
}

export interface LeaveQueueData {
  player_id: string;
}

// Socket event responses
export interface GameJoinedResponse {
  game_id: string;
  game_state: GameState | null;
  start_time?: number;
}

export interface GameStartResponse {
  game_id: string;
  start_time: number;
}

export interface OpponentCodeReadyResponse {
  code: string;
  from_player: string;
  language: string;
  timestamp: number;
  instant?: boolean;
  reason?: string;
}

export interface PlayerCodeUpdatedResponse {
  player_id: string;
  timestamp: number;
  instant?: boolean;
}

export interface PlayerLanguageChangedResponse {
  player_id: string;
  language: string;
  immediate: boolean;
}

export interface PlayerStatusChangedResponse {
  player_id: string;
  status: string;
  data?: Record<string, any>;
}

export interface SolutionSubmittedResponse {
  player_id: string;
  submission: TestResultsData;
  game_state: GameState | null;
}

export interface GameFinishedResponse {
  winner: string;
  game_state: GameState;
}

export interface PlayerLeftResponse {
  player_id: string;
  game_ended: boolean;
}

export interface ErrorResponse {
  message: string;
}

// Socket event names (for type safety)
export enum SocketEvents {
  // Outgoing (client to server)
  JOIN_GAME = "join_game",
  CODE_UPDATE = "code_update", 
  INSTANT_CODE_UPDATE = "instant_code_update",
  PLAYER_STATUS_UPDATE = "player_status_update",
  SUBMIT_SOLUTION = "submit_solution",
  LEAVE_GAME = "leave_game",
  JOIN_QUEUE = "join_queue",
  LEAVE_QUEUE = "leave_queue",
  
  // Incoming (server to client)
  GAME_JOINED = "game_joined",
  GAME_START = "game_start",
  OPPONENT_CODE_READY = "opponent_code_ready",
  PLAYER_CODE_UPDATED = "player_code_updated",
  PLAYER_LANGUAGE_CHANGED = "player_language_changed",
  PLAYER_STATUS_CHANGED = "player_status_changed",
  SOLUTION_SUBMITTED = "solution_submitted",
  GAME_FINISHED = "game_finished",
  PLAYER_LEFT = "player_left",
  MATCH_FOUND = "match_found",
  QUEUE_UPDATE = "queue_update",
  ERROR = "error"
}