import { twoSumSolutions, twoSumSolutionsBruteForce } from './two-sum-solutions';
import { addTwoNumbersSolutions } from './add-two-numbers-solutions';
import { longestSubstringSolutions, longestSubstringSolutionsSet } from './longest-substring-solutions';
import type { Language } from '../../types/languages';

export type QuestionName = 'two-sum' | 'add-two-numbers' | 'longest-substring-without-repeating-characters';

export interface SolutionSet {
  [key: string]: string;
}

export class SolutionManager {
  private static solutions: Record<QuestionName, SolutionSet> = {
    'two-sum': twoSumSolutions,
    'add-two-numbers': addTwoNumbersSolutions,
    'longest-substring-without-repeating-characters': longestSubstringSolutions
  };

  private static alternativeSolutions: Record<string, SolutionSet> = {
    'two-sum-brute-force': twoSumSolutionsBruteForce,
    'longest-substring-set': longestSubstringSolutionsSet
  };

  /**
   * Get the optimal solution for a question in a specific language
   */
  static getOptimalSolution(questionName: QuestionName, language: Language): string {
    const solution = this.solutions[questionName]?.[language];
    if (!solution) {
      throw new Error(`No solution found for ${questionName} in ${language}`);
    }
    return solution;
  }

  /**
   * Get an alternative solution (e.g., brute force for testing slower approaches)
   */
  static getAlternativeSolution(questionName: string, language: Language): string {
    const solution = this.alternativeSolutions[questionName]?.[language];
    if (!solution) {
      throw new Error(`No alternative solution found for ${questionName} in ${language}`);
    }
    return solution;
  }

  /**
   * Get all available solutions for a question
   */
  static getAllSolutions(questionName: QuestionName): SolutionSet {
    return this.solutions[questionName] || {};
  }

  /**
   * Get all supported languages for a question
   */
  static getSupportedLanguages(questionName: QuestionName): Language[] {
    const solutions = this.solutions[questionName];
    if (!solutions) return [];
    return Object.keys(solutions) as Language[];
  }

  /**
   * Check if a solution exists for a given question and language
   */
  static hasSolution(questionName: QuestionName, language: Language): boolean {
    return !!this.solutions[questionName]?.[language];
  }

  /**
   * Get all supported questions
   */
  static getSupportedQuestions(): QuestionName[] {
    return Object.keys(this.solutions) as QuestionName[];
  }

  /**
   * Get a winning solution (optimized for speed and correctness)
   * This is used in E2E tests to simulate a player submitting a correct solution
   */
  static getWinningSolution(questionName: QuestionName, language: Language): string {
    return this.getOptimalSolution(questionName, language);
  }

  /**
   * Get a losing solution (intentionally slow or incorrect)
   * This is used in E2E tests to simulate a player who doesn't win
   */
  static getLosingSolution(questionName: QuestionName, language: Language): string {
    // Try to get brute force first, otherwise return optimal but with delay simulation
    const alternativeKey = `${questionName}-brute-force`;
    try {
      return this.getAlternativeSolution(alternativeKey, language);
    } catch {
      // Return optimal solution but we can simulate delay in the test
      return this.getOptimalSolution(questionName, language);
    }
  }

  /**
   * Get code with intentional syntax errors for testing error handling
   */
  static getBrokenSolution(questionName: QuestionName, language: Language): string {
    const solution = this.getOptimalSolution(questionName, language);
    
    // Introduce language-specific syntax errors
    switch (language) {
      case 'python':
        return solution.replace('def ', 'def broken_syntax '); // Invalid function name
      case 'javascript':
        return solution.replace('{', '{ missing_bracket'); // Missing closing bracket
      case 'java':
        return solution.replace('class', 'Class'); // Wrong capitalization
      case 'cpp':
        return solution.replace(';', ''); // Missing semicolon
      default:
        return solution.replace(/[{}]/g, ''); // Remove all brackets
    }
  }
}