# Testing Standards

## Overview
This skill provides comprehensive testing standards for the Turbonomic Resource Dashboard, covering unit testing, integration testing, end-to-end testing, and quality assurance practices.

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

### Testing Principles

1. **Write Tests First** - Test-Driven Development (TDD)
2. **Test Behavior, Not Implementation** - Focus on what, not how
3. **Keep Tests Simple** - One assertion per test when possible
4. **Make Tests Independent** - No test should depend on another
5. **Use Descriptive Names** - Test names should explain what they test
6. **Maintain Tests** - Update tests when code changes
7. **Automate Everything** - Run tests automatically in CI/CD
8. **Test Edge Cases** - Don't just test happy paths

## Testing Stack

### Frontend Testing
- **Jest** - Test runner and assertion library
- **React Testing Library** - Component testing
- **MSW (Mock Service Worker)** - API mocking
- **Cypress** - End-to-end testing

### Backend Testing
- **Jest** - Test runner
- **Supertest** - HTTP assertion library
- **Nock** - HTTP mocking

### Installation
```bash
# Frontend
npm install --save-dev jest @testing-library/react @testing-library/jest-dom @testing-library/user-event msw

# Backend
npm install --save-dev jest supertest nock
```

## Unit Testing

### Frontend Component Tests

#### Basic Component Test
```javascript
import { render, screen } from '@testing-library/react';
import { TurbonomicOverview } from './TurbonomicOverview';

describe('TurbonomicOverview', () => {
  test('renders without crashing', () => {
    render(<TurbonomicOverview entities={[]} actions={[]} targets={[]} />);
    expect(screen.getByText(/Entity Distribution/i)).toBeInTheDocument();
  });

  test('displays loading state', () => {
    render(<TurbonomicOverview loading={true} />);
    expect(screen.getByText(/Loading overview data/i)).toBeInTheDocument();
  });

  test('displays empty state when no data', () => {
    render(<TurbonomicOverview entities={[]} actions={[]} targets={[]} />);
    expect(screen.getByText(/No entity data available/i)).toBeInTheDocument();
  });

  test('displays metric cards with correct values', () => {
    const entities = [{ id: 1 }, { id: 2 }, { id: 3 }];
    const actions = [{ id: 1 }, { id: 2 }];
    const targets = [{ id: 1 }];

    render(
      <TurbonomicOverview 
        entities={entities} 
        actions={actions} 
        targets={targets} 
      />
    );

    expect(screen.getByText('3')).toBeInTheDocument(); // Total entities
    expect(screen.getByText('2')).toBeInTheDocument(); // Pending actions
    expect(screen.getByText('1')).toBeInTheDocument(); // Configured targets
  });
});
```

#### Testing User Interactions
```javascript
import { render, screen, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import App from './App';

describe('App User Interactions', () => {
  test('expands configuration section when clicked', async () => {
    const user = userEvent.setup();
    render(<App />);

    const expandButton = screen.getByText(/Turbonomic Configuration/i);
    await user.click(expandButton);

    expect(screen.getByLabelText(/Turbonomic Host/i)).toBeVisible();
  });

  test('loads data when button clicked', async () => {
    const user = userEvent.setup();
    render(<App />);

    const hostInput = screen.getByLabelText(/Turbonomic Host/i);
    const usernameInput = screen.getByLabelText(/Username/i);
    const passwordInput = screen.getByLabelText(/Password/i);
    const loadButton = screen.getByText(/Load Data/i);

    await user.type(hostInput, 'https://test.com');
    await user.type(usernameInput, 'admin');
    await user.type(passwordInput, 'password');
    await user.click(loadButton);

    expect(screen.getByText(/Loading/i)).toBeInTheDocument();
  });

  test('displays error message on failed load', async () => {
    const user = userEvent.setup();
    render(<App />);

    const loadButton = screen.getByText(/Load Data/i);
    await user.click(loadButton);

    expect(screen.getByText(/Please configure Turbonomic credentials/i)).toBeInTheDocument();
  });
});
```

#### Testing Hooks
```javascript
import { renderHook, act } from '@testing-library/react';
import { useDataFetching } from './useDataFetching';

describe('useDataFetching', () => {
  test('initializes with loading false', () => {
    const { result } = renderHook(() => useDataFetching());
    expect(result.current.loading).toBe(false);
  });

  test('sets loading true when fetching', async () => {
    const { result } = renderHook(() => useDataFetching());

    act(() => {
      result.current.fetchData();
    });

    expect(result.current.loading).toBe(true);
  });

  test('handles errors correctly', async () => {
    const { result } = renderHook(() => useDataFetching());

    await act(async () => {
      await result.current.fetchData();
    });

    expect(result.current.error).toBeTruthy();
  });
});
```

### Backend Unit Tests

#### API Endpoint Tests
```javascript
const request = require('supertest');
const app = require('../src/server');

describe('Turbonomic API Endpoints', () => {
  describe('GET /health', () => {
    test('returns healthy status', async () => {
      const response = await request(app).get('/health');
      
      expect(response.status).toBe(200);
      expect(response.body).toHaveProperty('status', 'healthy');
      expect(response.body).toHaveProperty('timestamp');
    });
  });

  describe('POST /api/turbonomic/actions', () => {
    test('returns 400 when credentials missing', async () => {
      const response = await request(app)
        .post('/api/turbonomic/actions')
        .send({});
      
      expect(response.status).toBe(400);
      expect(response.body).toHaveProperty('error');
      expect(response.body.error).toContain('credentials');
    });

    test('returns actions when credentials valid', async () => {
      const response = await request(app)
        .post('/api/turbonomic/actions')
        .send({
          turboHost: 'https://test.com',
          turboUsername: 'admin',
          turboPassword: 'password'
        });
      
      expect(response.status).toBe(200);
      expect(Array.isArray(response.body)).toBe(true);
    });

    test('handles API errors gracefully', async () => {
      const response = await request(app)
        .post('/api/turbonomic/actions')
        .send({
          turboHost: 'https://invalid.com',
          turboUsername: 'admin',
          turboPassword: 'wrong'
        });
      
      expect(response.status).toBe(500);
      expect(response.body).toHaveProperty('error');
    });
  });
});
```

#### Service Layer Tests
```javascript
const turbonomicProxy = require('../src/turbonomic-proxy');
const nock = require('nock');

describe('Turbonomic Proxy Service', () => {
  afterEach(() => {
    nock.cleanAll();
  });

  describe('getPendingActions', () => {
    test('fetches actions successfully', async () => {
      const mockActions = [
        { uuid: '123', actionType: 'RESIZE' },
        { uuid: '456', actionType: 'MOVE' }
      ];

      nock('https://test.com')
        .post('/api/v3/actions')
        .reply(200, mockActions);

      const actions = await turbonomicProxy.getPendingActions(
        'https://test.com',
        'admin',
        'password'
      );

      expect(actions).toEqual(mockActions);
      expect(actions).toHaveLength(2);
    });

    test('throws error on API failure', async () => {
      nock('https://test.com')
        .post('/api/v3/actions')
        .reply(500, { message: 'Internal server error' });

      await expect(
        turbonomicProxy.getPendingActions(
          'https://test.com',
          'admin',
          'password'
        )
      ).rejects.toThrow();
    });

    test('handles network errors', async () => {
      nock('https://test.com')
        .post('/api/v3/actions')
        .replyWithError('Network error');

      await expect(
        turbonomicProxy.getPendingActions(
          'https://test.com',
          'admin',
          'password'
        )
      ).rejects.toThrow('Network error');
    });
  });
});
```

## Integration Testing

### API Integration Tests
```javascript
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { rest } from 'msw';
import { setupServer } from 'msw/node';
import App from './App';

// Setup MSW server
const server = setupServer(
  rest.post('/api/turbonomic/actions', (req, res, ctx) => {
    return res(
      ctx.json([
        { uuid: '123', actionType: 'RESIZE', entity: 'VM-1' },
        { uuid: '456', actionType: 'MOVE', entity: 'VM-2' }
      ])
    );
  }),
  rest.post('/api/turbonomic/entities', (req, res, ctx) => {
    return res(
      ctx.json([
        { id: '1', className: 'VirtualMachine' },
        { id: '2', className: 'Container' }
      ])
    );
  }),
  rest.post('/api/turbonomic/targets', (req, res, ctx) => {
    return res(
      ctx.json([
        { id: '1', type: 'Kubernetes', status: 'ONLINE' }
      ])
    );
  })
);

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

describe('App Integration Tests', () => {
  test('loads and displays data from API', async () => {
    const user = userEvent.setup();
    render(<App />);

    // Fill in credentials
    await user.type(screen.getByLabelText(/Turbonomic Host/i), 'https://test.com');
    await user.type(screen.getByLabelText(/Username/i), 'admin');
    await user.type(screen.getByLabelText(/Password/i), 'password');

    // Click load button
    await user.click(screen.getByText(/Load Data/i));

    // Wait for data to load
    await waitFor(() => {
      expect(screen.getByText(/Pending Actions/i)).toBeInTheDocument();
    });

    // Verify data is displayed
    expect(screen.getByText('2')).toBeInTheDocument(); // Actions count
    expect(screen.getByText('2')).toBeInTheDocument(); // Entities count
    expect(screen.getByText('1')).toBeInTheDocument(); // Targets count
  });

  test('handles API errors gracefully', async () => {
    server.use(
      rest.post('/api/turbonomic/actions', (req, res, ctx) => {
        return res(ctx.status(500), ctx.json({ error: 'Server error' }));
      })
    );

    const user = userEvent.setup();
    render(<App />);

    await user.type(screen.getByLabelText(/Turbonomic Host/i), 'https://test.com');
    await user.type(screen.getByLabelText(/Username/i), 'admin');
    await user.type(screen.getByLabelText(/Password/i), 'password');
    await user.click(screen.getByText(/Load Data/i));

    await waitFor(() => {
      expect(screen.getByText(/error/i)).toBeInTheDocument();
    });
  });
});
```

## End-to-End Testing

### Cypress Setup

#### cypress.config.js
```javascript
const { defineConfig } = require('cypress');

module.exports = defineConfig({
  e2e: {
    baseUrl: 'http://localhost:3000',
    supportFile: 'cypress/support/e2e.js',
    specPattern: 'cypress/e2e/**/*.cy.{js,jsx,ts,tsx}',
    video: false,
    screenshotOnRunFailure: true,
    viewportWidth: 1280,
    viewportHeight: 720
  }
});
```

#### E2E Test Examples
```javascript
// cypress/e2e/dashboard.cy.js
describe('Turbonomic Dashboard E2E', () => {
  beforeEach(() => {
    cy.visit('/');
  });

  it('loads the dashboard', () => {
    cy.contains('Turbonomic Resource Dashboard').should('be.visible');
  });

  it('expands configuration section', () => {
    cy.contains('Turbonomic Configuration').click();
    cy.get('input[id="turbo-host"]').should('be.visible');
  });

  it('loads data with valid credentials', () => {
    // Expand configuration
    cy.contains('Turbonomic Configuration').click();

    // Fill in credentials
    cy.get('input[id="turbo-host"]').type('https://test.com');
    cy.get('input[id="turbo-username"]').type('admin');
    cy.get('input[id="turbo-password"]').type('password');

    // Intercept API calls
    cy.intercept('POST', '/api/turbonomic/actions', {
      fixture: 'actions.json'
    }).as('getActions');

    cy.intercept('POST', '/api/turbonomic/entities', {
      fixture: 'entities.json'
    }).as('getEntities');

    cy.intercept('POST', '/api/turbonomic/targets', {
      fixture: 'targets.json'
    }).as('getTargets');

    // Click load button
    cy.contains('Load Data').click();

    // Wait for API calls
    cy.wait(['@getActions', '@getEntities', '@getTargets']);

    // Verify data is displayed
    cy.contains('Overview').should('be.visible');
    cy.contains('Pending Actions').should('be.visible');
  });

  it('displays error on invalid credentials', () => {
    cy.contains('Turbonomic Configuration').click();
    cy.contains('Load Data').click();
    cy.contains('Please configure Turbonomic credentials').should('be.visible');
  });

  it('navigates between tabs', () => {
    // Load data first
    cy.contains('Turbonomic Configuration').click();
    cy.get('input[id="turbo-host"]').type('https://test.com');
    cy.get('input[id="turbo-username"]').type('admin');
    cy.get('input[id="turbo-password"]').type('password');
    cy.contains('Load Data').click();

    // Navigate to Pending Actions tab
    cy.contains('Pending Actions').click();
    cy.contains('Action Type').should('be.visible');

    // Navigate back to Overview
    cy.contains('Overview').click();
    cy.contains('Entity Distribution').should('be.visible');
  });

  it('filters pending actions', () => {
    // Load data and navigate to Pending Actions
    cy.contains('Turbonomic Configuration').click();
    cy.get('input[id="turbo-host"]').type('https://test.com');
    cy.get('input[id="turbo-username"]').type('admin');
    cy.get('input[id="turbo-password"]').type('password');
    cy.contains('Load Data').click();
    cy.contains('Pending Actions').click();

    // Apply filter
    cy.get('[data-testid="action-type-filter"]').click();
    cy.contains('RESIZE').click();

    // Verify filtered results
    cy.get('[data-testid="action-row"]').should('have.length.greaterThan', 0);
  });
});
```

### Cypress Fixtures
```json
// cypress/fixtures/actions.json
[
  {
    "uuid": "123",
    "actionType": "RESIZE",
    "entity": "VM-1",
    "risk": { "severity": "CRITICAL" }
  },
  {
    "uuid": "456",
    "actionType": "MOVE",
    "entity": "VM-2",
    "risk": { "severity": "MAJOR" }
  }
]
```

## Test Coverage

### Jest Configuration
```javascript
// jest.config.js
module.exports = {
  testEnvironment: 'jsdom',
  setupFilesAfterEnv: ['<rootDir>/jest.setup.js'],
  moduleNameMapper: {
    '\\.(css|less|scss|sass)$': 'identity-obj-proxy',
    '\\.(jpg|jpeg|png|gif|svg)$': '<rootDir>/__mocks__/fileMock.js'
  },
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

### Running Tests with Coverage
```bash
# Frontend
npm test -- --coverage

# Backend
npm test -- --coverage

# View coverage report
open coverage/lcov-report/index.html
```

## Continuous Integration

### GitHub Actions Workflow
```yaml
name: Test

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  test-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'npm'
          cache-dependency-path: frontend/package-lock.json
      
      - name: Install dependencies
        working-directory: ./frontend
        run: npm ci
      
      - name: Run tests
        working-directory: ./frontend
        run: npm test -- --coverage
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./frontend/coverage/lcov.info
          flags: frontend

  test-backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'npm'
          cache-dependency-path: backend/package-lock.json
      
      - name: Install dependencies
        working-directory: ./backend
        run: npm ci
      
      - name: Run tests
        working-directory: ./backend
        run: npm test -- --coverage
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./backend/coverage/lcov.info
          flags: backend

  e2e-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
      
      - name: Install dependencies
        run: |
          cd frontend && npm ci
          cd ../backend && npm ci
      
      - name: Start backend
        working-directory: ./backend
        run: npm start &
      
      - name: Start frontend
        working-directory: ./frontend
        run: npm run dev &
      
      - name: Wait for services
        run: |
          npx wait-on http://localhost:3000
          npx wait-on http://localhost:4000
      
      - name: Run Cypress tests
        uses: cypress-io/github-action@v5
        with:
          working-directory: ./frontend
          browser: chrome
```

## Testing Best Practices

### ✅ DO
1. Write tests before code (TDD)
2. Test behavior, not implementation
3. Use descriptive test names
4. Keep tests simple and focused
5. Mock external dependencies
6. Test edge cases and errors
7. Maintain high test coverage (>80%)
8. Run tests automatically in CI/CD
9. Use fixtures for test data
10. Clean up after tests

### ❌ DON'T
1. Test implementation details
2. Write tests that depend on each other
3. Skip error cases
4. Use real API calls in tests
5. Ignore failing tests
6. Write overly complex tests
7. Test third-party libraries
8. Hardcode test data
9. Skip integration tests
10. Forget to update tests when code changes

## Test Naming Conventions

### Unit Tests
```javascript
describe('ComponentName', () => {
  describe('methodName', () => {
    test('should do something when condition', () => {
      // Test implementation
    });
  });
});
```

### Integration Tests
```javascript
describe('Feature Integration', () => {
  test('completes user workflow successfully', () => {
    // Test implementation
  });
});
```

### E2E Tests
```javascript
describe('User Journey', () => {
  it('allows user to complete task', () => {
    // Test implementation
  });
});
```

## Resources

- [Jest Documentation](https://jestjs.io/)
- [React Testing Library](https://testing-library.com/react)
- [Cypress Documentation](https://docs.cypress.io/)
- [Testing Best Practices](https://testingjavascript.com/)
- [Test-Driven Development](https://martinfowler.com/bliki/TestDrivenDevelopment.html)

---
*Testing Standards for Turbonomic Resource Dashboard*