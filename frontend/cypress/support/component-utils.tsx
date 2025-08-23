/**
 * Component mounting utilities for Cypress tests
 * Provides proper providers and mocking for testing React components
 */

import React from "react";
import { mount } from "cypress/react";

// Mock Next.js router
const mockPush = cy.stub().as("routerPush");
const mockReplace = cy.stub().as("routerReplace");
const mockBack = cy.stub().as("routerBack");
const mockForward = cy.stub().as("routerForward");
const mockRefresh = cy.stub().as("routerRefresh");

// Mock useRouter hook
const mockRouter = {
  push: mockPush,
  replace: mockReplace,
  back: mockBack,
  forward: mockForward,
  refresh: mockRefresh,
  prefetch: cy.stub(),
};

// Mock useParams hook
const createMockParams = (questionName: string) => ({
  questionName,
});

// Mock useSession hook
const mockSession = {
  data: {
    user: {
      id: "test-user-id",
      email: "test@example.com",
      name: "Test User",
    },
  },
  status: "authenticated",
};

// Mock providers wrapper
interface MockProvidersProps {
  children: React.ReactNode;
  questionName?: string;
}

const MockProviders: React.FC<MockProvidersProps> = ({
  children,
  questionName = "two-sum",
}) => {
  // Mock Next.js hooks
  React.useEffect(() => {
    // Mock next/navigation hooks
    cy.window().then((win) => {
      const w = win as unknown as Window & {
        useRouter?: () => unknown;
        useParams?: () => { questionName: string };
        useSession?: () => unknown;
      };
      w.useRouter = () => mockRouter as unknown;
      w.useParams = () => createMockParams(questionName);
      w.useSession = () => mockSession as unknown;
    });
  }, [questionName]);

  return <>{children}</>;
};

/**
 * Mount a component with proper providers and mocking
 */
export const mountWithProviders = (
  component: React.ReactElement,
  options: {
    questionName?: string;
    mockApis?: boolean;
    customProviders?: React.ComponentType<{ children: React.ReactNode }>;
  } = {}
) => {
  const {
    questionName = "two-sum",
    mockApis = true,
    customProviders,
  } = options;

  if (mockApis) {
    // Mock API endpoints
    cy.intercept("GET", `**/api/get-question/${questionName}`, {
      statusCode: 200,
      body: {
        title: `Test Question: ${questionName}`,
        description: "Test description for component testing",
        starter_code: {
          python: "class Solution:\n    def solution(self):\n        pass",
          javascript:
            "class Solution {\n    solution() {\n        // TODO\n    }\n}",
          java: "class Solution {\n    public void solution() {\n        // TODO\n    }\n}",
          cpp: "class Solution {\npublic:\n    void solution() {\n        // TODO\n    }\n};",
        },
        examples: [
          {
            input: "test input",
            output: "test output",
            explanation: "test explanation",
          },
        ],
        constraints: ["test constraint"],
      },
    }).as(`getQuestion-${questionName}`);

    // Mock test execution endpoints
    cy.intercept("POST", `**/api/${questionName}/test-sample`, {
      statusCode: 200,
      body: {
        success: true,
        test_results: [
          {
            input: "sample input",
            expected_output: "expected",
            actual_output: "expected",
            passed: true,
            error: null,
            execution_time: 5,
          },
        ],
        total_passed: 1,
        total_failed: 0,
        error: null,
      },
    }).as(`runSampleTests-${questionName}`);

    cy.intercept("POST", `**/api/${questionName}/test`, {
      statusCode: 200,
      body: {
        success: true,
        test_results: Array(5).fill({
          input: "test input",
          expected_output: "expected",
          actual_output: "expected",
          passed: true,
          error: null,
          execution_time: 10,
        }),
        total_passed: 5,
        total_failed: 0,
        error: null,
      },
    }).as(`runAllTests-${questionName}`);
  }

  const Providers = customProviders || MockProviders;

  return mount(<Providers questionName={questionName}>{component}</Providers>);
};

/**
 * Wait for component to be ready and question data to load
 */
export const waitForComponentReady = (questionName = "two-sum") => {
  cy.wait(`@getQuestion-${questionName}`);
  cy.get('[data-testid="practice-page"]', { timeout: 10000 }).should(
    "be.visible"
  );
};

/**
 * Get language selector and select a specific language
 * Uses robust Radix Select interaction pattern to avoid flaky tests
 */
export const selectLanguage = (
  language: "python" | "javascript" | "cpp" | "java"
) => {
  // Step 1: Open the select dropdown
  cy.get('[data-testid="language-selector"]').should("be.visible").click();

  // Step 2: Wait for the dropdown content to be fully open and stable
  // Target the open listbox using role and state attributes (more stable than class names)
  cy.get('[role="listbox"][data-state="open"]', { timeout: 10000 })
    .should("be.visible")
    .within(() => {
      // Step 3: Find and click the specific language option within the open dropdown
      cy.get(`[data-testid="language-option-${language}"]`)
        .should("be.visible")
        .click();
    });

  // Step 4: Verify the language selection was successful
  const display =
    language === "cpp"
      ? "C++"
      : language === "javascript"
      ? "JavaScript"
      : language.charAt(0).toUpperCase() + language.slice(1);

  cy.get('[data-testid="language-selector"]').should("contain.text", display);
};

/**
 * Interact with Monaco editor to replace content using user-like paste to keep indentation
 */
export const replaceEditorContent = (newCode: string) => {
  // Focus on the Monaco editor
  cy.get(".monaco-editor").should("be.visible").click();

  // Wait for editor to be ready
  cy.wait(200);

  const preview = (() => {
    const first =
      newCode
        .split("\n")
        .map((l) => l.trim())
        .find(Boolean) || "";
    return first.substring(0, 40);
  })();

  // Prefer clipboard paste to mimic real user paste behavior (keeps indentation)
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
        .writeText(newCode)
        .then(() => {
          cy.get(".monaco-editor .view-lines").first().click({ force: true });
          cy.focused().type("{cmd+a}{backspace}{cmd+v}", { force: true });
          cy.log("Used clipboard paste for Monaco editor (component test)");
        })
        .catch(() => {
          cy.wrap(null);
        });
    }

    // Fallback 1: direct textarea manipulation
    cy.get(".monaco-editor textarea")
      .first()
      .then(($textarea) => {
        if ($textarea.length > 0) {
          const textarea = $textarea[0] as HTMLTextAreaElement;
          textarea.value = "";
          textarea.focus();
          textarea.dispatchEvent(new Event("input", { bubbles: true }));
          textarea.dispatchEvent(new Event("change", { bubbles: true }));

          textarea.value = newCode;
          textarea.dispatchEvent(new Event("input", { bubbles: true }));
          textarea.dispatchEvent(new Event("change", { bubbles: true }));
          cy.log("Used direct textarea manipulation for Monaco editor");
        } else {
          // Fallback 2: typing
          cy.get(".monaco-editor .view-lines").first().click();
          cy.focused().type("{cmd+a}", { force: true });
          cy.wait(50);
          cy.focused().type(newCode, {
            parseSpecialCharSequences: false,
            delay: 0,
          });
          cy.log("Used typing fallback for Monaco editor");
        }
      });
  });

  // Wait for the editor to reflect changes
  cy.wait(400);

  // Verify content appears in rendered surface
  cy.get(".monaco-editor").should("contain.text", preview);
};

/**
 * Click run button and wait for sample tests to complete
 */
export const runSampleTests = (questionName = "two-sum") => {
  cy.get('[data-testid="run-button"]').should("be.visible").click();
  cy.wait(`@runSampleTests-${questionName}`);

  // Wait for results to appear
  cy.get('[data-testid="test-results"]', { timeout: 10000 }).should(
    "be.visible"
  );
};

/**
 * Click submit button and wait for all tests to complete
 */
export const submitSolution = (questionName = "two-sum") => {
  cy.get('[data-testid="submit-button"]').should("be.visible").click();
  cy.wait(`@runAllTests-${questionName}`);

  // Wait for results to appear
  cy.get('[data-testid="test-results"]', { timeout: 15000 }).should(
    "be.visible"
  );
};

/**
 * Verify test results show success
 */
export const verifySuccessfulSubmission = () => {
  cy.get('[data-testid="test-results"]').within(() => {
    cy.get('[data-testid="test-status"]').should("contain.text", "Passed");
    cy.get('[data-testid="tests-passed"]').should("not.contain.text", "0/");
  });
};

/**
 * Clean up mocks and stubs
 */
export const cleanupMocks = () => {
  mockPush.reset();
  mockReplace.reset();
  mockBack.reset();
  mockForward.reset();
  mockRefresh.reset();
};
