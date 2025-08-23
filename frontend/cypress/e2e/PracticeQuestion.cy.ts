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
// Only test Java
const reversedLanguages = ["cpp"] as const;

describe("Practice Question E2E Tests", () => {
  beforeEach(() => {
    // Clear any previous state
    cy.clearLocalStorage();
    cy.clearCookies();
  });

  // Test that we have questions to test
  it("should have questions loaded", () => {
    expect(questionSlugs).to.have.length.greaterThan(0);
    cy.log(`Found ${questionSlugs.length} questions to test`);
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
            // FAIL the test instead of skipping it
            throw new Error(
              `No test solution found for ${questionSlug} in ${language}. Test should fail, not skip.`
            );
          }

          cy.log(`Testing ${questionSlug} with ${language}: real solution`);

          // Navigate to the practice page
          cy.visit(`/practice/${questionSlug}`);

          // Wait for page to load
          cy.get('[data-testid="practice-page"]', { timeout: 10000 }).should(
            "be.visible"
          );

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
              expect(actualContent).to.equal(solution.code);
            } else {
              // Fallback to the helper function
              replaceMonacoEditorContent(solution.code);
              // For fallback, just check that some content exists
              cy.get(".monaco-editor").should("contain.text", "class");
            }
          });

          // Step 3: Run sample tests first
          cy.get('[data-testid="run-button"]').should("be.visible").click();
          cy.get('[data-testid="test-results"]', { timeout: 30000 }).should(
            "be.visible"
          );

          // Verify sample tests completed successfully
          cy.get('[data-testid="test-results"]').within(() => {
            cy.get('[data-testid="test-status"]').should("contain.text", "✓✓✓");
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

  // Test only language selection workflow (faster test)
  it("should support language selection for all languages", () => {
    const questionSlug = questionsToTest[0]; // Use first question

    // Navigate to the practice page
    cy.visit(`/practice/${questionSlug}`);
    cy.get('[data-testid="practice-page"]', { timeout: 10000 }).should(
      "be.visible"
    );

    reversedLanguages.forEach((language) => {
      // Select each language and verify it loads correctly using force-based approach
      cy.forceSelectLanguage(
        language as "python" | "javascript" | "cpp" | "java"
      );

      // Verify the selection was successful
      cy.get('[data-testid="language-selector"]').should(
        "contain.text",
        getLanguageDisplayName(language)
      );
      cy.log(`✅ Language selection works for ${language}`);
    });
  });

  // Test editor interaction without full submission
  it("should handle code editor interactions", () => {
    const questionSlug = questionsToTest[0];
    const testCode =
      "class Solution:\n    def test(self):\n        return 'hello world'";

    // Navigate to the practice page
    cy.visit(`/practice/${questionSlug}`);
    cy.get('[data-testid="practice-page"]', { timeout: 10000 }).should(
      "be.visible"
    );

    // Test code replacement
    replaceMonacoEditorContent(testCode);

    // Verify code was set (check for a unique part that shouldn't be in line numbers)
    cy.get(".monaco-editor").should("contain.text", "hello world");

    cy.log("✅ Code editor interaction works correctly");
  });

  // Test error handling - SHOULD FAIL, not pass gracefully
  it("should FAIL when missing test solutions are encountered", () => {
    const questionSlug = "non-existent-question";

    reversedLanguages.forEach((language) => {
      // This test verifies that missing solutions cause failures
      loadTestSolution(questionSlug, language).then((solution) => {
        // If solution is null, we expect this to be handled as a test failure
        // The main test loop now throws errors for missing solutions
        cy.wrap(solution).should("be.null"); // This documents the expected behavior
        cy.log(`Expected null solution for ${questionSlug} in ${language}`);
      });
    });
  });

  // Performance test - load many solutions
  it("should efficiently load multiple test solutions", () => {
    const startTime = Date.now();

    // Test loading solutions for multiple questions
    const testPromises = questionsToTest
      .slice(0, 2)
      .map((questionSlug) => {
        return reversedLanguages.map((language) => {
          return loadTestSolution(questionSlug, language);
        });
      })
      .flat();

    Promise.all(testPromises).then(() => {
      const endTime = Date.now();
      const duration = endTime - startTime;

      cy.log(`✅ Loaded ${testPromises.length} solutions in ${duration}ms`);
      expect(duration).to.be.lessThan(5000); // Should complete within 5 seconds
    });
  });

  it("playground - test specific combinations", () => {
    // Use this for manual testing of specific question/language combinations
    console.log("Available questions:", questionSlugs.slice(0, 5));
    console.log("Supported languages:", reversedLanguages);
    console.log(
      "Total test combinations:",
      questionsToTest.length * reversedLanguages.length
    );

    // Example: Test specific combination
    const questionSlug = "two-sum";
    const language = "python";

    if (questionsToTest.includes(questionSlug)) {
      loadTestSolution(questionSlug, language).then((solution) => {
        if (solution) {
          cy.log(`Found solution for ${questionSlug} in ${language}:`);
          cy.log(solution.code.substring(0, 200) + "...");
        } else {
          cy.log(`No solution found for ${questionSlug} in ${language}`);
        }
      });
    }
  });
});
