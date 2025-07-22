/**
 * Socket.IO event Zod schemas and TypeScript types
 * Provides runtime validation and compile-time type safety for real-time communication
 */

import { z } from 'zod';
import { TestResultsDataSchema } from './user';
import { GameStateSchema, DifficultyStateSchema } from './game';

// Socket event payload schemas
export const JoinGameDataSchema = z.object({
  game_id: z.string(),
  player_id: z.string(),
});
export type JoinGameData = z.infer<typeof JoinGameDataSchema>;

export const CodeUpdateDataSchema = z.object({
  game_id: z.string(),
  player_id: z.string(),
  code: z.string(),
  language: z.string(),
});
export type CodeUpdateData = z.infer<typeof CodeUpdateDataSchema>;

export const InstantCodeUpdateDataSchema = CodeUpdateDataSchema.extend({
  reason: z.string(),
});
export type InstantCodeUpdateData = z.infer<typeof InstantCodeUpdateDataSchema>;

export const PlayerStatusUpdateDataSchema = z.object({
  game_id: z.string(),
  player_id: z.string(),
  status: z.string(),
  data: z.record(z.string(), z.any()).optional(),
});
export type PlayerStatusUpdateData = z.infer<typeof PlayerStatusUpdateDataSchema>;

export const SubmitSolutionDataSchema = z.object({
  game_id: z.string(),
  player_id: z.string(),
  submission: TestResultsDataSchema,
});
export type SubmitSolutionData = z.infer<typeof SubmitSolutionDataSchema>;

export const LeaveGameDataSchema = z.object({
  game_id: z.string(),
  player_id: z.string(),
});
export type LeaveGameData = z.infer<typeof LeaveGameDataSchema>;

export const JoinQueueDataSchema = z.object({
  player_id: z.string(),
  player_name: z.string(),
  question_name: z.string(),
  anonymous: z.boolean(),
  image_url: z.string().url().optional(),
  selected_difficulties: DifficultyStateSchema,
});
export type JoinQueueData = z.infer<typeof JoinQueueDataSchema>;

export const LeaveQueueDataSchema = z.object({
  player_id: z.string(),
});
export type LeaveQueueData = z.infer<typeof LeaveQueueDataSchema>;

// Socket event response schemas
export const GameJoinedResponseSchema = z.object({
  game_id: z.string(),
  game_state: GameStateSchema.optional(),
  start_time: z.number().optional(),
});
export type GameJoinedResponse = z.infer<typeof GameJoinedResponseSchema>;

export const GameStartResponseSchema = z.object({
  game_id: z.string(),
  start_time: z.number(),
});
export type GameStartResponse = z.infer<typeof GameStartResponseSchema>;

export const OpponentCodeReadyResponseSchema = z.object({
  code: z.string(),
  from_player: z.string(),
  language: z.string(),
  timestamp: z.number(),
  instant: z.boolean().optional(),
  reason: z.string().optional(),
});
export type OpponentCodeReadyResponse = z.infer<typeof OpponentCodeReadyResponseSchema>;

export const PlayerCodeUpdatedResponseSchema = z.object({
  player_id: z.string(),
  timestamp: z.number(),
  instant: z.boolean().optional(),
});
export type PlayerCodeUpdatedResponse = z.infer<typeof PlayerCodeUpdatedResponseSchema>;

export const PlayerLanguageChangedResponseSchema = z.object({
  player_id: z.string(),
  language: z.string(),
  immediate: z.boolean(),
});
export type PlayerLanguageChangedResponse = z.infer<typeof PlayerLanguageChangedResponseSchema>;

export const PlayerStatusChangedResponseSchema = z.object({
  player_id: z.string(),
  status: z.string(),
  data: z.record(z.string(), z.any()).optional(),
});
export type PlayerStatusChangedResponse = z.infer<typeof PlayerStatusChangedResponseSchema>;

export const SolutionSubmittedResponseSchema = z.object({
  player_id: z.string(),
  submission: TestResultsDataSchema,
  game_state: GameStateSchema.optional(),
});
export type SolutionSubmittedResponse = z.infer<typeof SolutionSubmittedResponseSchema>;

export const GameFinishedResponseSchema = z.object({
  winner: z.string(),
  game_state: GameStateSchema,
});
export type GameFinishedResponse = z.infer<typeof GameFinishedResponseSchema>;

export const PlayerLeftResponseSchema = z.object({
  player_id: z.string(),
  game_ended: z.boolean(),
});
export type PlayerLeftResponse = z.infer<typeof PlayerLeftResponseSchema>;

export const ErrorResponseSchema = z.object({
  message: z.string(),
});
export type ErrorResponse = z.infer<typeof ErrorResponseSchema>;

// Socket Events Enum
export const SocketEventsSchema = z.enum([
  // Outgoing (client to server)
  'join_game',
  'code_update', 
  'instant_code_update',
  'player_status_update',
  'submit_solution',
  'leave_game',
  'join_queue',
  'leave_queue',
  
  // Incoming (server to client)
  'game_joined',
  'game_start',
  'opponent_code_ready',
  'player_code_updated',
  'player_language_changed',
  'player_status_changed',
  'solution_submitted',
  'game_finished',
  'player_left',
  'match_found',
  'queue_update',
  'error'
]);
export type SocketEvents = z.infer<typeof SocketEventsSchema>;

// Validation functions
export const validateJoinGameData = (data: unknown): JoinGameData => {
  return JoinGameDataSchema.parse(data);
};

export const validateCodeUpdateData = (data: unknown): CodeUpdateData => {
  return CodeUpdateDataSchema.parse(data);
};

export const validateInstantCodeUpdateData = (data: unknown): InstantCodeUpdateData => {
  return InstantCodeUpdateDataSchema.parse(data);
};

export const validateGameJoinedResponse = (data: unknown): GameJoinedResponse => {
  return GameJoinedResponseSchema.parse(data);
};

export const validateOpponentCodeReadyResponse = (data: unknown): OpponentCodeReadyResponse => {
  return OpponentCodeReadyResponseSchema.parse(data);
};