import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '../utils/test-utils';
import FinishedPage from '@/components/FinishedPage';
import type { OpponentData, CustomUser } from '@/shared/types';

// Mock next-themes
vi.mock('next-themes', () => ({
  useTheme: () => ({
    theme: 'dark',
    setTheme: vi.fn(),
    resolvedTheme: 'dark'
  })
}));

describe('FinishedPage Component', () => {
  const mockOpponent: OpponentData = {
    id: 'opponent-123',
    name: 'Test Opponent',
    image_url: 'https://via.placeholder.com/150'
  };

  const mockUser: CustomUser = {
    id: 'user-123',
    name: 'Test User',
    email: 'test@example.com',
    image: 'https://via.placeholder.com/150'
  };

  const mockUserWinGameEndData = {
    message: 'Test User won the game!',
    winner_id: 'user-123',
    winner_name: 'Test User',
    loser_id: 'opponent-123',
    loser_name: 'Test Opponent',
    game_end_reason: 'first_win',
    game_end_time: Date.now() / 1000,
    winner_stats: {
      player_name: 'Test User',
      implement_time: 120,
      complexity: 'O(n)',
      final_time: 80,
      success: true
    }
  };

  const mockOpponentWinGameEndData = {
    message: 'Test Opponent won the game!',
    winner_id: 'opponent-123',
    winner_name: 'Test Opponent',
    loser_id: 'user-123',
    loser_name: 'Test User',
    game_end_reason: 'first_win',
    game_end_time: Date.now() / 1000,
    winner_stats: {
      player_name: 'Test Opponent',
      implement_time: 95,
      complexity: 'O(n)',
      final_time: 65,
      success: true
    }
  };

  describe('User Wins Scenario', () => {
    it('should display congratulations when user wins', () => {
      render(
        <FinishedPage
          opponent={mockOpponent}
          user={mockUser}
          gameEndData={mockUserWinGameEndData}
        />
      );

      expect(screen.getByText('Game Complete')).toBeInTheDocument();
      expect(screen.getByText('Congratulations! You won!')).toBeInTheDocument();
      expect(screen.getByText('Winner')).toBeInTheDocument();
      expect(screen.getByText('Test User')).toBeInTheDocument();
    });

    it('should show correct winner and loser cards', () => {
      render(
        <FinishedPage
          opponent={mockOpponent}
          user={mockUser}
          gameEndData={mockUserWinGameEndData}
        />
      );

      // Check winner section
      expect(screen.getByText('Winner')).toBeInTheDocument();
      expect(screen.getByText('Test User')).toBeInTheDocument();
      
      // Check loser section
      expect(screen.getByText('Loser')).toBeInTheDocument();
      expect(screen.getByText('Test Opponent')).toBeInTheDocument();
    });

    it('should display winner stats correctly', () => {
      render(
        <FinishedPage
          opponent={mockOpponent}
          user={mockUser}
          gameEndData={mockUserWinGameEndData}
        />
      );

      expect(screen.getByText('O(n)')).toBeInTheDocument();
      expect(screen.getByText('80')).toBeInTheDocument();
    });
  });

  describe('User Loses Scenario', () => {
    it('should display appropriate message when user loses', () => {
      render(
        <FinishedPage
          opponent={mockOpponent}
          user={mockUser}
          gameEndData={mockOpponentWinGameEndData}
        />
      );

      expect(screen.getByText('Game Complete')).toBeInTheDocument();
      expect(screen.getByText('Great effort! Better luck next time!')).toBeInTheDocument();
    });

    it('should show opponent as winner when user loses', () => {
      render(
        <FinishedPage
          opponent={mockOpponent}
          user={mockUser}
          gameEndData={mockOpponentWinGameEndData}
        />
      );

      // Winner should be opponent
      const winnerSection = screen.getByText('Winner').parentElement?.parentElement;
      expect(winnerSection).toHaveTextContent('Test Opponent');

      // Loser should be user
      const loserSection = screen.getByText('Loser').parentElement?.parentElement;
      expect(loserSection).toHaveTextContent('Test User');
    });
  });

  describe('Game End Reasons', () => {
    it('should display "First to Solve" for first_win reason', () => {
      render(
        <FinishedPage
          opponent={mockOpponent}
          user={mockUser}
          gameEndData={mockUserWinGameEndData}
        />
      );

      expect(screen.getByText('First to Solve')).toBeInTheDocument();
    });

    it('should handle disconnection scenario', () => {
      const disconnectionGameEndData = {
        ...mockUserWinGameEndData,
        game_end_reason: 'disconnection',
        message: 'You won! Opponent disconnected.'
      };

      render(
        <FinishedPage
          opponent={mockOpponent}
          user={mockUser}
          gameEndData={disconnectionGameEndData}
        />
      );

      expect(screen.getByText('Game Complete')).toBeInTheDocument();
      expect(screen.getByText('Winner')).toBeInTheDocument();
    });
  });

  describe('Incomplete Player Scenarios', () => {
    it('should handle when loser did not complete the challenge', () => {
      const incompleteGameEndData = {
        ...mockUserWinGameEndData,
        // No loser stats provided
      };

      render(
        <FinishedPage
          opponent={mockOpponent}
          user={mockUser}
          gameEndData={incompleteGameEndData}
        />
      );

      expect(screen.getByText('Winner')).toBeInTheDocument();
      expect(screen.getByText('Loser')).toBeInTheDocument();
      expect(screen.getByText("Didn't complete")).toBeInTheDocument();
    });

    it('should show "Player didn\'t complete the challenge" when no stats available', () => {
      const noStatsGameEndData = {
        ...mockOpponentWinGameEndData,
        winner_stats: undefined
      };

      render(
        <FinishedPage
          opponent={mockOpponent}
          user={mockUser}
          gameEndData={noStatsGameEndData}
          userStats={undefined}
        />
      );

      expect(screen.getByText("Player didn't complete the challenge")).toBeInTheDocument();
    });
  });

  describe('Navigation Buttons', () => {
    it('should render "Back to Main Menu" button', () => {
      render(
        <FinishedPage
          opponent={mockOpponent}
          user={mockUser}
          gameEndData={mockUserWinGameEndData}
        />
      );

      const mainMenuButton = screen.getByRole('button', { name: /back to main menu/i });
      expect(mainMenuButton).toBeInTheDocument();
    });

    it('should render "Play Again" button', () => {
      render(
        <FinishedPage
          opponent={mockOpponent}
          user={mockUser}
          gameEndData={mockUserWinGameEndData}
        />
      );

      const playAgainButton = screen.getByRole('button', { name: /play again/i });
      expect(playAgainButton).toBeInTheDocument();
    });
  });

  describe('Match Statistics Section', () => {
    it('should display match statistics', () => {
      render(
        <FinishedPage
          opponent={mockOpponent}
          user={mockUser}
          gameEndData={mockUserWinGameEndData}
        />
      );

      expect(screen.getByText('Match Statistics')).toBeInTheDocument();
      expect(screen.getByText('Game Result')).toBeInTheDocument();
      expect(screen.getByText('Winner\'s Complexity')).toBeInTheDocument();
      expect(screen.getByText('Winner\'s Time')).toBeInTheDocument();
    });

    it('should show correct winner complexity and time in stats', () => {
      render(
        <FinishedPage
          opponent={mockOpponent}
          user={mockUser}
          gameEndData={mockUserWinGameEndData}
        />
      );

      // Should show winner's stats
      const statsSections = screen.getAllByText('O(n)');
      expect(statsSections.length).toBeGreaterThan(0);
      
      expect(screen.getByText('80s')).toBeInTheDocument();
    });
  });

  describe('Visual Elements', () => {
    it('should display trophy icons', () => {
      render(
        <FinishedPage
          opponent={mockOpponent}
          user={mockUser}
          gameEndData={mockUserWinGameEndData}
        />
      );

      // Trophy icons should be present in the header and cards
      const trophyElements = document.querySelectorAll('[data-testid*="trophy"], .lucide-trophy');
      expect(trophyElements.length).toBeGreaterThan(0);
    });

    it('should display user and opponent avatars', () => {
      render(
        <FinishedPage
          opponent={mockOpponent}
          user={mockUser}
          gameEndData={mockUserWinGameEndData}
        />
      );

      const avatars = screen.getAllByRole('img');
      expect(avatars.length).toBeGreaterThanOrEqual(2); // At least winner and loser avatars
    });
  });

  describe('Edge Cases', () => {
    it('should handle missing game end data gracefully', () => {
      render(
        <FinishedPage
          opponent={mockOpponent}
          user={mockUser}
          gameEndData={null as any}
        />
      );

      // Should still render the basic structure
      expect(screen.getByText('Game Complete')).toBeInTheDocument();
    });

    it('should handle missing user data', () => {
      render(
        <FinishedPage
          opponent={mockOpponent}
          user={null}
          gameEndData={mockUserWinGameEndData}
        />
      );

      expect(screen.getByText('Game Complete')).toBeInTheDocument();
    });

    it('should handle missing opponent data', () => {
      render(
        <FinishedPage
          opponent={null as any}
          user={mockUser}
          gameEndData={mockUserWinGameEndData}
        />
      );

      expect(screen.getByText('Game Complete')).toBeInTheDocument();
    });
  });

  describe('Performance Stats Display', () => {
    it('should show N/A when stats are missing', () => {
      const noStatsGameEndData = {
        ...mockUserWinGameEndData,
        winner_stats: {
          player_name: 'Test User',
          success: true
        }
      };

      render(
        <FinishedPage
          opponent={mockOpponent}
          user={mockUser}
          gameEndData={noStatsGameEndData}
        />
      );

      const naElements = screen.getAllByText('N/A');
      expect(naElements.length).toBeGreaterThan(0);
    });

    it('should format time correctly', () => {
      render(
        <FinishedPage
          opponent={mockOpponent}
          user={mockUser}
          gameEndData={mockUserWinGameEndData}
        />
      );

      // Should show time with 's' suffix in stats section
      expect(screen.getByText('80s')).toBeInTheDocument();
    });
  });
});