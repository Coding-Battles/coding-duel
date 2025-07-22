/**
 * User-related Zod schemas and TypeScript types
 * Provides runtime validation and compile-time type safety
 */

import { z } from 'zod';

// Move DifficultyLevel here to avoid circular imports
export const DifficultyLevelSchema = z.enum([
  'easy',
  'medium',
  'hard'
]);
export type DifficultyLevel = z.infer<typeof DifficultyLevelSchema>;

// Enums
export const PlayerStatusSchema = z.enum([
  'waiting',
  'typing', 
  'running',
  'idle',
  'submitted'
]);
export type PlayerStatus = z.infer<typeof PlayerStatusSchema>;

// Base User Schema
export const BaseUserSchema = z.object({
  id: z.string(),
  name: z.string().optional(),
  email: z.string().email().optional(),
});
export type BaseUser = z.infer<typeof BaseUserSchema>;

// Custom User Schema (extends BaseUser)
export const CustomUserSchema = BaseUserSchema.extend({
  username: z.string().optional(),
  image: z.string().url().optional(),
  selectedPfp: z.number().optional(),
  anonymous: z.boolean().optional(),
  game_ids: z.array(z.number()).optional(),
});
export type CustomUser = z.infer<typeof CustomUserSchema>;

// Test Case Schema
export const TestCaseSchema = z.object({
  input: z.record(z.string(), z.any()),
  expected_output: z.string(),
  actual_output: z.string(),
  passed: z.boolean(),
  error: z.string().optional(),
  execution_time: z.number(),
});
export type TestCase = z.infer<typeof TestCaseSchema>;

// Test Results Data Schema
export const TestResultsDataSchema = z.object({
  success: z.boolean(),
  test_results: z.array(TestCaseSchema),
  total_passed: z.number(),
  total_failed: z.number(),
  error: z.string().optional(),
  message: z.string(),
  code: z.string(),
  player_name: z.string().optional(),
  opponent_id: z.string(),
  complexity: z.string().optional(),
  implement_time: z.number().optional(),
  final_time: z.number().optional(),
});
export type TestResultsData = z.infer<typeof TestResultsDataSchema>;

// Player Info Schema
export const PlayerInfoSchema = z.object({
  id: z.string(),
  sid: z.string(), // Socket ID
  name: z.string(),
  anonymous: z.boolean().default(true),
  image_url: z.string().url().optional(),
  game_stats: TestResultsDataSchema.optional(),
});
export type PlayerInfo = z.infer<typeof PlayerInfoSchema>;

// Player Schema
export const PlayerSchema = z.object({
  id: z.string(),
  name: z.string(),
  status: PlayerStatusSchema,
  code: z.string().optional(),
  language: z.string().optional(),
  last_update: z.number().optional(),
  submitted: z.boolean().optional(),
  submit_time: z.number().optional(),
});
export type Player = z.infer<typeof PlayerSchema>;

// Opponent Data Schema
export const OpponentDataSchema = z.object({
  id: z.string().optional(),
  name: z.string().optional(),
  image_url: z.string().url().optional(),
  status: z.string().optional(),
  timesRan: z.number().optional(),
  timeElapsed: z.string().optional(),
  wins: z.number().optional(),
});
export type OpponentData = z.infer<typeof OpponentDataSchema>;

// Game Participant Schema
export const GameParticipantSchema = z.object({
  id: z.number().optional(),
  game_id: z.number(),
  player_name: z.string(),
  player_code: z.string(),
  implement_time: z.string(),
  time_complexity: z.string(),
  final_time: z.string(),
  user_id: z.string(),
});
export type GameParticipant = z.infer<typeof GameParticipantSchema>;

// User Stats Schema
export const UserStatsSchema = z.object({
  totalSolved: z.number(),
  easySolved: z.number(),
  mediumSolved: z.number(),
  hardSolved: z.number(),
  totalSubmissions: z.number(),
  acceptanceRate: z.number(),
  ranking: z.number(),
  streak: z.number(),
});
export type UserStats = z.infer<typeof UserStatsSchema>;

// Validation functions
export const validateCustomUser = (data: unknown): CustomUser => {
  return CustomUserSchema.parse(data);
};

export const safeValidateCustomUser = (data: unknown) => {
  return CustomUserSchema.safeParse(data);
};

export const validatePlayerInfo = (data: unknown): PlayerInfo => {
  return PlayerInfoSchema.parse(data);
};

export const validateTestResultsData = (data: unknown): TestResultsData => {
  return TestResultsDataSchema.parse(data);
};

export const validateUserStats = (data: unknown): UserStats => {
  return UserStatsSchema.parse(data);
};