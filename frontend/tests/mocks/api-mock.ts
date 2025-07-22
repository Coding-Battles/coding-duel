import { http, HttpResponse } from 'msw';
import type { QuestionData } from '@/shared/types';
import type { TestResultsData } from '@/shared/types';

// Mock question data
const mockQuestions: Record<string, QuestionData> = {
  'two-sum': {
    id: '1',
    title: 'Two Sum',
    methodName: 'twoSum',
    difficulty: 'Easy',
    description_html: '<p>Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target.</p>',
    starter_code: {
      python: 'class Solution:\n    def twoSum(self, nums: list[int], target: int) -> list[int]:\n        ',
      javascript: 'class Solution {\n    twoSum(nums, target) {\n        \n    }\n}',
      java: 'class Solution {\n    public int[] twoSum(int[] nums, int target) {\n        \n    }\n}',
      cpp: 'class Solution {\npublic:\n    vector<int> twoSum(vector<int>& nums, int target) {\n        \n    }\n};'
    }
  },
  'add-two-numbers': {
    id: '2',
    title: 'Add Two Numbers',
    methodName: 'addTwoNumbers',
    difficulty: 'Medium',
    description_html: '<p>You are given two non-empty linked lists representing two non-negative integers.</p>',
    starter_code: {
      python: 'class Solution:\n    def addTwoNumbers(self, l1: Optional[ListNode], l2: Optional[ListNode]) -> Optional[ListNode]:\n        ',
      javascript: 'class Solution {\n    addTwoNumbers(l1, l2) {\n        \n    }\n}',
      java: 'class Solution {\n    public ListNode addTwoNumbers(ListNode l1, ListNode l2) {\n        \n    }\n}',
      cpp: 'class Solution {\npublic:\n    ListNode* addTwoNumbers(ListNode* l1, ListNode* l2) {\n        \n    }\n};'
    }
  },
  'longest-substring-without-repeating-characters': {
    id: '3',
    title: 'Longest Substring Without Repeating Characters',
    methodName: 'lengthOfLongestSubstring',
    difficulty: 'Medium',
    description_html: '<p>Given a string s, find the length of the longest substring without repeating characters.</p>',
    starter_code: {
      python: 'class Solution:\n    def lengthOfLongestSubstring(self, s: str) -> int:\n        ',
      javascript: 'class Solution {\n    lengthOfLongestSubstring(s) {\n        \n    }\n}',
      java: 'class Solution {\n    public int lengthOfLongestSubstring(String s) {\n        \n    }\n}',
      cpp: 'class Solution {\npublic:\n    int lengthOfLongestSubstring(string s) {\n        \n    }\n};'
    }
  }
};

// API request handlers
export const apiHandlers = [
  // Get question endpoint
  http.get('http://localhost:8000/api/get-question/:questionName', ({ params }) => {
    const { questionName } = params;
    const question = mockQuestions[questionName as string];
    
    if (!question) {
      return HttpResponse.json(
        { detail: `Question '${questionName}' not found` },
        { status: 404 }
      );
    }
    
    return HttpResponse.json(question);
  }),

  // Run sample tests endpoint
  http.post('http://localhost:8000/api/run-sample-tests', async ({ request }) => {
    const body = await request.json() as any;
    
    // Simulate successful test results for valid code
    const isValidSolution = body.code && body.code.length > 50; // Simple heuristic
    
    const mockResult: TestResultsData = {
      success: isValidSolution,
      test_results: [
        { input: '[2,7,11,15], 9', expected: '[0,1]', actual: '[0,1]', passed: isValidSolution },
        { input: '[3,2,4], 6', expected: '[1,2]', actual: '[1,2]', passed: isValidSolution }
      ],
      total_passed: isValidSolution ? 2 : 0,
      total_failed: isValidSolution ? 0 : 2,
      player_name: body.player_id || 'Test Player',
      error: isValidSolution ? null : 'Syntax error or incorrect logic',
      message: isValidSolution ? 'All tests passed!' : 'Some tests failed',
      code: body.code,
      opponent_id: '',
      complexity: 'O(n)',
      implement_time: 120,
      final_time: 100
    };
    
    return HttpResponse.json(mockResult);
  }),

  // Run all tests endpoint (for actual game submission)
  http.post('http://localhost:8000/api/:gameId/run-all-tests', async ({ params, request }) => {
    const { gameId } = params;
    const body = await request.json() as any;
    
    // Simulate game submission results
    const isWinningSolution = body.code && body.code.includes('Map') || body.code.includes('dict') || body.code.includes('unordered_map');
    
    const mockResult: TestResultsData = {
      success: isWinningSolution,
      test_results: Array.from({ length: 12 }, (_, i) => ({
        input: `Test case ${i + 1}`,
        expected: 'Expected result',
        actual: isWinningSolution ? 'Expected result' : 'Wrong result',
        passed: isWinningSolution
      })),
      total_passed: isWinningSolution ? 12 : Math.floor(Math.random() * 8),
      total_failed: isWinningSolution ? 0 : Math.ceil(Math.random() * 4),
      player_name: body.player_id || 'Test Player',
      error: isWinningSolution ? null : 'Some test cases failed',
      message: isWinningSolution ? 'All tests passed! You won!' : 'Some tests failed',
      code: body.code,
      opponent_id: 'opponent-123',
      complexity: isWinningSolution ? 'O(n)' : 'O(n²)',
      implement_time: body.timer || 180,
      final_time: isWinningSolution ? 80 : 120
    };
    
    return HttpResponse.json(mockResult);
  }),

  // Send emoji endpoint
  http.post('http://localhost:8000/api/:gameId/send-emoji', async ({ params, request }) => {
    const { gameId } = params;
    const body = await request.json() as any;
    
    return HttpResponse.json({
      message: 'Emoji sent successfully',
      gameId,
      emoji: body.emoji
    });
  }),

  // User game history endpoint
  http.get('http://localhost:8000/api/user/:userId/game-history', ({ params }) => {
    const { userId } = params;
    
    return HttpResponse.json([
      {
        game_id: 1,
        user_id: userId,
        created_at: new Date().toISOString(),
        player_name: 'Test Player',
        implement_time: 120,
        time_complexity: 'O(n)',
        final_time: 100,
        player_code: 'test code'
      }
    ]);
  })
];

export default apiHandlers;