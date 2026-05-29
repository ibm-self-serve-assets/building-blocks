# Secret Scanner Application Capabilities

## Core Features

### 1. Dashboard
- Overview of scanning statistics and recent activity
- Real-time metrics display
- Quick access to all major features
- Visual representation of scan results

### 2. Secret Scanner
- Code scanning for hardcoded secrets and sensitive data
- Pattern-based detection (40+ secret patterns)
- Real-time scanning feedback
- Detailed findings with severity levels

### 3. Vault Status
- HashiCorp Vault connection monitoring
- Health status checks
- Seal/unseal status display
- Connection diagnostics

### 4. Git Repository Scanner
- Scan entire Git repositories for secrets
- Support for remote and local repositories
- Branch-specific scanning
- Historical commit analysis

### 5. Refactored Code Documentation
- Documentation for code remediation patterns
- Best practices for secret management
- Code examples and templates
- Integration guides

### 6. Settings
- Application configuration
- Vault connection settings
- Scan preferences
- User preferences

## Navigation Structure

The application uses IBM Carbon Design System's ProductionShell pattern with:
- **Header**: Application branding and global actions
- **Side Navigation**: Main feature navigation
- **Breadcrumbs**: Current location context
- **Content Area**: Feature-specific content

## Recent Implementations

### Carbon g100 Dark Theme (2026-05-28)

**Problem**: Application was displaying with white/light background instead of dark theme, despite SCSS theme configuration.

**Root Cause**: SCSS theme imports alone are insufficient - Carbon requires the `Theme` component wrapper to properly apply theme tokens to all components.

**Solution**: Wrapped application with Carbon's `Theme` component and added CSS overrides for custom containers.

**Implementation Details**:

```jsx
// App.js - Wrap entire app with Theme component
import { Theme } from '@carbon/react';

function App() {
  return (
    <Theme theme="g100">
      <Router>
        <AppContent />
      </Router>
    </Theme>
  );
}
```

```scss
// App.scss - Override Carbon Content and ensure dark backgrounds
.cds--content {
  background: var(--cds-background) !important;
  color: var(--cds-text-primary);
}

html,
body,
#root {
  background: var(--cds-background);
  color: var(--cds-text-primary);
}

.production-content,
.app-container {
  background: var(--cds-background);
}
```

**Result**:
- Consistent dark background throughout entire application
- Proper Carbon g100 theme colors applied to all components
- Excellent contrast and readability
- Professional enterprise appearance

**Files Modified**:
- `frontend/src/App.js` - Added Theme wrapper
- `frontend/src/App.scss` - Added theme-specific CSS overrides

### Menu Auto-Close (2026-05-28)

**Problem**: Side navigation menu remained open after clicking menu items, requiring manual close.

**Solution**: Implemented auto-close functionality in ProductionShell component.

**Implementation Details**:

```javascript
// Modified handleNavigation to accept closeSideNav parameter
const handleNavigation = (e, page, closeSideNav) => {
  e.preventDefault();
  if (onNavigate) {
    onNavigate(page);
  }
  // Auto-close the side navigation menu after navigation
  if (closeSideNav) {
    closeSideNav();
  }
};

// Updated all navigation click handlers
onClick={(e) => handleNavigation(e, 'dashboard', onClickSideNavExpand)}
```

**Applied To**:
- Header name (IBM Secret Scanner logo)
- Settings icon in global header
- All 6 side navigation menu items
- Breadcrumb navigation links

**Result**: Side navigation menu now automatically closes when any menu option is clicked, providing a cleaner user experience.

**File Modified**: `secret_scanner_app/frontend/src/components/ProductionShell.js`

## Technical Stack

- **Frontend**: React 18+ with IBM Carbon Design System
- **Backend**: Flask (Python) REST API
- **Security**: HashiCorp Vault integration
- **Styling**: SCSS with Carbon design tokens
- **Icons**: Carbon Icons React