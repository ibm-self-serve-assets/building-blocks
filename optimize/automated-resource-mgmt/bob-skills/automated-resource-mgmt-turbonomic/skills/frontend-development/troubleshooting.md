# Frontend Troubleshooting Guide

Common issues and solutions for Carbon Design System v11 and React development.

## Carbon CSS Import Errors

### Error: ENOENT: no such file or directory, open '@carbon/react/css/index.css'

**Root Cause:** Carbon Design System v11 does not have a `css/index.css` file in the `@carbon/react` package.

**Solution:**
```css
/* Use CDN import in index.css */
@import 'https://unpkg.com/@carbon/styles@1.59.0/css/styles.min.css';
```

Or import via JavaScript:
```javascript
import '@carbon/charts-react/styles.css';
```

## Component Import Issues

### Error: Stack component is undefined

**Root Cause:** `Stack` component does not exist in Carbon Design System v11.

**Solution:** Replace with flexbox:
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

### Error: PasswordInput is undefined

**Root Cause:** In Carbon v11, `PasswordInput` is a separate component, not a sub-component of `TextInput`.

**Solution:**
```javascript
// ❌ WRONG
import { TextInput } from '@carbon/react';
<TextInput.PasswordInput />

// ✅ CORRECT
import { TextInput, PasswordInput } from '@carbon/react';
<PasswordInput />
```

### Error: BarChart is not exported

**Root Cause:** Carbon Charts v1.x does not export `BarChart`. The correct name is `SimpleBarChart`.

**Solution:**
```javascript
// ❌ WRONG
import { BarChart } from '@carbon/charts-react';

// ✅ CORRECT
import { SimpleBarChart } from '@carbon/charts-react';
```

## Package Dependency Issues

### Error: No matching version found for @carbon/styles

**Root Cause:** `@carbon/styles` is not a separate npm package.

**Solution:** Remove from package.json and use CDN or component imports:
```json
{
  "dependencies": {
    "@carbon/react": "^1.108.0",
    "@carbon/charts-react": "^1.27.11"
  }
}
```

## Build Issues

### Vite build fails with SASS errors

**Solution:** Add sass to devDependencies:
```json
{
  "devDependencies": {
    "sass": "^1.77.0"
  }
}
```

### Module not found errors

**Solution:** Clear cache and reinstall:
```bash
rm -rf node_modules package-lock.json
npm install
```

## Runtime Issues

### Styles not applied

**Checklist:**
- [ ] Carbon CSS imported in index.css or main.jsx
- [ ] Theme component wraps your app
- [ ] Component imports are correct
- [ ] No conflicting CSS overriding Carbon styles

### Chart not rendering

**Checklist:**
- [ ] Chart styles imported: `import '@carbon/charts-react/styles.css'`
- [ ] Data format matches chart requirements
- [ ] Container has defined height
- [ ] Using correct chart component name (e.g., `SimpleBarChart` not `BarChart`)

## Carbon v11 Component Changes

| v10 | v11 | Notes |
|-----|-----|-------|
| `TextInput.PasswordInput` | `PasswordInput` | Now separate component |
| `Stack` | Use `div` with flexbox | Component removed |
| `@carbon/react/css/index.css` | CDN or component imports | Path changed |
| `BarChart` | `SimpleBarChart` | Component renamed |

## Quick Fix Checklist

- [ ] Remove `@carbon/styles` from package.json
- [ ] Use CDN import in index.css
- [ ] Import `PasswordInput` separately
- [ ] Replace `Stack` with styled `div`
- [ ] Import chart styles
- [ ] Use `SimpleBarChart` for bar charts
- [ ] Verify all imports from `@carbon/react`
- [ ] Ensure `Theme` component wraps app

## Debugging Steps

1. **Check Browser Console** - Look for specific error messages
2. **Verify Package Versions** - Run `npm list @carbon/react`
3. **Clear Cache** - Delete node_modules and reinstall
4. **Restart Dev Server** - After package.json changes
5. **Check Network Tab** - Verify CSS files are loading

## Resources

- [Carbon Design System v11 Documentation](https://carbondesignsystem.com/)
- [Carbon React Components](https://react.carbondesignsystem.com/)
- [Carbon Charts](https://charts.carbondesignsystem.com/)
- [Migration Guide v10 to v11](https://github.com/carbon-design-system/carbon/blob/main/docs/migration/v11.md)