// Import questions data and proper types
import questionsData from "../../../backend/data/questions.json";

// Import utilities
import {
  loadTestSolution,
  SUPPORTED_LANGUAGES,
  getLanguageDisplayName,
} from "../support/test-solutions-loader";
import { replaceMonacoEditorContent } from "../support/e2e-utils";

// Import custom commands
import "../support/commands";

// This is the actual structure in your questions.json file
interface QuestionFromJson {
  slug: string;
  id: number;
  title: string;
  difficulty: string;
}

// Type for the questions data structure
interface QuestionsData {
  questions: {
    easy: QuestionFromJson[];
    medium?: QuestionFromJson[];
    hard?: QuestionFromJson[];
  };
}

// Extract all question slugs from the data
const getAllQuestionSlugs = (): string[] => {
  const slugs: string[] = [];
  const typedData = questionsData as QuestionsData;

  Object.values(typedData.questions).forEach(
    (difficultyQuestions: QuestionFromJson[]) => {
      difficultyQuestions.forEach((question: QuestionFromJson) => {
        if (question.slug) {
          slugs.push(question.slug);
        }
      });
    }
  );
  return slugs;
};

const questionSlugs = getAllQuestionSlugs();
// Helper to run languages in reverse so combinations run "backwards"
// const reversedLanguages = [...SUPPORTED_LANGUAGES].reverse();
// Only test JavaScript
const reversedLanguages = ["java", "cpp", "python", "javascript"] as const;

describe("Practice Question E2E Tests", () => {
  beforeEach(() => {
    // Clear any previous state
    cy.clearLocalStorage();
    cy.clearCookies();
  });

  // Test a subset of questions (to avoid long test runs)
  // Reverse the questions list so we iterate from last->first
  const questionsToTest = [...questionSlugs].reverse();

  // Test language-specific functionality with real solutions
  questionsToTest.forEach((questionSlug) => {
    reversedLanguages.forEach((language) => {
      it(`should complete full workflow for ${questionSlug} in ${language}`, () => {
        // Load test solution for this question and language
        loadTestSolution(questionSlug, language).then((solution) => {
          if (!solution) {
            // FAIL the test instead of skipping it - this should never happen for valid questions
            cy.task(
              "log",
              `❌ CRITICAL FAILURE: No test solution found for ${questionSlug} in ${language}`
            );
            throw new Error(
              `❌ CRITICAL FAILURE: No test solution found for ${questionSlug} in ${language}. This indicates missing harness or test data.`
            );
          }

          // Additional validation - solution should have meaningful content
          if (!solution.code || solution.code.trim().length < 10) {
            throw new Error(
              `❌ CRITICAL FAILURE: Invalid solution for ${questionSlug} in ${language}. Solution code is too short or empty.`
            );
          }

          cy.log(`Testing ${questionSlug} with ${language}: real solution`);

          // Navigate to the practice page with error handling
          cy.visit(`/practice/${questionSlug}`, { failOnStatusCode: true });

          // Wait for page to load with strict error checking
          cy.get('[data-testid="practice-page"]', { timeout: 10000 })
            .should("be.visible")
            .should("exist");

          // Verify we're actually on the right page
          cy.url().should("include", `/practice/${questionSlug}`);

          // Additional check - page should not show error messages
          cy.get("body").should("not.contain.text", "Page not found");
          cy.get("body").should("not.contain.text", "Error 404");

          // Step 1: Select the target language using robust pattern
          cy.get('[data-testid="language-selector"]')
            .should("be.visible")
            .then(($selector) => {
              const current = $selector.text().trim().toLowerCase();
              if (!current.includes(language.toLowerCase())) {
                // Use the force-based approach that bypasses visibility issues
                cy.forceSelectLanguage(
                  language as "python" | "javascript" | "cpp" | "java"
                );
              }
            });

          // Verify language was selected
          cy.get('[data-testid="language-selector"]').should(
            "contain.text",
            getLanguageDisplayName(language)
          );

          // Wait for language change to complete and Monaco editor to remount
          cy.wait(1500);

          // Wait for Monaco editor to be fully loaded and available after language change
          cy.get(".monaco-editor", { timeout: 15000 }).should("be.visible");

          // Use Monaco editor API directly since we know it exists
          cy.window().then((win) => {
            const editor = (win as any).__monacoEditor; // eslint-disable-line @typescript-eslint/no-explicit-any
            if (editor && typeof editor.setValue === "function") {
              editor.setValue(solution.code);
              cy.wait(200); // Brief wait for editor to update

              // Verify using the editor API, not DOM content
              const actualContent = editor.getValue();
              if (actualContent !== solution.code) {
                throw new Error(
                  `❌ CRITICAL FAILURE: Editor content mismatch for ${questionSlug} in ${language}. Expected length: ${solution.code.length}, Actual length: ${actualContent.length}`
                );
              }
            } else {
              // Fallback to the helper function
              replaceMonacoEditorContent(solution.code);
              // For fallback, just check that some content exists - but fail if completely empty
              cy.get(".monaco-editor").should("contain.text", "class");
              cy.get(".monaco-editor").should("not.be.empty");
            }
          });

          // Step 3: Run sample tests first
          cy.get('[data-testid="run-button"]')
            .should("be.visible")
            .should("not.be.disabled")
            .click();

          // Wait for test results with timeout - FAIL if tests don't complete
          cy.get('[data-testid="test-results"]', { timeout: 30000 })
            .should("be.visible")
            .should("exist")
            .should("not.be.empty");

          // Additional check - ensure test results actually contain content
          cy.get('[data-testid="test-results"]').within(() => {
            cy.get('[data-testid="test-status"]')
              .should("exist")
              .should("not.be.empty");
          });

          // Verify sample tests completed successfully
          cy.get('[data-testid="test-results"]').within(() => {
            // FAIL if we don't see success indicators
            cy.get('[data-testid="test-status"]').should("contain.text", "✓✓✓");

            // Additional validation - should not contain any failure indicators
            cy.get('[data-testid="test-status"]').should(
              "not.contain.text",
              "✗"
            );
            cy.get('[data-testid="test-status"]').should(
              "not.contain.text",
              "Error"
            );
            cy.get('[data-testid="test-status"]').should(
              "not.contain.text",
              "Failed"
            );

            // Check that we actually ran tests (not 0/3 passed)
            cy.get('[data-testid="tests-passed"]').should(
              "not.contain.text",
              "0/"
            );
          });

          // // Step 4: Submit full solution - COMMENTED OUT to only test samples
          // cy.get('[data-testid="submit-button"]').should("be.visible").click();
          // cy.get('[data-testid="test-results"]', { timeout: 45000 }).should(
          //   "be.visible"
          // );

          // // Verify full submission was successful - MUST PASS ALL TESTS
          // cy.get('[data-testid="test-results"]').within(() => {
          //   // Check that we have a success status - if tests fail, this will fail the Cypress test
          //   cy.get('[data-testid="test-status"]').should(
          //     "contain.text",
          //     "✓✓✓✓✓✓✓✓✓✓✓✓"
          //   );
          //   // Ensure we're not showing 0 passed tests
          //   cy.get('[data-testid="tests-passed"]').should(
          //     "not.contain.text",
          //     "0/"
          //   );
          //   // Ensure we have some meaningful number of passed tests
          //   cy.get('[data-testid="tests-passed"]').should("contain.text", "/");
          // });

          // Log successful completion of sample tests
          cy.log(
            `✅ Successfully completed sample tests for ${questionSlug} in ${language}`
          );
        });
      });
    });
  });
});
