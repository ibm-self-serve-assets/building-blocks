---
name: frontend-development
description: Build enterprise-grade React applications with IBM Carbon Design System, including reusable components and responsive design patterns
---

Build React applications with IBM Carbon Design System:

<Steps>
<Step>
Setup React project with Carbon dependencies (@carbon/react, @carbon/icons-react)
</Step>
<Step>
Configure Carbon theme in SCSS (g100 dark theme recommended)
</Step>
<Step>
**CRITICAL**: Wrap app with Theme component: `<Theme theme="g100">` - SCSS alone is insufficient
</Step>
<Step>
Use ProductionShell template from `components/ProductionShellTemplate.jsx` for navigation
</Step>
<Step>
Build components using Carbon components (never create custom versions)
</Step>
<Step>
Apply responsive design with Carbon Grid system (lg, md, sm breakpoints)
</Step>
<Step>
Use shared styles from `styles/SharedStyles.scss` for consistency
</Step>
<Step>
Implement proper state management and API integration patterns
</Step>
<Step>
Ensure accessibility with ARIA labels and keyboard navigation
</Step>
<Step>
Test across breakpoints and build for production
</Step>
</Steps>

**Key Resources:**
- `carbon-design-guide.md` - Quick reference for Carbon components
- `components/ProductionShellTemplate.jsx` - Enterprise shell with header, side nav, breadcrumbs
- `styles/SharedStyles.scss` - Reusable styles, utilities, animations

**Essential Patterns:**
- **MUST wrap app with Theme component**: `<Theme theme="g100"><App /></Theme>`
- Always use Carbon Grid: `<Grid fullWidth><Column lg={16}>`
- Use design tokens: `var(--cds-text-primary)`, `$spacing-05`
- Follow ProductionShell pattern for consistent navigation
- Add loading states: `<Loading description="Loading..." />`
- Handle errors: `<InlineNotification kind="error" />`

**Common Issues:**
- **White background on dark theme**: Missing Theme component wrapper - add `<Theme theme="g100">` around app
- Hamburger menu not visible: Add `.cds--header__menu-toggle { display: flex !important; }`
- Styles not loading: Verify SCSS imports order (themes → theme → react)
- Components not rendering: Check imports and exports match
- Menu not auto-closing: Pass `onClickSideNavExpand` to navigation handlers (see `app-capabilities.md`)
- Theme not applying: Ensure both SCSS config AND Theme component wrapper are present

**Application Reference:**
See `app-capabilities.md` for complete feature list, navigation structure, and recent implementations including the menu auto-close fix.