/**
 * API request and response Zod schemas and TypeScript types
 * Provides runtime validation and compile-time type safety for HTTP API data structures
 */

import { z } from 'zod';
import { TestResultsDataSchema, GameParticipantSchema, UserStatsSchema } from './user';
import { QuestionDataSchema } from './question';

// API Request schemas
export const CreateGameRequestSchema = z.object({
  player_ids: z.array(z.string()),
  question_name: z.string(),
});
export type CreateGameRequest = z.infer<typeof CreateGameRequestSchema>;

export const UpdateGameRequestSchema = z.object({
  player_id: z.string(),
  code: z.string().optional(),
  language: z.string().optional(),
  status: z.string().optional(),
});
export type UpdateGameRequest = z.infer<typeof UpdateGameRequestSchema>;

export const SubmitCodeRequestSchema = z.object({
  player_id: z.string(),
  code: z.string(),
  language: z.string(),
});
export type SubmitCodeRequest = z.infer<typeof SubmitCodeRequestSchema>;

export const JoinQueueRequestSchema = z.object({
  player_id: z.string(),
  player_name: z.string(),
  question_name: z.string(),
  anonymous: z.boolean(),
  image_url: z.string().url().optional(),
  selected_difficulties: z.object({
    easy: z.boolean(),
    medium: z.boolean(),
    hard: z.boolean(),
  }),
});
export type JoinQueueRequest = z.infer<typeof JoinQueueRequestSchema>;

// API Response schemas
export const CreateGameResponseSchema = z.object({
  game_id: z.string(),
  status: z.string(),
  message: z.string(),
});
export type CreateGameResponse = z.infer<typeof CreateGameResponseSchema>;

export const GameStatusResponseSchema = z.object({
  game_id: z.string(),
  status: z.string(),
  players: z.array(z.any()),
  created_at: z.string(),
  updated_at: z.string(),
});
export type GameStatusResponse = z.infer<typeof GameStatusResponseSchema>;

export const SubmitCodeResponseSchema = z.object({
  success: z.boolean(),
  message: z.string(),
  test_results: TestResultsDataSchema.optional(),
});
export type SubmitCodeResponse = z.infer<typeof SubmitCodeResponseSchema>;

export const ApiQueueStatusResponseSchema = z.object({
  in_queue: z.boolean(),
  position: z.number(),
  estimated_wait_time: z.number(),
});
export type ApiQueueStatusResponse = z.infer<typeof ApiQueueStatusResponseSchema>;

export const GameHistoryResponseSchema = z.object({
  games: z.array(GameParticipantSchema),
  total_count: z.number(),
});
export type GameHistoryResponse = z.infer<typeof GameHistoryResponseSchema>;

export const UserStatsResponseSchema = z.object({
  user_id: z.string(),
  stats: UserStatsSchema,
});
export type UserStatsResponse = z.infer<typeof UserStatsResponseSchema>;

export const QuestionListResponseSchema = z.object({
  questions: z.array(QuestionDataSchema),
  total_count: z.number(),
});
export type QuestionListResponse = z.infer<typeof QuestionListResponseSchema>;

export const QuestionDetailsResponseSchema = z.object({
  question: QuestionDataSchema,
});
export type QuestionDetailsResponse = z.infer<typeof QuestionDetailsResponseSchema>;

// Generic API response wrapper
export const ApiResponseSchema = z.object({
  success: z.boolean(),
  message: z.string(),
  data: z.any().optional(),
  error: z.string().optional(),
});
export type ApiResponse<T = any> = z.infer<typeof ApiResponseSchema> & {
  data?: T;
};

// API error response
export const ApiErrorSchema = z.object({
  success: z.literal(false),
  message: z.string(),
  error: z.string(),
  code: z.number().optional(),
});
export type ApiError = z.infer<typeof ApiErrorSchema>;

// Pagination parameters
export const PaginationParamsSchema = z.object({
  page: z.number().optional(),
  limit: z.number().optional(),
  offset: z.number().optional(),
});
export type PaginationParams = z.infer<typeof PaginationParamsSchema>;

// Common query parameters
export const QueryParamsSchema = PaginationParamsSchema.extend({
  search: z.string().optional(),
  sort_by: z.string().optional(),
  sort_order: z.enum(['asc', 'desc']).optional(),
  filter: z.record(z.string(), z.any()).optional(),
});
export type QueryParams = z.infer<typeof QueryParamsSchema>;

// Validation functions
export const validateCreateGameRequest = (data: unknown): CreateGameRequest => {
  return CreateGameRequestSchema.parse(data);
};

export const validateSubmitCodeRequest = (data: unknown): SubmitCodeRequest => {
  return SubmitCodeRequestSchema.parse(data);
};

export const validateSubmitCodeResponse = (data: unknown): SubmitCodeResponse => {
  return SubmitCodeResponseSchema.parse(data);
};

export const validateApiResponse = <T>(data: unknown): ApiResponse<T> => {
  return ApiResponseSchema.parse(data) as ApiResponse<T>;
};

export const safeValidateApiResponse = <T>(data: unknown) => {
  const result = ApiResponseSchema.safeParse(data);
  return result.success ? { ...result, data: result.data as ApiResponse<T> } : result;
};

export const validateGameHistoryResponse = (data: unknown): GameHistoryResponse => {
  return GameHistoryResponseSchema.parse(data);
};

export const validateUserStatsResponse = (data: unknown): UserStatsResponse => {
  return UserStatsResponseSchema.parse(data);
};