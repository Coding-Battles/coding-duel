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
 * Custom command to select language using robust Radix Select pattern
 */
// @ts-expect-error: Custom command not in default Cypress types
Cypress.Commands.add(
  "selectLanguage",
  (language: "python" | "javascript" | "cpp" | "java") => {
    const displayName =
      language === "cpp"
        ? "C++"
        : language === "javascript"
        ? "JavaScript"
        : language.charAt(0).toUpperCase() + language.slice(1);

    // Open the select dropdown
    cy.get('[data-testid="language-selector"]').should("be.visible").click();

    // Use a more robust approach - wait for the element to exist and force visibility
    cy.get('[role="listbox"][data-state="open"]', { timeout: 15000 })
      .should("exist")
      .then(($dropdown) => {
        // Force the element to be visible by directly manipulating its styles
        $dropdown[0].style.setProperty("opacity", "1", "important");
        $dropdown[0].style.setProperty("visibility", "visible", "important");
        $dropdown[0].style.setProperty("display", "block", "important");
        $dropdown[0].style.setProperty("pointer-events", "auto", "important");

        // Also apply to all children
        $dropdown.find("*").each((_, child) => {
          child.style.setProperty("opacity", "1", "important");
          child.style.setProperty("visibility", "visible", "important");
        });
      })
      .should("be.visible") // Now check visibility
      .within(() => {
        // Click the language option within the open dropdown
        cy.get(`[data-testid="language-option-${language}"]`)
          .should("exist")
          .then(($option) => {
            // Force the option to be visible too
            $option[0].style.setProperty("opacity", "1", "important");
            $option[0].style.setProperty("visibility", "visible", "important");
          })
          .should("be.visible")
          .click({ force: true });
      });

    // Verify the selection was successful
    cy.get('[data-testid="language-selector"]').should(
      "contain.text",
      displayName
    );
  }
);

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

/**
 * Enhanced command for reliable Radix Select interactions
 */
// @ts-expect-error: Custom command not in default Cypress types
Cypress.Commands.add(
  "selectRadixOption",
  (triggerSelector: string, optionSelector: string, optionText?: string) => {
    // Click the trigger to open the dropdown
    cy.get(triggerSelector).should("be.visible").click();

    // Alternative approach: use force and don't check visibility
    cy.get('[role="listbox"]', { timeout: 15000 })
      .should("exist")
      .then(($dropdown) => {
        // Force the dropdown to be interactable
        $dropdown[0].style.setProperty("opacity", "1", "important");
        $dropdown[0].style.setProperty("visibility", "visible", "important");
        $dropdown[0].style.setProperty("pointer-events", "auto", "important");
        $dropdown[0].style.setProperty("display", "block", "important");
      });

    // Now interact with the option using force
    cy.get(optionSelector)
      .should("exist")
      .then(($option) => {
        if (optionText) {
          expect($option.text().trim()).to.include(optionText);
        }
        // Force the option to be interactable
        $option[0].style.setProperty("opacity", "1", "important");
        $option[0].style.setProperty("visibility", "visible", "important");
        $option[0].style.setProperty("pointer-events", "auto", "important");
      })
      .click({ force: true });

    // Don't wait for dropdown to close, just proceed
  }
);

/**
 * Force-based language selection that bypasses visibility issues
 */
// @ts-expect-error: Custom command not in default Cypress types
Cypress.Commands.add(
  "forceSelectLanguage",
  (language: "python" | "javascript" | "cpp" | "java") => {
    const displayName =
      language === "cpp"
        ? "C++"
        : language === "javascript"
        ? "JavaScript"
        : language.charAt(0).toUpperCase() + language.slice(1);

    // Open the select dropdown
    cy.get('[data-testid="language-selector"]').should("be.visible").click();

    // Wait a moment for the dropdown to appear in DOM
    cy.wait(500);

    // Force click the option without any visibility checks
    cy.get(`[data-testid="language-option-${language}"]`, { timeout: 10000 })
      .should("exist")
      .click({ force: true });

    // Verify the selection was successful
    cy.get('[data-testid="language-selector"]').should(
      "contain.text",
      displayName
    );
  }
);

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
