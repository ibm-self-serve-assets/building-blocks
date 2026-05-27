---
name: frontend-development
description: Comprehensive React and Carbon Design System development for building modern, accessible UI components with proper styling, state management, and performance optimization
---

# Frontend Development Skill

Use this skill when building or modifying frontend components, implementing UI designs, working with Carbon Design System, ensuring design consistency, or writing user-facing content.

## When to Use This Skill

- Creating new React components
- Implementing Carbon Design System components
-  Styling components and layouts
- Managing component state and hooks
- Optimizing frontend performance
- Writing accessible UI code
- Creating user-facing content and copy

## Core Technologies

- React 18 with hooks
- Carbon Design System v11
- Vite build tool
- CSS/SASS for styling
- Carbon Charts for data visualization

## Key Principles

1. **Component-First Architecture** - Build reusable, focused components
2. **Carbon Design Consistency** - Follow IBM Carbon Design System patterns
3. **Accessibility** - Ensure WCAG 2.1 AA compliance
4. **Performance** - Optimize rendering and bundle size
5. **User-Centered Content** - Write clear, concise UI text

## Quick Reference

### React Component Pattern
```javascript
import { useState, useEffect } from 'react';
import { Button, TextInput } from '@carbon/react';

export const MyComponent = ({ initialValue }) => {
  const [value, setValue] = useState(initialValue);
  
  useEffect(() => {
    // Side effects here
  }, [value]);
  
  return (
    <div>
      <TextInput
        id="input"
        labelText="Label"
        value={value}
        onChange={(e) => setValue(e.target.value)}
      />
      <Button onClick={() => console.log(value)}>
        Submit
      </Button>
    </div>
  );
};
```

### Carbon Design System Setup
```javascript
// Import Carbon styles (in main.jsx or index.css)
import '@carbon/charts-react/styles.css';

// Or use CDN in index.css
@import 'https://unpkg.com/@carbon/styles@1.59.0/css/styles.min.css';

// Import components
import {
  Theme,
  Button,
  TextInput,
  PasswordInput,  // Separate component in v11
  DataTable,
  Tabs,
  TabList,
  Tab
} from '@carbon/react';
```

### Common Patterns

**State Management:**
- Use `useState` for local component state
- Use `useContext` for shared state across components
- Lift state up when multiple components need access

**Performance Optimization:**
- Use `React.memo()` for expensive components
- Use `useCallback` for function props
- Use `useMemo` for expensive calculations
- Implement code splitting with `React.lazy()`

**Accessibility:**
- Always include ARIA labels
- Ensure keyboard navigation works
- Maintain proper color contrast (4.5:1 minimum)
- Use semantic HTML elements

## Important Notes

### Carbon v11 Changes
- `PasswordInput` is now a separate component (not `TextInput.PasswordInput`)
- `Stack` component removed - use flexbox with styled divs
- Import styles via CDN or component imports
- Use `SimpleBarChart` instead of `BarChart` for bar charts

### File Organization
```
frontend/src/
├── components/          # Reusable components
├── services/           # API clients
├── hooks/              # Custom hooks
├── utils/              # Helper functions
├── App.jsx             # Main app component
└── main.jsx            # Entry point
```

## Supporting Documentation

Refer to the following files in this skill folder for detailed guidance:
- `react-patterns.md` - React development patterns and hooks
- `carbon-components.md` - Carbon Design System component usage
- `styling-guide.md` - CSS architecture and styling patterns
- `accessibility.md` - Accessibility standards and implementation
- `content-guidelines.md` - Writing standards for UI text

## Best Practices

### DO ✅
- Use functional components with hooks
- Follow Carbon Design System patterns
- Write accessible, semantic HTML
- Optimize performance with memoization
- Keep components focused and reusable
- Test components thoroughly
- Use TypeScript or PropTypes for type safety

### DON'T ❌
- Use class components (prefer functional)
- Ignore accessibility requirements
- Hardcode styles (use Carbon tokens)
- Create overly complex components
- Skip error boundaries
- Forget to handle loading/error states
- Use inline styles excessively

## Troubleshooting

Common issues and solutions are documented in `troubleshooting.md` in this folder.

## Resources

- [React Documentation](https://react.dev/)
- [Carbon Design System](https://carbondesignsystem.com/)
- [Carbon React Components](https://react.carbondesignsystem.com/)
- [Carbon Charts](https://charts.carbondesignsystem.com/)
- [WCAG Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)