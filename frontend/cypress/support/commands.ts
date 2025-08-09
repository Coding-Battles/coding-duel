/// <reference types="cypress" />
// ***********************************************
// This example commands.ts shows you how to
// create various custom commands and overwrite
// existing commands.
//
// For more comprehensive examples of custom
// commands please read more here:
// https://on.cypress.io/custom-commands
// ***********************************************

/**
 * Custom command to replace content in Monaco editor
 */
// @ts-expect-error: Custom command not in default Cypress types
Cypress.Commands.add("setMonacoEditorContent", (content: string) => {
  // Click on the Monaco editor to ensure it's focused
  cy.get(".monaco-editor").should("be.visible").click();

  // Wait for editor to be ready
  cy.wait(200);

  // Prefer clipboard paste to preserve indentation
  cy.window().then((win) => {
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
        .writeText(content)
        .then(() => {
          cy.get(".monaco-editor .view-lines").first().click({ force: true });
          cy.focused().type("{cmd+a}{backspace}{cmd+v}", { force: true });
          cy.log("Used clipboard paste for Monaco editor");
        })
        .catch(() => {
          cy.wrap(null);
        });
    }

    // Fallback: textarea manipulation or typing
    cy.get(".monaco-editor").then(($editor) => {
      const textarea = $editor.find("textarea")[0] as HTMLTextAreaElement;

      if (textarea) {
        textarea.value = content;
        textarea.focus();
        textarea.dispatchEvent(new Event("input", { bubbles: true }));
        textarea.dispatchEvent(new Event("change", { bubbles: true }));
        cy.log("Used direct textarea manipulation for Monaco editor");
      } else {
        cy.get(".monaco-editor textarea").then(($textarea) => {
          if ($textarea.length > 0) {
            cy.wrap($textarea).first().focus().clear().type(content, {
              parseSpecialCharSequences: false,
              delay: 0,
            });
            cy.log("Used Cypress textarea commands for Monaco editor");
          } else {
            cy.get(".monaco-editor .view-lines").first().click();
            cy.focused().clear();
            cy.focused().type(content, {
              parseSpecialCharSequences: false,
              delay: 0,
            });
            cy.log("Used focused element typing for Monaco editor");
          }
        });
      }
    });
  });

  // Wait for the editor to update
  cy.wait(200);
});

//
// -- This is a parent command --
// Cypress.Commands.add('login', (email, password) => { ... })
//
//
// -- This is a child command --
// Cypress.Commands.add('drag', { prevSubject: 'element'}, (subject, options) => { ... })
//
//
// -- This is a dual command --
// Cypress.Commands.add('dismiss', { prevSubject: 'optional'}, (subject, options) => { ... })
//
//
// -- This will overwrite an existing command --
// Cypress.Commands.overwrite('visit', (originalFn, url, options) => { ... })
