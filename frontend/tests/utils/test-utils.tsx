import React, { ReactElement } from 'react';
import { render, RenderOptions } from '@testing-library/react';
import { vi } from 'vitest';
import { createMockSocket } from '../mocks/socket-mock';
import { createMockGameContext, type MockGameContext } from '../mocks/game-context-mock';

// Mock Next.js specific modules
vi.mock('next/navigation', () => ({
  useRouter: vi.fn(() => ({
    push: vi.fn(),
    replace: vi.fn(),
    pathname: '/',
    searchParams: new URLSearchParams(),
  })),
  useParams: vi.fn(() => ({ questionName: 'two-sum' })),
  useSearchParams: vi.fn(() => new URLSearchParams()),
  usePathname: vi.fn(() => '/'),
}));

vi.mock('next-themes', () => ({
  useTheme: vi.fn(() => ({
    theme: 'dark',
    setTheme: vi.fn(),
    resolvedTheme: 'dark'
  }))
}));

// Mock auth client
vi.mock('@/lib/auth-client', () => ({
  useSession: vi.fn(() => ({
    data: {
      user: {
        id: 'test-user-123',
        name: 'Test User',
        email: 'test@example.com',
        image: 'https://via.placeholder.com/150'
      }
    }
  })),
  getAvatarUrl: vi.fn(() => 'https://via.placeholder.com/150')
}));

// Custom render function with providers
interface CustomRenderOptions extends Omit<RenderOptions, 'wrapper'> {
  gameContext?: Partial<MockGameContext>;
  withSocket?: boolean;
}

function customRender(
  ui: ReactElement,
  options: CustomRenderOptions = {}
) {
  const { gameContext = {}, withSocket = false, ...renderOptions } = options;

  // Create mock context with socket if requested
  const mockContext = createMockGameContext({
    ...gameContext,
    socket: withSocket ? createMockSocket() : gameContext.socket
  });

  // Mock the game context hook
  vi.mocked(require('../mocks/game-context-mock').mockUseGameContext).mockReturnValue(mockContext);

  return render(ui, renderOptions);
}

// Utility functions for testing
export const waitFor = (condition: () => boolean, timeout: number = 5000): Promise<void> => {
  return new Promise((resolve, reject) => {
    const startTime = Date.now();
    const check = () => {
      if (condition()) {
        resolve();
      } else if (Date.now() - startTime > timeout) {
        reject(new Error('Timeout waiting for condition'));
      } else {
        setTimeout(check, 100);
      }
    };
    check();
  });
};

export const sleep = (ms: number): Promise<void> => {
  return new Promise(resolve => setTimeout(resolve, ms));
};

// Helper to simulate typing in Monaco Editor
export const simulateMonacoTyping = (container: HTMLElement, text: string) => {
  // Monaco editor is complex to mock, so we'll simulate by finding textarea
  const textareas = container.querySelectorAll('textarea');
  const textarea = textareas[0]; // Monaco usually creates a hidden textarea
  
  if (textarea) {
    textarea.value = text;
    textarea.dispatchEvent(new Event('input', { bubbles: true }));
  }
};

// Helper to wait for socket events
export const waitForSocketEvent = (socket: any, event: string, timeout: number = 5000): Promise<any> => {
  return new Promise((resolve, reject) => {
    const timer = setTimeout(() => {
      reject(new Error(`Timeout waiting for socket event: ${event}`));
    }, timeout);

    socket.on(event, (data: any) => {
      clearTimeout(timer);
      resolve(data);
    });
  });
};

// Game flow simulation helpers
export const simulateCompleteGameFlow = async (
  socket: any,
  questionName: string = 'two-sum',
  userWins: boolean = true
) => {
  // Simulate match found
  socket.simulateMatchFound(
    { name: 'Test Opponent', image_url: 'https://via.placeholder.com/150' },
    questionName
  );
  await sleep(1100);

  // Simulate game join
  socket.simulateGameJoin();
  await sleep(600);

  // Simulate game start
  socket.simulateGameStart();
  await sleep(2100);

  // Simulate opponent activity
  if (!userWins) {
    socket.simulateOpponentSubmission(true); // Opponent wins
  } else {
    socket.simulateOpponentSubmission(false); // Opponent loses
  }

  // Simulate game completion
  setTimeout(() => {
    socket.simulateGameCompletion(userWins);
  }, userWins ? 5000 : 1000);
};

// Re-export everything from testing-library
export * from '@testing-library/react';
export { customRender as render };

export default customRender;