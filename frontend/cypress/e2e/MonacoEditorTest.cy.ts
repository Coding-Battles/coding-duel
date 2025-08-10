// Simple test to verify Monaco editor interaction fix with proper formatting
import { replaceMonacoEditorContent } from "../support/e2e-utils";

describe("Monaco Editor Interaction Test", () => {
  it("should set Monaco editor content with proper formatting", () => {
    // This test assumes the application is running on localhost:3000
    // and that there is a practice page with Monaco editor

    // Visit a practice page (adjust URL as needed)
    cy.visit("http://localhost:3000/practice/two-sum");

    // Wait for page to load
    cy.get('[data-testid="practice-page"]', { timeout: 10000 }).should(
      "be.visible"
    );

    const testCode = `class Solution:
    def twoSum(self, nums: list[int], target: int) -> list[int]:
        num_map = {}
        for i, num in enumerate(nums):
            complement = target - num
            if complement in num_map:
                return [num_map[complement], i]
            num_map[num] = i
        return []`;

    // Use the shared helper that preserves indentation with clipboard when available
    replaceMonacoEditorContent(testCode);

    // Wait for the change to take effect
    cy.wait(500);

    // Verify content was set correctly - check for key parts of the code
    cy.get(".monaco-editor").should("contain.text", "class Solution");
    cy.get(".monaco-editor").should("contain.text", "def twoSum");
    cy.get(".monaco-editor").should("contain.text", "num_map = {}");
    cy.get(".monaco-editor").should("contain.text", "enumerate(nums)");

    cy.log("✅ Monaco editor interaction successful with proper formatting!");
  });

  it("should handle code with proper indentation structure", () => {
    // Visit a practice page
    cy.visit("http://localhost:3000/practice/two-sum");
    cy.get('[data-testid="practice-page"]', { timeout: 10000 }).should(
      "be.visible"
    );

    const pythonCode = `def solution():
    if True:
        for i in range(10):
            if i % 2 == 0:
                print(f"Even: {i}")
            else:
                print(f"Odd: {i}")
    return "Done"`;

    // Use the same helper here as well
    replaceMonacoEditorContent(pythonCode);

    cy.wait(500);

    // Verify the indentation is preserved
    cy.get(".monaco-editor").should("contain.text", "def solution():");
    cy.get(".monaco-editor").should("contain.text", "if True:");
    cy.get(".monaco-editor").should("contain.text", "for i in range(10):");
    cy.get(".monaco-editor").should("contain.text", 'print(f"Even: {i}")');

    cy.log("✅ Indentation preserved correctly!");
  });
});
