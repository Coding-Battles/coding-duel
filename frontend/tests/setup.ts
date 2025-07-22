import '@testing-library/jest-dom'
import { afterEach, beforeAll, afterAll } from 'vitest'
import { cleanup } from '@testing-library/react'
import { setupServer } from 'msw/node'
import apiHandlers from './mocks/api-mock'

// Setup MSW server for API mocking
export const server = setupServer(...apiHandlers)

// Start server before all tests
beforeAll(() => {
  server.listen({ onUnhandledRequest: 'error' })
})

// Reset handlers after each test
afterEach(() => {
  cleanup()
  server.resetHandlers()
})

// Close server after all tests
afterAll(() => {
  server.close()
})

// Mock Next.js router
vi.mock('next/router', () => ({
  useRouter: () => ({
    push: vi.fn(),
    replace: vi.fn(),
    pathname: '/',
    query: {},
    asPath: '/',
  }),
}))

// Mock Next.js navigation
vi.mock('next/navigation', () => ({
  useRouter: () => ({
    push: vi.fn(),
    replace: vi.fn(),
    pathname: '/',
    searchParams: new URLSearchParams(),
  }),
  useParams: () => ({ questionName: 'two-sum' }),
  useSearchParams: () => new URLSearchParams(),
  usePathname: () => '/',
}))

// Mock Socket.IO
vi.mock('socket.io-client', () => ({
  io: vi.fn(() => {
    const { createMockSocket } = require('./mocks/socket-mock')
    return createMockSocket()
  })
}))

// Mock Monaco Editor
vi.mock('@monaco-editor/react', () => ({
  default: ({ onChange, value, onMount }: any) => {
    return React.createElement('textarea', {
      'data-testid': 'monaco-editor',
      value: value || '',
      onChange: (e: any) => onChange?.(e.target.value),
      ref: (el: HTMLTextAreaElement) => onMount?.(el, {})
    })
  }
}))

// Mock environment variables
process.env.NEXT_PUBLIC_API_BASE_URL = 'http://localhost:8000'
process.env.NEXT_PUBLIC_BETTER_AUTH_URL = 'http://localhost:3000'