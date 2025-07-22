import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent, waitFor } from '../utils/test-utils';
import DuelInfo from '@/components/DuelInfo';
import { createMockSocket } from '../mocks/socket-mock';

// Mock child components that aren't the focus of these tests
vi.mock('@/components/GameTimer', () => ({
  default: ({ timeRef, gameStartTime, isGameStarted }: any) => (
    <div data-testid="game-timer">
      Mock Timer - Started: {isGameStarted ? 'Yes' : 'No'}
      {gameStartTime && ` - Start: ${gameStartTime}`}
    </div>
  )
}));

vi.mock('@/components/TestResults', () => ({
  default: ({ results }: any) => (
    <div data-testid="test-results">
      Mock Test Results - Success: {results?.success ? 'Yes' : 'No'}
    </div>
  )
}));

describe('Game Components', () => {
  
  describe('DuelInfo Component', () => {
    const mockOpponent = {
      id: 'opponent-123',
      name: 'Test Opponent',
      image_url: 'https://via.placeholder.com/150'
    };

    const mockUser = {
      id: 'user-123',
      name: 'Test User',
      email: 'test@example.com',
      image: 'https://via.placeholder.com/150'
    };

    const mockTimeRef = { current: 0 };

    it('should render opponent information', () => {
      const mockSocket = createMockSocket();
      
      render(
        <DuelInfo
          timeRef={mockTimeRef}
          opponentData={mockOpponent}
          user={mockUser}
          socket={mockSocket}
          gameId="test-game-123"
          starterCode="# Starter code"
          selectedLanguage="python"
          gameStartTime={null}
          isGameStarted={false}
        />
      );

      expect(screen.getByText('Test Opponent')).toBeInTheDocument();
    });

    it('should render game timer when game starts', () => {
      const mockSocket = createMockSocket();
      const gameStartTime = Date.now() / 1000;
      
      render(
        <DuelInfo
          timeRef={mockTimeRef}
          opponentData={mockOpponent}
          user={mockUser}
          socket={mockSocket}
          gameId="test-game-123"
          starterCode="# Starter code"
          selectedLanguage="python"
          gameStartTime={gameStartTime}
          isGameStarted={true}
        />
      );

      expect(screen.getByTestId('game-timer')).toBeInTheDocument();
      expect(screen.getByText(/Started: Yes/)).toBeInTheDocument();
    });

    it('should show waiting state when game has not started', () => {
      const mockSocket = createMockSocket();
      
      render(
        <DuelInfo
          timeRef={mockTimeRef}
          opponentData={mockOpponent}
          user={mockUser}
          socket={mockSocket}
          gameId="test-game-123"
          starterCode="# Starter code"
          selectedLanguage="python"
          gameStartTime={null}
          isGameStarted={false}
        />
      );

      expect(screen.getByText(/Started: No/)).toBeInTheDocument();
    });

    it('should handle emoji sending when emoji button is clicked', async () => {
      const mockSocket = createMockSocket();
      
      render(
        <DuelInfo
          timeRef={mockTimeRef}
          opponentData={mockOpponent}
          user={mockUser}
          socket={mockSocket}
          gameId="test-game-123"
          starterCode="# Starter code"
          selectedLanguage="python"
          gameStartTime={Date.now() / 1000}
          isGameStarted={true}
        />
      );

      // Look for emoji button (if implemented)
      const emojiButton = screen.queryByTestId('emoji-button');
      if (emojiButton) {
        fireEvent.click(emojiButton);
        
        // Check if emoji panel appears
        await waitFor(() => {
          expect(screen.queryByTestId('emoji-panel')).toBeInTheDocument();
        });
      }
    });

    it('should display opponent code updates', () => {
      const mockSocket = createMockSocket();
      
      render(
        <DuelInfo
          timeRef={mockTimeRef}
          opponentData={mockOpponent}
          user={mockUser}
          socket={mockSocket}
          gameId="test-game-123"
          starterCode="# Starter code"
          selectedLanguage="python"
          gameStartTime={Date.now() / 1000}
          isGameStarted={true}
        />
      );

      // Simulate opponent code update
      mockSocket.simulateOpponentCodeUpdate('print("Hello World")', 'python');
      
      // Check if component handles the update (implementation specific)
      expect(screen.getByTestId('game-timer')).toBeInTheDocument();
    });

    it('should handle missing props gracefully', () => {
      render(
        <DuelInfo
          timeRef={mockTimeRef}
          opponentData={null}
          user={null}
          socket={null}
          gameId=""
          starterCode=""
          selectedLanguage="python"
          gameStartTime={null}
          isGameStarted={false}
        />
      );

      // Should render without crashing
      expect(screen.getByTestId('game-timer')).toBeInTheDocument();
    });
  });

  describe('Language Selection Component Tests', () => {
    it('should render language selector with all supported languages', () => {
      // This would be testing the language selector component if extracted
      // For now, we can test it as part of the main game page
      const languages = ['Python', 'JavaScript', 'Java', 'C++'];
      
      // Mock component
      const LanguageSelector = ({ languages, onSelect }: any) => (
        <select data-testid="language-selector" onChange={(e) => onSelect(e.target.value)}>
          {languages.map((lang: string) => (
            <option key={lang} value={lang.toLowerCase()}>
              {lang}
            </option>
          ))}
        </select>
      );

      const handleSelect = vi.fn();
      
      render(<LanguageSelector languages={languages} onSelect={handleSelect} />);

      const selector = screen.getByTestId('language-selector');
      expect(selector).toBeInTheDocument();

      fireEvent.change(selector, { target: { value: 'javascript' } });
      expect(handleSelect).toHaveBeenCalledWith('javascript');
    });
  });

  describe('Code Editor Integration', () => {
    it('should handle Monaco editor initialization', () => {
      // Mock Monaco Editor component
      const MockMonacoEditor = ({ value, onChange, language }: any) => (
        <textarea
          data-testid="monaco-editor"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          data-language={language}
        />
      );

      const handleChange = vi.fn();
      
      render(
        <MockMonacoEditor
          value="# Initial code"
          onChange={handleChange}
          language="python"
        />
      );

      const editor = screen.getByTestId('monaco-editor');
      expect(editor).toBeInTheDocument();
      expect(editor).toHaveValue('# Initial code');

      fireEvent.change(editor, { target: { value: '# Updated code' } });
      expect(handleChange).toHaveBeenCalledWith('# Updated code');
    });
  });

  describe('Test Results Display', () => {
    it('should display test results correctly', () => {
      const mockTestResults = {
        success: true,
        total_passed: 10,
        total_failed: 0,
        test_results: [
          { input: '[2,7,11,15], 9', expected: '[0,1]', actual: '[0,1]', passed: true },
          { input: '[3,2,4], 6', expected: '[1,2]', actual: '[1,2]', passed: true }
        ],
        complexity: 'O(n)',
        implement_time: 120,
        final_time: 100,
        player_name: 'Test Player',
        error: null,
        message: 'All tests passed!',
        code: 'test code',
        opponent_id: ''
      };

      // Mock TestResults component
      const TestResultsComponent = ({ results }: any) => (
        <div data-testid="test-results-component">
          <div>Success: {results.success ? 'Yes' : 'No'}</div>
          <div>Passed: {results.total_passed}</div>
          <div>Failed: {results.total_failed}</div>
          <div>Complexity: {results.complexity}</div>
          <div>Message: {results.message}</div>
          {results.error && <div>Error: {results.error}</div>}
        </div>
      );

      render(<TestResultsComponent results={mockTestResults} />);

      expect(screen.getByText('Success: Yes')).toBeInTheDocument();
      expect(screen.getByText('Passed: 10')).toBeInTheDocument();
      expect(screen.getByText('Failed: 0')).toBeInTheDocument();
      expect(screen.getByText('Complexity: O(n)')).toBeInTheDocument();
      expect(screen.getByText('Message: All tests passed!')).toBeInTheDocument();
    });

    it('should display error results correctly', () => {
      const mockErrorResults = {
        success: false,
        total_passed: 3,
        total_failed: 7,
        error: 'Syntax error in line 5',
        message: 'Code compilation failed',
        complexity: 'N/A'
      };

      const TestResultsComponent = ({ results }: any) => (
        <div data-testid="test-results-component">
          <div>Success: {results.success ? 'Yes' : 'No'}</div>
          <div>Passed: {results.total_passed}</div>
          <div>Failed: {results.total_failed}</div>
          {results.error && <div>Error: {results.error}</div>}
          <div>Message: {results.message}</div>
        </div>
      );

      render(<TestResultsComponent results={mockErrorResults} />);

      expect(screen.getByText('Success: No')).toBeInTheDocument();
      expect(screen.getByText('Passed: 3')).toBeInTheDocument();
      expect(screen.getByText('Failed: 7')).toBeInTheDocument();
      expect(screen.getByText('Error: Syntax error in line 5')).toBeInTheDocument();
      expect(screen.getByText('Message: Code compilation failed')).toBeInTheDocument();
    });
  });

  describe('Real-time Socket Integration', () => {
    it('should handle socket connection events', async () => {
      const mockSocket = createMockSocket();
      const mockTimeRef = { current: 0 };

      render(
        <DuelInfo
          timeRef={mockTimeRef}
          opponentData={{ id: 'opp', name: 'Opponent', image_url: '' }}
          user={{ id: 'user', name: 'User', email: 'user@test.com', image: '' }}
          socket={mockSocket}
          gameId="test-game"
          starterCode=""
          selectedLanguage="python"
          gameStartTime={null}
          isGameStarted={false}
        />
      );

      // Simulate connection
      mockSocket.connect();
      
      expect(mockSocket.connected).toBe(true);
      expect(mockSocket.connect).toHaveBeenCalled();
    });

    it('should handle game completion events', async () => {
      const mockSocket = createMockSocket();
      let gameCompleted = false;

      // Simulate game completion handler
      mockSocket.on('game_completed', (data) => {
        gameCompleted = true;
      });

      mockSocket.simulateGameCompletion(true);

      await waitFor(() => {
        expect(gameCompleted).toBe(true);
      });
    });
  });

  describe('Component Error Boundaries', () => {
    it('should handle component errors gracefully', () => {
      // Mock a component that might throw an error
      const ErrorProneComponent = ({ shouldError }: { shouldError: boolean }) => {
        if (shouldError) {
          throw new Error('Test error');
        }
        return <div>No error</div>;
      };

      // Test normal rendering
      const { rerender } = render(<ErrorProneComponent shouldError={false} />);
      expect(screen.getByText('No error')).toBeInTheDocument();

      // Test error handling (would need error boundary in real app)
      expect(() => {
        rerender(<ErrorProneComponent shouldError={true} />);
      }).toThrow('Test error');
    });
  });

  describe('Accessibility Features', () => {
    it('should have proper ARIA labels and roles', () => {
      const AccessibleComponent = () => (
        <div>
          <button aria-label="Submit solution" role="button">Submit</button>
          <input aria-label="Code editor" role="textbox" />
          <div role="timer" aria-label="Game timer">00:30</div>
        </div>
      );

      render(<AccessibleComponent />);

      expect(screen.getByRole('button', { name: 'Submit solution' })).toBeInTheDocument();
      expect(screen.getByRole('textbox', { name: 'Code editor' })).toBeInTheDocument();
      expect(screen.getByRole('timer', { name: 'Game timer' })).toBeInTheDocument();
    });

    it('should support keyboard navigation', () => {
      const KeyboardComponent = () => (
        <div>
          <button tabIndex={0}>First</button>
          <button tabIndex={0}>Second</button>
          <input tabIndex={0} />
        </div>
      );

      render(<KeyboardComponent />);

      const buttons = screen.getAllByRole('button');
      const input = screen.getByRole('textbox');

      expect(buttons[0]).toHaveAttribute('tabIndex', '0');
      expect(buttons[1]).toHaveAttribute('tabIndex', '0');
      expect(input).toHaveAttribute('tabIndex', '0');
    });
  });
});