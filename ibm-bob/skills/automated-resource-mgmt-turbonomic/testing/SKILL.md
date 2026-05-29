---
name: testing
description: Comprehensive testing strategies covering unit, integration, and end-to-end testing with Jest, React Testing Library, and Cypress
---

# Testing Skill

Use this skill when writing tests, setting up testing infrastructure, ensuring code quality through automated testing, or implementing test-driven development.

## When to Use This Skill

- Writing unit tests for components or functions
- Creating integration tests for API endpoints
- Setting up end-to-end tests with Cypress
- Configuring test coverage requirements
- Implementing test-driven development (TDD)
- Setting up CI/CD test automation
- Debugging failing tests

## Core Technologies

- **Jest** - Test runner and assertion library
- **React Testing Library** - Component testing
- **Supertest** - HTTP assertion for backend
- **MSW (Mock Service Worker)** - API mocking
- **Cypress** - End-to-end testing

## Testing Philosophy

### Testing Pyramid
```
        /\
       /  \
      / E2E \          Few - Slow - Expensive
     /______\
    /        \
   /Integration\      Some - Medium - Moderate
  /____________\
 /              \
/  Unit Tests    \    Many - Fast - Cheap
/__________________\
```

### Key Principles

1. **Test Behavior, Not Implementation** - Focus on what, not how
2. **Keep Tests Simple** - One assertion per test when possible
3. **Make Tests Independent** - No test should depend on another
4. **Write Tests First** - Test-Driven Development (TDD)
5. **Maintain Tests** - Update tests when code changes

## Quick Reference

### Frontend Component Test
```javascript
import { render, screen, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MyComponent } from './MyComponent';

describe('MyComponent', () => {
  test('renders without crashing', () => {
    render(<MyComponent />);
    expect(screen.getByText(/expected text/i)).toBeInTheDocument();
  });

  test('handles user interaction', async () => {
    const user = userEvent.setup();
    render(<MyComponent />);
    
    const button = screen.getByRole('button', { name: /submit/i });
    await user.click(button);
    
    expect(screen.getByText(/success/i)).toBeInTheDocument();
  });

  test('displays error state', () => {
    render(<MyComponent error="Error message" />);
    expect(screen.getByText(/error message/i)).toBeInTheDocument();
  });
});
```

### Backend API Test
```javascript
const request = require('supertest');
const app = require('../src/server');

describe('API Endpoints', () => {
  describe('GET /health', () => {
    test('returns healthy status', async () => {
      const response = await request(app).get('/health');
      
      expect(response.status).toBe(200);
      expect(response.body).toHaveProperty('status', 'healthy');
    });
  });

  describe('POST /api/data', () => {
    test('creates new data', async () => {
      const newData = { name: 'Test', value: 123 };
      
      const response = await request(app)
        .post('/api/data')
        .send(newData);
      
      expect(response.status).toBe(201);
      expect(response.body).toMatchObject(newData);
    });

    test('validates required fields', async () => {
      const response = await request(app)
        .post('/api/data')
        .send({});
      
      expect(response.status).toBe(400);
      expect(response.body).toHaveProperty('error');
    });
  });
});
```

### Integration Test with MSW
```javascript
import { render, screen, waitFor } from '@testing-library/react';
import { rest } from 'msw';
import { setupServer } from 'msw/node';
import App from './App';

const server = setupServer(
  rest.get('/api/data', (req, res, ctx) => {
    return res(ctx.json([
      { id: 1, name: 'Item 1' },
      { id: 2, name: 'Item 2' }
    ]));
  })
);

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

describe('App Integration', () => {
  test('loads and displays data', async () => {
    render(<App />);
    
    await waitFor(() => {
      expect(screen.getByText('Item 1')).toBeInTheDocument();
      expect(screen.getByText('Item 2')).toBeInTheDocument();
    });
  });

  test('handles API errors', async () => {
    server.use(
      rest.get('/api/data', (req, res, ctx) => {
        return res(ctx.status(500));
      })
    );
    
    render(<App />);
    
    await waitFor(() => {
      expect(screen.getByText(/error/i)).toBeInTheDocument();
    });
  });
});
```

### Cypress E2E Test
```javascript
describe('User Journey', () => {
  beforeEach(() => {
    cy.visit('/');
  });

  it('completes full workflow', () => {
    // Navigate to form
    cy.contains('Get Started').click();
    
    // Fill in form
    cy.get('input[name="email"]').type('user@example.com');
    cy.get('input[name="password"]').type('password123');
    
    // Submit form
    cy.get('button[type="submit"]').click();
    
    // Verify success
    cy.contains('Welcome').should('be.visible');
    cy.url().should('include', '/dashboard');
  });

  it('validates form inputs', () => {
    cy.contains('Get Started').click();
    cy.get('button[type="submit"]').click();
    
    cy.contains('Email is required').should('be.visible');
  });
});
```

## Common Testing Patterns

### Testing Hooks
```javascript
import { renderHook, act } from '@testing-library/react';
import { useCounter } from './useCounter';

describe('useCounter', () => {
  test('initializes with default value', () => {
    const { result } = renderHook(() => useCounter());
    expect(result.current.count).toBe(0);
  });

  test('increments counter', () => {
    const { result } = renderHook(() => useCounter());
    
    act(() => {
      result.current.increment();
    });
    
    expect(result.current.count).toBe(1);
  });
});
```

### Testing Async Operations
```javascript
test('fetches data successfully', async () => {
  render(<DataComponent />);
  
  // Wait for loading to finish
  await waitFor(() => {
    expect(screen.queryByText(/loading/i)).not.toBeInTheDocument();
  });
  
  // Verify data is displayed
  expect(screen.getByText('Data loaded')).toBeInTheDocument();
});
```

### Mocking External Services
```javascript
const nock = require('nock');

describe('External API', () => {
  afterEach(() => {
    nock.cleanAll();
  });

  test('calls external API', async () => {
    nock('https://api.example.com')
      .get('/data')
      .reply(200, { result: 'success' });
    
    const result = await fetchExternalData();
    expect(result).toEqual({ result: 'success' });
  });
});
```

## Test Coverage Configuration

### Jest Configuration
```javascript
// jest.config.js
module.exports = {
  testEnvironment: 'jsdom',
  setupFilesAfterEnv: ['<rootDir>/jest.setup.js'],
  collectCoverageFrom: [
    'src/**/*.{js,jsx}',
    '!src/index.js',
    '!src/**/*.test.{js,jsx}',
    '!src/**/__tests__/**'
  ],
  coverageThresholds: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80
    }
  }
};
```

### Running Tests
```bash
# Run all tests
npm test

# Run with coverage
npm test -- --coverage

# Run specific test file
npm test -- MyComponent.test.js

# Run in watch mode
npm test -- --watch

# Update snapshots
npm test -- -u
```

## CI/CD Integration

### GitHub Actions Example
```yaml
name: Test

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'npm'
      
      - name: Install dependencies
        run: npm ci
      
      - name: Run tests
        run: npm test -- --coverage
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage/lcov.info
```

## Test Organization

### File Structure
```
src/
├── components/
│   ├── MyComponent.jsx
│   └── __tests__/
│       └── MyComponent.test.jsx
├── services/
│   ├── api.js
│   └── __tests__/
│       └── api.test.js
└── utils/
    ├── helpers.js
    └── __tests__/
        └── helpers.test.js
```

### Naming Conventions
```javascript
// Unit tests
describe('ComponentName', () => {
  describe('methodName', () => {
    test('should do something when condition', () => {
      // Test implementation
    });
  });
});

// Integration tests
describe('Feature Integration', () => {
  test('completes user workflow successfully', () => {
    // Test implementation
  });
});

// E2E tests
describe('User Journey', () => {
  it('allows user to complete task', () => {
    // Test implementation
  });
});
```

## Supporting Documentation

Refer to the following files in this skill folder for detailed guidance:
- `unit-testing.md` - Unit testing patterns and examples
- `integration-testing.md` - Integration testing strategies
- `e2e-testing.md` - End-to-end testing with Cypress
- `mocking.md` - Mocking strategies and patterns
- `coverage.md` - Test coverage requirements and tools

## Best Practices

### DO ✅
- Write tests before code (TDD)
- Test behavior, not implementation
- Use descriptive test names
- Keep tests simple and focused
- Mock external dependencies
- Test edge cases and errors
- Maintain high test coverage (>80%)
- Run tests automatically in CI/CD
- Use fixtures for test data
- Clean up after tests

### DON'T ❌
- Test implementation details
- Write tests that depend on each other
- Skip error cases
- Use real API calls in tests
- Ignore failing tests
- Write overly complex tests
- Test third-party libraries
- Hardcode test data
- Skip integration tests
- Forget to update tests when code changes

## Troubleshooting

### Common Issues

**Tests timing out:**
```javascript
// Increase timeout for slow tests
test('slow operation', async () => {
  // Test code
}, 10000); // 10 second timeout
```

**Async tests not waiting:**
```javascript
// Use waitFor for async operations
await waitFor(() => {
  expect(screen.getByText('Loaded')).toBeInTheDocument();
});
```

**Mock not working:**
```javascript
// Reset mocks between tests
afterEach(() => {
  jest.clearAllMocks();
});
```

## Resources

- [Jest Documentation](https://jestjs.io/)
- [React Testing Library](https://testing-library.com/react)
- [Cypress Documentation](https://docs.cypress.io/)
- [Testing Best Practices](https://testingjavascript.com/)
- [Test-Driven Development](https://martinfowler.com/bliki/TestDrivenDevelopment.html)