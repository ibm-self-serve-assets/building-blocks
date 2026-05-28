# IBM Carbon Design System Quick Reference

## Theme Setup

### SCSS Theme Configuration

```scss
@use '@carbon/react/scss/themes';
@use '@carbon/react/scss/theme' with (
  $theme: themes.$g100  // Dark theme (g10, g90, g100, white)
);
@use '@carbon/react';
@use '@carbon/react/scss/spacing' as *;
@use '@carbon/react/scss/type' as *;
```

### React Theme Component (REQUIRED)

**IMPORTANT**: You MUST wrap your app with the `Theme` component to properly apply Carbon themes. SCSS imports alone are not sufficient.

```jsx
import { Theme } from '@carbon/react';

function App() {
  return (
    <Theme theme="g100">
      {/* Your app content */}
    </Theme>
  );
}
```

**Available Themes:**
- `white` - White theme (light)
- `g10` - Gray 10 theme (light)
- `g90` - Gray 90 theme (dark)
- `g100` - Gray 100 theme (darkest) ⭐ Recommended for enterprise apps

### Theme-Specific CSS Overrides

When using g100 theme, ensure dark backgrounds are applied:

```scss
// Override Carbon Content component background
.cds--content {
  background: var(--cds-background) !important;
  color: var(--cds-text-primary);
}

// Ensure root elements have dark background
html,
body,
#root {
  margin: 0;
  padding: 0;
  min-height: 100vh;
  background: var(--cds-background);
  color: var(--cds-text-primary);
}

// Content containers
.production-content,
.app-container {
  background: var(--cds-background);
}
```

## Grid System

```jsx
<Grid fullWidth>
  <Column lg={16} md={8} sm={4}>Full width</Column>
  <Column lg={8} md={4} sm={4}>Half width on large</Column>
  <Column lg={4} md={2} sm={4}>Quarter width on large</Column>
</Grid>
```

**Breakpoints:**
- sm: 320px - 671px (mobile)
- md: 672px - 1055px (tablet)
- lg: 1056px - 1311px (desktop)
- xlg: 1312px - 1583px (large desktop)
- max: 1584px+ (extra large)

## Common Components

### Header & Navigation
```jsx
<HeaderContainer
  render={({ isSideNavExpanded, onClickSideNavExpand }) => (
    <>
      <Header>
        <HeaderMenuButton onClick={onClickSideNavExpand} />
        <HeaderName prefix="IBM">App Name</HeaderName>
        <SideNav expanded={isSideNavExpanded}>
          <SideNavItems>
            <SideNavLink renderIcon={Dashboard}>Dashboard</SideNavLink>
          </SideNavItems>
        </SideNav>
      </Header>
    </>
  )}
/>
```

### Forms
```jsx
<TextInput
  id="field"
  labelText="Label"
  value={value}
  onChange={(e) => setValue(e.target.value)}
/>

<Button kind="primary" onClick={handleClick}>Submit</Button>
```

### Data Display
```jsx
<Tile>Content here</Tile>
<ClickableTile onClick={handleClick}>Clickable content</ClickableTile>

<DataTable rows={rows} headers={headers}>
  {({ rows, headers, getTableProps }) => (
    <Table {...getTableProps()}>
      <TableHead>
        <TableRow>
          {headers.map(header => (
            <TableHeader key={header.key}>{header.header}</TableHeader>
          ))}
        </TableRow>
      </TableHead>
      <TableBody>
        {rows.map(row => (
          <TableRow key={row.id}>
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

### Notifications
```jsx
<InlineNotification
  kind="error"  // success, info, warning, error
  title="Error"
  subtitle="Error message"
  onCloseButtonClick={() => setError(null)}
/>
```

### Loading States
```jsx
<Loading description="Loading..." withOverlay={false} />
```

## Typography

```scss
.title {
  @include type-style('productive-heading-05');
}

.subtitle {
  @include type-style('body-long-02');
}
```

## Spacing

```scss
.component {
  padding: $spacing-05;  // 1rem
  margin: $spacing-07;   // 2rem
  gap: $spacing-03;      // 0.5rem
}
```

## Colors (Design Tokens)

### Background Colors
```scss
.component {
  background: var(--cds-background);        // Main background
  background: var(--cds-layer-01);          // First layer (tiles, cards)
  background: var(--cds-layer-02);          // Second layer (nested elements)
  background: var(--cds-layer-03);          // Third layer (deeply nested)
  background: var(--cds-background-inverse); // Inverse background (header)
}
```

### Text Colors
```scss
.text {
  color: var(--cds-text-primary);    // Primary text
  color: var(--cds-text-secondary);  // Secondary text
  color: var(--cds-text-placeholder); // Placeholder text
  color: var(--cds-text-on-color);   // Text on colored backgrounds
  color: var(--cds-text-inverse);    // Inverse text (on dark)
}
```

### Border Colors
```scss
.bordered {
  border: 1px solid var(--cds-border-subtle);  // Subtle borders
  border: 1px solid var(--cds-border-strong);  // Strong borders
  border: 1px solid var(--cds-border-inverse); // Inverse borders
}
```

### Interactive Colors
```scss
.interactive {
  color: var(--cds-link-primary);           // Links
  background: var(--cds-interactive);       // Interactive elements
  background: var(--cds-focus);             // Focus states
  background: var(--cds-hover-ui);          // Hover states
}
```

### Status Colors
```scss
.status {
  color: var(--cds-support-error);    // Error state
  color: var(--cds-support-success);  // Success state
  color: var(--cds-support-warning);  // Warning state
  color: var(--cds-support-info);     // Info state
}
```

### g100 Theme Specific Values
When using `theme="g100"`, these tokens resolve to:
- `--cds-background`: `#161616` (near black)
- `--cds-layer-01`: `#262626` (dark gray)
- `--cds-layer-02`: `#393939` (medium gray)
- `--cds-text-primary`: `#f4f4f4` (near white)
- `--cds-text-secondary`: `#c6c6c6` (light gray)

## Icons

```jsx
import { Add, Close, Settings } from '@carbon/icons-react';

<Button renderIcon={Add}>Add Item</Button>
<Settings size={20} />
```

## Accessibility

- Use semantic HTML elements
- Add `aria-label` for screen readers
- Support keyboard navigation (Tab, Enter, Escape)
- Ensure proper focus management
- Meet WCAG AA color contrast standards
- Provide alt text for images

## Responsive Design

```scss
@media (max-width: 672px) {
  .component {
    padding: $spacing-03;
  }
}
```

## Best Practices

1. **Always use Carbon components** - Don't create custom versions
2. **Follow the grid system** - Use Column components for layout
3. **Use design tokens** - Never hardcode colors, spacing, or typography
4. **Test responsiveness** - Check all breakpoints
5. **Ensure accessibility** - Add ARIA labels and keyboard support
6. **Keep it consistent** - Follow Carbon patterns throughout