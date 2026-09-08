import React from 'react';
import { Tabs, TabList, Tab } from '@carbon/react';
import { Dashboard, Code, Settings, Renew } from '@carbon/icons-react';

const Navigation = ({ activeTab, onTabChange }) => {
  const tabs = [
    { id: 'config', label: 'Configuration', icon: Settings },
    { id: 'dashboard', label: 'Dashboard', icon: Dashboard },
    { id: 'scripts', label: 'Scripts', icon: Code },
    { id: 'conversion', label: 'Java Code Conversion', icon: Renew },
  ];

  const selectedIndex = tabs.findIndex(tab => tab.id === activeTab);

  return (
    <div style={{ 
      backgroundColor: 'var(--cds-layer-01)', 
      borderBottom: '1px solid var(--cds-border-subtle-01)',
      position: 'sticky',
      top: '48px',
      zIndex: 100
    }}>
      <Tabs
        selectedIndex={selectedIndex}
        onChange={({ selectedIndex }) => {
          onTabChange(tabs[selectedIndex].id);
        }}
      >
        <TabList aria-label="Navigation tabs" contained>
          {tabs.map((tab) => {
            const Icon = tab.icon;
            return (
              <Tab key={tab.id} renderIcon={Icon}>
                {tab.label}
              </Tab>
            );
          })}
        </TabList>
      </Tabs>
    </div>
  );
};

export default Navigation;

// Made with Bob
