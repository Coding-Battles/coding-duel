/**
 * Simple diagnostic test to check Monaco editor mounting
 */

describe("Simple Monaco Diagnostic", () => {
  it("should check if Monaco editor mounts correctly", () => {
    // Navigate to practice page
    cy.visit("/practice/two-sum");

    // Wait for page to load
    cy.get('[data-testid="practice-page"]', { timeout: 10000 }).should(
      "be.visible"
    );

    // Wait for Monaco editor to be visible
    cy.get(".monaco-editor", { timeout: 15000 }).should("be.visible");

    // Check window properties immediately
    cy.window().then((win) => {
      console.log(
        "Window properties that include 'monaco':",
        Object.keys(win).filter((key) => key.toLowerCase().includes("monaco"))
      );
      console.log("Has __monacoEditor:", "__monacoEditor" in win);
      console.log("__monacoEditor value:", (win as any).__monacoEditor);
    });

    // Wait 3 seconds and check again
    cy.wait(3000);
    cy.window().then((win) => {
      console.log(
        "After 3 seconds - Has __monacoEditor:",
        "__monacoEditor" in win
      );
      console.log(
        "After 3 seconds - __monacoEditor:",
        (win as any).__monacoEditor
      );
    });
  });
});
