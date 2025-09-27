/**
 * Game-related interfaces and types
 * Consolidates all game state, matchmaking, and game flow data structures
 */

import React from 'react';
import { PlayerInfo, CustomUser, OpponentData, TestResultsData } from './User';

// GameHistoryItem (from profile page)
export interface GameHistoryItem {
  game_id: number;
  participants: GameParticipant[];
  user_won: boolean;
  result: "won" | "lost" | "tie";
  user_time: number;
  opponent_best_time: number;
}

export interface GameParticipant {
  game_id: number;
  player_name: string;
  player_code: string;
  implement_time: string;
  time_complexity: string;
  final_time: string;
  user_id: string;
}

export interface GameState {
  game_id: string;
  players: Record<string, PlayerInfo>;
  finished_players: Set<string>;
  created_at: Date;
  question_name: string;
  
  // Player assignments
  player1: string;
  player2: string;
  
  // Legacy code storage
  player1_code: string;
  player2_code: string;
  player1_code_timestamp?: number;
  player2_code_timestamp?: number;
  
  // Language-aware code storage
  player_codes: Record<string, Record<string, string>>; // {player_id: {language: code}}
  player_code_timestamps: Record<string, Record<string, number>>; // {player_id: {language: timestamp}}
  current_languages: Record<string, string>; // {player_id: current_language}
  
  // Game timing
  game_start_time?: number;
  players_joined: Set<string>;
  
  // Starter code for comparison
  starter_codes: Record<string, string>; // {language: code}
}

export interface PlayerGameState {
  id: string;
  name: string;
  status: GameStatus;
  created_at: Date;
  last_update: Date;
  current_code?: string;
  submitted_code?: string;
  language: string;
  test_results?: any;
  final_stats?: TestResultsData;
}

export interface GameUpdate {
  game_id: string;
  player_id: string;
  event_type: string;
  data: any;
  timestamp: Date;
}

export interface MatchFoundData {
  game_id: string;
  opponent_Name: string;
  opponentImageURL: string;
  question_name: string;
}

export interface MatchFoundResponse {
  game_id: string;
  opponent_id: string;
  opponent_name: string;
  opponent_image_url: string;
  question_name: string;
  difficulty: string;
}

export interface QueueStatus {
  in_queue: boolean;
  selected_difficulties: DifficultyState;
  estimated_wait_time?: number;
  queue_position?: number;
}

export interface QueueStatusResponse {
  in_queue: boolean;
  position: number;
  estimated_wait_time: number;
}

export interface DifficultyState {
  easy: boolean;
  medium: boolean;
  hard: boolean;
}

export interface GameContextType {
  socket: any;
  user: CustomUser | null;
  loading: boolean;
  opponent: OpponentData;
  gameId: string;
  isAnonymous?: boolean;
  anonymousId?: string;
  selectedDifficulties?: DifficultyState;
  playerLp?: number;
  setSelectedDifficulties?: React.Dispatch<React.SetStateAction<DifficultyState>>;
  foundGame?: React.MutableRefObject<boolean>;
  handleFindGame?: () => void;
  clearGameData?: () => void;
}


// Enums
export enum GameStatus {
  WAITING = "waiting",
  IN_PROGRESS = "in_progress", 
  FINISHED = "finished",
  CANCELLED = "cancelled"
}

export enum DifficultyLevel {
  EASY = "easy",
  MEDIUM = "medium", 
  HARD = "hard"
}