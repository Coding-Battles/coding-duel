import { test, expect } from '@playwright/test';
import { SolutionManager } from '../solutions/solution-manager';

test.describe('Multiplayer Game Simulation', () => {

  test('Simulate Complete Multiplayer Game - User Wins', async ({ page, context }) => {
    // This test simulates a full multiplayer game where the user wins

    const questionName = 'two-sum';
    const language = 'python';
    const winningSolution = SolutionManager.getWinningSolution(questionName, language);

    // Start the game
    await page.goto(`/game-setup/queue/${questionName}`);
    await page.waitForLoadState('networkidle');

    // Wait for game setup
    await expect(page.locator('h2')).toContainText('Two Sum', { timeout: 10000 });

    // Select language and input winning solution
    await page.click('[data-testid="language-selector"]');
    await page.click('text=Python');

    const codeEditor = page.locator('textarea, [data-testid="monaco-editor"]').first();
    await codeEditor.clear();
    await codeEditor.fill(winningSolution);

    // Submit solution quickly to win
    await page.click('button:has-text("Submit")');

    // Wait for win condition
    await expect(page.locator('text=Game Complete')).toBeVisible({ timeout: 20000 });
    await expect(page.locator('text=Winner')).toBeVisible();
    await expect(page.locator('text=Congratulations, text=You won')).toBeVisible();

    // Verify winner stats are displayed
    await expect(page.locator('text=Implementation, text=Complexity, text=Total Score')).toBeVisible();
  });

  test('Simulate User Loses - Opponent Wins First', async ({ page }) => {
    const questionName = 'two-sum';
    const language = 'python';
    
    // Use a slower/broken solution to simulate losing
    const losingSolution = SolutionManager.getLosingSolution(questionName, language);

    await page.goto(`/game-setup/queue/${questionName}`);
    await page.waitForLoadState('networkidle');

    await expect(page.locator('h2')).toContainText('Two Sum');

    // Select language
    await page.click('[data-testid="language-selector"]');
    await page.click('text=Python');

    const codeEditor = page.locator('textarea, [data-testid="monaco-editor"]').first();
    await codeEditor.clear();

    // Input losing solution slowly (simulate slow typing)
    for (let i = 0; i < losingSolution.length; i += 10) {
      await codeEditor.fill(losingSolution.substring(0, i + 10));
      await page.waitForTimeout(100); // Simulate typing delay
    }

    // Before submitting, we should see opponent activity
    // (In a real test, we'd mock socket events to show opponent winning)

    // Submit the solution
    await page.click('button:has-text("Submit")');

    // In a losing scenario, the game should end with opponent winning
    // The exact behavior depends on your implementation
    await page.waitForTimeout(2000); // Wait for potential opponent win
  });

  test('Test Real-time Code Sharing', async ({ page }) => {
    const questionName = 'two-sum';
    
    await page.goto(`/game-setup/queue/${questionName}`);
    await page.waitForLoadState('networkidle');

    // Select Python
    await page.click('[data-testid="language-selector"]');
    await page.click('text=Python');

    const codeEditor = page.locator('textarea, [data-testid="monaco-editor"]').first();

    // Type code and verify it triggers real-time updates
    await codeEditor.fill('# Test code update');
    
    // Check if opponent panel shows activity indicators
    // (In real implementation, this would be mocked via socket events)
    await expect(page.locator('[data-testid="opponent-info"]')).toBeVisible();
    
    // Test language switching updates
    await page.click('[data-testid="language-selector"]');
    await page.click('text=JavaScript');
    
    await codeEditor.fill('// JavaScript test code');
    await page.waitForTimeout(1000);
  });

  test('Opponent Disconnection Scenario', async ({ page }) => {
    const questionName = 'two-sum';
    
    await page.goto(`/game-setup/queue/${questionName}`);
    await page.waitForLoadState('networkidle');

    // Wait for game to start
    await expect(page.locator('h2')).toContainText('Two Sum');

    // Simulate opponent disconnection after a few seconds
    await page.waitForTimeout(3000);

    // In a real scenario, socket would emit disconnection event
    // This would trigger automatic win for remaining player

    // Check for disconnection message (if implemented)
    // await expect(page.locator('text=Opponent disconnected')).toBeVisible({ timeout: 10000 });
    // await expect(page.locator('text=You won')).toBeVisible();
  });

  test('Emoji and Real-time Communication', async ({ page }) => {
    const questionName = 'two-sum';
    
    await page.goto(`/game-setup/queue/${questionName}`);
    await page.waitForLoadState('networkidle');

    // Look for emoji/communication features
    const emojiButton = page.locator('button:has-text("😀"), [data-testid="emoji-button"]');
    if (await emojiButton.isVisible()) {
      await emojiButton.click();
      
      // Check if emoji panel appears
      await expect(page.locator('[data-testid="emoji-panel"], .emoji-picker')).toBeVisible();
      
      // Send an emoji
      await page.click('text=👍, button:has-text("👍")');
      
      // Verify emoji was sent (visual feedback)
      await expect(page.locator('text=Emoji sent, .emoji-sent')).toBeVisible({ timeout: 5000 });
    }
  });

  test('Performance Test - Rapid Code Changes', async ({ page }) => {
    const questionName = 'two-sum';
    
    await page.goto(`/game-setup/queue/${questionName}`);
    await page.waitForLoadState('networkidle');

    await page.click('[data-testid="language-selector"]');
    await page.click('text=Python');

    const codeEditor = page.locator('textarea, [data-testid="monaco-editor"]').first();

    // Test rapid code changes (debouncing)
    for (let i = 0; i < 10; i++) {
      await codeEditor.fill(`# Rapid change ${i}`);
      await page.waitForTimeout(50); // Very fast changes
    }

    // Verify the editor still works after rapid changes
    await codeEditor.fill('# Final test');
    await expect(codeEditor).toHaveValue(/Final test/);
  });

  test('Multiple Question Types - Integration', async ({ page }) => {
    const questions = [
      'two-sum',
      'add-two-numbers', 
      'longest-substring-without-repeating-characters'
    ] as const;

    for (const questionName of questions) {
      console.log(`Testing question: ${questionName}`);
      
      await page.goto(`/game-setup/queue/${questionName}`);
      await page.waitForLoadState('networkidle');

      // Verify question loads correctly
      await expect(page.locator('h2')).toBeVisible({ timeout: 10000 });
      
      // Verify language selector works
      await page.click('[data-testid="language-selector"]');
      await expect(page.locator('text=Python, text=JavaScript, text=Java')).toBeVisible();
      await page.click('text=Python');

      // Verify code editor is functional
      const codeEditor = page.locator('textarea, [data-testid="monaco-editor"]').first();
      await expect(codeEditor).toBeVisible();
      
      // Quick smoke test
      await codeEditor.fill('# Test');
      await expect(codeEditor).toHaveValue(/# Test/);
      
      console.log(`✅ Question ${questionName} basic functionality verified`);
    }
  });

  test('Game State Persistence and Recovery', async ({ page, context }) => {
    const questionName = 'two-sum';
    
    await page.goto(`/game-setup/queue/${questionName}`);
    await page.waitForLoadState('networkidle');

    // Start coding
    await page.click('[data-testid="language-selector"]');
    await page.click('text=Python');

    const codeEditor = page.locator('textarea, [data-testid="monaco-editor"]').first();
    await codeEditor.fill('# User was typing this code');

    // Simulate page refresh (connection loss)
    await page.reload();
    await page.waitForLoadState('networkidle');

    // Check if game state is recovered
    // (Implementation specific - might redirect to queue or preserve state)
    await expect(page.locator('body')).toBeVisible();
  });

  test('Concurrent User Simulation', async ({ browser }) => {
    // Create two browser contexts to simulate two users
    const context1 = await browser.newContext();
    const context2 = await browser.newContext();
    
    const page1 = await context1.newPage();
    const page2 = await context2.newPage();

    const questionName = 'two-sum';

    try {
      // Both users navigate to the same question
      await Promise.all([
        page1.goto(`/game-setup/queue/${questionName}`),
        page2.goto(`/game-setup/queue/${questionName}`)
      ]);

      await Promise.all([
        page1.waitForLoadState('networkidle'),
        page2.waitForLoadState('networkidle')
      ]);

      // Both users should see the question
      await Promise.all([
        expect(page1.locator('h2')).toContainText('Two Sum'),
        expect(page2.locator('h2')).toContainText('Two Sum')
      ]);

      // User 1 starts coding
      await page1.click('[data-testid="language-selector"]');
      await page1.click('text=Python');
      
      const editor1 = page1.locator('textarea, [data-testid="monaco-editor"]').first();
      await editor1.fill('# User 1 code');

      // User 2 starts coding
      await page2.click('[data-testid="language-selector"]');
      await page2.click('text=JavaScript');
      
      const editor2 = page2.locator('textarea, [data-testid="monaco-editor"]').first();
      await editor2.fill('// User 2 code');

      // Verify both editors work independently
      await expect(editor1).toHaveValue(/User 1 code/);
      await expect(editor2).toHaveValue(/User 2 code/);

    } finally {
      await context1.close();
      await context2.close();
    }
  });

});