/**
 * Debug test to isolate the Monaco editor and test result issues
 */

import { replaceMonacoEditorContent } from "../support/e2e-utils";

describe("Debug Monaco Editor and Test Results", () => {
  it("should debug Monaco editor content setting", () => {
    const pythonCode = `class Solution:
    def twoSum(self, nums: list[int], target: int) -> list[int]:
        num_map = {}
        for i, num in enumerate(nums):
            complement = target - num
            if complement in num_map:
                return [num_map[complement], i]
            num_map[num] = i
        return []`;

    // Navigate to the practice page
    cy.visit("/practice/two-sum");
    cy.get('[data-testid="practice-page"]', { timeout: 10000 }).should(
      "be.visible"
    );

    // Ensure Python is selected using robust pattern
    cy.get('[data-testid="language-selector"]')
      .should("be.visible")
      .then(($selector) => {
        const current = $selector.text().trim().toLowerCase();
        if (!current.includes("python")) {
          cy.wrap($selector).click();

          // Wait for dropdown to be open and stable
          cy.get('[role="listbox"][data-state="open"]', { timeout: 10000 })
            .should("be.visible")
            .within(() => {
              cy.get('[data-testid="language-option-python"]')
                .should("be.visible")
                .click();
            });
        }
      });

    // Wait for editor to load
    cy.wait(1000);

    // Replace content
    replaceMonacoEditorContent(pythonCode);

    // Debug: Log the actual textarea content
    cy.get(".monaco-editor textarea").then(($textarea) => {
      if ($textarea.length > 0) {
        const textareaValue = ($textarea[0] as HTMLTextAreaElement).value;
        cy.log("=== Actual Monaco Editor Content ===");
        cy.log(textareaValue);
        cy.log("=== End Content ===");
      }
    });

    // Try running the tests
    cy.get('[data-testid="run-button"]').should("be.visible").click();

    // Wait for results
    cy.get('[data-testid="test-results"]', { timeout: 30000 }).should(
      "be.visible"
    );

    // Debug: Log the test results content
    cy.get('[data-testid="test-results"]').then(($results) => {
      cy.log("=== Test Results HTML ===");
      cy.log($results.html());
      cy.log("=== End Results ===");
    });

    // Debug: Check what test status element contains
    cy.get('[data-testid="test-status"]').then(($status) => {
      cy.log("=== Test Status ===");
      cy.log($status.text());
      cy.log("=== End Status ===");
    });
  });
});
