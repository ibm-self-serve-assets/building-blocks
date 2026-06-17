import React, { useState, useEffect } from 'react';
import {
  Grid,
  Column,
  Tile,
  TextInput,
  Button,
  InlineNotification,
  Loading,
  Form,
  FormGroup,
  PasswordInput,
  Select,
  SelectItem,
} from '@carbon/react';
import { CheckmarkFilled, ConnectionSignal, Save, Add, Checkmark } from '@carbon/icons-react';
import { connectionAPI } from '../services/api';

const MaximoConfig = () => {
  const [environments, setEnvironments] = useState([]);
  const [selectedEnv, setSelectedEnv] = useState('');
  const [isAddingNew, setIsAddingNew] = useState(false);
  const [config, setConfig] = useState({
    environmentName: '',
    maximoUrl: '',
    apiKey: '',
  });
  const [testing, setTesting] = useState(false);
  const [saving, setSaving] = useState(false);
  const [testResult, setTestResult] = useState(null);
  const [error, setError] = useState(null);
  const [isTestSuccessful, setIsTestSuccessful] = useState(false);
  const [fieldsReadOnly, setFieldsReadOnly] = useState(false);

  useEffect(() => {
    loadEnvironments();
  }, []);

  const loadEnvironments = () => {
    const saved = localStorage.getItem('maximoEnvironments');
    if (saved) {
      const parsedEnvs = JSON.parse(saved);
      setEnvironments(parsedEnvs);
      if (parsedEnvs.length > 0 && !selectedEnv) {
        setSelectedEnv(parsedEnvs[0].environmentName);
        loadEnvironmentConfig(parsedEnvs[0].environmentName, parsedEnvs);
      }
    }
  };

  const loadEnvironmentConfig = (envName, envList = environments) => {
    const env = envList.find(e => e.environmentName === envName);
    if (env) {
      setConfig(env);
      // Save as active config for API interceptor
      localStorage.setItem('maximoConfig', JSON.stringify(env));
      setFieldsReadOnly(true);
      setIsTestSuccessful(false);
      setTestResult(null);
      setError(null);
    }
  };

  const handleEnvironmentSelect = (e) => {
    const envName = e.target.value;
    setSelectedEnv(envName);
    setIsAddingNew(false);
    loadEnvironmentConfig(envName);
  };

  const handleAddNewEnvironment = () => {
    setIsAddingNew(true);
    setSelectedEnv('');
    setConfig({
      environmentName: '',
      maximoUrl: '',
      apiKey: '',
      username: '',
    });
    setFieldsReadOnly(false);
    setIsTestSuccessful(false);
    setTestResult(null);
    setError(null);
  };

  const handleInputChange = (field, value) => {
    setConfig(prev => ({ ...prev, [field]: value }));
    setTestResult(null);
    setError(null);
    setIsTestSuccessful(false);
  };

  const handleTestConnection = async () => {
    try {
      setTesting(true);
      setError(null);
      setTestResult(null);

      const result = await connectionAPI.testConnection(config);
      
      setTestResult({
        success: true,
        message: result.message || 'Connection successful!',
        scriptsFound: result.scriptsFound || 0,
      });
      setIsTestSuccessful(true);
      setFieldsReadOnly(true);
    } catch (err) {
      setError(err.message);
      setTestResult({ success: false });
      setIsTestSuccessful(false);
    } finally {
      setTesting(false);
    }
  };

  const handleSaveConfig = () => {
    try {
      setSaving(true);
      
      // Validate environment name
      if (!config.environmentName.trim()) {
        setError('Environment name is required');
        setSaving(false);
        return;
      }

      let updatedEnvs = [...environments];
      const existingIndex = updatedEnvs.findIndex(e => e.environmentName === config.environmentName);
      
      if (existingIndex >= 0) {
        updatedEnvs[existingIndex] = config;
      } else {
        updatedEnvs.push(config);
      }
      
      localStorage.setItem('maximoEnvironments', JSON.stringify(updatedEnvs));
      // Also save the current active config for API interceptor
      localStorage.setItem('maximoConfig', JSON.stringify(config));
      setEnvironments(updatedEnvs);
      setSelectedEnv(config.environmentName);
      setIsAddingNew(false);
      
      setTimeout(() => {
        setSaving(false);
        setTestResult({
          success: true,
          message: 'Configuration saved successfully!',
        });
        setIsTestSuccessful(false);
      }, 500);
    } catch (err) {
      setError('Failed to save configuration');
      setSaving(false);
    }
  };

  const isConfigValid = config.maximoUrl && config.apiKey && config.environmentName;

  return (
    <Grid style={{ paddingTop: '3rem' }}>
      {/* Header */}
      <Column sm={4} md={8} lg={16}>
        <div style={{ marginBottom: '2rem' }}>
          <h2 style={{ fontSize: '2rem', fontWeight: '400', marginBottom: '0.5rem' }}>
            Maximo Environment Configuration
          </h2>
          <p style={{ color: 'var(--cds-text-secondary)' }}>
            Configure your Maximo instance connection to fetch and analyze automation scripts.
          </p>
        </div>
      </Column>

      {/* Configuration Form */}
      <Column sm={4} md={8} lg={10}>
        <Tile style={{ padding: '2rem' }}>
          <Form>
            {/* Environment Selection */}
            <FormGroup legendText="" style={{ marginBottom: '2rem' }}>
              <Select
                id="environment-select"
                labelText="Select Environment"
                value={selectedEnv}
                onChange={handleEnvironmentSelect}
                disabled={isAddingNew}
              >
                <SelectItem value="" text="Choose an environment" />
                {environments.map((env) => (
                  <SelectItem
                    key={env.environmentName}
                    value={env.environmentName}
                    text={env.environmentName}
                  />
                ))}
              </Select>
            </FormGroup>

            {/* Add New Environment Button */}
            <div style={{ marginBottom: '2rem', marginTop: '1rem' }}>
              <Button
                kind="primary"
                renderIcon={Add}
                onClick={handleAddNewEnvironment}
                size="md"
                style={{
                  background: 'linear-gradient(135deg, #0f62fe 0%, #0043ce 100%)',
                  border: 'none',
                  borderRadius: '6px',
                  boxShadow: '0 2px 8px rgba(15, 98, 254, 0.25)',
                  transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                  fontWeight: '500'
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.transform = 'translateY(-2px)';
                  e.currentTarget.style.boxShadow = '0 4px 12px rgba(15, 98, 254, 0.35)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.transform = 'translateY(0)';
                  e.currentTarget.style.boxShadow = '0 2px 8px rgba(15, 98, 254, 0.25)';
                }}
              >
                Add New Environment
              </Button>
            </div>

            {/* Show fields only when adding new or editing */}
            {(isAddingNew || selectedEnv) && (
              <>
                {/* Environment Name (only for new) */}
                {isAddingNew && (
                  <FormGroup legendText="">
                    <TextInput
                      id="environment-name"
                      labelText="Environment Name"
                      placeholder="e.g., Dev, Test, Production"
                      value={config.environmentName}
                      onChange={(e) => handleInputChange('environmentName', e.target.value)}
                      helperText="Enter a unique name for this environment"
                      readOnly={fieldsReadOnly && !isAddingNew}
                    />
                  </FormGroup>
                )}

                <FormGroup legendText="">
                  <TextInput
                    id="maximo-url"
                    labelText="Maximo Instance URL"
                    placeholder="https://your-maximo-instance.com"
                    value={config.maximoUrl}
                    onChange={(e) => handleInputChange('maximoUrl', e.target.value)}
                    helperText="Enter the base URL of your Maximo instance"
                    readOnly={fieldsReadOnly}
                  />
                </FormGroup>

                <FormGroup legendText="">
                  <PasswordInput
                    id="api-key"
                    labelText="API Key"
                    placeholder="Enter your Maximo API key"
                    value={config.apiKey}
                    onChange={(e) => handleInputChange('apiKey', e.target.value)}
                    helperText="Required for authentication"
                    readOnly={fieldsReadOnly}
                  />
                </FormGroup>

                <div style={{ display: 'flex', gap: '12px', marginTop: '2rem', flexWrap: 'wrap' }}>
                  <button
                    onClick={handleTestConnection}
                    disabled={!isConfigValid || testing || fieldsReadOnly}
                    style={{
                      flex: '1',
                      minWidth: '200px',
                      padding: '14px 24px',
                      background: isTestSuccessful && !fieldsReadOnly
                        ? 'linear-gradient(135deg, #24a148 0%, #198038 100%)'
                        : 'linear-gradient(135deg, #0f62fe 0%, #0043ce 100%)',
                      border: 'none',
                      borderRadius: '8px',
                      color: 'white',
                      fontSize: '15px',
                      fontWeight: '600',
                      cursor: (!isConfigValid || testing || fieldsReadOnly) ? 'not-allowed' : 'pointer',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      gap: '10px',
                      boxShadow: isTestSuccessful
                        ? '0 4px 16px rgba(36, 161, 72, 0.3)'
                        : '0 4px 12px rgba(15, 98, 254, 0.25)',
                      transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                      opacity: (!isConfigValid || testing || fieldsReadOnly) ? 0.5 : 1,
                      animation: isTestSuccessful && !fieldsReadOnly ? 'pulse 1.5s ease-in-out' : 'none'
                    }}
                    onMouseEnter={(e) => {
                      if (!e.currentTarget.disabled) {
                        e.currentTarget.style.transform = 'translateY(-3px) scale(1.02)';
                        e.currentTarget.style.boxShadow = isTestSuccessful
                          ? '0 8px 24px rgba(36, 161, 72, 0.4)'
                          : '0 8px 20px rgba(15, 98, 254, 0.4)';
                      }
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.transform = 'translateY(0) scale(1)';
                      e.currentTarget.style.boxShadow = isTestSuccessful
                        ? '0 4px 16px rgba(36, 161, 72, 0.3)'
                        : '0 4px 12px rgba(15, 98, 254, 0.25)';
                    }}
                    onMouseDown={(e) => {
                      if (!e.currentTarget.disabled) {
                        e.currentTarget.style.transform = 'translateY(-1px) scale(0.98)';
                      }
                    }}
                    onMouseUp={(e) => {
                      if (!e.currentTarget.disabled) {
                        e.currentTarget.style.transform = 'translateY(-3px) scale(1.02)';
                      }
                    }}
                  >
                    <ConnectionSignal size={20} />
                    <span>{testing ? 'Testing...' : isTestSuccessful ? 'Test Successful!' : 'Test Connection'}</span>
                  </button>
                  
                  <button
                    onClick={handleSaveConfig}
                    disabled={!isConfigValid || !isTestSuccessful || saving}
                    style={{
                      flex: '1',
                      minWidth: '200px',
                      padding: '14px 24px',
                      background: isTestSuccessful
                        ? 'linear-gradient(135deg, #8a3ffc 0%, #6929c4 100%)'
                        : 'linear-gradient(135deg, #8d8d8d 0%, #6f6f6f 100%)',
                      border: 'none',
                      borderRadius: '8px',
                      color: 'white',
                      fontSize: '15px',
                      fontWeight: '600',
                      cursor: (!isConfigValid || !isTestSuccessful || saving) ? 'not-allowed' : 'pointer',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      gap: '10px',
                      boxShadow: isTestSuccessful
                        ? '0 4px 16px rgba(138, 63, 252, 0.3)'
                        : '0 4px 12px rgba(141, 141, 141, 0.2)',
                      transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                      opacity: (!isConfigValid || !isTestSuccessful || saving) ? 0.5 : 1,
                      animation: isTestSuccessful ? 'pulse 1.5s ease-in-out infinite' : 'none'
                    }}
                    onMouseEnter={(e) => {
                      if (!e.currentTarget.disabled) {
                        e.currentTarget.style.transform = 'translateY(-3px) scale(1.02)';
                        e.currentTarget.style.boxShadow = '0 8px 24px rgba(138, 63, 252, 0.4)';
                      }
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.transform = 'translateY(0) scale(1)';
                      e.currentTarget.style.boxShadow = isTestSuccessful
                        ? '0 4px 16px rgba(138, 63, 252, 0.3)'
                        : '0 4px 12px rgba(141, 141, 141, 0.2)';
                    }}
                    onMouseDown={(e) => {
                      if (!e.currentTarget.disabled) {
                        e.currentTarget.style.transform = 'translateY(-1px) scale(0.98)';
                      }
                    }}
                    onMouseUp={(e) => {
                      if (!e.currentTarget.disabled) {
                        e.currentTarget.style.transform = 'translateY(-3px) scale(1.02)';
                      }
                    }}
                  >
                    {isTestSuccessful ? <Checkmark size={20} /> : <Save size={20} />}
                    <span>{saving ? 'Saving...' : 'Save Configuration'}</span>
                  </button>

                  {fieldsReadOnly && !isAddingNew && (
                    <button
                      onClick={() => setFieldsReadOnly(false)}
                      style={{
                        flex: '1',
                        minWidth: '200px',
                        padding: '14px 24px',
                        background: 'transparent',
                        border: '2px solid #0f62fe',
                        borderRadius: '8px',
                        color: '#0f62fe',
                        fontSize: '15px',
                        fontWeight: '600',
                        cursor: 'pointer',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        gap: '10px',
                        transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)'
                      }}
                      onMouseEnter={(e) => {
                        e.currentTarget.style.backgroundColor = '#e8f4ff';
                        e.currentTarget.style.transform = 'translateY(-3px) scale(1.02)';
                        e.currentTarget.style.boxShadow = '0 8px 20px rgba(15, 98, 254, 0.2)';
                      }}
                      onMouseLeave={(e) => {
                        e.currentTarget.style.backgroundColor = 'transparent';
                        e.currentTarget.style.transform = 'translateY(0) scale(1)';
                        e.currentTarget.style.boxShadow = 'none';
                      }}
                      onMouseDown={(e) => {
                        e.currentTarget.style.transform = 'translateY(-1px) scale(0.98)';
                      }}
                      onMouseUp={(e) => {
                        e.currentTarget.style.transform = 'translateY(-3px) scale(1.02)';
                      }}
                    >
                      <span>Edit Configuration</span>
                    </button>
                  )}
                </div>
              </>
            )}
          </Form>
        </Tile>
      </Column>

      {/* Status Panel */}
      <Column sm={4} md={8} lg={6}>
        <Tile style={{ padding: '2rem', height: '100%' }}>
          <h3 style={{ fontSize: '1.25rem', fontWeight: '400', marginBottom: '1.5rem' }}>
            Connection Status
          </h3>

          {testing && (
            <Loading description="Testing connection..." withOverlay={false} small />
          )}

          {testResult && testResult.success && (
            <div style={{ 
              padding: '1.5rem',
              backgroundColor: 'var(--cds-notification-background-success)',
              borderLeft: '3px solid var(--cds-support-success)',
              borderRadius: '4px',
              marginBottom: '1rem'
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.5rem' }}>
                <CheckmarkFilled size={24} style={{ fill: 'var(--cds-support-success)' }} />
                <h4 style={{ fontSize: '1rem', fontWeight: '500', margin: 0 }}>
                  {isTestSuccessful ? 'Connection Successful - Ready to Save!' : 'Success'}
                </h4>
              </div>
              <p style={{ margin: '0.5rem 0 0 0', fontSize: '0.875rem' }}>
                {testResult.message}
              </p>
              {testResult.scriptsFound > 0 && (
                <p style={{ margin: '0.5rem 0 0 0', fontSize: '0.875rem', fontWeight: '500' }}>
                  Found {testResult.scriptsFound} automation scripts
                </p>
              )}
            </div>
          )}

          {error && (
            <InlineNotification
              kind="error"
              title="Connection Failed"
              subtitle={error}
              lowContrast
              hideCloseButton
            />
          )}

          {selectedEnv && !testResult && !error && !isAddingNew && (
            <div style={{ 
              padding: '1.5rem',
              backgroundColor: 'var(--cds-layer-accent-01)',
              borderRadius: '4px'
            }}>
              <h4 style={{ fontSize: '0.875rem', fontWeight: '600', marginBottom: '1rem', color: 'var(--cds-text-secondary)' }}>
                Current Environment: {config.environmentName}
              </h4>
              <div style={{ fontSize: '0.875rem', display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                <div>
                  <span style={{ color: 'var(--cds-text-secondary)' }}>URL: </span>
                  <span style={{ wordBreak: 'break-all' }}>{config.maximoUrl}</span>
                </div>
                <div>
                  <span style={{ color: 'var(--cds-text-secondary)' }}>API Key: </span>
                  <span>{'*'.repeat(20)}</span>
                </div>
              </div>
            </div>
          )}

          {!selectedEnv && !isAddingNew && environments.length === 0 && (
            <div style={{ 
              padding: '2rem',
              textAlign: 'center',
              color: 'var(--cds-text-secondary)'
            }}>
              <p>No environments configured yet.</p>
              <p style={{ fontSize: '0.875rem', marginTop: '0.5rem' }}>
                Click "Add New Environment" to get started.
              </p>
            </div>
          )}
        </Tile>
      </Column>


      <style>{`
        @keyframes pulse {
          0%, 100% {
            transform: scale(1);
            box-shadow: 0 0 0 0 rgba(14, 165, 233, 0.7);
          }
          50% {
            transform: scale(1.02);
            box-shadow: 0 0 0 8px rgba(14, 165, 233, 0);
          }
        }
      `}</style>
    </Grid>
  );
};

export default MaximoConfig;

// Made with Bob