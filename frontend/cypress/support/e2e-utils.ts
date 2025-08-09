/**
 * Utility functions for E2E tests
 */

/**
 * Replace content in Monaco editor with new code using a user-like paste
 * Prefers clipboard paste to preserve indentation, with fallbacks.
 */
export const replaceMonacoEditorContent = (newCode: string) => {
  cy.log(
    `Replacing Monaco editor content with: ${newCode.substring(0, 50)}...`
  );

  // Focus the Monaco editor surface
  cy.get(".monaco-editor").should("be.visible").click();
  cy.wait(200);

  const firstLinePreview = (() => {
    const line =
      newCode
        .split("\n")
        .map((l) => l.trim())
        .find(Boolean) || "";
    return line.substring(0, 40);
  })();

  // Try to use clipboard if available; otherwise fall back immediately
  cy.window().then((win) => {
    // Use optional chaining to avoid TS/ESLint any rules
    const clipboard =
      (win.navigator &&
        (
          win.navigator as Navigator & {
            clipboard?: { writeText?: (t: string) => Promise<void> };
          }
        ).clipboard) ||
      undefined;
    const canUseClipboard = !!(
      clipboard && typeof clipboard.writeText === "function"
    );

    if (canUseClipboard) {
      return clipboard!
        .writeText(newCode)
        .then(() => {
          cy.get(".monaco-editor .view-lines").first().click({ force: true });
          cy.focused()
            .type("{cmd+a}{backspace}", { force: true })
            .type("{cmd+v}", { force: true });
          cy.log("Used clipboard paste for Monaco editor");
        })
        .catch(() => {
          // If clipboard fails, continue to fallbacks below
          cy.wrap(null);
        });
    }

    // Fallback 1: direct textarea manipulation
    cy.get(".monaco-editor textarea")
      .first()
      .then(($textarea) => {
        if ($textarea.length > 0) {
          const textarea = $textarea[0] as HTMLTextAreaElement;
          textarea.value = ""; // clear
          textarea.focus();
          textarea.dispatchEvent(new Event("input", { bubbles: true }));
          textarea.dispatchEvent(new Event("change", { bubbles: true }));

          textarea.value = newCode;
          textarea.dispatchEvent(new Event("input", { bubbles: true }));
          textarea.dispatchEvent(new Event("change", { bubbles: true }));
          cy.log("Used direct textarea manipulation for Monaco editor");
        } else {
          // Fallback 2: type the content as a last resort
          cy.get(".monaco-editor .view-lines").first().click();
          cy.focused().type("{cmd+a}", { force: true });
          cy.wait(50);
          cy.focused().type(newCode, {
            parseSpecialCharSequences: false,
            delay: 0,
          });
          cy.log("Used select-all and type for Monaco editor");
        }
      });
  });

  // Wait for Monaco to process the change
  cy.wait(400);

  // Verify content was rendered in the editor surface (not the hidden textarea)
  cy.get(".monaco-editor").should("contain.text", firstLinePreview);

  cy.log("Successfully set Monaco editor content");
};

/**
 * Get the current content from Monaco editor
 */
export const getMonacoEditorContent = () => {
  return cy.get(".monaco-editor").then(($editor) => {
    // Monaco editor stores content in data attributes or can be accessed via the editor instance
    // For now, we'll use the text content as a basic check
    return $editor.text();
  });
};
