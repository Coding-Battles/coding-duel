/// <reference types="../support/commands" />

// Simple test to debug language selection issues
describe("Language Selection Debug", () => {
  beforeEach(() => {
    cy.visit("/practice/two-sum"); // Use a known question
    cy.get('[data-testid="practice-page"]', { timeout: 10000 }).should(
      "be.visible"
    );
  });

  it("should test force-based language selection", () => {
    // Try the force-based approach
    cy.forceSelectLanguage("java");

    // Verify it worked
    cy.get('[data-testid="language-selector"]').should("contain.text", "Java");
    cy.log("✅ Force-based language selection worked!");
  });

  it("should test regular language selection", () => {
    // Try the regular approach
    cy.selectLanguage("python");

    // Verify it worked
    cy.get('[data-testid="language-selector"]').should(
      "contain.text",
      "Python"
    );
    cy.log("✅ Regular language selection worked!");
  });

  it("should test direct DOM manipulation", () => {
    // Most aggressive approach - direct DOM manipulation
    cy.get('[data-testid="language-selector"]').should("be.visible").click();

    // Wait for dropdown and force it to be visible
    cy.get("body").then(() => {
      // Find any Radix dropdown that exists
      cy.get('[role="listbox"]', { timeout: 5000 })
        .should("exist")
        .then(($dropdown) => {
          // Force all styles
          const dropdown = $dropdown[0] as HTMLElement;
          dropdown.style.setProperty("opacity", "1", "important");
          dropdown.style.setProperty("visibility", "visible", "important");
          dropdown.style.setProperty("display", "block", "important");
          dropdown.style.setProperty("pointer-events", "auto", "important");
          dropdown.style.setProperty("z-index", "9999", "important");

          // Force all children to be visible too
          Array.from(dropdown.querySelectorAll("*")).forEach((child) => {
            (child as HTMLElement).style.setProperty(
              "opacity",
              "1",
              "important"
            );
            (child as HTMLElement).style.setProperty(
              "visibility",
              "visible",
              "important"
            );
          });
        });
    });

    // Now try to click the option
    cy.get('[data-testid="language-option-cpp"]')
      .should("exist")
      .then(($option) => {
        const option = $option[0] as HTMLElement;
        option.style.setProperty("opacity", "1", "important");
        option.style.setProperty("visibility", "visible", "important");
        option.style.setProperty("pointer-events", "auto", "important");
      })
      .click({ force: true });

    // Verify it worked
    cy.get('[data-testid="language-selector"]').should("contain.text", "C++");
    cy.log("✅ Direct DOM manipulation worked!");
  });
});
