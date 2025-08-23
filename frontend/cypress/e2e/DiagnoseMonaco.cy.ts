/**
 * Diagnostic test to figure out why Monaco editor isn't available in Cypress
 */

describe("Diagnose Monaco Editor Issue", () => {
  it("should diagnose Monaco editor availability step by step", () => {
    cy.visit("/practice/two-sum");

    // Step 1: Check if page loads
    cy.get('[data-testid="practice-page"]', { timeout: 10000 }).should(
      "be.visible"
    );
    cy.log("✅ Page loaded successfully");

    // Step 2: Check if Monaco editor element exists
    cy.get(".monaco-editor", { timeout: 15000 }).should("be.visible");
    cy.log("✅ Monaco editor element is visible");

    // Step 3: Check window object immediately
    cy.window().then((win) => {
      cy.log("=== IMMEDIATE WINDOW CHECK ===");
      cy.log("Window object:", win);
      cy.log("Has __monacoEditor property:", "__monacoEditor" in win);
      cy.log("__monacoEditor value:", (win as any).__monacoEditor);
      cy.log("Type of __monacoEditor:", typeof (win as any).__monacoEditor);
    });

    // Step 4: Wait and check again
    cy.wait(2000);
    cy.window().then((win) => {
      cy.log("=== AFTER 2 SECOND WAIT ===");
      cy.log("Has __monacoEditor property:", "__monacoEditor" in win);
      cy.log("__monacoEditor value:", (win as any).__monacoEditor);
      cy.log("Type of __monacoEditor:", typeof (win as any).__monacoEditor);

      if ((win as any).__monacoEditor) {
        const editor = (win as any).__monacoEditor;
        cy.log("Editor methods available:");
        cy.log("- setValue:", typeof editor.setValue);
        cy.log("- getValue:", typeof editor.getValue);
        cy.log("- onMount callback triggered:", true);
      }
    });

    // Step 5: Check with multiple waits and retries
    const checkWithRetries = (attempt = 1, maxAttempts = 10) => {
      cy.window().then((win) => {
        if ((win as any).__monacoEditor) {
          cy.log(`✅ Found Monaco editor on attempt ${attempt}`);
          return;
        }

        if (attempt < maxAttempts) {
          cy.log(`❌ Attempt ${attempt}: Monaco editor not found, retrying...`);
          cy.wait(500);
          checkWithRetries(attempt + 1, maxAttempts);
        } else {
          cy.log(`❌ Monaco editor not found after ${maxAttempts} attempts`);
        }
      });
    };

    checkWithRetries();

    // Step 6: Check all properties on window
    cy.window().then((win) => {
      cy.log("=== ALL WINDOW PROPERTIES ===");
      const windowProps = Object.getOwnPropertyNames(win);
      const monacoRelated = windowProps.filter(
        (prop) =>
          prop.toLowerCase().includes("monaco") ||
          prop.toLowerCase().includes("editor") ||
          prop.startsWith("__")
      );
      cy.log("Monaco/Editor related properties:", monacoRelated);

      // Check if there are any monaco-related properties
      monacoRelated.forEach((prop) => {
        cy.log(`${prop}:`, (win as any)[prop]);
      });
    });

    // Step 7: Trigger language change and see what happens using robust pattern
    cy.log("=== TESTING LANGUAGE CHANGE ===");
    cy.get('[data-testid="language-selector"]').should("be.visible").click();

    // Wait for dropdown to be open and stable
    cy.get('[role="listbox"][data-state="open"]', { timeout: 10000 })
      .should("be.visible")
      .within(() => {
        cy.get('[data-testid="language-option-java"]')
          .should("be.visible")
          .click();
      });

    // Wait for language change
    cy.wait(2000);

    cy.window().then((win) => {
      cy.log("After language change:");
      cy.log("Has __monacoEditor:", "__monacoEditor" in win);
      cy.log("__monacoEditor:", (win as any).__monacoEditor);
    });

    // Step 8: Check DOM structure
    cy.get(".monaco-editor").then(($editor) => {
      cy.log("=== DOM STRUCTURE ===");
      cy.log("Monaco editor DOM element:", $editor[0]);
      cy.log("Monaco editor children:", $editor[0].children);

      // Check for any data attributes or special properties
      const element = $editor[0];
      cy.log("Element attributes:");
      for (let i = 0; i < element.attributes.length; i++) {
        const attr = element.attributes[i];
        cy.log(`  ${attr.name}: ${attr.value}`);
      }
    });

    // Step 9: Try to interact with Monaco editor in different ways
    cy.log("=== TESTING ALTERNATIVE ACCESS METHODS ===");

    // Check if Monaco is available globally
    cy.window().then((win) => {
      cy.log("Global monaco:", (win as any).monaco);
      cy.log("Global MonacoEnvironment:", (win as any).MonacoEnvironment);
    });

    // Check React DevTools or any React fiber nodes
    cy.get(".monaco-editor").then(($editor) => {
      const element = $editor[0];
      cy.log(
        "React fiber:",
        (element as any)._reactInternalFiber ||
          (element as any).__reactInternalInstance
      );
    });
  });

  it("should test the CodeEditor component mounting process", () => {
    // Navigate fresh
    cy.visit("/practice/two-sum");
    cy.get('[data-testid="practice-page"]', { timeout: 10000 }).should(
      "be.visible"
    );

    // Monitor console logs
    cy.window().then((win) => {
      const originalConsoleLog = win.console.log;
      const logs: string[] = [];

      win.console.log = (...args: any[]) => {
        const message = args
          .map((arg) =>
            typeof arg === "object" ? JSON.stringify(arg, null, 2) : String(arg)
          )
          .join(" ");
        logs.push(message);
        originalConsoleLog.apply(win.console, args);
      };

      // Wait for Monaco to potentially load
      cy.wait(3000);

      // Check captured logs
      cy.then(() => {
        cy.log("=== CONSOLE LOGS CAPTURED ===");
        logs.forEach((log, index) => {
          cy.log(`Log ${index + 1}: ${log}`);
        });

        const monacoLogs = logs.filter(
          (log) =>
            log.toLowerCase().includes("monaco") ||
            log.toLowerCase().includes("editor") ||
            log.includes("window object") ||
            log.includes("exposed")
        );

        cy.log("Monaco-related logs:", monacoLogs);
      });
    });
  });
});
