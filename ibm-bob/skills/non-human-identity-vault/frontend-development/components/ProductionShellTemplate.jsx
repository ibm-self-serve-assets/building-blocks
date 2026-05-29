// Production Shell Template
// Enterprise-grade application shell with IBM Carbon Design System

import React from 'react';
import {
  Header,
  HeaderContainer,
  HeaderName,
  HeaderMenuButton,
  HeaderGlobalBar,
  HeaderGlobalAction,
  SkipToContent,
  SideNav,
  SideNavItems,
  SideNavLink,
  Breadcrumb,
  BreadcrumbItem,
  Theme,
} from '@carbon/react';
import {
  Dashboard,
  Settings,
  Notification,
  UserAvatar,
  Information,
} from '@carbon/icons-react';
import './ProductionShell.scss';

/**
 * ProductionShell Component
 *
 * Provides a consistent enterprise UI shell with:
 * - Responsive header with hamburger menu
 * - Collapsible side navigation
 * - Breadcrumb navigation
 * - Global actions bar
 * - Carbon g100 dark theme
 *
 * @param {Object} props
 * @param {string} props.currentPage - Active page identifier
 * @param {Function} props.onNavigate - Navigation handler
 * @param {ReactNode} props.children - Page content
 * @param {string} props.theme - Carbon theme (default: 'g100')
 */
const ProductionShell = ({ children, currentPage = 'dashboard', onNavigate, theme = 'g100' }) => {
  const handleNavigation = (e, page) => {
    e.preventDefault();
    if (onNavigate) {
      onNavigate(page);
    }
  };

  // Define navigation items
  const navItems = [
    { id: 'dashboard', label: 'Dashboard', icon: Dashboard },
    { id: 'settings', label: 'Settings', icon: Settings },
    // Add more navigation items as needed
  ];

  // Define breadcrumbs based on current page
  const getBreadcrumbs = () => {
    const breadcrumbs = {
      dashboard: [
        { label: 'Home', page: 'dashboard', isCurrentPage: true }
      ],
      settings: [
        { label: 'Home', page: 'dashboard' },
        { label: 'Settings', page: 'settings', isCurrentPage: true }
      ],
      // Add more breadcrumb configurations
    };
    return breadcrumbs[currentPage] || breadcrumbs.dashboard;
  };

  return (
    <Theme theme={theme}>
      <HeaderContainer
        render={({ isSideNavExpanded, onClickSideNavExpand }) => (
          <>
            <Header aria-label="Application Platform">
            <SkipToContent />
            <HeaderMenuButton
              aria-label={isSideNavExpanded ? 'Close menu' : 'Open menu'}
              onClick={onClickSideNavExpand}
              isActive={isSideNavExpanded}
            />
            <HeaderName
              href="#"
              prefix="IBM"
              onClick={(e) => handleNavigation(e, 'dashboard')}
            >
              Application Name
            </HeaderName>
            <HeaderGlobalBar>
              <HeaderGlobalAction
                aria-label="Settings"
                tooltipAlignment="end"
                onClick={(e) => handleNavigation(e, 'settings')}
              >
                <Settings size={20} />
              </HeaderGlobalAction>
              <HeaderGlobalAction
                aria-label="Notifications"
                tooltipAlignment="end"
              >
                <Notification size={20} />
              </HeaderGlobalAction>
              <HeaderGlobalAction
                aria-label="User Settings"
                tooltipAlignment="end"
              >
                <UserAvatar size={20} />
              </HeaderGlobalAction>
              <HeaderGlobalAction
                aria-label="Information"
                tooltipAlignment="end"
              >
                <Information size={20} />
              </HeaderGlobalAction>
            </HeaderGlobalBar>
            <SideNav
              aria-label="Side navigation"
              expanded={isSideNavExpanded}
              isPersistent={false}
            >
              <SideNavItems>
                {navItems.map((item) => (
                  <SideNavLink
                    key={item.id}
                    renderIcon={item.icon}
                    href="#"
                    isActive={currentPage === item.id}
                    onClick={(e) => handleNavigation(e, item.id)}
                  >
                    {item.label}
                  </SideNavLink>
                ))}
              </SideNavItems>
            </SideNav>
          </Header>
          
          <div className="production-content">
            <div className="breadcrumb-container">
              <Breadcrumb noTrailingSlash>
                {getBreadcrumbs().map((crumb, index) => (
                  <BreadcrumbItem
                    key={index}
                    href="#"
                    isCurrentPage={crumb.isCurrentPage}
                    onClick={(e) => !crumb.isCurrentPage && handleNavigation(e, crumb.page)}
                  >
                    {crumb.label}
                  </BreadcrumbItem>
                ))}
              </Breadcrumb>
            </div>
            {children}
          </div>
          </>
        )}
      />
    </Theme>
  );
};

export default ProductionShell;

// Made with Bob
