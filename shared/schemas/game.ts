/**
 * Game-related Zod schemas and TypeScript types
 * Provides runtime validation and compile-time type safety for game state and matchmaking
 */

import { z } from 'zod';
import { PlayerInfoSchema, CustomUserSchema, OpponentDataSchema, GameParticipantSchema, DifficultyLevelSchema } from './user';

// Enums
export const GameStatusSchema = z.enum([
  'waiting',
  'in_progress',
  'finished',
  'cancelled'
]);
export type GameStatus = z.infer<typeof GameStatusSchema>;

// Difficulty State Schema
export const DifficultyStateSchema = z.object({
  easy: z.boolean(),
  medium: z.boolean(),
  hard: z.boolean(),
});
export type DifficultyState = z.infer<typeof DifficultyStateSchema>;

// Game State Schema
export const GameStateSchema = z.object({
  game_id: z.string(),
  players: z.record(z.string(), PlayerInfoSchema).default({}),
  finished_players: z.set(z.string()).default(new Set()),
  created_at: z.date().default(() => new Date()),
  question_name: z.string().default(''),
  difficulty: DifficultyLevelSchema.default('easy'),
  
  // Player assignments
  player1: z.string().default(''),
  player2: z.string().default(''),
  
  // Legacy code storage
  player1_code: z.string().default(''),
  player2_code: z.string().default(''),
  player1_code_timestamp: z.number().optional(),
  player2_code_timestamp: z.number().optional(),
  
  // Language-aware code storage
  player_codes: z.record(z.string(), z.record(z.string(), z.string())).default({}), // {player_id: {language: code}}
  player_code_timestamps: z.record(z.string(), z.record(z.string(), z.number())).default({}), // {player_id: {language: timestamp}}
  current_languages: z.record(z.string(), z.string()).default({}), // {player_id: current_language}
  
  // Game timing
  game_start_time: z.number().optional(),
  players_joined: z.set(z.string()).default(new Set()),
  
  // Starter code for comparison
  starter_codes: z.record(z.string(), z.string()).default({}), // {language: code}
});
export type GameState = z.infer<typeof GameStateSchema>;

// Match Found Data Schema
export const MatchFoundDataSchema = z.object({
  game_id: z.string(),
  opponent_Name: z.string(),
  opponentImageURL: z.string().url().optional(),
  question_name: z.string(),
});
export type MatchFoundData = z.infer<typeof MatchFoundDataSchema>;

// Match Found Response Schema
export const MatchFoundResponseSchema = z.object({
  game_id: z.string(),
  opponent_id: z.string(),
  opponent_name: z.string(),
  opponent_image_url: z.string().url().optional(),
  question_name: z.string(),
});
export type MatchFoundResponse = z.infer<typeof MatchFoundResponseSchema>;

// Queue Status Schema
export const QueueStatusSchema = z.object({
  in_queue: z.boolean(),
  selected_difficulties: DifficultyStateSchema,
  estimated_wait_time: z.number().optional(),
  queue_position: z.number().optional(),
});
export type QueueStatus = z.infer<typeof QueueStatusSchema>;

// Queue Status Response Schema
export const QueueStatusResponseSchema = z.object({
  in_queue: z.boolean(),
  position: z.number(),
  estimated_wait_time: z.number(),
});
export type QueueStatusResponse = z.infer<typeof QueueStatusResponseSchema>;

// Game History Item Schema
export const GameHistoryItemSchema = z.object({
  game_id: z.number(),
  difficulty: z.string(),
  question_name: z.string(),
  participants: z.array(GameParticipantSchema),
  user_won: z.boolean(),
  result: z.enum(['won', 'lost', 'tie']),
  user_time: z.number(),
  opponent_best_time: z.number(),
});
export type GameHistoryItem = z.infer<typeof GameHistoryItemSchema>;

// Game Context Type Schema (for React context)
export const GameContextTypeSchema = z.object({
  difficulty: DifficultyLevelSchema,
  question_name: z.string(),
  socket: z.any(), // Socket.IO socket - hard to type precisely
  user: CustomUserSchema.nullable(),
  loading: z.boolean(),
  opponent: OpponentDataSchema,
  gameId: z.string(),
  isAnonymous: z.boolean().optional(),
  anonymousId: z.string().optional(),
  selectedDifficulties: DifficultyStateSchema.optional(),
});
export type GameContextType = z.infer<typeof GameContextTypeSchema> & {
  setSelectedDifficulties?: React.Dispatch<React.SetStateAction<DifficultyState>>;
  handleFindGame?: () => void;
  clearGameData?: () => void;
};

// Emoji Request Schema
export const EmojiRequestSchema = z.object({
  emoji: z.string(),
  player1: z.string(),
});
export type EmojiRequest = z.infer<typeof EmojiRequestSchema>;

// Validation functions
export const validateGameState = (data: unknown): GameState => {
  return GameStateSchema.parse(data);
};

export const safeValidateGameState = (data: unknown) => {
  return GameStateSchema.safeParse(data);
};

export const validateMatchFoundData = (data: unknown): MatchFoundData => {
  return MatchFoundDataSchema.parse(data);
};

export const validateQueueStatus = (data: unknown): QueueStatus => {
  return QueueStatusSchema.parse(data);
};

export const validateGameHistoryItem = (data: unknown): GameHistoryItem => {
  return GameHistoryItemSchema.parse(data);
};