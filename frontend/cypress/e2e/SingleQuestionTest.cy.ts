// Import utilities
import {
  loadTestSolution,
  getLanguageDisplayName,
  type Language,
} from "../support/test-solutions-loader";
import { replaceMonacoEditorContent } from "../support/e2e-utils";

// Import custom commands
import "../support/commands";

// Monaco editor interface for type safety
interface WindowWithMonaco extends Window {
  __monacoEditor?: {
    setValue: (value: string) => void;
    getValue: () => string;
  };
}

// 🎯 CONFIGURE YOUR TEST HERE
// You can override these with environment variables:
// CYPRESS_QUESTION=house-robber CYPRESS_LANGUAGE=javascript npx cypress run --spec "cypress/e2e/SingleQuestionTest.cy.ts"
const TARGET_QUESTIONS = ["merge-intervals"];
const TARGET_LANGUAGES: Language[] = Cypress.env("LANGUAGE")
  ? [Cypress.env("LANGUAGE") as Language]
  : ["java"];

describe("JavaScript Problem Tests", () => {
  beforeEach(() => {
    // Clear any previous state
    cy.clearLocalStorage();
    cy.clearCookies();
  });

  // Test each question with each language
  TARGET_QUESTIONS.forEach((question) => {
    TARGET_LANGUAGES.forEach((language) => {
      it(`should work with ${question} in ${language}`, () => {
        // Load test solution for this question and language
        loadTestSolution(question, language).then((solution) => {
          if (!solution) {
            cy.log(
              `⚠️ Skipping ${question} in ${language}: No test solution found`
            );
            return;
          }

          cy.log(`Testing ${question} with ${language}: real solution`);

          // Navigate to the practice page
          cy.visit(`/practice/${question}`);

          // Wait for page to load
          cy.get('[data-testid="practice-page"]', { timeout: 10000 }).should(
            "be.visible"
          );

          // Select the target language
          cy.get('[data-testid="language-selector"]')
            .should("be.visible")
            .then(($selector) => {
              const current = $selector.text().trim().toLowerCase();
              if (!current.includes(language.toLowerCase())) {
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

          // Wait for language change to complete
          cy.wait(1500);

          // Wait for Monaco editor to be fully loaded
          cy.get(".monaco-editor", { timeout: 15000 }).should("be.visible");

          // Set the solution code
          cy.window().then((win) => {
            const editor = (win as WindowWithMonaco).__monacoEditor;
            if (editor && typeof editor.setValue === "function") {
              editor.setValue(solution.code);
              cy.wait(200);

              // Verify using the editor API
              const actualContent = editor.getValue();
              expect(actualContent).to.equal(solution.code);
            } else {
              // Fallback to the helper function
              replaceMonacoEditorContent(solution.code);
              cy.get(".monaco-editor").should("contain.text", "class");
            }
          });

          // Run sample tests
          cy.get('[data-testid="run-button"]').should("be.visible").click();
          cy.get('[data-testid="test-results"]', { timeout: 30000 }).should(
            "be.visible"
          );

          // Verify sample tests completed successfully
          cy.get('[data-testid="test-results"]').within(() => {
            cy.get('[data-testid="test-status"]').should("contain.text", "✓✓✓");
          });

          cy.log(`✅ Successfully completed ${question} in ${language}`);
        });
      });
    });

    // Quick validation test per question
    it(`should load the ${question} page`, () => {
      cy.visit(`/practice/${question}`);
      cy.get('[data-testid="practice-page"]', { timeout: 10000 }).should(
        "be.visible"
      );
      cy.log(`✅ Successfully loaded ${question} page`);
    });
  });

  // Test with just sample run (no submission)
  it("should handle sample test run only", () => {
    const question = TARGET_QUESTIONS[0]; // Use first question
    const language = TARGET_LANGUAGES[0]; // Use first language

    loadTestSolution(question, language).then((solution) => {
      if (!solution) {
        cy.log(`⚠️ Skipping: No test solution found for ${language}`);
        return;
      }

      cy.visit(`/practice/${question}`);
      cy.get('[data-testid="practice-page"]', { timeout: 10000 }).should(
        "be.visible"
      );

      // Select language
      cy.forceSelectLanguage(
        language as "python" | "javascript" | "cpp" | "java"
      );
      cy.wait(1500);

      // Set code
      cy.window().then((win) => {
        const editor = (win as WindowWithMonaco).__monacoEditor;
        if (editor && typeof editor.setValue === "function") {
          editor.setValue(solution.code);
        } else {
          replaceMonacoEditorContent(solution.code);
        }
      });

      // Only run sample tests (not submit)
      cy.get('[data-testid="run-button"]').click();
      cy.get('[data-testid="test-results"]', { timeout: 30000 }).should(
        "be.visible"
      );

      cy.log(`✅ Sample tests completed for ${question}`);
    });
  });

  // Debug test - check what solutions are available
  it("should list available solutions for debugging", () => {
    TARGET_QUESTIONS.forEach((question) => {
      TARGET_LANGUAGES.forEach((language) => {
        loadTestSolution(question, language).then((solution) => {
          if (solution) {
            cy.log(`✅ Found solution for ${question} in ${language}:`);
            cy.log(solution.code.substring(0, 100) + "...");
          } else {
            cy.log(`❌ No solution found for ${question} in ${language}`);
          }
        });
      });
    });
  });
});

// Alternative approach: Parameterized test that you can easily modify
describe("Quick Question Test (Configurable)", () => {
  // 🎯 Easy configuration - just change these variables
  const QUESTION_TO_TEST = "rotate-image"; // Change this easily
  const LANGUAGE_TO_TEST: Language = "python"; // Change this easily

  it(`should test ${QUESTION_TO_TEST} in ${LANGUAGE_TO_TEST}`, () => {
    loadTestSolution(QUESTION_TO_TEST, LANGUAGE_TO_TEST).then((solution) => {
      if (!solution) {
        cy.log(
          `⚠️ No solution found for ${QUESTION_TO_TEST} in ${LANGUAGE_TO_TEST}`
        );
        return;
      }

      cy.visit(`/practice/${QUESTION_TO_TEST}`);
      cy.get('[data-testid="practice-page"]', { timeout: 10000 }).should(
        "be.visible"
      );

      // Quick test - just verify page loads and solution exists
      cy.log(`✅ Found solution with ${solution.code.length} characters`);
      cy.log(`First 100 chars: ${solution.code.substring(0, 100)}`);
    });
  });
});
