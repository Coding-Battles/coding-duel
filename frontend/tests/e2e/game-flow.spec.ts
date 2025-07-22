import { test, expect } from '@playwright/test';
import { SolutionManager } from '../solutions/solution-manager';

test.describe('Complete Game Flow Testing', () => {
  
  test.beforeEach(async ({ page }) => {
    // Navigate to the app
    await page.goto('/');
    
    // Wait for the page to load
    await page.waitForLoadState('networkidle');
  });

  test('Two Sum - Python Solution Wins Game', async ({ page }) => {
    const questionName = 'two-sum';
    const language = 'python';
    const winningSolution = SolutionManager.getWinningSolution(questionName, language);

    // Navigate to the game page (simulating queue match)
    await page.goto(`/game-setup/queue/${questionName}`);
    await page.waitForLoadState('networkidle');

    // Wait for question to load
    await expect(page.locator('h2:has-text("Two Sum")')).toBeVisible({ timeout: 10000 });

    // Select Python language
    await page.click('[data-testid="language-selector"]', { timeout: 5000 });
    await page.click('text=Python');

    // Wait for Monaco editor to load and find the code input
    await page.waitForSelector('[data-testid="monaco-editor"], .monaco-editor, textarea', { timeout: 10000 });
    
    // Type the winning solution
    const codeEditor = page.locator('[data-testid="monaco-editor"], .monaco-editor textarea, textarea').first();
    await codeEditor.clear();
    await codeEditor.fill(winningSolution);

    // Submit the solution
    await page.click('button:has-text("Submit"), [data-testid="submit-button"]');

    // Wait for test results
    await page.waitForSelector('text=All tests passed, text=Test execution completed', { timeout: 15000 });

    // Wait for game completion (first to solve wins)
    await expect(page.locator('text=Game Complete, text=Congratulations')).toBeVisible({ timeout: 20000 });

    // Verify winner display
    await expect(page.locator('text=Winner')).toBeVisible();
    await expect(page.locator('text=You won, text=Congratulations')).toBeVisible();
  });

  test('Two Sum - All Languages Solutions Work', async ({ page }) => {
    const questionName = 'two-sum';
    const languages = ['python', 'javascript', 'java', 'cpp'] as const;

    for (const language of languages) {
      console.log(`Testing ${language} solution for ${questionName}`);
      
      // Get the winning solution
      const solution = SolutionManager.getWinningSolution(questionName, language);
      
      // Navigate to fresh game
      await page.goto(`/game-setup/queue/${questionName}`);
      await page.waitForLoadState('networkidle');

      // Wait for question to load
      await expect(page.locator('h2')).toContainText('Two Sum', { timeout: 10000 });

      // Select language
      await page.click('[data-testid="language-selector"]', { timeout: 5000 });
      const languageDisplayNames = {
        python: 'Python',
        javascript: 'JavaScript', 
        java: 'Java',
        cpp: 'C++'
      };
      await page.click(`text=${languageDisplayNames[language]}`);

      // Input the solution
      const codeEditor = page.locator('[data-testid="monaco-editor"], .monaco-editor textarea, textarea').first();
      await codeEditor.clear();
      await codeEditor.fill(solution);

      // Run sample tests first to verify solution works
      await page.click('button:has-text("Run"), [data-testid="run-button"]');
      await page.waitForSelector('text=passed, text=success', { timeout: 15000 });

      // Now submit for full test
      await page.click('button:has-text("Submit"), [data-testid="submit-button"]');
      
      // Wait for completion and verify success
      await expect(page.locator('text=All tests passed, text=success')).toBeVisible({ timeout: 15000 });
      
      console.log(`✅ ${language} solution passed for ${questionName}`);
    }
  });

  test('Add Two Numbers - Complete Game Flow', async ({ page }) => {
    const questionName = 'add-two-numbers';
    const language = 'javascript';
    const solution = SolutionManager.getWinningSolution(questionName, language);

    await page.goto(`/game-setup/queue/${questionName}`);
    await page.waitForLoadState('networkidle');

    // Verify question loaded
    await expect(page.locator('h2')).toContainText('Add Two Numbers', { timeout: 10000 });

    // Select JavaScript
    await page.click('[data-testid="language-selector"]');
    await page.click('text=JavaScript');

    // Input solution
    const codeEditor = page.locator('textarea, [data-testid="monaco-editor"]').first();
    await codeEditor.clear();
    await codeEditor.fill(solution);

    // Submit solution
    await page.click('button:has-text("Submit")');

    // Verify successful completion
    await expect(page.locator('text=success, text=passed')).toBeVisible({ timeout: 15000 });
  });

  test('Longest Substring - All Languages Test', async ({ page }) => {
    const questionName = 'longest-substring-without-repeating-characters';
    const languages = ['python', 'java'] as const; // Test subset for speed

    for (const language of languages) {
      const solution = SolutionManager.getWinningSolution(questionName, language);
      
      await page.goto(`/game-setup/queue/${questionName}`);
      await page.waitForLoadState('networkidle');

      await expect(page.locator('h2')).toContainText('Longest Substring', { timeout: 10000 });

      // Select language
      await page.click('[data-testid="language-selector"]');
      const langName = language === 'python' ? 'Python' : 'Java';
      await page.click(`text=${langName}`);

      // Input and test solution
      const codeEditor = page.locator('textarea, [data-testid="monaco-editor"]').first();
      await codeEditor.clear();
      await codeEditor.fill(solution);

      await page.click('button:has-text("Submit")');
      await expect(page.locator('text=success, text=passed')).toBeVisible({ timeout: 15000 });
    }
  });

  test('Error Handling - Broken Solutions', async ({ page }) => {
    const questionName = 'two-sum';
    const language = 'python';
    const brokenSolution = SolutionManager.getBrokenSolution(questionName, language);

    await page.goto(`/game-setup/queue/${questionName}`);
    await page.waitForLoadState('networkidle');

    await expect(page.locator('h2')).toContainText('Two Sum', { timeout: 10000 });

    // Select Python
    await page.click('[data-testid="language-selector"]');
    await page.click('text=Python');

    // Input broken solution
    const codeEditor = page.locator('textarea, [data-testid="monaco-editor"]').first();
    await codeEditor.clear();
    await codeEditor.fill(brokenSolution);

    // Submit and expect failure
    await page.click('button:has-text("Submit")');
    
    // Should show error or failure message
    await expect(page.locator('text=error, text=failed, text=syntax')).toBeVisible({ timeout: 15000 });
  });

  test('Game Timer and Real-time Features', async ({ page }) => {
    const questionName = 'two-sum';
    
    await page.goto(`/game-setup/queue/${questionName}`);
    await page.waitForLoadState('networkidle');

    // Check if timer appears (game started)
    await expect(page.locator('[data-testid="game-timer"], text=Timer, text=Time')).toBeVisible({ timeout: 10000 });

    // Check if opponent panel is visible
    await expect(page.locator('[data-testid="opponent-info"], text=Opponent')).toBeVisible({ timeout: 5000 });

    // Check if code editor is functional
    const codeEditor = page.locator('textarea, [data-testid="monaco-editor"]').first();
    await codeEditor.fill('# Test typing works');
    await expect(codeEditor).toHaveValue(/Test typing works/);
  });

  test('Finished Page Display', async ({ page }) => {
    const questionName = 'two-sum';
    const language = 'python';
    const solution = SolutionManager.getWinningSolution(questionName, language);

    await page.goto(`/game-setup/queue/${questionName}`);
    await page.waitForLoadState('networkidle');

    // Complete the game quickly
    await page.click('[data-testid="language-selector"]');
    await page.click('text=Python');

    const codeEditor = page.locator('textarea, [data-testid="monaco-editor"]').first();
    await codeEditor.clear();
    await codeEditor.fill(solution);

    await page.click('button:has-text("Submit")');
    
    // Wait for game to complete and finished page to appear
    await expect(page.locator('text=Game Complete, text=Winner')).toBeVisible({ timeout: 20000 });

    // Verify finished page elements
    await expect(page.locator('text=Winner, text=Loser')).toBeVisible();
    await expect(page.locator('button:has-text("Play Again"), button:has-text("Main Menu")')).toBeVisible();

    // Test navigation buttons work
    await page.click('button:has-text("Main Menu")');
    await expect(page.url()).toMatch(/\/$|\/home/);
  });

  test('Language Switching During Game', async ({ page }) => {
    const questionName = 'two-sum';
    
    await page.goto(`/game-setup/queue/${questionName}`);
    await page.waitForLoadState('networkidle');

    // Start with Python
    await page.click('[data-testid="language-selector"]');
    await page.click('text=Python');

    const codeEditor = page.locator('textarea, [data-testid="monaco-editor"]').first();
    await codeEditor.fill('# Python code');

    // Switch to JavaScript
    await page.click('[data-testid="language-selector"]');
    await page.click('text=JavaScript');

    // Verify starter code changed
    await expect(codeEditor).toHaveValue(/class Solution/);
    await expect(codeEditor).not.toHaveValue(/# Python code/);

    // Switch back to Python
    await page.click('[data-testid="language-selector"]');
    await page.click('text=Python');

    // Verify it has Python starter code
    await expect(codeEditor).toHaveValue(/def twoSum/);
  });

});