import { describe, it, expect } from 'vitest';
import { SolutionManager } from '../solutions/solution-manager';
import type { Language } from '../../types/languages';

describe('SolutionManager', () => {
  const supportedLanguages: Language[] = ['python', 'javascript', 'java', 'cpp'];
  const supportedQuestions = ['two-sum', 'add-two-numbers', 'longest-substring-without-repeating-characters'] as const;

  describe('Basic Functionality', () => {
    it('should return supported questions', () => {
      const questions = SolutionManager.getSupportedQuestions();
      expect(questions).toContain('two-sum');
      expect(questions).toContain('add-two-numbers');
      expect(questions).toContain('longest-substring-without-repeating-characters');
    });

    it('should return supported languages for each question', () => {
      supportedQuestions.forEach(question => {
        const languages = SolutionManager.getSupportedLanguages(question);
        expect(languages).toEqual(expect.arrayContaining(supportedLanguages));
      });
    });

    it('should check if solution exists', () => {
      supportedQuestions.forEach(question => {
        supportedLanguages.forEach(language => {
          expect(SolutionManager.hasSolution(question, language)).toBe(true);
        });
      });
    });

    it('should throw error for non-existent question', () => {
      expect(() => {
        SolutionManager.getOptimalSolution('non-existent' as any, 'python');
      }).toThrow('No solution found');
    });

    it('should throw error for non-existent language', () => {
      expect(() => {
        SolutionManager.getOptimalSolution('two-sum', 'ruby' as any);
      }).toThrow('No solution found');
    });
  });

  describe('Two Sum Solutions', () => {
    it('should return valid Python solution for two-sum', () => {
      const solution = SolutionManager.getOptimalSolution('two-sum', 'python');
      expect(solution).toContain('class Solution');
      expect(solution).toContain('def twoSum');
      expect(solution).toContain('num_map');
      expect(solution).toContain('enumerate');
    });

    it('should return valid JavaScript solution for two-sum', () => {
      const solution = SolutionManager.getOptimalSolution('two-sum', 'javascript');
      expect(solution).toContain('class Solution');
      expect(solution).toContain('twoSum');
      expect(solution).toContain('numMap');
      expect(solution).toContain('Map');
    });

    it('should return valid Java solution for two-sum', () => {
      const solution = SolutionManager.getOptimalSolution('two-sum', 'java');
      expect(solution).toContain('class Solution');
      expect(solution).toContain('public int[] twoSum');
      expect(solution).toContain('HashMap');
      expect(solution).toContain('containsKey');
    });

    it('should return valid C++ solution for two-sum', () => {
      const solution = SolutionManager.getOptimalSolution('two-sum', 'cpp');
      expect(solution).toContain('class Solution');
      expect(solution).toContain('vector<int> twoSum');
      expect(solution).toContain('unordered_map');
      expect(solution).toContain('find');
    });
  });

  describe('Add Two Numbers Solutions', () => {
    it('should return valid solutions for all languages', () => {
      supportedLanguages.forEach(language => {
        const solution = SolutionManager.getOptimalSolution('add-two-numbers', language);
        expect(solution).toContain('class Solution');
        expect(solution).toContain('addTwoNumbers');
        expect(solution).toContain('ListNode');
        expect(solution).toContain('carry');
      });
    });
  });

  describe('Longest Substring Solutions', () => {
    it('should return valid solutions for all languages', () => {
      supportedLanguages.forEach(language => {
        const solution = SolutionManager.getOptimalSolution('longest-substring-without-repeating-characters', language);
        expect(solution).toContain('class Solution');
        expect(solution).toContain('length');
        expect(solution).toContain('left');
        expect(solution).toContain('right');
      });
    });
  });

  describe('Alternative Solutions', () => {
    it('should provide brute force solutions for two-sum', () => {
      supportedLanguages.forEach(language => {
        const solution = SolutionManager.getAlternativeSolution('two-sum-brute-force', language);
        expect(solution).toContain('class Solution');
        expect(solution).toContain('for');
        expect(solution).not.toContain('Map');
        expect(solution).not.toContain('dict');
        expect(solution).not.toContain('HashMap');
      });
    });

    it('should provide set-based solutions for longest substring', () => {
      supportedLanguages.forEach(language => {
        const solution = SolutionManager.getAlternativeSolution('longest-substring-set', language);
        expect(solution).toContain('class Solution');
        expect(solution).toContain('while');
        if (language === 'python') {
          expect(solution).toContain('set()');
        } else if (language === 'javascript') {
          expect(solution).toContain('Set()');
        }
      });
    });
  });

  describe('Winning and Losing Solutions', () => {
    it('should return winning solutions (optimal)', () => {
      supportedQuestions.forEach(question => {
        supportedLanguages.forEach(language => {
          const optimal = SolutionManager.getOptimalSolution(question, language);
          const winning = SolutionManager.getWinningSolution(question, language);
          expect(winning).toBe(optimal);
        });
      });
    });

    it('should return losing solutions (brute force when available)', () => {
      const solution = SolutionManager.getLosingSolution('two-sum', 'python');
      // Should be brute force (nested loops) rather than optimal hash map
      expect(solution).toContain('for i in range');
      expect(solution).toContain('for j in range');
      expect(solution).not.toContain('dict');
    });
  });

  describe('Broken Solutions', () => {
    it('should create intentionally broken Python solutions', () => {
      const broken = SolutionManager.getBrokenSolution('two-sum', 'python');
      const optimal = SolutionManager.getOptimalSolution('two-sum', 'python');
      expect(broken).not.toBe(optimal);
      expect(broken).toContain('def broken_syntax');
    });

    it('should create intentionally broken JavaScript solutions', () => {
      const broken = SolutionManager.getBrokenSolution('two-sum', 'javascript');
      expect(broken).toContain('missing_bracket');
    });

    it('should create intentionally broken Java solutions', () => {
      const broken = SolutionManager.getBrokenSolution('two-sum', 'java');
      expect(broken).toContain('Class'); // Wrong capitalization
    });

    it('should create intentionally broken C++ solutions', () => {
      const broken = SolutionManager.getBrokenSolution('two-sum', 'cpp');
      const optimal = SolutionManager.getOptimalSolution('two-sum', 'cpp');
      expect(broken.length).toBeLessThan(optimal.length); // Missing semicolons
    });
  });

  describe('Solution Quality Checks', () => {
    it('should have non-empty solutions for all combinations', () => {
      supportedQuestions.forEach(question => {
        supportedLanguages.forEach(language => {
          const solution = SolutionManager.getOptimalSolution(question, language);
          expect(solution.trim().length).toBeGreaterThan(50);
          expect(solution).toContain('class Solution');
        });
      });
    });

    it('should have language-appropriate syntax', () => {
      const pythonSolution = SolutionManager.getOptimalSolution('two-sum', 'python');
      expect(pythonSolution).toContain('def ');
      expect(pythonSolution).toContain(':');
      expect(pythonSolution).not.toContain(';');

      const javaSolution = SolutionManager.getOptimalSolution('two-sum', 'java');
      expect(javaSolution).toContain('public ');
      expect(javaSolution).toContain(';');
      expect(javaSolution).toContain('{');

      const jsSolution = SolutionManager.getOptimalSolution('two-sum', 'javascript');
      expect(jsSolution).toContain('twoSum(');
      expect(jsSolution).toContain('{');

      const cppSolution = SolutionManager.getOptimalSolution('two-sum', 'cpp');
      expect(cppSolution).toContain('public:');
      expect(cppSolution).toContain('vector<int>');
    });
  });

  describe('Performance Characteristics', () => {
    it('should use optimal algorithms in winning solutions', () => {
      // Two Sum should use hash map (O(n)) not brute force (O(n²))
      supportedLanguages.forEach(language => {
        const solution = SolutionManager.getWinningSolution('two-sum', language);
        if (language === 'python') {
          expect(solution).toContain('{}') || expect(solution).toContain('dict');
        } else if (language === 'javascript') {
          expect(solution).toContain('Map');
        } else if (language === 'java') {
          expect(solution).toContain('HashMap');
        } else if (language === 'cpp') {
          expect(solution).toContain('unordered_map');
        }
      });
    });

    it('should use less optimal algorithms in losing solutions where available', () => {
      const losingSolution = SolutionManager.getLosingSolution('two-sum', 'python');
      expect(losingSolution).toContain('range(len(nums))');
      expect(losingSolution).toContain('range(i + 1');
    });
  });
});