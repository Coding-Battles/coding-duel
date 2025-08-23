/// <reference types="cypress" />

declare namespace Cypress {
  interface Chainable {
    /**
     * Custom command to select a language using robust Radix Select pattern
     * @param language - The language to select
     * @example cy.selectLanguage('java')
     */
    selectLanguage(
      language: "python" | "javascript" | "cpp" | "java"
    ): Chainable<Element>;

    /**
     * Custom command to set content in Monaco editor
     * @param content - The code content to set in the editor
     * @example cy.setMonacoEditorContent('console.log("Hello World");')
     */
    setMonacoEditorContent(content: string): Chainable<Element>;

    /**
     * Enhanced command for reliable Radix Select interactions
     * @param triggerSelector - Selector for the element that opens the dropdown
     * @param optionSelector - Selector for the option to click
     * @param optionText - Optional text to verify in the option
     * @example cy.selectRadixOption('[data-testid="language-selector"]', '[data-testid="language-option-python"]', 'Python')
     */
    selectRadixOption(
      triggerSelector: string,
      optionSelector: string,
      optionText?: string
    ): Chainable<Element>;

    /**
     * Force-based language selection that bypasses visibility issues
     * @param language - The language to select
     * @example cy.forceSelectLanguage('java')
     */
    forceSelectLanguage(
      language: "python" | "javascript" | "cpp" | "java"
    ): Chainable<Element>;
  }
}
