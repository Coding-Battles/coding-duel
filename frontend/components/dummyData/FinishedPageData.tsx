// Dummy variables for FinishedPage component testing

// Dummy UserData
const dummyUser = {
    id: "user123",
    name: "Alice Johnson",
    email: "alice@example.com",
    image_url: "https://images.unsplash.com/photo-1494790108755-2616b612b786?w=150&h=150&fit=crop&crop=face",
    // Add any other UserData properties you need
  };
  
  const dummyOpponent = {
    id: "opponent456",
    name: "Bob Smith",
    email: "bob@example.com",
    image_url: "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&h=150&fit=crop&crop=face",
    // Add any other UserData properties you need
  };
  
  // Updated TestCase interface
  interface TestCase {
    input: Record<string, any>;
    expected_output: string;
    actual_output: string;
    passed: boolean;
    error?: string;
    execution_time: number;
  }
  
  // Updated TestResultsData interface
  interface TestResultsData {
    message: string;
    code: string;
    opponent_id: string;
    player_name: string;
    success: boolean;
    test_results: TestCase[];
    total_passed: number;
    total_failed: number;
    error?: string;
    complexity?: string;
    implement_time?: number;
    final_time?: number;
  }
  
  // Dummy test cases with Record<string, any> input
  const dummyTestCases: TestCase[] = [
    {
      input: { arr: [1, 2, 3, 4, 5], target: 15 },
      expected_output: "15",
      actual_output: "15",
      passed: true,
      execution_time: 0.5
    },
    {
      input: { arr: [10, 20, 30], target: 60 },
      expected_output: "60",
      actual_output: "60",
      passed: true,
      execution_time: 0.3
    },
    {
      input: { arr: [], target: 0 },
      expected_output: "0",
      actual_output: "0",
      passed: true,
      execution_time: 0.1
    },
    {
      input: { arr: [100, 200, 300, 400], target: 1000 },
      expected_output: "1000",
      actual_output: "1000",
      passed: true,
      execution_time: 0.7
    },
    {
      input: { arr: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10], target: 55 },
      expected_output: "55",
      actual_output: "55",
      passed: true,
      execution_time: 1.2
    }
  ];
  
  const dummyTestCasesWithFailures: TestCase[] = [
    ...dummyTestCases.slice(0, 3),
    {
      input: { arr: [100, 200, 300, 400], target: 1000 },
      expected_output: "1000",
      actual_output: "900",
      passed: false,
      execution_time: 0.8
    },
    {
      input: { arr: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10], target: 55 },
      expected_output: "55",
      actual_output: "50",
      passed: false,
      execution_time: 1.5
    }
  ];
  
  const dummyTestCasesWithErrors: TestCase[] = [
    ...dummyTestCases.slice(0, 2),
    {
      input: { arr: [1, 2, 3], target: 6 },
      expected_output: "6",
      actual_output: "",
      passed: false,
      error: "TypeError: Cannot read property 'length' of undefined",
      execution_time: 0.2
    },
    {
      input: { arr: [5, 10, 15], target: 30 },
      expected_output: "30",
      actual_output: "",
      passed: false,
      error: "ReferenceError: sum is not defined",
      execution_time: 0.1
    }
  ];
  
  // Dummy TestResultsData
  const dummyUserStats: TestResultsData = {
    message: "Solution submitted successfully",
    code: `function sumArray(arr) {
      if (!arr || arr.length === 0) return 0;
      return arr.reduce((sum, num) => sum + num, 0);
  }`,
    opponent_id: "opponent456",
    player_name: "Alice Johnson",
    success: true,
    test_results: dummyTestCases,
    total_passed: 5,
    total_failed: 0,
    complexity: "O(n)",
    implement_time: 165, // 2 minutes 45 seconds in seconds
    final_time: 165
  };
  
  const dummyOpponentStats: TestResultsData = {
    message: "Solution submitted successfully",
    code: `function sumArray(numbers) {
      let total = 0;
      for (let i = 0; i < numbers.length; i++) {
          total += numbers[i];
      }
      return total;
  }`,
    opponent_id: "user123",
    player_name: "Bob Smith",
    success: true,
    test_results: dummyTestCasesWithFailures,
    total_passed: 3,
    total_failed: 2,
    complexity: "O(n)",
    implement_time: 200, // 3 minutes 20 seconds in seconds
    final_time: 200
  };
  
  // Alternative scenario where opponent wins
  const dummyUserStatsLosing: TestResultsData = {
    message: "Solution submitted with errors",
    code: `function sumArray(arr) {
      let sum = 0;
      for (let i = 0; i <= arr.length; i++) { // Bug: should be < not <=
          sum += arr[i];
      }
      return sum;
  }`,
    opponent_id: "opponent456",
    player_name: "Alice Johnson",
    success: false,
    test_results: dummyTestCasesWithFailures,
    total_passed: 3,
    total_failed: 2,
    error: "Runtime error: Cannot read property of undefined",
    complexity: "O(n)",
    implement_time: 255, // 4 minutes 15 seconds in seconds
    final_time: 255
  };
  
  const dummyOpponentStatsWinning: TestResultsData = {
    message: "Perfect solution!",
    code: `const sumArray = (arr) => arr.reduce((a, b) => a + b, 0);`,
    opponent_id: "user123",
    player_name: "Bob Smith",
    success: true,
    test_results: dummyTestCases,
    total_passed: 5,
    total_failed: 0,
    complexity: "O(n)",
    implement_time: 150, // 2 minutes 30 seconds in seconds
    final_time: 150
  };
  
  // Props object ready to use (updated with new interface)
  const dummyProps = {
    opponent: dummyOpponent,
    user: dummyUser,
    opponentStats: dummyOpponentStats,
    userStats: dummyUserStats
  };
  
  // Alternative props where opponent wins
  const dummyPropsOpponentWins = {
    opponent: dummyOpponent,
    user: dummyUser,
    opponentStats: dummyOpponentStatsWinning,
    userStats: dummyUserStatsLosing
  };
  
  // Additional scenarios for testing
  const dummyPropsWithErrors: TestResultsData = {
    message: "Compilation failed",
    code: `function sumArray(arr) {
      let sum = 0;
      for (let i = 0; i < arr.length; i++) {
          sum += arr[i;  // Missing closing bracket
      }
      return sum;
  }`,
    opponent_id: "user123",
    player_name: "Charlie Brown",
    success: false,
    test_results: dummyTestCasesWithErrors,
    total_passed: 2,
    total_failed: 2,
    error: "SyntaxError: Unexpected token ';'",
    complexity: "O(n)",
    implement_time: 180,
    final_time: 180
  };
  
  const dummyPropsWithCompilationError = {
    opponent: dummyOpponent,
    user: dummyUser,
    opponentStats: dummyPropsWithErrors,
    userStats: dummyUserStats
  };
  
  // Usage examples:
  // <FinishedPage {...dummyProps} />                    // User wins
  // <FinishedPage {...dummyPropsOpponentWins} />        // Opponent wins
  // <FinishedPage {...dummyPropsWithCompilationError} />  // One player has errors
  
  // Mock router for testing (if needed)
  const mockRouter = {
    push: (path: string) => console.log(`Navigating to: ${path}`),
    back: () => console.log('Going back'),
    forward: () => console.log('Going forward'),
    refresh: () => console.log('Refreshing'),
    replace: (path: string) => console.log(`Replacing with: ${path}`),
    pathname: '/finished',
    query: {},
    asPath: '/finished'
  };
  
  // Helper function to format time from seconds to MM:SS
  const formatTime = (seconds: number): string => {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
  };
  
  // Helper function to format test input for display
  const formatTestInput = (input: Record<string, any>): string => {
    return Object.entries(input)
      .map(([key, value]) => `${key}: ${JSON.stringify(value)}`)
      .join(', ');
  };
  
  // If you need to mock useRouter:
  // jest.mock('next/navigation', () => ({
  //   useRouter: () => mockRouter
  // }));
  
  export {
    dummyUser,
    dummyOpponent,
    dummyUserStats,
    dummyOpponentStats,
    dummyUserStatsLosing,
    dummyOpponentStatsWinning,
    dummyProps,
    dummyPropsOpponentWins,
    dummyPropsWithCompilationError,
    dummyPropsWithErrors,
    mockRouter,
    formatTime,
    formatTestInput,
    dummyTestCases,
    dummyTestCasesWithFailures,
    dummyTestCasesWithErrors
  };