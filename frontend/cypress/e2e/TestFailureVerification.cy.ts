/**
 * Test Failure Verification
 * This test verifies that our testing system actually fails when it should
 */

describe("Test Failure Verification", () => {
  beforeEach(() => {
    cy.clearLocalStorage();
    cy.clearCookies();
  });

  // Test that wrong solutions actually fail
  ["two-sum", "container-with-most-water", "group-anagrams"].forEach(
    (questionSlug) => {
      ["python", "javascript", "java", "cpp"].forEach((language) => {
        it(`should FAIL when wrong solution is provided for ${questionSlug} in ${language}`, () => {
          // Navigate to the practice page
          cy.visit(`/practice/${questionSlug}`);
          cy.get('[data-testid="practice-page"]', { timeout: 10000 }).should(
            "be.visible"
          );

          // Select the target language
          cy.forceSelectLanguage(
            language as "python" | "javascript" | "cpp" | "java"
          );
          cy.wait(1500);

          // Get wrong solution based on language
          const wrongSolutions = {
            python: `class Solution:
    def ${getMethodName(questionSlug)}(self, *args):
        return None  # Wrong answer`,
            javascript: `class Solution {
    ${getMethodName(questionSlug)}(...args) {
        return null; // Wrong answer
    }
}`,
            java: `class Solution {
    public ${getReturnType(questionSlug)} ${getMethodName(
              questionSlug
            )}(${getJavaParams(questionSlug)}) {
        return ${getJavaDefaultReturn(questionSlug)}; // Wrong answer
    }
}`,
            cpp: `class Solution {
public:
    ${getCppReturnType(questionSlug)} ${getMethodName(
              questionSlug
            )}(${getCppParams(questionSlug)}) {
        return ${getCppDefaultReturn(questionSlug)}; // Wrong answer
    }
};`,
          };

          // Set wrong solution in editor
          cy.window().then((win) => {
            const editor = (win as any).__monacoEditor; // eslint-disable-line @typescript-eslint/no-explicit-any
            if (editor && typeof editor.setValue === "function") {
              editor.setValue(
                wrongSolutions[language as keyof typeof wrongSolutions]
              );
              cy.wait(500);
            }
          });

          // Run sample tests - these should FAIL
          cy.get('[data-testid="run-button"]').should("be.visible").click();
          cy.get('[data-testid="test-results"]', { timeout: 30000 }).should(
            "be.visible"
          );

          // Verify that tests actually FAILED (not all passed)
          cy.get('[data-testid="test-results"]').within(() => {
            // Should NOT show all checkmarks
            cy.get('[data-testid="test-status"]').should(
              "not.contain.text",
              "✓✓✓"
            );

            // Should show some failures
            cy.get('[data-testid="test-status"]').should("contain.text", "❌");

            // Should show 0 passed or partial failures
            cy.get('[data-testid="tests-passed"]').then(($el) => {
              const text = $el.text();
              // Should either be "0/" or show partial success like "1/3" but not all passed
              expect(text).to.match(/^0\/|^[1-2]\/[3-9]/);
            });
          });

          cy.log(
            `✅ Correctly failed ${questionSlug} in ${language} with wrong solution`
          );
        });
      });
    }
  );

  // Test that completely broken code fails
  it("should fail with syntax errors", () => {
    const questionSlug = "two-sum";

    cy.visit(`/practice/${questionSlug}`);
    cy.get('[data-testid="practice-page"]', { timeout: 10000 }).should(
      "be.visible"
    );

    // Set broken Python code
    cy.forceSelectLanguage("python");
    cy.wait(1500);

    const brokenCode = `class Solution:
    def twoSum(self
        # Syntax error - missing closing parenthesis and colon
        return broken syntax here`;

    cy.window().then((win) => {
      const editor = (win as any).__monacoEditor; // eslint-disable-line @typescript-eslint/no-explicit-any
      if (editor && typeof editor.setValue === "function") {
        editor.setValue(brokenCode);
        cy.wait(500);
      }
    });

    // Run tests - should fail with compilation/syntax error
    cy.get('[data-testid="run-button"]').should("be.visible").click();
    cy.get('[data-testid="test-results"]', { timeout: 30000 }).should(
      "be.visible"
    );

    // Should show error state
    cy.get('[data-testid="test-results"]').should("contain.text", "❌");

    cy.log("✅ Correctly failed with syntax error");
  });
});

// Helper functions to get method signatures for wrong solutions
function getMethodName(questionSlug: string): string {
  const methodMap: Record<string, string> = {
    "two-sum": "twoSum",
    "container-with-most-water": "maxArea",
    "group-anagrams": "groupAnagrams",
  };
  return methodMap[questionSlug] || "solve";
}

function getReturnType(questionSlug: string): string {
  const typeMap: Record<string, string> = {
    "two-sum": "int[]",
    "container-with-most-water": "int",
    "group-anagrams": "List<List<String>>",
  };
  return typeMap[questionSlug] || "Object";
}

function getJavaParams(questionSlug: string): string {
  const paramMap: Record<string, string> = {
    "two-sum": "int[] nums, int target",
    "container-with-most-water": "int[] height",
    "group-anagrams": "String[] strs",
  };
  return paramMap[questionSlug] || "Object[] args";
}

function getJavaDefaultReturn(questionSlug: string): string {
  const returnMap: Record<string, string> = {
    "two-sum": "new int[]{0, 0}",
    "container-with-most-water": "0",
    "group-anagrams": "new ArrayList<>()",
  };
  return returnMap[questionSlug] || "null";
}

function getCppReturnType(questionSlug: string): string {
  const typeMap: Record<string, string> = {
    "two-sum": "vector<int>",
    "container-with-most-water": "int",
    "group-anagrams": "vector<vector<string>>",
  };
  return typeMap[questionSlug] || "int";
}

function getCppParams(questionSlug: string): string {
  const paramMap: Record<string, string> = {
    "two-sum": "vector<int>& nums, int target",
    "container-with-most-water": "vector<int>& height",
    "group-anagrams": "vector<string>& strs",
  };
  return paramMap[questionSlug] || "vector<int>& args";
}

function getCppDefaultReturn(questionSlug: string): string {
  const returnMap: Record<string, string> = {
    "two-sum": "{}",
    "container-with-most-water": "0",
    "group-anagrams": "{}",
  };
  return returnMap[questionSlug] || "0";
}
