# Frontend Development Guide

## Overview

This comprehensive guide covers all aspects of frontend development for the Turbonomic Resource Dashboard, including React development, Carbon Design System implementation, UI/UX standards, styling patterns, and content guidelines.

**Technology Stack:**
- React 18.3.1 with hooks and concurrent features
- Vite 5.4.21 for fast builds and development
- IBM Carbon Design System v11 for enterprise UI
- Carbon Charts for data visualization
- Axios for API communication

---

## Table of Contents

### Part 1: React Development
1. [Project Structure](#1-project-structure)
2. [Component Architecture](#2-component-architecture)
3. [React 18 Features](#3-react-18-features)
4. [Hooks Patterns](#4-hooks-patterns)
5. [State Management](#5-state-management)
6. [Performance Optimization](#6-performance-optimization)

### Part 2: Carbon Design System
7. [Carbon Fundamentals](#7-carbon-fundamentals)
8. [Design Tokens](#8-design-tokens)
9. [Component Library](#9-component-library)
10. [Grid System](#10-grid-system)
11. [Carbon Charts](#11-carbon-charts)

### Part 3: UI/UX Standards
12. [Design Principles](#12-design-principles)
13. [Layout Standards](#13-layout-standards)
14. [Component Standards](#14-component-standards)
15. [Interaction Patterns](#15-interaction-patterns)
16. [Accessibility](#16-accessibility)

### Part 4: Styling Patterns
17. [CSS Architecture](#17-css-architecture)
18. [Color Palette](#18-color-palette)
19. [Typography](#19-typography)
20. [Spacing & Layout](#20-spacing--layout)
21. [Reusable Patterns](#21-reusable-patterns)

### Part 5: Content Guidelines
22. [Writing Principles](#22-writing-principles)
23. [Voice & Tone](#23-voice--tone)
24. [Content Types](#24-content-types)
25. [Terminology Standards](#25-terminology-standards)

---

# Part 1: React Development

## 1. Project Structure

```
frontend/
├── public/
│   └── config.js              # Runtime configuration
├── src/
│   ├── main.jsx              # Application entry point
│   ├── App.jsx               # Root component
│   ├── index.css             # Global styles
│   ├── components/           # React components
│   │   ├── TurbonomicOverview.jsx
│   │   └── TurbonomicPendingActions.jsx
│   └── services/             # API service layer
│       └── turbonomicApi.js
├── index.html                # HTML template
├── vite.config.js           # Vite configuration
├── package.json             # Dependencies
├── Dockerfile               # Container image
└── nginx.conf               # Production web server
```

### Key Dependencies

```json
{
  "@carbon/react": "^1.108.0",
  "@carbon/charts": "^1.27.11",
  "@carbon/charts-react": "^1.27.11",
  "@carbon/icons-react": "^11.x",
  "react": "^18.3.1",
  "react-dom": "^18.3.1",
  "axios": "^1.7.0",
  "vite": "^5.4.21"
}
```

### Vite Configuration

```javascript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    host: true,
    proxy: {
      '/api': {
        target: 'http://localhost:4000',
        changeOrigin: true
      }
    }
  },
  build: {
    outDir: 'dist',
    sourcemap: false,
    rollupOptions: {
      output: {
        manualChunks: {
          'carbon-react': ['@carbon/react'],
          'carbon-charts': ['@carbon/charts', '@carbon/charts-react'],
          'vendor': ['react', 'react-dom', 'axios']
        }
      }
    }
  },
  optimizeDeps: {
    include: ['@carbon/react', '@carbon/charts-react']
  }
})
```

## 2. Component Architecture

### Component Hierarchy

```
App (Root)
├── Header (Carbon)
├── ActionableNotification (Welcome banner)
└── Dashboard Container
    ├── ExpandableTile (Configuration)
    ├── InlineNotification (Errors)
    ├── Loading (Data fetch)
    └── Tabs (Main content)
        ├── TurbonomicOverview
        └── TurbonomicPendingActions
```

### Functional Components with Hooks

```jsx
import React, { useState, useEffect, useMemo, useCallback } from 'react';

const MyComponent = ({ data, onAction }) => {
  const [state, setState] = useState(initialValue);
  
  useEffect(() => {
    // Side effects
    return () => {
      // Cleanup
    };
  }, [dependencies]);
  
  const computed = useMemo(() => {
    // Expensive computation
    return processData(data);
  }, [data]);
  
  const handleClick = useCallback(() => {
    onAction(state);
  }, [state, onAction]);
  
  return (
    <div>
      {/* JSX */}
    </div>
  );
};

export default MyComponent;
```

### Props Destructuring

```jsx
// ✅ Good: Destructure with defaults
const TurbonomicOverview = ({ 
  entities = [], 
  actions = [], 
  targets = [],
  loading = false,
  error = null,
  onRefresh
}) => {
  // Component logic
};

// ❌ Avoid: Accessing props directly
const TurbonomicOverview = (props) => {
  const entities = props.entities || [];
  // ...
};
```

## 3. React 18 Features

### Automatic Batching

```javascript
// React 18 automatically batches state updates
function handleClick() {
  setCount(c => c + 1);
  setFlag(f => !f);
  // Both updates batched into single re-render
}

// Works in timeouts, promises, and native event handlers
setTimeout(() => {
  setCount(c => c + 1);
  setFlag(f => !f);
  // Still batched!
}, 1000);
```

### Transitions

```javascript
import { useTransition } from 'react';

function SearchResults() {
  const [isPending, startTransition] = useTransition();
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);

  function handleChange(e) {
    const value = e.target.value;
    setQuery(value); // Urgent update
    
    startTransition(() => {
      // Non-urgent update
      setResults(searchData(value));
    });
  }

  return (
    <>
      <input value={query} onChange={handleChange} />
      {isPending && <Loading />}
      <ResultsList results={results} />
    </>
  );
}
```

### Suspense for Data Fetching

```javascript
import { Suspense } from 'react';

function App() {
  return (
    <Suspense fallback={<Loading />}>
      <DataComponent />
    </Suspense>
  );
}
```

## 4. Hooks Patterns

### useState

```javascript
// Simple state
const [count, setCount] = useState(0);

// Object state
const [user, setUser] = useState({ name: '', email: '' });

// Functional updates
setCount(prevCount => prevCount + 1);

// Lazy initialization
const [state, setState] = useState(() => {
  return expensiveComputation();
});
```

### useEffect

```javascript
// Component mount/unmount
useEffect(() => {
  console.log('Component mounted');
  return () => console.log('Component unmounted');
}, []);

// Dependency tracking
useEffect(() => {
  fetchData(id);
}, [id]);

// Cleanup
useEffect(() => {
  const subscription = subscribeToData();
  return () => subscription.unsubscribe();
}, []);
```

### useCallback

```javascript
// Memoize callback functions
const handleSubmit = useCallback((data) => {
  api.submit(data);
}, []);

// With dependencies
const handleUpdate = useCallback((id) => {
  updateItem(id, filter);
}, [filter]);
```

### useMemo

```javascript
// Memoize expensive computations
const sortedData = useMemo(() => {
  return data.sort((a, b) => a.value - b.value);
}, [data]);

// Avoid unnecessary re-renders
const config = useMemo(() => ({
  option1: value1,
  option2: value2
}), [value1, value2]);
```

### useContext

```javascript
import { createContext, useContext } from 'react';

const ThemeContext = createContext('light');

function App() {
  return (
    <ThemeContext.Provider value="dark">
      <ThemedComponent />
    </ThemeContext.Provider>
  );
}

function ThemedComponent() {
  const theme = useContext(ThemeContext);
  return <div className={theme}>Content</div>;
}
```

### Custom Hooks

```javascript
// useApi custom hook
function useApi(url) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let cancelled = false;
    
    async function fetchData() {
      try {
        setLoading(true);
        const response = await fetch(url);
        const json = await response.json();
        
        if (!cancelled) {
          setData(json);
          setError(null);
        }
      } catch (err) {
        if (!cancelled) {
          setError(err);
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }
    
    fetchData();
    
    return () => {
      cancelled = true;
    };
  }, [url]);

  return { data, loading, error };
}

// Usage
function MyComponent() {
  const { data, loading, error } = useApi('/api/data');
  
  if (loading) return <Loading />;
  if (error) return <Error message={error.message} />;
  return <DataDisplay data={data} />;
}
```

## 5. State Management

### Local State

```javascript
// Component-level state
function Counter() {
  const [count, setCount] = useState(0);
  
  return (
    <button onClick={() => setCount(count + 1)}>
      Count: {count}
    </button>
  );
}
```

### Lifting State Up

```javascript
// Parent manages shared state
function Dashboard() {
  const [credentials, setCredentials] = useState(null);
  
  return (
    <>
      <ConfigPanel onSave={setCredentials} />
      <DataView credentials={credentials} />
    </>
  );
}
```

### Context for Global State

```javascript
// Create context
const AppContext = createContext();

// Provider component
function AppProvider({ children }) {
  const [config, setConfig] = useState(null);
  const [data, setData] = useState([]);
  
  const value = {
    config,
    setConfig,
    data,
    setData
  };
  
  return (
    <AppContext.Provider value={value}>
      {children}
    </AppContext.Provider>
  );
}

// Consumer hook
function useApp() {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error('useApp must be used within AppProvider');
  }
  return context;
}

// Usage
function MyComponent() {
  const { config, setConfig } = useApp();
  // ...
}
```

## 6. Performance Optimization

### Code Splitting

```javascript
import { lazy, Suspense } from 'react';

// Lazy load components
const TurbonomicOverview = lazy(() => import('./components/TurbonomicOverview'));
const TurbonomicPendingActions = lazy(() => import('./components/TurbonomicPendingActions'));

function App() {
  return (
    <Suspense fallback={<Loading />}>
      <Routes>
        <Route path="/overview" element={<TurbonomicOverview />} />
        <Route path="/actions" element={<TurbonomicPendingActions />} />
      </Routes>
    </Suspense>
  );
}
```

### Memoization

```javascript
import { memo } from 'react';

// Memoize component
const ExpensiveComponent = memo(({ data }) => {
  return <div>{/* Expensive rendering */}</div>;
});

// Custom comparison
const OptimizedComponent = memo(
  ({ data }) => <div>{data.value}</div>,
  (prevProps, nextProps) => {
    return prevProps.data.id === nextProps.data.id;
  }
);
```

### Virtual Scrolling

```javascript
// For large lists, use virtualization
import { FixedSizeList } from 'react-window';

function LargeList({ items }) {
  const Row = ({ index, style }) => (
    <div style={style}>
      {items[index].name}
    </div>
  );

  return (
    <FixedSizeList
      height={600}
      itemCount={items.length}
      itemSize={50}
      width="100%"
    >
      {Row}
    </FixedSizeList>
  );
}
```

---

# Part 2: Carbon Design System

## 7. Carbon Fundamentals

### Design Philosophy

Carbon is built on four core principles:
1. **Clarity** - Clear, concise, and consistent
2. **Efficiency** - Streamlined workflows
3. **Consistency** - Unified experience
4. **Beauty** - Thoughtful, elegant design

### Installation

```bash
npm install @carbon/react @carbon/charts @carbon/charts-react @carbon/icons-react
```

### CSS Import

```jsx
// main.jsx
import '@carbon/styles/css/styles.css';
import '@carbon/charts/styles.css';
```

### Theme Configuration

```jsx
import { Theme } from '@carbon/react';

<Theme theme="white">  {/* white, g10, g90, g100 */}
  <App />
</Theme>
```

## 8. Design Tokens

### Color Tokens

```css
/* Text Colors */
--cds-text-primary: #161616;
--cds-text-secondary: #525252;
--cds-text-placeholder: #a8a8a8;
--cds-text-on-color: #ffffff;
--cds-text-helper: #6f6f6f;
--cds-text-error: #da1e28;

/* Background Colors */
--cds-background: #ffffff;
--cds-layer-01: #f4f4f4;
--cds-layer-02: #ffffff;
--cds-layer-03: #f4f4f4;

/* Interactive Colors */
--cds-interactive: #0f62fe;
--cds-link-primary: #0f62fe;
--cds-focus: #0f62fe;

/* Status Colors */
--cds-support-error: #da1e28;
--cds-support-success: #24a148;
--cds-support-warning: #f1c21b;
--cds-support-info: #0f62fe;
```

### Spacing Tokens

```css
--cds-spacing-01: 0.125rem;  /* 2px */
--cds-spacing-02: 0.25rem;   /* 4px */
--cds-spacing-03: 0.5rem;    /* 8px */
--cds-spacing-04: 0.75rem;   /* 12px */
--cds-spacing-05: 1rem;      /* 16px */
--cds-spacing-06: 1.5rem;    /* 24px */
--cds-spacing-07: 2rem;      /* 32px */
--cds-spacing-08: 2.5rem;    /* 40px */
--cds-spacing-09: 3rem;      /* 48px */
--cds-spacing-10: 4rem;      /* 64px */
```

### Typography Tokens

```css
/* Headings */
--cds-heading-01: 0.875rem;  /* 14px */
--cds-heading-02: 1rem;      /* 16px */
--cds-heading-03: 1.25rem;   /* 20px */
--cds-heading-04: 1.75rem;   /* 28px */
--cds-heading-05: 2rem;      /* 32px */
--cds-heading-06: 2.625rem;  /* 42px */
--cds-heading-07: 3.375rem;  /* 54px */

/* Body */
--cds-body-01: 0.875rem;     /* 14px */
--cds-body-02: 1rem;         /* 16px */

/* Code */
--cds-code-01: 0.75rem;      /* 12px */
--cds-code-02: 0.875rem;     /* 14px */
```

## 9. Component Library

### Buttons

```jsx
import { Button } from '@carbon/react';

// Primary button
<Button>Primary Action</Button>

// Secondary button
<Button kind="secondary">Secondary</Button>

// Tertiary button
<Button kind="tertiary">Tertiary</Button>

// Danger button
<Button kind="danger">Delete</Button>

// Ghost button
<Button kind="ghost">Ghost</Button>

// With icon
<Button renderIcon={Add16}>Add Item</Button>

// Sizes
<Button size="sm">Small</Button>
<Button size="md">Medium</Button>
<Button size="lg">Large</Button>
```

### Notifications

```jsx
import { InlineNotification, ToastNotification, ActionableNotification } from '@carbon/react';

// Inline notification
<InlineNotification
  kind="error"
  title="Error"
  subtitle="Failed to load data"
  onClose={() => {}}
/>

// Toast notification
<ToastNotification
  kind="success"
  title="Success"
  subtitle="Data saved successfully"
  timeout={3000}
/>

// Actionable notification
<ActionableNotification
  kind="info"
  title="Welcome"
  subtitle="Configure your connection to get started"
  actionButtonLabel="Configure"
  onActionButtonClick={() => {}}
/>
```

### Data Tables

```jsx
import { DataTable, Table, TableHead, TableRow, TableHeader, TableBody, TableCell } from '@carbon/react';

const headers = [
  { key: 'name', header: 'Name' },
  { key: 'status', header: 'Status' },
  { key: 'value', header: 'Value' }
];

const rows = [
  { id: '1', name: 'Item 1', status: 'Active', value: 100 },
  { id: '2', name: 'Item 2', status: 'Pending', value: 200 }
];

<DataTable rows={rows} headers={headers}>
  {({ rows, headers, getTableProps, getHeaderProps, getRowProps }) => (
    <Table {...getTableProps()}>
      <TableHead>
        <TableRow>
          {headers.map(header => (
            <TableHeader {...getHeaderProps({ header })}>
              {header.header}
            </TableHeader>
          ))}
        </TableRow>
      </TableHead>
      <TableBody>
        {rows.map(row => (
          <TableRow {...getRowProps({ row })}>
            {row.cells.map(cell => (
              <TableCell key={cell.id}>{cell.value}</TableCell>
            ))}
          </TableRow>
        ))}
      </TableBody>
    </Table>
  )}
</DataTable>
```

### Forms

```jsx
import { TextInput, Select, SelectItem, Checkbox, RadioButton, RadioButtonGroup } from '@carbon/react';

// Text input
<TextInput
  id="username"
  labelText="Username"
  placeholder="Enter username"
  value={username}
  onChange={(e) => setUsername(e.target.value)}
/>

// Select
<Select
  id="country"
  labelText="Country"
  value={country}
  onChange={(e) => setCountry(e.target.value)}
>
  <SelectItem value="" text="Choose an option" />
  <SelectItem value="us" text="United States" />
  <SelectItem value="uk" text="United Kingdom" />
</Select>

// Checkbox
<Checkbox
  id="terms"
  labelText="I agree to terms"
  checked={agreed}
  onChange={(e) => setAgreed(e.target.checked)}
/>

// Radio buttons
<RadioButtonGroup
  name="size"
  valueSelected={size}
  onChange={setSize}
>
  <RadioButton value="small" labelText="Small" />
  <RadioButton value="medium" labelText="Medium" />
  <RadioButton value="large" labelText="Large" />
</RadioButtonGroup>
```

## 10. Grid System

### 16-Column Grid

```jsx
import { Grid, Column } from '@carbon/react';

<Grid>
  <Column lg={16} md={8} sm={4}>
    Full width
  </Column>
  
  <Column lg={8} md={4} sm={4}>
    Half width on large
  </Column>
  <Column lg={8} md={4} sm={4}>
    Half width on large
  </Column>
  
  <Column lg={4} md={2} sm={4}>
    Quarter width
  </Column>
  <Column lg={4} md={2} sm={4}>
    Quarter width
  </Column>
  <Column lg={4} md={2} sm={4}>
    Quarter width
  </Column>
  <Column lg={4} md={2} sm={4}>
    Quarter width
  </Column>
</Grid>
```

### Breakpoints

```css
/* Small (sm): 320px - 671px */
@media (min-width: 320px) { }

/* Medium (md): 672px - 1055px */
@media (min-width: 672px) { }

/* Large (lg): 1056px - 1311px */
@media (min-width: 1056px) { }

/* X-Large (xlg): 1312px - 1583px */
@media (min-width: 1312px) { }

/* Max (max): 1584px+ */
@media (min-width: 1584px) { }
```

## 11. Carbon Charts

### Line Chart

```jsx
import { LineChart } from '@carbon/charts-react';

const data = [
  { group: 'Dataset 1', date: '2024-01-01', value: 10 },
  { group: 'Dataset 1', date: '2024-01-02', value: 15 },
  { group: 'Dataset 1', date: '2024-01-03', value: 12 }
];

const options = {
  title: 'Resource Usage Over Time',
  axes: {
    bottom: {
      title: 'Date',
      mapsTo: 'date',
      scaleType: 'time'
    },
    left: {
      title: 'Value',
      mapsTo: 'value'
    }
  },
  height: '400px'
};

<LineChart data={data} options={options} />
```

### Donut Chart

```jsx
import { DonutChart } from '@carbon/charts-react';

const data = [
  { group: 'Active', value: 65 },
  { group: 'Pending', value: 25 },
  { group: 'Failed', value: 10 }
];

const options = {
  title: 'Status Distribution',
  resizable: true,
  donut: {
    center: {
      label: 'Total'
    }
  },
  height: '400px'
};

<DonutChart data={data} options={options} />
```

---

# Part 3: UI/UX Standards

## 12. Design Principles

### 1. Clarity
- Clear visual hierarchy
- Consistent patterns
- Meaningful labels
- Logical organization

### 2. Efficiency
- Minimal clicks
- Smart defaults
- Bulk actions
- Keyboard shortcuts

### 3. Feedback
- Loading states
- Success confirmation
- Error messages
- Hover states

### 4. Accessibility
- Keyboard navigation
- Screen reader support
- Color contrast (WCAG AA)
- Focus indicators

## 13. Layout Standards

### Page Structure

```
┌─────────────────────────────────────────┐
│ Header (48px fixed)                     │
├─────────────────────────────────────────┤
│ Banner (optional, dismissible)          │
├─────────────────────────────────────────┤
│ ┌─────────────────────────────────────┐ │
│ │ Main Content Area                   │ │
│ │ ┌─────────────────────────────────┐ │ │
│ │ │ Configuration Section           │ │ │
│ │ └─────────────────────────────────┘ │ │
│ │ ┌─────────────────────────────────┐ │ │
│ │ │ Tabs Navigation                 │ │ │
│ │ ├─────────────────────────────────┤ │ │
│ │ │ Tab Content                     │ │ │
│ │ └─────────────────────────────────┘ │ │
│ └─────────────────────────────────────┘ │
└─────────────────────────────────────────┘
```

### Spacing Guidelines

**Container Padding:**
- Desktop (lg+): 24px
- Tablet (md): 16px
- Mobile (sm): 16px

**Section Spacing:**
- Between major sections: 32px
- Between related groups: 16px
- Between elements: 8px

### Responsive Breakpoints

**Mobile (320px - 671px):**
- Single column layout
- Stacked components
- Full-width elements
- Touch-friendly targets (44px min)

**Tablet (672px - 1055px):**
- Two-column layout
- Side-by-side charts
- Compact tables

**Desktop (1056px+):**
- Multi-column layout
- Full-featured interface
- Expanded tables

## 14. Component Standards

### Headers

```jsx
<Header aria-label="Turbonomic Dashboard">
  <HeaderName prefix="IBM">
    Turbonomic Resource Dashboard
  </HeaderName>
</Header>
```

### Metric Cards

```jsx
<Tile className="metric-card">
  <div className="metric-value">1,234</div>
  <div className="metric-label">Total Resources</div>
  <div className="metric-trend positive">+12%</div>
</Tile>
```

### Loading States

```jsx
<Loading
  description="Loading data..."
  withOverlay={true}
/>
```

### Empty States

```jsx
<div className="empty-state">
  <EmptyStateIcon />
  <h3>No data available</h3>
  <p>Configure your connection to view resources</p>
  <Button>Configure Now</Button>
</div>
```

## 15. Interaction Patterns

### Hover States

```css
.interactive-element:hover {
  background-color: var(--cds-layer-hover);
  cursor: pointer;
}
```

### Focus States

```css
.interactive-element:focus {
  outline: 2px solid var(--cds-focus);
  outline-offset: 2px;
}
```

### Transitions

```css
.smooth-transition {
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}
```

## 16. Accessibility

### ARIA Labels

```jsx
<button aria-label="Close notification">
  <Close16 />
</button>

<input
  aria-describedby="username-helper"
  aria-invalid={hasError}
/>
```

### Keyboard Navigation

```jsx
<div
  role="button"
  tabIndex={0}
  onKeyDown={(e) => {
    if (e.key === 'Enter' || e.key === ' ') {
      handleClick();
    }
  }}
>
  Clickable Element
</div>
```

### Color Contrast

- Normal text: 4.5:1 minimum
- Large text: 3:1 minimum
- UI components: 3:1 minimum

---

# Part 4: Styling Patterns

## 17. CSS Architecture

### File Structure

```
src/
├── index.css              # Global styles
├── App.jsx               # Component styles
└── components/
    ├── Component.jsx     # Component-specific styles
    └── Component.module.css
```

### Import Order

```css
/* 1. Carbon Design System */
@import '@carbon/styles/css/styles.css';
@import '@carbon/charts/styles.css';

/* 2. Design Tokens */
:root {
  /* Custom tokens */
}

/* 3. Global Styles */
* { /* Reset */ }
body { /* Base */ }

/* 4. Component Styles */
.component { /* Styles */ }

/* 5. Utilities */
.utility { /* Helpers */ }

/* 6. Responsive */
@media (max-width: 672px) { }
```

## 18. Color Palette

### Primary Colors

```css
:root {
  /* IBM Blue */
  --color-blue-60: #0f62fe;  /* Primary */
  --color-blue-70: #0043ce;
  --color-blue-80: #002d9c;
}
```

### Status Colors

```css
:root {
  /* Error */
  --color-red-60: #da1e28;
  
  /* Success */
  --color-green-50: #24a148;
  
  /* Warning */
  --color-yellow-30: #f1c21b;
  
  /* Info */
  --color-blue-60: #0f62fe;
}
```

### Gradient Patterns

```css
.gradient-blue {
  background: linear-gradient(135deg, #0f62fe 0%, #0043ce 100%);
}

.gradient-green {
  background: linear-gradient(135deg, #24a148 0%, #198038 100%);
}

.gradient-red {
  background: linear-gradient(135deg, #da1e28 0%, #a2191f 100%);
}
```

## 19. Typography

### Font Family

```css
body {
  font-family: 'IBM Plex Sans', 'Helvetica Neue', Arial, sans-serif;
}

code {
  font-family: 'IBM Plex Mono', 'Menlo', 'Courier New', monospace;
}
```

### Type Scale

```css
.heading-01 { font-size: 0.875rem; }  /* 14px */
.heading-02 { font-size: 1rem; }      /* 16px */
.heading-03 { font-size: 1.25rem; }   /* 20px */
.heading-04 { font-size: 1.75rem; }   /* 28px */
.heading-05 { font-size: 2rem; }      /* 32px */

.body-01 { font-size: 0.875rem; }     /* 14px */
.body-02 { font-size: 1rem; }         /* 16px */
```

## 20. Spacing & Layout

### Spacing Scale

```css
.spacing-01 { margin: 0.125rem; }  /* 2px */
.spacing-03 { margin: 0.5rem; }    /* 8px */
.spacing-05 { margin: 1rem; }      /* 16px */
.spacing-07 { margin: 2rem; }      /* 32px */
```

### Flexbox Patterns

```css
.flex-row {
  display: flex;
  flex-direction: row;
  gap: 1rem;
}

.flex-center {
  display: flex;
  align-items: center;
  justify-content: center;
}

.flex-between {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
```

## 21. Reusable Patterns

### Card Pattern

```css
.card {
  background: var(--cds-layer-01);
  border-radius: 4px;
  padding: 1rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.card:hover {
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}
```

### Metric Card

```css
.metric-card {
  padding: 1.5rem;
  background: linear-gradient(135deg, #0f62fe 0%, #0043ce 100%);
  color: white;
  border-radius: 4px;
}

.metric-value {
  font-size: 2rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
}

.metric-label {
  font-size: 0.875rem;
  opacity: 0.9;
}
```

---

# Part 5: Content Guidelines

## 22. Writing Principles

### 1. Clarity
- Use simple language
- Be specific
- Be concise
- Use active voice

### 2. Consistency
- Same terminology
- Professional tone
- Consistent format
- Similar patterns

### 3. User-Focused
- Address the user
- Explain benefits
- Provide context
- Guide actions

### 4. Accessibility
- Screen reader friendly
- Plain language
- Meaningful text
- Alternative text

## 23. Voice & Tone

### Voice (Consistent)
- Professional
- Helpful
- Clear
- Confident

### Tone (Contextual)

**Success:**
```
✅ "Actions executed successfully"
❌ "Yay! Everything worked!"
```

**Error:**
```
✅ "Unable to connect. Please check your credentials."
❌ "Connection failed! Something went wrong!"
```

**Informational:**
```
✅ "Configure your connection to view data"
❌ "You need to set this up first"
```

## 24. Content Types

### Page Titles
- Title Case
- 2-5 words
- Descriptive

```
✅ "Turbonomic Resource Dashboard"
❌ "dashboard"
```

### Button Labels
- Action verbs
- 1-3 words
- Clear purpose

```
✅ "Save Configuration"
❌ "Click Here"
```

### Error Messages
- What happened
- Why it happened
- How to fix it

```
✅ "Unable to connect to Turbonomic. Please verify your credentials and try again."
❌ "Error 500"
```

## 25. Terminology Standards

### Consistent Terms

| Use | Don't Use |
|-----|-----------|
| Configuration | Settings, Setup |
| Credentials | Login, Auth |
| Resource | Asset, Item |
| Action | Task, Job |
| Dashboard | Home, Main |

### Capitalization

- **Title Case**: Page titles, section headings
- **Sentence case**: Body text, descriptions
- **ALL CAPS**: Avoid except for acronyms

---

## Best Practices Summary

### DO ✅

- Use functional components with hooks
- Implement proper error boundaries
- Follow Carbon Design System guidelines
- Use design tokens for consistency
- Write accessible HTML with ARIA labels
- Optimize performance with memoization
- Test components thoroughly
- Use semantic HTML elements
- Implement responsive design
- Follow content guidelines

### DON'T ❌

- Use class components for new code
- Ignore accessibility requirements
- Hardcode colors or spacing values
- Skip error handling
- Forget loading states
- Ignore performance optimization
- Mix styling approaches
- Use inline styles excessively
- Forget mobile responsiveness
- Use inconsistent terminology

---

## Troubleshooting

### Common Issues and Solutions

#### SASS Compilation Errors with Vite

**Issue:** SASS compilation errors when using Carbon Design System SCSS mixins with Vite:
```
[sass] Declarations may only be used within style rules
[sass] (md: (font-size: 3.375rem, ...)) isn't a valid CSS value
```

**Solution:** Use CSS imports instead of SCSS mixins for better Vite compatibility:

```scss
// ❌ DON'T: Use SCSS mixins (causes compilation errors)
@use '@carbon/react';
@include react.theme();
@include react.grid();

// ✅ DO: Use CSS imports
@import '@carbon/styles/css/styles.css';
```

For component-specific styles, use CSS custom properties instead of SCSS mixins:

```scss
// ❌ DON'T: Use SCSS type mixins
@use '@carbon/react/scss/type' as *;
.metric-value {
  @include type-style('display-03');
}

// ✅ DO: Use direct CSS values or custom properties
.metric-value {
  font-size: 3rem;
  font-weight: 300;
  color: var(--cds-text-primary);
}
```

#### Module Resolution Issues

**Issue:** Cannot find module errors for Carbon components.

**Solution:** Ensure all Carbon packages are installed:
```bash
npm install @carbon/react @carbon/charts @carbon/charts-react @carbon/icons-react
```

#### Styling Not Applied

**Issue:** Carbon styles not appearing in the application.

**Solution:** Verify the CSS import in your main entry file:
```javascript
// src/index.scss or src/main.jsx
import '@carbon/styles/css/styles.css';
```

#### Chart Rendering Issues
#### PasswordInput Import Error

**Issue:** Error "Element type is invalid: expected a string... but got: undefined" when using `TextInput.PasswordInput`.

**Cause:** In Carbon v11, `PasswordInput` is a separate component, not a property of `TextInput`.

**❌ Incorrect:**
```javascript
import { TextInput } from '@carbon/react';

<TextInput.PasswordInput
  id="password"
  labelText="Password"
  value={password}
  onChange={handleChange}
/>
```

**✅ Correct:**
```javascript
import { TextInput, PasswordInput } from '@carbon/react';

<PasswordInput
  id="password"
  labelText="Password"
  value={password}
  onChange={handleChange}
/>
```

**Key Points:**
- Always import `PasswordInput` separately from `@carbon/react`
- Do not use `TextInput.PasswordInput` syntax
- Both components have similar props and behavior
- This applies to other specialized input components in Carbon v11


**Issue:** Carbon Charts not rendering or showing errors.

**Solution:** 
1. Import chart styles:
```javascript
import '@carbon/charts-react/styles.css';
```

2. Ensure proper data format:
```javascript
const chartData = [
  { group: 'Category', value: 10 },
  { group: 'Category2', value: 20 }
];
```

#### Development Server Issues

**Issue:** `npm run install:all` script not found.

**Solution:** Install dependencies individually:
```bash
cd frontend && npm install
cd ../backend && npm install
```

---

## Resources

### Official Documentation
- [React Documentation](https://react.dev/)
- [Carbon Design System](https://carbondesignsystem.com/)
- [Carbon React Components](https://react.carbondesignsystem.com/)
- [Carbon Charts](https://charts.carbondesignsystem.com/)
- [Vite Documentation](https://vitejs.dev/)

### Design Resources
- [IBM Design Language](https://www.ibm.com/design/language/)
- [Carbon Design Kit](https://www.carbondesignsystem.com/designing/kits/sketch)
- [Carbon Icons](https://www.carbondesignsystem.com/guidelines/icons/library)

### Accessibility
- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [ARIA Authoring Practices](https://www.w3.org/WAI/ARIA/apg/)

---

**Last Updated:** 2026-05-22  
**Version:** 2.0.0  
**Maintainer:** Operations Dashboard Team