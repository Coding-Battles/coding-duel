# Frontend Testing Suite

A comprehensive testing suite for the Coding Duel frontend application, covering unit tests, integration tests, and end-to-end testing scenarios.

## Overview

This testing suite validates the complete gameplay experience, including:
- **Language-specific solutions** for all supported programming languages
- **Complete game flow testing** from queue to finished page
- **Real-time multiplayer simulation** with Socket.IO
- **API integration testing** with mock backend services
- **Performance and edge case testing**

## Test Structure

```
tests/
├── README.md                    # This file
├── setup.ts                     # Test configuration and global setup
├── e2e/                         # End-to-end tests (Playwright)
│   ├── game-flow.spec.ts        # Complete game flow testing
│   └── multiplayer-simulation.spec.ts  # Multiplayer scenarios
├── unit/                        # Unit and integration tests (Vitest)
│   ├── solution-manager.test.ts # Solution management testing
│   ├── api-integration.test.ts  # API endpoint testing
│   ├── finished-page.test.tsx   # Component testing
│   ├── game-components.test.tsx # Game UI component tests
│   └── performance-edge-cases.test.ts  # Performance and edge cases
├── mocks/                       # Mock implementations
│   ├── api-mock.ts             # MSW API mocking
│   ├── socket-mock.ts          # Socket.IO mocking
│   └── game-context-mock.ts    # Game context mocking
├── solutions/                   # Working code solutions
│   ├── solution-manager.ts     # Solution management system
│   ├── two-sum-solutions.ts    # Two Sum solutions
│   ├── add-two-numbers-solutions.ts    # Add Two Numbers solutions
│   └── longest-substring-solutions.ts  # Longest Substring solutions
└── utils/                      # Test utilities
    └── test-utils.tsx          # Custom render and utility functions
```

## Available Solutions

The test suite includes working solutions for all supported questions and languages:

### Questions
- **Two Sum** (Easy) - Hash map approach, O(n) time complexity
- **Add Two Numbers** (Medium) - Linked list traversal with carry
- **Longest Substring Without Repeating Characters** (Medium) - Sliding window

### Languages
- **Python** - Optimal solutions using dictionaries and built-in functions
- **JavaScript** - Modern ES6+ solutions with Map and Set
- **Java** - HashMap-based solutions with proper type handling
- **C++** - STL-based solutions with unordered_map and vectors

## Test Scripts

### Unit and Integration Tests
```bash
# Run all tests
npm run test

# Run tests with UI
npm run test:ui

# Run tests once (CI mode)
npm run test:run

# Run with coverage
npm run test:coverage

# Run specific test pattern
npm run test:game
```

### End-to-End Tests
```bash
# Run E2E tests
npm run test:e2e

# Run E2E tests with UI
npm run test:e2e-ui

# Run all tests (unit + E2E)
npm run test:all
```

## Key Testing Features

### 1. Solution Validation
Tests verify that all provided solutions:
- Pass all test cases for their respective problems
- Use optimal algorithms (O(n) for Two Sum, etc.)
- Follow language-specific best practices
- Handle edge cases correctly

### 2. Game Flow Testing
Complete game simulation including:
- Question loading and display
- Language selection and code editing
- Sample test execution
- Full test submission and winning conditions
- Finished page display with winner/loser information

### 3. Multiplayer Simulation
Real-time testing of:
- Socket connection and game joining
- Opponent code updates and status
- Game completion events (first to solve wins)
- Player disconnection scenarios
- Emoji and communication features

### 4. Performance Testing
- Rapid code changes and debouncing
- Concurrent user simulation
- Memory usage and cleanup
- API response time validation

## Mock Services

### API Mocking (MSW)
- Mock backend endpoints for all game operations
- Realistic response times and data structures
- Error scenario simulation
- Test data management

### Socket.IO Mocking
- Complete Socket.IO client simulation
- Event emission and listening
- Game state synchronization
- Connection/disconnection handling

### Game Context Mocking
- User authentication states
- Game room management
- Opponent data simulation
- Anonymous user support

## Usage Examples

### Running Solution Tests
```bash
# Test all language solutions for Two Sum
npm run test -- --testNamePattern="Two Sum.*All Languages"

# Test specific language
npm run test -- --testNamePattern="Python solutions"

# Test error handling
npm run test -- --testNamePattern="Broken solutions"
```

### Running Game Flow Tests
```bash
# Test complete game experience
npm run test:e2e -- --grep "Complete Game Flow"

# Test multiplayer scenarios
npm run test:e2e -- --grep "Multiplayer"

# Test performance
npm run test -- --testNamePattern="Performance"
```

### Debugging Tests
```bash
# Run with verbose output
npm run test -- --reporter=verbose

# Run specific test file
npm run test tests/unit/solution-manager.test.ts

# Debug E2E tests with browser UI
npm run test:e2e-ui
```

## Test Data

### Sample Game End Data
```typescript
const gameEndData = {
  message: "Test User won the game!",
  winner_id: "user-123",
  winner_name: "Test User",
  loser_id: "opponent-123", 
  loser_name: "Test Opponent",
  game_end_reason: "first_win",
  game_end_time: Date.now() / 1000,
  winner_stats: {
    player_name: "Test User",
    implement_time: 120,
    complexity: "O(n)",
    final_time: 80,
    success: true
  }
}
```

### Solution Testing
```typescript
// Get winning solution
const solution = SolutionManager.getWinningSolution('two-sum', 'python');

// Get intentionally slow solution
const slowSolution = SolutionManager.getLosingSolution('two-sum', 'python');

// Get broken solution for error testing
const brokenSolution = SolutionManager.getBrokenSolution('two-sum', 'python');
```

## CI/CD Integration

### GitHub Actions Example
```yaml
name: Frontend Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      
      - name: Install dependencies
        run: npm ci
      
      - name: Run unit tests
        run: npm run test:run
      
      - name: Run E2E tests
        run: npm run test:e2e
      
      - name: Upload test results
        uses: actions/upload-artifact@v3
        if: always()
        with:
          name: test-results
          path: test-results/
```

## Contributing

### Adding New Tests
1. **Unit tests**: Add to `tests/unit/` directory
2. **E2E tests**: Add to `tests/e2e/` directory
3. **New solutions**: Add to `tests/solutions/` directory
4. **Mock services**: Update files in `tests/mocks/` directory

### Test Naming Conventions
- Test files: `*.test.ts` or `*.spec.ts`
- E2E tests: `*.spec.ts` in `e2e/` directory
- Describe blocks: Feature or component being tested
- Test cases: Specific behavior or scenario

### Best Practices
- Use descriptive test names that explain the scenario
- Mock external dependencies consistently
- Test both success and failure scenarios  
- Include performance considerations for complex operations
- Maintain test data in separate files when possible
- Use proper cleanup in test teardown

## Troubleshooting

### Common Issues

**Tests failing with "Module not found"**
```bash
# Check that all dependencies are installed
npm install

# Verify test setup
npm run test:run -- --reporter=verbose
```

**E2E tests timing out**
```bash
# Increase timeout in playwright.config.ts
# Check that frontend server is running
npm run dev
```

**Socket tests not working**
```bash
# Verify mock setup in setup.ts
# Check socket event names match implementation
```

**Performance tests failing**
```bash
# May indicate actual performance issues
# Check memory usage and optimize if needed
```

## Metrics and Reporting

### Coverage Reports
Tests generate coverage reports showing:
- Line coverage percentage
- Branch coverage
- Function coverage
- Uncovered code sections

### Performance Metrics
- Test execution time
- Memory usage during tests
- API response times
- Socket event handling speed

### Test Results
- Total tests run
- Pass/fail counts
- Error details and stack traces
- Screenshots for E2E test failures

This comprehensive testing suite ensures the Coding Duel application works correctly across all supported languages and scenarios, providing confidence for both development and production deployments.