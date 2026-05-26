# Turbonomic Dashboard - Troubleshooting Guide

## Overview
This guide documents common issues encountered when building the Turbonomic Resource Dashboard and their solutions.

---

## Issue 1: Carbon CSS Import Path Error

### Error Message
```
[plugin:vite:css] [postcss] ENOENT: no such file or directory, open '@carbon/react/css/index.css'
```

### Root Cause
Carbon Design System v11 does not have a `css/index.css` file in the `@carbon/react` package. The CSS structure changed in v11.

### Solution
**Option 1: Use CDN (Recommended for Quick Setup)**
```css
/* frontend/src/index.css */
@import 'https://unpkg.com/@carbon/styles@1.59.0/css/styles.min.css';
```

**Option 2: Import via JavaScript**
```javascript
// frontend/src/App.jsx
import '@carbon/charts-react/styles.css';
```

### Files Modified
- `frontend/src/index.css` - Added CDN import
- `frontend/src/main.jsx` - Removed incorrect imports

---

## Issue 2: Invalid Stack Component

### Error Message
```
Error: Element type is invalid: expected a string (for built-in components) or a class/function (for composite components) but got: undefined.
Check the render method of `App`.
```

### Root Cause
`Stack` component does not exist in Carbon Design System v11. It was incorrectly used in the configuration panel.

### Solution
Replace `Stack` with a styled `div` using flexbox:

```javascript
// ❌ WRONG
<Stack gap={5}>
  <TextInput />
</Stack>

// ✅ CORRECT
<div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
  <TextInput />
</div>
```

### Files Modified
- `frontend/src/App.jsx` - Lines 155 and 192

---

## Issue 3: TextInput.PasswordInput Not Found

### Error Message
```
Error: Element type is invalid: expected a string (for built-in components) or a class/function (for composite components) but got: undefined.
```

### Root Cause
In Carbon v11, `PasswordInput` is a separate component, not a sub-component of `TextInput`.

### Solution
Import and use `PasswordInput` as a standalone component:

```javascript
// ❌ WRONG
import { TextInput } from '@carbon/react';
<TextInput.PasswordInput />

// ✅ CORRECT
import { TextInput, PasswordInput } from '@carbon/react';
<PasswordInput />
```

### Files Modified
- `frontend/src/App.jsx` - Line 18 (import) and Line 174 (usage)

---

## Issue 4: @carbon/styles Package Not Found

### Error Message
```
npm error notarget No matching version found for @carbon/styles@^1.108.0
```

### Root Cause
`@carbon/styles` is not a separate npm package. Styles are included in `@carbon/react` or accessed via CDN.

### Solution
Remove `@carbon/styles` from dependencies and use CDN or component imports:

```json
// ❌ WRONG
{
  "dependencies": {
    "@carbon/styles": "^1.108.0"
  }
}

// ✅ CORRECT
{
  "dependencies": {
    "@carbon/react": "^1.108.0"
  }
}
```

### Files Modified
- `frontend/package.json` - Removed @carbon/styles dependency

---

## Issue 5: Missing Sass Dependency

### Error Message
```
[plugin:vite:css] [postcss] ENOENT: no such file or directory, open '@carbon/react/scss/index.scss'
```

### Root Cause
Attempting to import SCSS files without the `sass` package installed.

### Solution
Either:
1. Add `sass` to devDependencies if using SCSS imports
2. Use CSS imports or CDN instead (recommended)

```json
// If using SCSS
{
  "devDependencies": {
    "sass": "^1.77.0"
  }
}
```

### Files Modified
- `frontend/package.json` - Added sass to devDependencies (optional)

---

## Carbon Design System v11 - Correct Setup

### Recommended Package.json
```json
{
  "dependencies": {
    "@carbon/react": "^1.108.0",
    "@carbon/charts": "^1.27.11",
    "@carbon/charts-react": "^1.27.11",
    "@carbon/icons-react": "^11.49.0",
    "react": "^18.3.1",
    "react-dom": "^18.3.1",
    "axios": "^1.7.0"
  },
  "devDependencies": {
    "@vitejs/plugin-react": "^4.3.4",
    "vite": "^5.4.21",
    "sass": "^1.77.0"
  }
}
```

### Recommended CSS Import (index.css)
```css
/* Import Carbon Design System styles via CDN */
@import 'https://unpkg.com/@carbon/styles@1.59.0/css/styles.min.css';

/* Your custom styles */
* {
  box-sizing: border-box;
}
```

### Recommended Component Imports
```javascript
import {
  Header,
  HeaderName,
  Content,
  Theme,
  Button,
  TextInput,
  PasswordInput,  // Separate import, not TextInput.PasswordInput
  Accordion,
  AccordionItem,
  Tabs,
  TabList,
  Tab,
  TabPanels,
  TabPanel,
} from '@carbon/react';

import { Renew, Settings } from '@carbon/icons-react';
import '@carbon/charts-react/styles.css';
```

---

## Common Carbon v11 Component Changes

### Components That Changed

| v10 | v11 | Notes |
|-----|-----|-------|
| `TextInput.PasswordInput` | `PasswordInput` | Now separate component |
| `Stack` | Use `div` with flexbox | Component removed |
| `@carbon/react/css/index.css` | CDN or component imports | Path changed |
| `@carbon/styles` package | Use `@carbon/react` | Separate package doesn't exist |

---

## Issue 6: Carbon Charts Import Error - BarChart Not Found

### Error Message
```
Uncaught SyntaxError: The requested module '/node_modules/.vite/deps/@carbon_charts-react.js?v=5b9f3925' does not provide an export named 'BarChart'
```

### Root Cause
Carbon Charts v1.x does not export a component named `BarChart`. The correct component name is `SimpleBarChart`.

### Solution
Use the correct chart component names from Carbon Charts:

```javascript
// ❌ WRONG
import { DonutChart, BarChart } from '@carbon/charts-react';

<BarChart data={data} options={options} />

// ✅ CORRECT
import { DonutChart, SimpleBarChart } from '@carbon/charts-react';

<SimpleBarChart data={data} options={options} />
```

### Available Chart Components
Carbon Charts v1.x provides these chart components:
- `SimpleBarChart` ✅ (not `BarChart`)
- `GroupedBarChart` ✅
- `StackedBarChart` ✅
- `DonutChart` ✅
- `PieChart` ✅
- `LineChart` ✅
- `ScatterChart` ✅
- `AreaChart` ✅
- `BubbleChart` ✅
- `MeterChart` ✅
- `GaugeChart` ✅

### Files Modified
- `frontend/src/components/TurbonomicOverview.jsx` - Lines 3 and 133

### Reference
- [Carbon Charts Documentation](https://charts.carbondesignsystem.com/)
- [Carbon Charts React Components](https://charts.carbondesignsystem.com/?path=/docs/docs-tutorials-getting-started--docs)

---

## Debugging Tips

### 1. Check Component Imports
Always verify component names in Carbon v11 documentation:
- https://react.carbondesignsystem.com/

### 2. Inspect Browser Console
Look for specific error messages about undefined components or missing modules.

### 3. Verify Package Versions
```bash
npm list @carbon/react
npm list @carbon/charts-react
```

### 4. Clear Cache
```bash
rm -rf node_modules package-lock.json
npm install
```

### 5. Check Vite Dev Server
Restart the dev server after package.json changes:
```bash
npm run dev
```

---

## Quick Fix Checklist

When encountering Carbon-related errors:

- [ ] Remove `@carbon/styles` from package.json
- [ ] Use CDN import in index.css
- [ ] Import `PasswordInput` separately, not as `TextInput.PasswordInput`
- [ ] Replace `Stack` with styled `div`
- [ ] Import chart styles: `@carbon/charts-react/styles.css`
- [ ] Use `SimpleBarChart` instead of `BarChart` for bar charts
- [ ] Verify all Carbon components are imported from `@carbon/react`
- [ ] Check that `Theme` component wraps your app
- [ ] Ensure `sass` is in devDependencies if using SCSS

---

## Additional Resources

- [Carbon Design System v11 Documentation](https://carbondesignsystem.com/)
- [Carbon React Components](https://react.carbondesignsystem.com/)
- [Carbon Charts](https://charts.carbondesignsystem.com/)
- [Migration Guide v10 to v11](https://github.com/carbon-design-system/carbon/blob/main/docs/migration/v11.md)

---

**Last Updated:** 2026-05-22  
**Version:** 1.0.0  
**Maintainer:** Operations Dashboard Team