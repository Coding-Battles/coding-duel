/// <reference types="cypress" />

declare namespace Cypress {
  interface Chainable {
    /**
     * Custom command to set content in Monaco editor
     * @param content - The code content to set in the editor
     * @example cy.setMonacoEditorContent('console.log("Hello World");')
     */
    setMonacoEditorContent(content: string): Chainable<Element>;
  }
}
