import { describe, it, expect, beforeEach } from 'vitest';
import { SolutionManager } from '../solutions/solution-manager';

describe('API Integration Tests', () => {
  const baseURL = 'http://localhost:8000';

  describe('Get Question Endpoint', () => {
    it('should fetch two-sum question successfully', async () => {
      const response = await fetch(`${baseURL}/api/get-question/two-sum`);
      expect(response.ok).toBe(true);

      const question = await response.json();
      expect(question.title).toBe('Two Sum');
      expect(question.difficulty).toBe('Easy');
      expect(question.starter_code).toHaveProperty('python');
      expect(question.starter_code).toHaveProperty('javascript');
      expect(question.starter_code).toHaveProperty('java');
      expect(question.starter_code).toHaveProperty('cpp');
    });

    it('should fetch add-two-numbers question successfully', async () => {
      const response = await fetch(`${baseURL}/api/get-question/add-two-numbers`);
      expect(response.ok).toBe(true);

      const question = await response.json();
      expect(question.title).toBe('Add Two Numbers');
      expect(question.difficulty).toBe('Medium');
      expect(question.starter_code).toBeDefined();
    });

    it('should fetch longest-substring question successfully', async () => {
      const response = await fetch(`${baseURL}/api/get-question/longest-substring-without-repeating-characters`);
      expect(response.ok).toBe(true);

      const question = await response.json();
      expect(question.title).toBe('Longest Substring Without Repeating Characters');
      expect(question.starter_code).toBeDefined();
    });

    it('should return 404 for non-existent question', async () => {
      const response = await fetch(`${baseURL}/api/get-question/non-existent-question`);
      expect(response.status).toBe(404);

      const error = await response.json();
      expect(error.detail).toContain('not found');
    });
  });

  describe('Run Sample Tests Endpoint', () => {
    it('should run sample tests with valid Python solution', async () => {
      const solution = SolutionManager.getWinningSolution('two-sum', 'python');
      
      const response = await fetch(`${baseURL}/api/run-sample-tests`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          player_id: 'test-player',
          code: solution,
          question_name: 'two-sum',
          language: 'python',
          timer: 120
        })
      });

      expect(response.ok).toBe(true);
      const result = await response.json();
      
      expect(result.success).toBe(true);
      expect(result.total_passed).toBeGreaterThan(0);
      expect(result.total_failed).toBe(0);
      expect(result.test_results).toBeDefined();
      expect(Array.isArray(result.test_results)).toBe(true);
    });

    it('should run sample tests with valid JavaScript solution', async () => {
      const solution = SolutionManager.getWinningSolution('two-sum', 'javascript');
      
      const response = await fetch(`${baseURL}/api/run-sample-tests`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          player_id: 'test-player',
          code: solution,
          question_name: 'two-sum',
          language: 'javascript',
          timer: 130
        })
      });

      expect(response.ok).toBe(true);
      const result = await response.json();
      
      expect(result.success).toBe(true);
      expect(result.player_name).toBe('test-player');
    });

    it('should handle broken solutions correctly', async () => {
      const brokenSolution = SolutionManager.getBrokenSolution('two-sum', 'python');
      
      const response = await fetch(`${baseURL}/api/run-sample-tests`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          player_id: 'test-player',
          code: brokenSolution,
          question_name: 'two-sum',
          language: 'python',
          timer: 180
        })
      });

      expect(response.ok).toBe(true);
      const result = await response.json();
      
      expect(result.success).toBe(false);
      expect(result.total_failed).toBeGreaterThan(0);
      expect(result.error).toBeTruthy();
    });

    it('should handle empty code submission', async () => {
      const response = await fetch(`${baseURL}/api/run-sample-tests`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          player_id: 'test-player',
          code: '',
          question_name: 'two-sum',
          language: 'python',
          timer: 10
        })
      });

      expect(response.ok).toBe(true);
      const result = await response.json();
      
      expect(result.success).toBe(false);
      expect(result.error).toBeTruthy();
    });
  });

  describe('Run All Tests Endpoint (Game Submission)', () => {
    it('should submit winning solution and trigger win condition', async () => {
      const gameId = 'test-game-123';
      const solution = SolutionManager.getWinningSolution('two-sum', 'python');
      
      const response = await fetch(`${baseURL}/api/${gameId}/run-all-tests`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          player_id: 'test-player-123',
          code: solution,
          question_name: 'two-sum',
          language: 'python',
          timer: 95
        })
      });

      expect(response.ok).toBe(true);
      const result = await response.json();
      
      expect(result.success).toBe(true);
      expect(result.total_passed).toBe(12); // All test cases
      expect(result.total_failed).toBe(0);
      expect(result.complexity).toBe('O(n)');
      expect(result.final_time).toBeLessThan(result.implement_time);
      expect(result.opponent_id).toBe('opponent-123');
    });

    it('should handle losing solution correctly', async () => {
      const gameId = 'test-game-456';
      const solution = SolutionManager.getLosingSolution('two-sum', 'python');
      
      const response = await fetch(`${baseURL}/api/${gameId}/run-all-tests`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          player_id: 'test-player-456',
          code: solution,
          question_name: 'two-sum',
          language: 'python',
          timer: 200
        })
      });

      expect(response.ok).toBe(true);
      const result = await response.json();
      
      // Losing solution might pass some tests but not optimally
      expect(result.total_passed).toBeLessThan(12);
      expect(result.success).toBe(false);
      expect(result.complexity).toBe('O(n²)'); // Brute force complexity
    });

    it('should return 404 for non-existent game', async () => {
      const solution = SolutionManager.getWinningSolution('two-sum', 'python');
      
      const response = await fetch(`${baseURL}/api/non-existent-game/run-all-tests`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          player_id: 'test-player',
          code: solution,
          question_name: 'two-sum',
          language: 'python',
          timer: 120
        })
      });

      expect(response.status).toBe(404);
    });
  });

  describe('Multi-language Solution Testing', () => {
    const languages = ['python', 'javascript', 'java', 'cpp'] as const;
    const questions = ['two-sum', 'add-two-numbers', 'longest-substring-without-repeating-characters'] as const;

    languages.forEach(language => {
      describe(`${language} solutions`, () => {
        questions.forEach(questionName => {
          it(`should pass sample tests for ${questionName}`, async () => {
            const solution = SolutionManager.getWinningSolution(questionName, language);
            
            const response = await fetch(`${baseURL}/api/run-sample-tests`, {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
              },
              body: JSON.stringify({
                player_id: `test-${language}-player`,
                code: solution,
                question_name: questionName,
                language: language,
                timer: 150
              })
            });

            expect(response.ok).toBe(true);
            const result = await response.json();
            
            expect(result.success).toBe(true);
            expect(result.total_failed).toBe(0);
            expect(result.complexity).toBeTruthy();
          });
        });
      });
    });
  });

  describe('Emoji and Communication Features', () => {
    it('should send emoji successfully', async () => {
      const gameId = 'test-game-789';
      
      const response = await fetch(`${baseURL}/api/${gameId}/send-emoji`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          player1: 'test-player-1',
          emoji: '👍'
        })
      });

      expect(response.ok).toBe(true);
      const result = await response.json();
      
      expect(result.message).toBe('Emoji sent successfully');
      expect(result.emoji).toBe('👍');
    });
  });

  describe('User Game History', () => {
    it('should fetch user game history', async () => {
      const userId = 'test-user-123';
      
      const response = await fetch(`${baseURL}/api/user/${userId}/game-history`);
      expect(response.ok).toBe(true);

      const history = await response.json();
      expect(Array.isArray(history)).toBe(true);
      
      if (history.length > 0) {
        const game = history[0];
        expect(game).toHaveProperty('game_id');
        expect(game).toHaveProperty('player_name');
        expect(game).toHaveProperty('implement_time');
        expect(game).toHaveProperty('time_complexity');
      }
    });
  });

  describe('Performance and Load Testing', () => {
    it('should handle multiple concurrent sample test requests', async () => {
      const solution = SolutionManager.getWinningSolution('two-sum', 'python');
      
      const promises = Array.from({ length: 5 }, (_, i) => 
        fetch(`${baseURL}/api/run-sample-tests`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            player_id: `concurrent-player-${i}`,
            code: solution,
            question_name: 'two-sum',
            language: 'python',
            timer: 120
          })
        })
      );

      const responses = await Promise.all(promises);
      
      responses.forEach(response => {
        expect(response.ok).toBe(true);
      });

      const results = await Promise.all(responses.map(r => r.json()));
      
      results.forEach(result => {
        expect(result.success).toBe(true);
      });
    });

    it('should handle rapid sequential requests', async () => {
      const solution = SolutionManager.getWinningSolution('two-sum', 'javascript');
      
      for (let i = 0; i < 3; i++) {
        const response = await fetch(`${baseURL}/api/run-sample-tests`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            player_id: `rapid-player-${i}`,
            code: solution,
            question_name: 'two-sum',
            language: 'javascript',
            timer: 100 + i * 10
          })
        });

        expect(response.ok).toBe(true);
        const result = await response.json();
        expect(result.success).toBe(true);
      }
    });
  });
});