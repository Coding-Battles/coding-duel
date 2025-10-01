/**
 * User-related interfaces and types
 * Consolidates all user, player, and profile related data structures
 */

export interface BaseUser {
  id: string;
  name?: string;
  email?: string;
}

export interface GameParticipant {
  id?: number;
  question_name: string;
  difficulty: string;
  game_id: number;
  player_name: string;
  player_code: string;
  implement_time: number;
  time_complexity: string;
  final_time: number;
  user_id: string;
}

export interface CustomUser extends BaseUser {
  username?: string;
  image?: string;
  selectedPfp?: number;
  anonymous?: boolean;
  game_ids?: number[];
  easylp?: number; // LP for easy games
  mediumlp?: number; // LP for medium games
  hardlp?: number; // LP for hard games
}

export interface PlayerInfo {
  id: string;
  sid: string; // Socket ID
  name: string;
  anonymous: boolean;
  image_url?: string;
  game_stats?: TestResultsData;
}

export interface Player {
  id: string;
  name: string;
  status: PlayerStatus;
  code?: string;
  language?: string;
  last_update?: number;
  submitted?: boolean;
  submit_time?: number;
}

export interface OpponentData {
  id?: string;
  name?: string;
  image_url?: string;
  status?: string;
  timesRan?: number;
  timeElapsed?: string;
  playerLp?: number;
  wins?: number;
}


export interface UserStats {
  totalSolved: number;
  easySolved: number;
  mediumSolved: number;
  hardSolved: number;
  totalSubmissions: number;
  acceptanceRate: number;
  ranking: number;
  streak: number;
}

// Enums
export enum PlayerStatus {
  WAITING = "waiting",
  TYPING = "typing", 
  RUNNING = "running",
  IDLE = "idle",
  SUBMITTED = "submitted"
}

// Import from Question.ts to avoid circular dependency
export interface TestResultsData {
  success: boolean;
  test_results: any[];
  total_passed: number;
  total_failed: number;
  error?: string;
  message: string;
  code: string;
  player_name: string;
  opponent_id: string;
  complexity?: string;
  implement_time?: number;
  final_time?: number;
}