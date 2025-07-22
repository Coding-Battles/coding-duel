/**
 * Question and test case related Zod schemas and TypeScript types
 * Provides runtime validation and compile-time type safety for problems and test cases
 */

import { z } from 'zod';
import { TestCaseSchema, DifficultyLevelSchema } from './user';

// Programming Language Schema
export const ProgrammingLanguageSchema = z.enum([
  'python',
  'javascript',
  'java',
  'cpp',
  'csharp',
  'go',
  'rust',
  'typescript'
]);
export type ProgrammingLanguage = z.infer<typeof ProgrammingLanguageSchema>;

// Problem Schema
export const ProblemSchema = z.object({
  id: z.number(),
  title: z.string(),
  difficulty: z.enum(['Easy', 'Medium', 'Hard']),
  status: z.enum(['Solved', 'Attempted', 'Not Attempted']),
  category: z.string(),
  submittedAt: z.string().optional(),
});
export type Problem = z.infer<typeof ProblemSchema>;

// Question Data Schema
export const QuestionDataSchema = z.object({
  id: z.string(),
  name: z.string(),
  title: z.string(),
  description: z.string(),
  examples: z.array(z.any()).default([]),
  constraints: z.array(z.string()).default([]),
  starter_code: z.record(z.string(), z.string()).default({}), // {language: code}
  test_cases: z.array(TestCaseSchema).optional(),
  difficulty: DifficultyLevelSchema,
  category: z.string().optional(),
});
export type QuestionData = z.infer<typeof QuestionDataSchema>;

// Time Complexity Schema
export const TimeComplexitySchema = z.object({
  code: z.string(),
});
export type TimeComplexity = z.infer<typeof TimeComplexitySchema>;

// Time Complexity Response Schema
export const TimeComplexityResponseSchema = z.object({
  time_complexity: z.string(),
});
export type TimeComplexityResponse = z.infer<typeof TimeComplexityResponseSchema>;

// Test Case Result Schema
export const TestCaseResultSchema = z.object({
  input: z.record(z.string(), z.any()),
  expected_output: z.any(),
  actual_output: z.string().optional(),
  passed: z.boolean(),
  error: z.string().optional(),
  execution_time: z.number().optional(),
});
export type TestCaseResult = z.infer<typeof TestCaseResultSchema>;

// Code Test Result Schema
export const CodeTestResultSchema = z.object({
  message: z.string(),
  code: z.string(),
  opponent_id: z.string(),
  player_name: z.string(),
  success: z.boolean(),
  test_results: z.array(TestCaseResultSchema),
  total_passed: z.number(),
  total_failed: z.number(),
  error: z.string().optional(),
  complexity: z.string().optional(),
  implement_time: z.number().optional(),
  final_time: z.number().optional(),
});
export type CodeTestResult = z.infer<typeof CodeTestResultSchema>;

// Run Test Cases Request Schema
export const RunTestCasesRequestSchema = z.object({
  player_id: z.string(),
  code: z.string(),
  language: z.string(),
  question_name: z.string(),
  timeout: z.number().default(5),
  timer: z.number(),
});
export type RunTestCasesRequest = z.infer<typeof RunTestCasesRequestSchema>;

// Run Test Cases Response Schema
export const RunTestCasesResponseSchema = z.object({
  success: z.boolean(),
  test_results: z.array(TestCaseResultSchema),
  total_passed: z.number(),
  total_failed: z.number(),
  error: z.string().optional(),
});
export type RunTestCasesResponse = z.infer<typeof RunTestCasesResponseSchema>;

// Starter Code Schema
export const StarterCodeSchema = z.object({
  python: z.string(),
  javascript: z.string(),
  java: z.string(),
  cpp: z.string(),
});
export type StarterCode = z.infer<typeof StarterCodeSchema>;

// Validation functions
export const validateQuestionData = (data: unknown): QuestionData => {
  return QuestionDataSchema.parse(data);
};

export const safeValidateQuestionData = (data: unknown) => {
  return QuestionDataSchema.safeParse(data);
};

export const validateProblem = (data: unknown): Problem => {
  return ProblemSchema.parse(data);
};

export const validateCodeTestResult = (data: unknown): CodeTestResult => {
  return CodeTestResultSchema.parse(data);
};

export const validateRunTestCasesRequest = (data: unknown): RunTestCasesRequest => {
  return RunTestCasesRequestSchema.parse(data);
};