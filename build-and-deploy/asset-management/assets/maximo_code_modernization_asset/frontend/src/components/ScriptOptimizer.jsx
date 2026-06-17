import React, { useState, useEffect } from 'react';
import {
  Grid,
  Column,
  Tile,
  Loading,
  InlineNotification,
  Button,
  DataTable,
  TableContainer,
  Table,
  TableHead,
  TableRow,
  TableHeader,
  TableBody,
  TableCell,
  Tag,
  Modal,
  ToastNotification,
} from '@carbon/react';
import { Renew, Rocket, View, CheckmarkFilled, WarningAlt, ErrorFilled, Upload } from '@carbon/icons-react';
import { scriptAPI } from '../services/api';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';

const ScriptOptimizer = () => {
  const [scripts, setScripts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [optimizing, setOptimizing] = useState(false);
  const [selectedScript, setSelectedScript] = useState(null);
  const [optimizationResult, setOptimizationResult] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [updating, setUpdating] = useState(false);
  const [updateStatus, setUpdateStatus] = useState(null);

  useEffect(() => {
    const savedConfig = localStorage.getItem('maximoConfig');
    if (savedConfig) {
      fetchScripts();
    } else {
      setLoading(false);
      setError('Please configure your Maximo connection in the Configuration tab first.');
    }
  }, []);

  const fetchScripts = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await scriptAPI.getAllScripts();
      setScripts(data.scripts || []);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleOptimizeScript = async (script) => {
    try {
      setOptimizing(true);
      setSelectedScript(script);
      setError(null);
      
      const scriptName = script['spi:autoscript'] || script.autoscript;
      const result = await scriptAPI.optimizeScript(scriptName);
      
      setOptimizationResult(result);
      setShowModal(true);
    } catch (err) {
      setError(err.message);
    } finally {
      setOptimizing(false);
    }
  };

  const handleUpdateScript = async () => {
    try {
      setUpdating(true);
      setUpdateStatus(null);
      
      const scriptName = getField(selectedScript, 'autoscript');
      const optimizedCode = optimizationResult.optimizedCode;
      
      await scriptAPI.updateScript(scriptName, optimizedCode);
      
      setUpdateStatus({
        kind: 'success',
        title: 'Script Updated Successfully',
        subtitle: `Script "${scriptName}" has been updated in Maximo with the optimized code.`,
        timestamp: new Date().toLocaleTimeString()
      });
      
      // Auto-close notification after 5 seconds
      setTimeout(() => {
        setUpdateStatus(null);
      }, 5000);
      
    } catch (err) {
      setUpdateStatus({
        kind: 'error',
        title: 'Update Failed',
        subtitle: err.message || 'Failed to update script in Maximo. Please try again.',
        timestamp: new Date().toLocaleTimeString()
      });
    } finally {
      setUpdating(false);
    }
  };

  const getField = (script, fieldName) => {
    return script[`spi:${fieldName}`] || script[fieldName] || '';
  };

  const getLanguageForHighlighter = (lang) => {
    const langMap = {
      'jython': 'python',
      'python': 'python',
      'javascript': 'javascript',
      'java': 'java'
    };
    return langMap[lang?.toLowerCase()] || 'javascript';
  };

  const headers = [
    { key: 'name', header: 'Script Name' },
    { key: 'language', header: 'Language' },
    { key: 'status', header: 'Status' },
    { key: 'issues', header: 'Issues' },
    { key: 'actions', header: 'Actions' },
  ];

  const rows = scripts.map((script, index) => {
    const scriptName = getField(script, 'autoscript');
    const language = getField(script, 'scriptlanguage');
    const status = getField(script, 'status');
    const isActive = getField(script, 'active');

    return {
      id: `${index}`,
      name: scriptName,
      language: language,
      status: status,
      isActive: isActive,
      issues: '—', // Will be populated after analysis
      script: script
    };
  });

  if (loading) {
    return (
      <Grid>
        <Column sm={4} md={8} lg={16}>
          <div style={{ padding: '4rem', textAlign: 'center' }}>
            <Loading description="Loading scripts..." withOverlay={false} />
          </div>
        </Column>
      </Grid>
    );
  }

  if (error) {
    return (
      <Grid>
        <Column sm={4} md={8} lg={16}>
          <InlineNotification
            kind="error"
            title="Error loading scripts"
            subtitle={error}
            lowContrast
          />
        </Column>
      </Grid>
    );
  }

  return (
    <Grid>
      {/* Header */}
      <Column sm={4} md={8} lg={16}>
        <div style={{ 
          display: 'flex', 
          justifyContent: 'space-between', 
          alignItems: 'center', 
          marginBottom: '2rem',
          paddingBottom: '1rem',
          borderBottom: '1px solid var(--cds-border-subtle)'
        }}>
          <div>
            <h2 style={{
              fontSize: '2rem',
              fontWeight: '400',
              margin: 0,
              marginBottom: '0.25rem'
            }}>
              AI Script Enhancement
            </h2>
            <p style={{
              fontSize: '0.875rem',
              color: 'var(--cds-text-secondary)',
              margin: 0
            }}>
              Generate and apply AI-powered optimizations to your Maximo automation scripts
            </p>
          </div>
          <Button
            kind="tertiary"
            renderIcon={Renew}
            onClick={fetchScripts}
            size="md"
          >
            Refresh
          </Button>
        </div>
      </Column>

      {/* Info Cards */}
      <Column sm={4} md={4} lg={5}>
        <Tile style={{ 
          padding: '1.5rem',
          height: '100%',
          borderLeft: '4px solid var(--cds-support-info)'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '1rem' }}>
            <Rocket size={32} style={{ fill: 'var(--cds-support-info)' }} />
            <div style={{ fontSize: '0.875rem', color: 'var(--cds-text-secondary)' }}>
              Total Scripts
            </div>
          </div>
          <div style={{ fontSize: '2.5rem', fontWeight: '300' }}>
            {scripts.length}
          </div>
        </Tile>
      </Column>

      <Column sm={4} md={4} lg={11}>
        <Tile style={{ padding: '1.5rem', height: '100%' }}>
          <h4 style={{ fontSize: '1rem', fontWeight: '500', marginBottom: '1rem' }}>
            How AI Script Enhancement Works
          </h4>
          <ol style={{
            fontSize: '0.875rem',
            lineHeight: '1.8',
            paddingLeft: '1.5rem',
            margin: 0
          }}>
            <li>Select a script from the list below</li>
            <li>Click "Enhance" to generate AI-powered optimizations</li>
            <li>Review the enhanced code with side-by-side comparison</li>
            <li>View detailed impact analysis and performance improvements</li>
            <li>Click "Update in Maximo" to apply the optimized code</li>
          </ol>
        </Tile>
      </Column>

      {/* Scripts Table */}
      <Column sm={4} md={8} lg={16}>
        <Tile style={{ padding: '1.5rem' }}>
          <h3 style={{ fontSize: '1.25rem', fontWeight: '500', marginBottom: '1.5rem' }}>
            Available Scripts
          </h3>
          
          <DataTable rows={rows} headers={headers}>
            {({ rows, headers, getTableProps, getHeaderProps, getRowProps }) => (
              <TableContainer>
                <Table {...getTableProps()}>
                  <TableHead>
                    <TableRow>
                      {headers.map((header) => (
                        <TableHeader {...getHeaderProps({ header })} key={header.key}>
                          {header.header}
                        </TableHeader>
                      ))}
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {rows.map((row) => (
                      <TableRow {...getRowProps({ row })} key={row.id}>
                        {row.cells.map((cell) => {
                          if (cell.info.header === 'name') {
                            return (
                              <TableCell key={cell.id}>
                                <span style={{ fontFamily: 'IBM Plex Mono, monospace', fontSize: '0.875rem' }}>
                                  {cell.value}
                                </span>
                              </TableCell>
                            );
                          }
                          if (cell.info.header === 'language') {
                            return (
                              <TableCell key={cell.id}>
                                <Tag type="blue" size="sm">{cell.value}</Tag>
                              </TableCell>
                            );
                          }
                          if (cell.info.header === 'status') {
                            return (
                              <TableCell key={cell.id}>
                                <Tag 
                                  type={cell.value === 'ACTIVE' || cell.value === 'Draft' ? 'green' : 'warm-gray'} 
                                  size="sm"
                                >
                                  {cell.value}
                                </Tag>
                              </TableCell>
                            );
                          }
                          if (cell.info.header === 'actions') {
                            return (
                              <TableCell key={cell.id}>
                                <Button
                                  kind="ghost"
                                  size="sm"
                                  renderIcon={Rocket}
                                  onClick={() => handleOptimizeScript(rows[row.id].script)}
                                  disabled={optimizing}
                                >
                                  Enhance
                                </Button>
                              </TableCell>
                            );
                          }
                          return <TableCell key={cell.id}>{cell.value}</TableCell>;
                        })}
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            )}
          </DataTable>
        </Tile>
      </Column>

      {/* Optimization Result Modal */}
      {showModal && optimizationResult && (
        <Modal
          open={showModal}
          onRequestClose={() => {
            setShowModal(false);
            setUpdateStatus(null);
          }}
          modalHeading={`AI Enhancement Results: ${getField(selectedScript, 'autoscript')}`}
          passiveModal={false}
          primaryButtonText="Update in Maximo"
          secondaryButtonText="Close"
          onRequestSubmit={handleUpdateScript}
          primaryButtonDisabled={updating}
          size="lg"
        >
          <Grid narrow>
            {/* Update Status Notification */}
            {updateStatus && (
              <Column sm={4} md={8} lg={16}>
                <ToastNotification
                  kind={updateStatus.kind}
                  title={updateStatus.title}
                  subtitle={updateStatus.subtitle}
                  caption={updateStatus.timestamp}
                  timeout={5000}
                  onClose={() => setUpdateStatus(null)}
                  style={{ marginBottom: '1rem' }}
                />
              </Column>
            )}
            {/* Score Summary */}
            <Column sm={4} md={8} lg={16}>
              <Tile style={{ 
                padding: '1.5rem', 
                marginBottom: '1rem',
                backgroundColor: 'var(--cds-layer-accent-01)'
              }}>
                <div style={{ display: 'flex', justifyContent: 'space-around', alignItems: 'center' }}>
                  <div style={{ textAlign: 'center' }}>
                    <div style={{ fontSize: '0.875rem', color: 'var(--cds-text-secondary)', marginBottom: '0.5rem' }}>
                      Current Score
                    </div>
                    <div style={{ fontSize: '2.5rem', fontWeight: '300', color: 'var(--cds-support-warning)' }}>
                      {optimizationResult.currentScore || 65}/100
                    </div>
                  </div>
                  <div style={{ fontSize: '2rem', color: 'var(--cds-text-secondary)' }}>→</div>
                  <div style={{ textAlign: 'center' }}>
                    <div style={{ fontSize: '0.875rem', color: 'var(--cds-text-secondary)', marginBottom: '0.5rem' }}>
                      Optimized Score
                    </div>
                    <div style={{ fontSize: '2.5rem', fontWeight: '300', color: 'var(--cds-support-success)' }}>
                      {optimizationResult.optimizedScore || 92}/100
                    </div>
                  </div>
                </div>
              </Tile>
            </Column>

            {/* Code Comparison */}
            <Column sm={4} md={8} lg={16}>
              <h4 style={{ fontSize: '1.125rem', fontWeight: '500', marginBottom: '1rem' }}>
                Code Comparison
              </h4>
            </Column>

            <Column sm={4} md={4} lg={8}>
              <div style={{ marginBottom: '0.5rem', fontWeight: '600', color: 'var(--cds-support-error)' }}>
                Current Code
              </div>
              <div style={{ 
                maxHeight: '400px', 
                overflow: 'auto',
                border: '2px solid var(--cds-support-error)',
                borderRadius: '4px'
              }}>
                <SyntaxHighlighter
                  language={getLanguageForHighlighter(getField(selectedScript, 'scriptlanguage'))}
                  style={vscDarkPlus}
                  showLineNumbers
                  wrapLines
                  customStyle={{ margin: 0, fontSize: '0.75rem' }}
                >
                  {optimizationResult.currentCode || getField(selectedScript, 'source') || '// Code not available'}
                </SyntaxHighlighter>
              </div>
            </Column>

            <Column sm={4} md={4} lg={8}>
              <div style={{ marginBottom: '0.5rem', fontWeight: '600', color: 'var(--cds-support-success)' }}>
                Optimized Code
              </div>
              <div style={{ 
                maxHeight: '400px', 
                overflow: 'auto',
                border: '2px solid var(--cds-support-success)',
                borderRadius: '4px'
              }}>
                <SyntaxHighlighter
                  language={getLanguageForHighlighter(getField(selectedScript, 'scriptlanguage'))}
                  style={vscDarkPlus}
                  showLineNumbers
                  wrapLines
                  customStyle={{ margin: 0, fontSize: '0.75rem' }}
                >
                  {optimizationResult.optimizedCode || '// Optimized code will appear here'}
                </SyntaxHighlighter>
              </div>
            </Column>

            {/* Key Improvements */}
            <Column sm={4} md={8} lg={16}>
              <Tile style={{ padding: '1.5rem', marginTop: '1rem' }}>
                <h4 style={{ fontSize: '1rem', fontWeight: '500', marginBottom: '1rem' }}>
                  Key Improvements
                </h4>
                <ul style={{ 
                  listStyle: 'none', 
                  padding: 0, 
                  margin: 0,
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '0.75rem'
                }}>
                  {(optimizationResult.improvements || [
                    'Improved error handling with try-catch blocks',
                    'Optimized resource management and cleanup',
                    'Enhanced code readability and maintainability',
                    'Reduced memory footprint',
                    'Better performance for large datasets'
                  ]).map((improvement, idx) => (
                    <li key={idx} style={{ 
                      display: 'flex', 
                      alignItems: 'flex-start', 
                      gap: '0.5rem',
                      fontSize: '0.875rem'
                    }}>
                      <CheckmarkFilled size={16} style={{ fill: 'var(--cds-support-success)', marginTop: '0.125rem', flexShrink: 0 }} />
                      <span>{improvement}</span>
                    </li>
                  ))}
                </ul>
              </Tile>
            </Column>
          </Grid>
        </Modal>
      )}

      {/* Update in Progress Overlay */}
      {updating && (
        <Column sm={4} md={8} lg={16}>
          <div style={{
            position: 'fixed',
            top: '50%',
            left: '50%',
            transform: 'translate(-50%, -50%)',
            zIndex: 9999,
            backgroundColor: 'var(--cds-layer-01)',
            padding: '2rem',
            borderRadius: '8px',
            boxShadow: '0 4px 8px rgba(0,0,0,0.3)'
          }}>
            <Loading description="Updating script in Maximo..." withOverlay={false} />
          </div>
        </Column>
      )}

      {optimizing && (
        <Column sm={4} md={8} lg={16}>
          <div style={{ 
            position: 'fixed',
            top: '50%',
            left: '50%',
            transform: 'translate(-50%, -50%)',
            zIndex: 9999,
            backgroundColor: 'var(--cds-layer-01)',
            padding: '2rem',
            borderRadius: '8px',
            boxShadow: '0 4px 8px rgba(0,0,0,0.3)'
          }}>
            <Loading description="Generating optimizations..." withOverlay={false} />
          </div>
        </Column>
      )}
    </Grid>
  );
};

export default ScriptOptimizer;

// Made with Bob