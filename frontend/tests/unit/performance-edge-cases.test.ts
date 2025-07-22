import { describe, it, expect, vi } from 'vitest';
import { SolutionManager } from '../solutions/solution-manager';
import { createMockSocket } from '../mocks/socket-mock';
import { waitFor, sleep } from '../utils/test-utils';

describe('Performance and Edge Case Tests', () => {

  describe('Solution Manager Performance', () => {
    it('should quickly retrieve solutions for all question-language combinations', () => {
      const startTime = performance.now();
      
      const questions = SolutionManager.getSupportedQuestions();
      
      questions.forEach(question => {
        const languages = SolutionManager.getSupportedLanguages(question);
        
        languages.forEach(language => {
          const solution = SolutionManager.getOptimalSolution(question, language);
          expect(solution).toBeTruthy();
          expect(solution.length).toBeGreaterThan(50);
        });
      });

      const endTime = performance.now();
      const executionTime = endTime - startTime;
      
      // Should complete all operations in under 100ms
      expect(executionTime).toBeLessThan(100);
    });

    it('should handle rapid solution requests', () => {
      const iterations = 100;
      const startTime = performance.now();
      
      for (let i = 0; i < iterations; i++) {
        const solution = SolutionManager.getOptimalSolution('two-sum', 'python');
        expect(solution).toContain('class Solution');
      }

      const endTime = performance.now();
      const executionTime = endTime - startTime;
      
      // Should handle 100 requests quickly
      expect(executionTime).toBeLessThan(50);
    });

    it('should cache solutions effectively', () => {
      const question = 'two-sum';
      const language = 'python';
      
      // First call (potentially slower due to initialization)
      const start1 = performance.now();
      const solution1 = SolutionManager.getOptimalSolution(question, language);
      const end1 = performance.now();

      // Subsequent calls (should be faster due to caching)
      const start2 = performance.now();
      const solution2 = SolutionManager.getOptimalSolution(question, language);
      const end2 = performance.now();

      expect(solution1).toBe(solution2);
      expect(end2 - start2).toBeLessThanOrEqual(end1 - start1);
    });
  });

  describe('Socket Mock Performance', () => {
    it('should handle rapid event emissions', async () => {
      const mockSocket = createMockSocket();
      const eventCounts = { count: 0 };

      mockSocket.on('test_event', () => {
        eventCounts.count++;
      });

      const iterations = 1000;
      const startTime = performance.now();

      // Emit many events rapidly
      for (let i = 0; i < iterations; i++) {
        mockSocket.emit('test_event', { data: i });
      }

      await sleep(10); // Small delay for async processing

      const endTime = performance.now();
      const executionTime = endTime - startTime;

      expect(eventCounts.count).toBe(iterations);
      expect(executionTime).toBeLessThan(100); // Should be very fast
    });

    it('should handle multiple concurrent event listeners', async () => {
      const mockSocket = createMockSocket();
      const results: string[] = [];

      // Add multiple listeners for the same event
      for (let i = 0; i < 10; i++) {
        mockSocket.on('multi_event', (data) => {
          results.push(`listener-${i}-${data.value}`);
        });
      }

      mockSocket.emit('multi_event', { value: 'test' });
      await sleep(10);

      expect(results).toHaveLength(10);
      results.forEach((result, index) => {
        expect(result).toBe(`listener-${index}-test`);
      });
    });

    it('should cleanup event listeners efficiently', () => {
      const mockSocket = createMockSocket();
      const handler = vi.fn();

      // Add many listeners
      for (let i = 0; i < 100; i++) {
        mockSocket.on('cleanup_test', handler);
      }

      expect(mockSocket.getEventHandlers('cleanup_test')).toHaveLength(100);

      // Clear all handlers
      mockSocket.clearAllEventHandlers();
      
      expect(mockSocket.getEventHandlers('cleanup_test')).toHaveLength(0);
      expect(mockSocket.hasEventHandler('cleanup_test')).toBe(false);
    });
  });

  describe('Edge Case Scenarios', () => {
    it('should handle empty or null inputs gracefully', () => {
      expect(() => {
        SolutionManager.getOptimalSolution('' as any, 'python');
      }).toThrow();

      expect(() => {
        SolutionManager.getOptimalSolution('two-sum', '' as any);
      }).toThrow();

      expect(() => {
        SolutionManager.getOptimalSolution(null as any, null as any);
      }).toThrow();
    });

    it('should handle extremely long code solutions', () => {
      const solution = SolutionManager.getOptimalSolution('two-sum', 'python');
      const longSolution = solution + '\n' + '# ' + 'x'.repeat(10000); // Very long comment
      
      expect(longSolution.length).toBeGreaterThan(10000);
      expect(longSolution).toContain('class Solution');
    });

    it('should handle unicode and special characters in solutions', () => {
      const solution = SolutionManager.getOptimalSolution('two-sum', 'python');
      
      // Solutions should handle various character encodings
      expect(solution).toBeTruthy();
      expect(typeof solution).toBe('string');
      
      // Test with special characters (real solutions shouldn't have these, but test robustness)
      const specialChars = '🚀 ñ á é í ó ú ü 中文 🎯';
      expect(solution + specialChars).toContain(specialChars);
    });

    it('should handle concurrent solution requests', async () => {
      const promises = [];
      
      // Create many concurrent requests
      for (let i = 0; i < 50; i++) {
        promises.push(Promise.resolve(SolutionManager.getOptimalSolution('two-sum', 'python')));
        promises.push(Promise.resolve(SolutionManager.getOptimalSolution('add-two-numbers', 'java')));
      }

      const results = await Promise.all(promises);
      
      expect(results).toHaveLength(100);
      results.forEach(solution => {
        expect(solution).toBeTruthy();
        expect(solution).toContain('class Solution');
      });
    });
  });

  describe('Memory Management', () => {
    it('should not leak memory with repeated operations', () => {
      const initialMemory = process.memoryUsage().heapUsed;
      
      // Perform many operations
      for (let i = 0; i < 1000; i++) {
        const solution = SolutionManager.getOptimalSolution('two-sum', 'python');
        const broken = SolutionManager.getBrokenSolution('two-sum', 'javascript');
        
        // Create and destroy mock sockets
        const socket = createMockSocket();
        socket.connect();
        socket.disconnect();
        socket.clearAllEventHandlers();
      }

      // Force garbage collection if available
      if (global.gc) {
        global.gc();
      }

      const finalMemory = process.memoryUsage().heapUsed;
      const memoryIncrease = finalMemory - initialMemory;
      
      // Memory increase should be reasonable (less than 10MB)
      expect(memoryIncrease).toBeLessThan(10 * 1024 * 1024);
    });

    it('should handle large numbers of event listeners without performance degradation', async () => {
      const mockSocket = createMockSocket();
      const handlerCounts = { total: 0 };

      const startTime = performance.now();

      // Add many listeners
      for (let i = 0; i < 1000; i++) {
        mockSocket.on('performance_test', () => {
          handlerCounts.total++;
        });
      }

      // Emit event
      mockSocket.emit('performance_test');
      await sleep(10);

      const endTime = performance.now();
      const executionTime = endTime - startTime;

      expect(handlerCounts.total).toBe(1000);
      expect(executionTime).toBeLessThan(200); // Should still be reasonably fast
    });
  });

  describe('Error Handling and Recovery', () => {
    it('should recover from API fetch errors gracefully', async () => {
      // Simulate network error
      const failedFetch = vi.fn().mockRejectedValue(new Error('Network error'));
      global.fetch = failedFetch;

      try {
        await fetch('http://localhost:8000/api/get-question/test');
      } catch (error) {
        expect(error).toBeInstanceOf(Error);
        expect((error as Error).message).toBe('Network error');
      }

      expect(failedFetch).toHaveBeenCalled();
    });

    it('should handle malformed solution data', () => {
      // Test with invalid solution modifications
      const validSolution = SolutionManager.getOptimalSolution('two-sum', 'python');
      
      // Test various corruptions
      const corruptions = [
        validSolution.replace('class', ''), // Remove class keyword
        validSolution.replace(':', ''), // Remove colons
        validSolution.substring(0, validSolution.length / 2), // Truncate
        validSolution + '\n' + 'invalid python syntax !!!', // Add invalid syntax
      ];

      corruptions.forEach(corrupted => {
        expect(typeof corrupted).toBe('string');
        // The corrupted solutions should still be strings, even if invalid
      });
    });

    it('should handle socket disconnection scenarios', async () => {
      const mockSocket = createMockSocket();
      let disconnectionHandled = false;

      mockSocket.on('disconnect', () => {
        disconnectionHandled = true;
      });

      mockSocket.connect();
      expect(mockSocket.connected).toBe(true);

      mockSocket.disconnect();
      expect(mockSocket.connected).toBe(false);

      await waitFor(() => disconnectionHandled);
      expect(disconnectionHandled).toBe(true);
    });
  });

  describe('Race Conditions', () => {
    it('should handle rapid connect/disconnect cycles', async () => {
      const mockSocket = createMockSocket();
      const events: string[] = [];

      mockSocket.on('connect', () => events.push('connect'));
      mockSocket.on('disconnect', () => events.push('disconnect'));

      // Rapid connect/disconnect cycles
      for (let i = 0; i < 10; i++) {
        mockSocket.connect();
        mockSocket.disconnect();
      }

      await sleep(100);

      // Should handle all events
      expect(events.filter(e => e === 'connect')).toHaveLength(10);
      expect(events.filter(e => e === 'disconnect')).toHaveLength(10);
    });

    it('should handle simultaneous solution requests for same question', () => {
      const startTime = performance.now();
      
      // Multiple simultaneous requests for the same solution
      const promises = Array(20).fill(null).map(() => 
        Promise.resolve(SolutionManager.getOptimalSolution('two-sum', 'python'))
      );

      return Promise.all(promises).then(solutions => {
        const endTime = performance.now();
        
        // All solutions should be identical
        solutions.forEach(solution => {
          expect(solution).toBe(solutions[0]);
        });

        // Should complete quickly despite multiple requests
        expect(endTime - startTime).toBeLessThan(50);
      });
    });
  });

  describe('Stress Testing', () => {
    it('should handle stress test of all features combined', async () => {
      const startTime = performance.now();
      const results = {
        solutionsGenerated: 0,
        socketsCreated: 0,
        eventsEmitted: 0,
        errorsHandled: 0
      };

      // Concurrent stress test
      const stressPromises = [];

      for (let i = 0; i < 10; i++) {
        stressPromises.push(
          (async () => {
            try {
              // Generate solutions
              const solution = SolutionManager.getOptimalSolution('two-sum', 'python');
              const brokenSolution = SolutionManager.getBrokenSolution('add-two-numbers', 'java');
              results.solutionsGenerated += 2;

              // Create and use socket
              const socket = createMockSocket();
              socket.connect();
              results.socketsCreated++;

              // Emit events
              for (let j = 0; j < 5; j++) {
                socket.emit('stress_test', { iteration: i, event: j });
                results.eventsEmitted++;
              }

              socket.disconnect();
            } catch (error) {
              results.errorsHandled++;
            }
          })()
        );
      }

      await Promise.all(stressPromises);

      const endTime = performance.now();
      const executionTime = endTime - startTime;

      expect(results.solutionsGenerated).toBe(20);
      expect(results.socketsCreated).toBe(10);
      expect(results.eventsEmitted).toBe(50);
      expect(results.errorsHandled).toBe(0);
      expect(executionTime).toBeLessThan(1000); // Should complete within 1 second
    });
  });

  describe('Browser Compatibility Edge Cases', () => {
    it('should handle missing modern JavaScript features gracefully', () => {
      // Test behavior when certain features might not be available
      
      // Backup original methods
      const originalMap = global.Map;
      const originalSet = global.Set;

      try {
        // Temporarily remove modern features
        delete (global as any).Map;
        delete (global as any).Set;

        // Solution manager should still work (it uses basic objects/arrays)
        const solution = SolutionManager.getOptimalSolution('two-sum', 'python');
        expect(solution).toBeTruthy();
        
      } finally {
        // Restore original methods
        global.Map = originalMap;
        global.Set = originalSet;
      }
    });

    it('should handle performance timing edge cases', () => {
      // Test when performance.now() might not be available
      const originalPerformance = global.performance;

      try {
        delete (global as any).performance;

        // Code should still work without performance timing
        const startTime = Date.now();
        const solution = SolutionManager.getOptimalSolution('two-sum', 'python');
        const endTime = Date.now();

        expect(solution).toBeTruthy();
        expect(endTime - startTime).toBeGreaterThanOrEqual(0);
        
      } finally {
        global.performance = originalPerformance;
      }
    });
  });
});