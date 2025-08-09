/**
 * Question and test case related interfaces and types
 * Consolidates all problem, test case, and submission data structures
 */

export interface Problem {
  id: number;
  title: string;
  difficulty: "Easy" | "Medium" | "Hard";
  status: "Solved" | "Attempted" | "Not Attempted";
  category: string;
  submittedAt?: string;
}

export interface TestCase {
  input: Record<string, any>;
  expected_output: string;
  actual_output: string;
  passed: boolean;
  error?: string;
  execution_time: number;
}

export interface QuestionData {
  id: string;
  title: string;
  problemDescription: string;
  examples: Array<{ input: string; output: string }>;
  constraints: string[];
  starter_code: Record<string, string>; // {language: code}
  test_cases?: TestCase[];
  difficulty: DifficultyLevel | string;
  category?: string;
}

// Enums
export enum DifficultyLevel {
  EASY = "easy",
  MEDIUM = "medium",
  HARD = "hard",
}

export enum ProgrammingLanguage {
  PYTHON = "python",
  JAVASCRIPT = "javascript",
  JAVA = "java",
  CPP = "cpp",
  CSHARP = "csharp",
  GO = "go",
  RUST = "rust",
  TYPESCRIPT = "typescript",
}

// Helper type for language display names
export const LanguageDisplayNames: Record<ProgrammingLanguage, string> = {
  [ProgrammingLanguage.PYTHON]: "Python",
  [ProgrammingLanguage.JAVASCRIPT]: "JavaScript",
  [ProgrammingLanguage.JAVA]: "Java",
  [ProgrammingLanguage.CPP]: "C++",
  [ProgrammingLanguage.CSHARP]: "C#",
  [ProgrammingLanguage.GO]: "Go",
  [ProgrammingLanguage.RUST]: "Rust",
  [ProgrammingLanguage.TYPESCRIPT]: "TypeScript",
};
