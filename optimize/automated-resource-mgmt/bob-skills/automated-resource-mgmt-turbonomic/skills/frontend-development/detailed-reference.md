# Frontend Development - Detailed Reference

This file contains comprehensive reference material for frontend development. Refer to SKILL.md for quick guidance and use this file for detailed examples and patterns.

## React Development Patterns

### Component Structure
```javascript
import { useState, useEffect, useCallback, useMemo } from 'react';
import { Button, TextInput, Loading } from '@carbon/react';
import PropTypes from 'prop-types';

export const MyComponent = ({ 
  initialData, 
  onSave, 
  isLoading = false 
}) => {
  // State
  const [data, setData] = useState(initialData);
  const [error, setError] = useState(null);

  // Effects
  useEffect(() => {
    // Side effects here
    return () => {
      // Cleanup
    };
  }, [data]);

  // Callbacks
  const handleSave = useCallback(() => {
    try {
      onSave(data);
    } catch (err) {
      setError(err.message);
    }
  }, [data, onSave]);

  // Memoized values
  const isValid = useMemo(() => {
    return data && data.length > 0;
  }, [data]);

  // Render
  if (isLoading) {
    return <Loading description="Loading data..." />;
  }

  if (error) {
    return <div className="error">{error}</div>;
  }

  return (
    <div className="my-component">
      <TextInput
        id="data-input"
        labelText="Data"
        value={data}
        onChange={(e) => setData(e.target.value)}
      />
      <Button 
        onClick={handleSave}
        disabled={!isValid}
      >
        Save
      </Button>
    </div>
  );
};

MyComponent.propTypes = {
  initialData: PropTypes.string,
  onSave: PropTypes.func.isRequired,
  isLoading: PropTypes.bool
};
```

### Custom Hooks
```javascript
// useDataFetching.js
import { useState, useEffect } from 'react';

export const useDataFetching = (url) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      setError(null);
      
      try {
        const response = await fetch(url);
        const result = await response.json();
        setData(result);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    if (url) {
      fetchData();
    }
  }, [url]);

  return { data, loading, error };
};

// Usage
const MyComponent = () => {
  const { data, loading, error } = useDataFetching('/api/data');
  
  if (loading) return <Loading />;
  if (error) return <div>Error: {error}</div>;
  
  return <div>{JSON.stringify(data)}</div>;
};
```

## Carbon Design System

### Complete Component Examples

#### Data Table
```javascript
import {
  DataTable,
  TableContainer,
  Table,
  TableHead,
  TableRow,
  TableHeader,
  TableBody,
  TableCell,
  TableToolbar,
  TableToolbarContent,
  TableToolbarSearch,
  Button
} from '@carbon/react';
import { Add } from '@carbon/icons-react';

const headers = [
  { key: 'name', header: 'Name' },
  { key: 'status', header: 'Status' },
  { key: 'value', header: 'Value' }
];

const rows = [
  { id: '1', name: 'Item 1', status: 'Active', value: 100 },
  { id: '2', name: 'Item 2', status: 'Inactive', value: 200 }
];

export const MyDataTable = () => {
  return (
    <DataTable rows={rows} headers={headers}>
      {({
        rows,
        headers,
        getTableProps,
        getHeaderProps,
        getRowProps,
        getToolbarProps,
        onInputChange
      }) => (
        <TableContainer>
          <TableToolbar {...getToolbarProps()}>
            <TableToolbarContent>
              <TableToolbarSearch onChange={onInputChange} />
              <Button renderIcon={Add}>Add new</Button>
            </TableToolbarContent>
          </TableToolbar>
          <Table {...getTableProps()}>
            <TableHead>
              <TableRow>
                {headers.map((header) => (
                  <TableHeader {...getHeaderProps({ header })}>
                    {header.header}
                  </TableHeader>
                ))}
              </TableRow>
            </TableHead>
            <TableBody>
              {rows.map((row) => (
                <TableRow {...getRowProps({ row })}>
                  {row.cells.map((cell) => (
                    <TableCell key={cell.id}>{cell.value}</TableCell>
                  ))}
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}
    </DataTable>
  );
};
```

#### Form with Validation
```javascript
import { useState } from 'react';
import {
  Form,
  TextInput,
  PasswordInput,
  Button,
  InlineNotification
} from '@carbon/react';

export const LoginForm = ({ onSubmit }) => {
  const [formData, setFormData] = useState({
    email: '',
    password: ''
  });
  const [errors, setErrors] = useState({});
  const [notification, setNotification] = useState(null);

  const validate = () => {
    const newErrors = {};
    
    if (!formData.email) {
      newErrors.email = 'Email is required';
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = 'Email is invalid';
    }
    
    if (!formData.password) {
      newErrors.password = 'Password is required';
    } else if (formData.password.length < 8) {
      newErrors.password = 'Password must be at least 8 characters';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validate()) {
      return;
    }
    
    try {
      await onSubmit(formData);
      setNotification({
        kind: 'success',
        title: 'Success',
        subtitle: 'Login successful'
      });
    } catch (error) {
      setNotification({
        kind: 'error',
        title: 'Error',
        subtitle: error.message
      });
    }
  };

  return (
    <Form onSubmit={handleSubmit}>
      {notification && (
        <InlineNotification
          kind={notification.kind}
          title={notification.title}
          subtitle={notification.subtitle}
          onCloseButtonClick={() => setNotification(null)}
        />
      )}
      
      <TextInput
        id="email"
        labelText="Email"
        type="email"
        value={formData.email}
        onChange={(e) => setFormData({ ...formData, email: e.target.value })}
        invalid={!!errors.email}
        invalidText={errors.email}
      />
      
      <PasswordInput
        id="password"
        labelText="Password"
        value={formData.password}
        onChange={(e) => setFormData({ ...formData, password: e.target.value })}
        invalid={!!errors.password}
        invalidText={errors.password}
      />
      
      <Button type="submit">Login</Button>
    </Form>
  );
};
```

### Carbon Charts Examples

#### Line Chart with Multiple Series
```javascript
import { LineChart } from '@carbon/charts-react';
import '@carbon/charts-react/styles.css';

const data = [
  { group: 'Series 1', date: '2024-01-01', value: 10 },
  { group: 'Series 1', date: '2024-01-02', value: 15 },
  { group: 'Series 2', date: '2024-01-01', value: 20 },
  { group: 'Series 2', date: '2024-01-02', value: 25 }
];

const options = {
  title: 'Performance Over Time',
  axes: {
    bottom: {
      title: 'Date',
      mapsTo: 'date',
      scaleType: 'time'
    },
    left: {
      title: 'Value',
      mapsTo: 'value',
      scaleType: 'linear'
    }
  },
  curve: 'curveMonotoneX',
  height: '400px'
};

export const PerformanceChart = () => {
  return <LineChart data={data} options={options} />;
};
```

## Styling Patterns

### CSS Module Pattern
```css
/* MyComponent.module.css */
.container {
  padding: var(--cds-spacing-05);
  background: var(--cds-layer-01);
  border-radius: 4px;
}

.header {
  font-size: var(--cds-heading-03-font-size);
  font-weight: var(--cds-heading-03-font-weight);
  color: var(--cds-text-primary);
  margin-bottom: var(--cds-spacing-05);
}

.content {
  display: flex;
  flex-direction: column;
  gap: var(--cds-spacing-03);
}

.button {
  margin-top: var(--cds-spacing-05);
}
```

```javascript
import styles from './MyComponent.module.css';

export const MyComponent = () => {
  return (
    <div className={styles.container}>
      <h2 className={styles.header}>Title</h2>
      <div className={styles.content}>
        <p>Content here</p>
      </div>
      <button className={styles.button}>Action</button>
    </div>
  );
};
```

### Responsive Grid Layout
```css
.grid-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: var(--cds-spacing-05);
  padding: var(--cds-spacing-05);
}

@media (max-width: 672px) {
  .grid-container {
    grid-template-columns: 1fr;
  }
}

@media (min-width: 1312px) {
  .grid-container {
    grid-template-columns: repeat(3, 1fr);
  }
}
```

## Accessibility Patterns

### Keyboard Navigation
```javascript
import { useEffect, useRef } from 'react';

export const AccessibleMenu = ({ items }) => {
  const menuRef = useRef(null);

  useEffect(() => {
    const handleKeyDown = (e) => {
      const focusableElements = menuRef.current.querySelectorAll(
        'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
      );
      const firstElement = focusableElements[0];
      const lastElement = focusableElements[focusableElements.length - 1];

      if (e.key === 'Tab') {
        if (e.shiftKey && document.activeElement === firstElement) {
          e.preventDefault();
          lastElement.focus();
        } else if (!e.shiftKey && document.activeElement === lastElement) {
          e.preventDefault();
          firstElement.focus();
        }
      }

      if (e.key === 'Escape') {
        // Close menu
      }
    };

    menuRef.current?.addEventListener('keydown', handleKeyDown);
    return () => menuRef.current?.removeEventListener('keydown', handleKeyDown);
  }, []);

  return (
    <nav ref={menuRef} role="navigation" aria-label="Main menu">
      {items.map((item) => (
        <button key={item.id} aria-label={item.label}>
          {item.label}
        </button>
      ))}
    </nav>
  );
};
```

### ARIA Live Regions
```javascript
export const StatusMessage = ({ message, type = 'polite' }) => {
  return (
    <div
      role="status"
      aria-live={type}
      aria-atomic="true"
      className="sr-only"
    >
      {message}
    </div>
  );
};

// Usage
const [status, setStatus] = useState('');

const handleAction = async () => {
  setStatus('Loading...');
  await performAction();
  setStatus('Action completed successfully');
};

return (
  <>
    <Button onClick={handleAction}>Perform Action</Button>
    <StatusMessage message={status} />
  </>
);
```

## Performance Optimization

### Code Splitting
```javascript
import { lazy, Suspense } from 'react';
import { Loading } from '@carbon/react';

const HeavyComponent = lazy(() => import('./HeavyComponent'));

export const App = () => {
  return (
    <Suspense fallback={<Loading description="Loading component..." />}>
      <HeavyComponent />
    </Suspense>
  );
};
```

### Memoization
```javascript
import { memo, useMemo, useCallback } from 'react';

// Memoize expensive component
export const ExpensiveComponent = memo(({ data, onUpdate }) => {
  // Component logic
  return <div>{/* Render */}</div>;
}, (prevProps, nextProps) => {
  // Custom comparison
  return prevProps.data.id === nextProps.data.id;
});

// Memoize expensive calculations
export const DataProcessor = ({ items }) => {
  const processedData = useMemo(() => {
    return items.map(item => ({
      ...item,
      computed: expensiveCalculation(item)
    }));
  }, [items]);

  const handleClick = useCallback((id) => {
    console.log('Clicked:', id);
  }, []);

  return (
    <div>
      {processedData.map(item => (
        <div key={item.id} onClick={() => handleClick(item.id)}>
          {item.computed}
        </div>
      ))}
    </div>
  );
};
```

## Error Boundaries
```javascript
import { Component } from 'react';
import { InlineNotification } from '@carbon/react';

export class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('Error caught by boundary:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <InlineNotification
          kind="error"
          title="Something went wrong"
          subtitle={this.state.error?.message || 'An unexpected error occurred'}
          onCloseButtonClick={() => this.setState({ hasError: false })}
        />
      );
    }

    return this.props.children;
  }
}

// Usage
<ErrorBoundary>
  <App />
</ErrorBoundary>
```

For the complete original guide with all sections, see the archived `frontend-guide.md` file.