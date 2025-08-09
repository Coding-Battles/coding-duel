/**
 * Test Solutions Loader
 * Utility for loading and managing test solutions for Cypress tests
 */

export interface TestSolution {
  questionSlug: string;
  language: string;
  code: string;
  fileExtension: string;
}

export type Language = "python" | "javascript" | "cpp" | "java";

export const LANGUAGE_EXTENSIONS: Record<Language, string> = {
  python: ".py",
  javascript: ".js",
  cpp: ".cpp",
  java: ".java",
};

// Visible labels in the UI (for assertions)
export const LANGUAGE_DISPLAY_NAMES: Record<Language, string> = {
  python: "Python",
  javascript: "JavaScript",
  cpp: "C++",
  java: "Java",
};

export const getLanguageDisplayName = (language: Language): string =>
  LANGUAGE_DISPLAY_NAMES[language];

export const SUPPORTED_LANGUAGES: Language[] = [
  "python",
  "javascript",
  "cpp",
  "java",
];

/**
 * Load test solution for a specific question and language
 * Uses Cypress task to read files from backend/test-solutions
 */
export const loadTestSolution = (
  questionSlug: string,
  language: Language
): Cypress.Chainable<TestSolution | null> => {
  const extension = LANGUAGE_EXTENSIONS[language];
  const filename = `${questionSlug}${extension}`;
  const filePath = `cypress/test-solutions/${filename}`;

  // Note: Cypress typing for task/then can be loose; cast final chain to expected type
  return cy.task("readTestSolution", filePath).then((code) => {
    const str = code as string | null;
    if (str) {
      return {
        questionSlug,
        language,
        code: str,
        fileExtension: extension,
      } as TestSolution;
    }
    cy.log(`No test solution found for ${questionSlug} in ${language}`);
    return null as TestSolution | null;
  }) as unknown as Cypress.Chainable<TestSolution | null>;
};

/**
 * Load all available test solutions for a question across all languages
 */
export const loadAllTestSolutions = (
  questionSlug: string
): Cypress.Chainable<TestSolution[]> => {
  const solutions: TestSolution[] = [];

  // Create a chain of promises for all languages
  let chain = cy.wrap(solutions);

  SUPPORTED_LANGUAGES.forEach((language) => {
    chain = chain.then((currentSolutions) => {
      return loadTestSolution(questionSlug, language).then((solution) => {
        if (solution) {
          currentSolutions.push(solution);
        }
        return currentSolutions;
      });
    });
  });

  return chain;
};

/**
 * Check if a test solution exists for a specific question and language
 */
export const hasTestSolution = (
  questionSlug: string,
  language: Language
): Cypress.Chainable<boolean> => {
  const extension = LANGUAGE_EXTENSIONS[language];
  const filename = `${questionSlug}${extension}`;

  return cy.task("fileExists", `backend/test-solutions/${filename}`);
};

/**
 * Get the expected starter code pattern for validation
 */
export const getStarterCodePattern = (language: Language): RegExp => {
  const patterns: Record<Language, RegExp> = {
    python: /class Solution:/,
    javascript: /class Solution \{/,
    java: /class Solution \{/,
    cpp: /class Solution \{/,
  };

  return patterns[language];
};

/**
 * Validate that test solution code follows expected format
 */
export const validateSolutionCode = (
  code: string,
  language: Language
): boolean => {
  const pattern = getStarterCodePattern(language);
  return pattern.test(code);
};

/**
 * Mock test solutions for testing (when actual files are not available)
 */
export const getMockTestSolution = (
  questionSlug: string,
  language: Language
): TestSolution => {
  const mockCode: Record<Language, string> = {
    python: `class Solution:
    def solution(self):
        # Mock solution for ${questionSlug}
        return "test_result"`,
    javascript: `class Solution {
    solution() {
        // Mock solution for ${questionSlug}
        return "test_result";
    }
}`,
    java: `class Solution {
    public String solution() {
        // Mock solution for ${questionSlug}
        return "test_result";
    }
}`,
    cpp: `class Solution {
public:
    string solution() {
        // Mock solution for ${questionSlug}
        return "test_result";
    }
};`,
  };

  return {
    questionSlug,
    language,
    code: mockCode[language],
    fileExtension: LANGUAGE_EXTENSIONS[language],
  };
};
