import React, { useState } from 'react';
import { Theme, Grid, Column } from '@carbon/react';
import MaximoConfig from './components/MaximoConfig';
import Dashboard from './components/Dashboard';
import ScriptList from './components/ScriptList';
import ScriptDetail from './components/ScriptDetail';
import CodeConversion from './components/CodeConversion';
import BatchCodeConversion from './components/BatchCodeConversion';
import Header from './components/Header';
import Navigation from './components/Navigation';
import '@carbon/styles/css/styles.css';

function App() {
  const [activeTab, setActiveTab] = useState('config');
  const [selectedScript, setSelectedScript] = useState(null);

  const handleSelectScript = (script) => {
    setSelectedScript(script);
  };

  const handleCloseDetail = () => {
    setSelectedScript(null);
  };

  return (
    <Theme theme="g100">
      <div style={{ minHeight: '100vh', backgroundColor: 'var(--cds-background)' }}>
        <Header />
        <Navigation activeTab={activeTab} onTabChange={setActiveTab} />
        
        <Grid fullWidth style={{ padding: '2rem 0', marginTop: '3rem' }}>
          <Column sm={4} md={8} lg={16}>
            {activeTab === 'config' && <MaximoConfig />}
            {activeTab === 'dashboard' && <Dashboard />}
            {activeTab === 'scripts' && <ScriptList onSelectScript={handleSelectScript} />}
            {activeTab === 'conversion' && <CodeConversion />}
            {activeTab === 'batch-conversion' && <BatchCodeConversion />}
          </Column>
        </Grid>

        {selectedScript && (
          <ScriptDetail script={selectedScript} onClose={handleCloseDetail} />
        )}
      </div>
    </Theme>
  );
}

export default App;

// Made with Bob
