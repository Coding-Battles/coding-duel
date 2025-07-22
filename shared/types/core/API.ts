/**
 * API request and response interfaces
 * Consolidates all HTTP API data structures
 */

import { TestResultsData, GameParticipant, UserStats } from './User';
import { QuestionData } from './Question';
import { GameHistoryItem } from './Game';

// API Request interfaces
export interface CreateGameRequest {
  player_ids: string[];
  question_name: string;
}

export interface UpdateGameRequest {
  player_id: string;
  code?: string;
  language?: string;
  status?: string;
}

export interface SubmitCodeRequest {
  player_id: string;
  code: string;
  language: string;
}

export interface JoinQueueRequest {
  player_id: string;
  player_name: string;
  question_name: string;
  anonymous: boolean;
  image_url?: string;
  selected_difficulties: {
    easy: boolean;
    medium: boolean;
    hard: boolean;
  };
}

// API Response interfaces
export interface CreateGameResponse {
  game_id: string;
  status: string;
  message: string;
}

export interface GameStatusResponse {
  game_id: string;
  status: string;
  players: any[];
  created_at: string;
  updated_at: string;
}

export interface SubmitCodeResponse {
  success: boolean;
  message: string;
  test_results?: TestResultsData;
}

export interface QueueStatusResponse {
  in_queue: boolean;
  position: number;
  estimated_wait_time: number;
}

export interface GameHistoryResponse {
  games: GameParticipant[];
  total_count: number;
}

export interface UserStatsResponse {
  user_id: string;
  stats: UserStats;
}

export interface QuestionListResponse {
  questions: QuestionData[];
  total_count: number;
}

export interface QuestionDetailsResponse {
  question: QuestionData;
}

// Generic API response wrapper
export interface ApiResponse<T = any> {
  success: boolean;
  message: string;
  data?: T;
  error?: string;
}

// API error response
export interface ApiError {
  success: false;
  message: string;
  error: string;
  code?: number;
}

// Pagination parameters
export interface PaginationParams {
  page?: number;
  limit?: number;
  offset?: number;
}

// Common query parameters
export interface QueryParams extends PaginationParams {
  search?: string;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
  filter?: Record<string, any>;
}