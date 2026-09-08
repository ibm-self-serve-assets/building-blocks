import React, { useState, useEffect } from 'react';
import {
  Modal,
  Grid,
  Column,
  Tile,
  Tag,
  Loading,
  InlineNotification,
  Button,
  Tabs,
  TabList,
  Tab,
  TabPanels,
  TabPanel,
  ToastNotification,
} from '@carbon/react';
import { ErrorFilled, WarningAlt, Information, CheckmarkFilled, Rocket, Upload } from '@carbon/icons-react';
import { scriptAPI } from '../services/api';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';

const ScriptDetail = ({ script, onClose }) => {
  const [analysis, setAnalysis] = useState(null);
  const [impactAnalysis, setImpactAnalysis] = useState(null);
  const [optimizationResult, setOptimizationResult] = useState(null);
  const [loading, setLoading] = useState(true);
  const [loadingImpact, setLoadingImpact] = useState(false);
  const [loadingOptimization, setLoadingOptimization] = useState(false);
  const [optimizing, setOptimizing] = useState(false);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState(0);
  const [updating, setUpdating] = useState(false);
  const [updateStatus, setUpdateStatus] = useState(null);

  // Helper function to get field value (handles spi: namespace)
  const getField = (fieldName) => {
    return script[`spi:${fieldName}`] || script[fieldName] || '';
  };

  const scriptName = getField('autoscript');
  const scriptLanguage = getField('scriptlanguage');
  const scriptStatus = getField('status');
  const scriptDescription = getField('description');
  const scriptSource = getField('source');
  const isActive = getField('active');
  const createdDate = getField('createddate');
  const changedBy = getField('changeby');
  const changeDate = getField('changedate');

  useEffect(() => {
    if (script && scriptName) {
      analyzeScript();
      analyzeScriptWithImpact();
      fetchOptimizedCode();
    }
  }, [script]);

  const analyzeScript = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await scriptAPI.analyzeScript(scriptName);
      setAnalysis(data.analysis);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const analyzeScriptWithImpact = async () => {
    try {
      setLoadingImpact(true);
      const data = await scriptAPI.analyzeScriptWithImpact(scriptName);
      setImpactAnalysis(data.analysis.impactAnalysis);
    } catch (err) {
      console.error('Failed to load impact analysis:', err);
    } finally {
      setLoadingImpact(false);
    }
  };

  const fetchOptimizedCode = async () => {
    try {
      setLoadingOptimization(true);
      const result = await scriptAPI.optimizeScript(scriptName);
      setOptimizationResult(result.optimization);
    } catch (err) {
      console.error('Failed to load optimized code:', err);
    } finally {
      setLoadingOptimization(false);
    }
  };

  const handleOptimizeScript = async () => {
    try {
      setOptimizing(true);
      setError(null);
      const result = await scriptAPI.optimizeScript(scriptName);
      setOptimizationResult(result);
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
      
      const optimizedCode = optimizationResult?.optimizedCode;
      
      if (!optimizedCode) {
        setUpdateStatus({
          kind: 'error',
          title: 'Update Failed',
          subtitle: 'No optimized code available. Please generate optimization first.',
          timestamp: new Date().toLocaleTimeString()
        });
        return;
      }
      
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

  // Fix line count calculation - filter empty lines
  const calculateLineCount = (code) => {
    if (!code) return 0;
    return code.split('\n').filter(line => line.trim() !== '').length;
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

  // Helper function to add line numbers to code
  const addLineNumbers = (code) => {
    if (!code) return '';
    const lines = code.split('\n');
    return lines.map((line, index) => {
      const lineNum = (index + 1).toString().padStart(3, ' ');
      return `<span style="color: #858585; user-select: none;">${lineNum} | </span>${line}`;
    }).join('\n');
  };

  // Generate full optimized code - use backend's actual optimized code
  const generateFullOptimizedCode = () => {
    // If we have the optimization result from backend, use it
    if (optimizationResult?.optimizedCode) {
      return optimizationResult.optimizedCode;
    }
    
    // Fallback: show loading or placeholder
    if (loadingOptimization) {
      return '// Loading optimized code...';
    }
    
    return '// Optimized code will be generated here';
  };

  // Calculate overall script score
  const calculateOverallScore = () => {
    if (!impactAnalysis?.currentState) return 0;
    const { currentState } = impactAnalysis;
    const codeQuality = currentState.codeQuality?.score || 0;
    const maintainability = currentState.maintainability?.score || 0;
    const performance = currentState.performance?.score || 50;
    const security = currentState.security?.score || 50;
    
    return Math.round((codeQuality + maintainability + performance + security) / 4);
  };

  const getScoreColor = (score) => {
    if (score >= 80) return 'var(--cds-support-success)';
    if (score >= 60) return 'var(--cds-support-warning)';
    return 'var(--cds-support-error)';
  };

  const getScoreLabel = (score) => {
    if (score >= 80) return 'Excellent';
    if (score >= 60) return 'Good';
    if (score >= 40) return 'Fair';
    return 'Needs Improvement';
  };

  if (!script) return null;

  const lineCount = calculateLineCount(scriptSource);
  const overallScore = calculateOverallScore();

  return (
    <Modal
      open={true}
      onRequestClose={onClose}
      modalHeading={scriptName}
      passiveModal
      size="lg"
    >
      <Tabs selectedIndex={activeTab} onChange={({ selectedIndex }) => setActiveTab(selectedIndex)}>
        <TabList aria-label="Script analysis tabs" contained>
          <Tab>Script Info</Tab>
          <Tab>AI Analysis</Tab>
          <Tab>AI Enhancement</Tab>
        </TabList>

        <TabPanels>
          {/* Script Info Tab */}
          <TabPanel>
            <Grid narrow>
              <Column sm={4} md={8} lg={16}>
                <Tile style={{ padding: '1.5rem', marginBottom: '1rem' }}>
                  <h4 style={{ marginBottom: '1rem', fontSize: '1.125rem' }}>Script Details</h4>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                    <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
                      <Tag type="blue">{scriptLanguage}</Tag>
                      <Tag type={scriptStatus === 'Draft' || scriptStatus === 'ACTIVE' ? 'green' : 'warm-gray'}>
                        {scriptStatus}
                      </Tag>
                      <Tag type={isActive === true || isActive === 'true' || isActive === 1 ? 'green' : 'red'}>
                        {isActive === true || isActive === 'true' || isActive === 1 ? 'Active' : 'Inactive'}
                      </Tag>
                    </div>
                    
                    {scriptDescription && (
                      <div>
                        <strong>Description:</strong>
                        <p style={{ marginTop: '0.25rem', color: 'var(--cds-text-secondary)' }}>
                          {scriptDescription}
                        </p>
                      </div>
                    )}
                    
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginTop: '0.5rem' }}>
                      {createdDate && (
                        <div>
                          <strong>Created:</strong>
                          <p style={{ marginTop: '0.25rem', color: 'var(--cds-text-secondary)' }}>
                            {new Date(createdDate).toLocaleString()}
                          </p>
                        </div>
                      )}
                      {changeDate && (
                        <div>
                          <strong>Last Modified:</strong>
                          <p style={{ marginTop: '0.25rem', color: 'var(--cds-text-secondary)' }}>
                            {new Date(changeDate).toLocaleString()}
                          </p>
                        </div>
                      )}
                      {changedBy && (
                        <div>
                          <strong>Modified By:</strong>
                          <p style={{ marginTop: '0.25rem', color: 'var(--cds-text-secondary)' }}>
                            {changedBy}
                          </p>
                        </div>
                      )}
                    </div>
                  </div>
                </Tile>
              </Column>
            </Grid>
          </TabPanel>

          {/* AI Analysis Tab */}
          <TabPanel>
            {loading || loadingImpact ? (
              <div style={{ padding: '2rem', textAlign: 'center' }}>
                <Loading description="Analyzing script..." withOverlay={false} />
              </div>
            ) : error ? (
              <InlineNotification
                kind="error"
                title="Analysis Error"
                subtitle={error}
                lowContrast
                style={{ marginBottom: '1rem' }}
              />
            ) : (
              <Grid narrow>
                {/* Section 1: Code Metrics with % symbols */}
                <Column sm={4} md={8} lg={16}>
                  <Tile style={{ marginBottom: '1.5rem', padding: '1.5rem' }}>
                    <h4 style={{ fontSize: '1.125rem', fontWeight: '600', marginBottom: '1.5rem', color: 'var(--cds-text-primary)' }}>
                      Code Metrics
                    </h4>
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(6, 1fr)', gap: '1.5rem' }}>
                      {/* Code Quality */}
                      {impactAnalysis?.currentState && (
                        <div style={{ textAlign: 'center' }}>
                          <div style={{ fontSize: '0.75rem', color: 'var(--cds-text-secondary)', marginBottom: '0.5rem', textTransform: 'uppercase', letterSpacing: '0.5px', fontWeight: '600' }}>
                            Code Quality
                          </div>
                          <div style={{
                            fontSize: '2.5rem',
                            fontWeight: '300',
                            color: getScoreColor(impactAnalysis.currentState.codeQuality?.score || 0)
                          }}>
                            {impactAnalysis.currentState.codeQuality?.score || 0}%
                          </div>
                          <div style={{ fontSize: '0.65rem', color: 'var(--cds-text-secondary)', marginTop: '0.5rem', lineHeight: '1.2' }}>
                            Overall code health
                          </div>
                        </div>
                      )}
                      
                      {/* Maintainability */}
                      {impactAnalysis?.currentState && (
                        <div style={{ textAlign: 'center' }}>
                          <div style={{ fontSize: '0.75rem', color: 'var(--cds-text-secondary)', marginBottom: '0.5rem', textTransform: 'uppercase', letterSpacing: '0.5px', fontWeight: '600' }}>
                            Maintainability
                          </div>
                          <div style={{
                            fontSize: '2.5rem',
                            fontWeight: '300',
                            color: getScoreColor(impactAnalysis.currentState.maintainability?.score || 0)
                          }}>
                            {impactAnalysis.currentState.maintainability?.score || 0}%
                          </div>
                          <div style={{ fontSize: '0.65rem', color: 'var(--cds-text-secondary)', marginTop: '0.5rem', lineHeight: '1.2' }}>
                            Easy to modify
                          </div>
                        </div>
                      )}
                      
                      {/* Performance */}
                      <div style={{ textAlign: 'center' }}>
                        <div style={{ fontSize: '0.75rem', color: 'var(--cds-text-secondary)', marginBottom: '0.5rem', textTransform: 'uppercase', letterSpacing: '0.5px', fontWeight: '600' }}>
                          Performance
                        </div>
                        <div style={{
                          fontSize: '2.5rem',
                          fontWeight: '300',
                          color: getScoreColor(50)
                        }}>
                          50%
                        </div>
                        <div style={{ fontSize: '0.65rem', color: 'var(--cds-text-secondary)', marginTop: '0.5rem', lineHeight: '1.2' }}>
                          Execution efficiency
                        </div>
                      </div>
                      
                      {/* Security */}
                      <div style={{ textAlign: 'center' }}>
                        <div style={{ fontSize: '0.75rem', color: 'var(--cds-text-secondary)', marginBottom: '0.5rem', textTransform: 'uppercase', letterSpacing: '0.5px', fontWeight: '600' }}>
                          Security
                        </div>
                        <div style={{
                          fontSize: '2.5rem',
                          fontWeight: '300',
                          color: getScoreColor(50)
                        }}>
                          50%
                        </div>
                        <div style={{ fontSize: '0.65rem', color: 'var(--cds-text-secondary)', marginTop: '0.5rem', lineHeight: '1.2' }}>
                          Vulnerability risk
                        </div>
                      </div>
                      
                      {/* Issues - Before/After */}
                      <div style={{ textAlign: 'center' }}>
                        <div style={{ fontSize: '0.75rem', color: 'var(--cds-text-secondary)', marginBottom: '0.5rem', textTransform: 'uppercase', letterSpacing: '0.5px', fontWeight: '600' }}>
                          Issues
                        </div>
                        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem' }}>
                          <div style={{ fontSize: '2.5rem', fontWeight: '300', color: 'var(--cds-support-error)' }}>
                            {optimizationResult?.metricsComparison?.before?.issues || analysis?.issues?.length || 0}
                          </div>
                          <div style={{ fontSize: '1.5rem', color: 'var(--cds-text-secondary)' }}>→</div>
                          <div style={{ fontSize: '2.5rem', fontWeight: '300', color: 'var(--cds-support-success)' }}>
                            {optimizationResult?.metricsComparison?.after?.issues || 0}
                          </div>
                        </div>
                        <div style={{ fontSize: '0.65rem', color: 'var(--cds-text-secondary)', marginTop: '0.5rem', lineHeight: '1.2' }}>
                          {optimizationResult?.metricsComparison?.improvement?.issuesFixed || 0} fixed
                        </div>
                      </div>
                      
                      {/* Warnings - Before/After */}
                      <div style={{ textAlign: 'center' }}>
                        <div style={{ fontSize: '0.75rem', color: 'var(--cds-text-secondary)', marginBottom: '0.5rem', textTransform: 'uppercase', letterSpacing: '0.5px', fontWeight: '600' }}>
                          Warnings
                        </div>
                        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem' }}>
                          <div style={{ fontSize: '2.5rem', fontWeight: '300', color: 'var(--cds-support-warning)' }}>
                            {optimizationResult?.metricsComparison?.before?.warnings || analysis?.warnings?.length || 0}
                          </div>
                          <div style={{ fontSize: '1.5rem', color: 'var(--cds-text-secondary)' }}>→</div>
                          <div style={{ fontSize: '2.5rem', fontWeight: '300', color: 'var(--cds-support-success)' }}>
                            {optimizationResult?.metricsComparison?.after?.warnings || 0}
                          </div>
                        </div>
                        <div style={{ fontSize: '0.65rem', color: 'var(--cds-text-secondary)', marginTop: '0.5rem', lineHeight: '1.2' }}>
                          {optimizationResult?.metricsComparison?.improvement?.warningsFixed || 0} fixed
                        </div>
                      </div>
                      
                      {/* Suggestions - Before/After */}
                      <div style={{ textAlign: 'center' }}>
                        <div style={{ fontSize: '0.75rem', color: 'var(--cds-text-secondary)', marginBottom: '0.5rem', textTransform: 'uppercase', letterSpacing: '0.5px', fontWeight: '600' }}>
                          Suggestions
                        </div>
                        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem' }}>
                          <div style={{ fontSize: '2.5rem', fontWeight: '300', color: 'var(--cds-support-info)' }}>
                            {optimizationResult?.metricsComparison?.before?.suggestions || analysis?.suggestions?.length || 0}
                          </div>
                          <div style={{ fontSize: '1.5rem', color: 'var(--cds-text-secondary)' }}>→</div>
                          <div style={{ fontSize: '2.5rem', fontWeight: '300', color: 'var(--cds-support-success)' }}>
                            {optimizationResult?.metricsComparison?.after?.suggestions || 0}
                          </div>
                        </div>
                        <div style={{ fontSize: '0.65rem', color: 'var(--cds-text-secondary)', marginTop: '0.5rem', lineHeight: '1.2' }}>
                          {optimizationResult?.metricsComparison?.improvement?.suggestionsImplemented || 0} implemented
                        </div>
                      </div>
                    </div>
                  </Tile>
                </Column>

                {/* Section 2: Full Code Comparison - Show complete source code */}
                {impactAnalysis?.optimizations && impactAnalysis.optimizations.length > 0 && (
                  <Column sm={4} md={8} lg={16}>
                    <Tile style={{ marginBottom: '1.5rem', padding: '1.5rem' }}>
                      <h4 style={{ fontSize: '1.125rem', fontWeight: '600', marginBottom: '1.5rem', color: 'var(--cds-text-primary)' }}>
                        Code Comparison
                      </h4>
                      <div style={{
                        display: 'grid',
                        gridTemplateColumns: '1fr 1fr',
                        gap: '0.75rem',
                        width: '100%',
                        maxWidth: '100%',
                        overflow: 'hidden'
                      }}>
                        {/* Original Source Code - FULL CODE */}
                        <div style={{ minWidth: 0, flex: 1 }}>
                          <div style={{
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'space-between',
                            marginBottom: '0.75rem',
                            paddingBottom: '0.5rem',
                            borderBottom: '2px solid var(--cds-border-subtle)'
                          }}>
                            <h5 style={{
                              fontSize: '0.875rem',
                              fontWeight: '600',
                              margin: 0,
                              color: 'var(--cds-text-primary)',
                              textTransform: 'uppercase',
                              letterSpacing: '0.5px'
                            }}>
                              Original Source Code
                            </h5>
                          </div>
                          <div style={{
                            height: '500px',
                            overflow: 'auto',
                            border: '1px solid var(--cds-border-subtle)',
                            borderRadius: '4px',
                            backgroundColor: '#1e1e1e',
                            padding: '0.75rem',
                            width: '100%'
                          }}>
                            <pre style={{
                              margin: 0,
                              whiteSpace: 'pre',
                              fontFamily: 'monospace',
                              fontSize: '0.75rem',
                              color: '#d4d4d4',
                              lineHeight: '1.5',
                              overflowX: 'auto'
                            }} dangerouslySetInnerHTML={{
                              __html: scriptSource ? addLineNumbers(scriptSource.replace(/\\n/g, '\n').replace(/</g, '<').replace(/>/g, '>')) : '// No source code available'
                            }} />
                          </div>
                        </div>

                        {/* AI Optimized Code - FULL CODE */}
                        <div style={{ minWidth: 0, flex: 1 }}>
                          <div style={{
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'space-between',
                            marginBottom: '0.75rem',
                            paddingBottom: '0.5rem',
                            borderBottom: '2px solid var(--cds-support-success)'
                          }}>
                            <h5 style={{
                              fontSize: '0.875rem',
                              fontWeight: '600',
                              margin: 0,
                              color: 'var(--cds-support-success)',
                              textTransform: 'uppercase',
                              letterSpacing: '0.5px'
                            }}>
                              AI Optimized Code
                            </h5>
                            <Tag type="green" size="sm">Improved</Tag>
                          </div>
                          <div style={{
                            height: '500px',
                            overflow: 'auto',
                            border: '1px solid var(--cds-support-success)',
                            borderRadius: '4px',
                            backgroundColor: '#1e1e1e',
                            padding: '0.75rem',
                            width: '100%'
                          }}>
                            <pre style={{
                              margin: 0,
                              whiteSpace: 'pre',
                              fontFamily: 'monospace',
                              fontSize: '0.75rem',
                              color: '#d4d4d4',
                              lineHeight: '1.5',
                              overflowX: 'auto'
                            }} dangerouslySetInnerHTML={{
                              __html: addLineNumbers(generateFullOptimizedCode().replace(/\\n/g, '\n').replace(/</g, '<').replace(/>/g, '>'))
                            }} />
                          </div>
                        </div>
                      </div>
                      
                    </Tile>
                  </Column>
                )}

                {/* Section 3: Issues & Fixes - Shows which issues are resolved by AI optimization */}
                {(analysis?.issues?.length > 0 || analysis?.warnings?.length > 0 || analysis?.suggestions?.length > 0) && (
                  <Column sm={4} md={8} lg={16}>
                    <Tile style={{ marginBottom: '1.5rem', padding: '1.5rem' }}>
                      <h4 style={{ fontSize: '1.125rem', fontWeight: '600', marginBottom: '1.5rem', color: 'var(--cds-text-primary)' }}>
                        Issues & Fixes
                      </h4>
                      
                      {/* Use optimized data if available, otherwise fall back to analysis */}
                      {optimizationResult?.issuesAndFixes && optimizationResult.issuesAndFixes.length > 0 ? (
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                          {optimizationResult.issuesAndFixes.map((item, idx) => {
                            const severityColor =
                              item.severity === 'critical' ? 'var(--cds-support-error)' :
                              item.severity === 'warning' ? 'var(--cds-support-warning)' :
                              'var(--cds-support-info)';
                            
                            const SeverityIcon =
                              item.severity === 'critical' ? ErrorFilled :
                              item.severity === 'warning' ? WarningAlt :
                              Information;
                            
                            return (
                              <div key={idx} style={{
                                padding: '1.25rem',
                                backgroundColor: 'var(--cds-layer-01)',
                                borderRadius: '4px',
                                borderLeft: `4px solid ${severityColor}`
                              }}>
                                <div style={{
                                  display: 'flex',
                                  justifyContent: 'space-between',
                                  alignItems: 'flex-start',
                                  marginBottom: '0.75rem',
                                  gap: '1rem'
                                }}>
                                  <div style={{
                                    display: 'flex',
                                    alignItems: 'center',
                                    gap: '0.5rem'
                                  }}>
                                    <SeverityIcon size={16} style={{ color: severityColor }} />
                                    <span style={{
                                      fontSize: '0.75rem',
                                      fontWeight: '600',
                                      textTransform: 'uppercase',
                                      letterSpacing: '0.5px',
                                      color: severityColor
                                    }}>
                                      {item.severity}
                                    </span>
                                  </div>
                                  <Tag type="green" size="sm" style={{ flexShrink: 0 }}>
                                    <CheckmarkFilled size={12} style={{ marginRight: '0.25rem' }} />
                                    {item.status}
                                  </Tag>
                                </div>
                                <div style={{
                                  fontSize: '0.875rem',
                                  color: 'var(--cds-text-primary)',
                                  marginBottom: '0.75rem',
                                  lineHeight: '1.5'
                                }}>
                                  <strong>Issue:</strong> {item.issue}
                                </div>
                                <div style={{
                                  fontSize: '0.875rem',
                                  color: 'var(--cds-text-secondary)',
                                  padding: '0.75rem',
                                  backgroundColor: 'var(--cds-layer-02)',
                                  borderRadius: '4px',
                                  lineHeight: '1.5'
                                }}>
                                  <strong style={{ color: 'var(--cds-support-success)' }}>✓ Fix Applied:</strong> {item.fix}
                                </div>
                              </div>
                            );
                          })}
                        </div>
                      ) : (
                        <>
                          {/* Critical Issues with Fix Status */}
                          {analysis?.issues && analysis.issues.length > 0 && (
                            <div style={{ marginBottom: analysis?.warnings?.length > 0 ? '2rem' : '0' }}>
                              <h5 style={{
                                fontSize: '0.875rem',
                                fontWeight: '600',
                                marginBottom: '1rem',
                                color: 'var(--cds-support-error)',
                                textTransform: 'uppercase',
                                letterSpacing: '0.5px',
                                display: 'flex',
                                alignItems: 'center',
                                gap: '0.5rem'
                              }}>
                                <ErrorFilled size={20} /> Critical Issues
                              </h5>
                              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                                {analysis.issues.map((issue, idx) => (
                                  <div key={idx} style={{
                                    padding: '1rem',
                                    backgroundColor: 'var(--cds-layer-01)',
                                    borderRadius: '4px',
                                    borderLeft: '3px solid var(--cds-support-success)',
                                    display: 'flex',
                                    justifyContent: 'space-between',
                                    alignItems: 'flex-start',
                                    gap: '1rem'
                                  }}>
                                    <div style={{ flex: 1 }}>
                                      <div style={{ fontSize: '0.875rem', color: 'var(--cds-text-primary)', marginBottom: '0.25rem' }}>
                                        {issue}
                                      </div>
                                    </div>
                                    <Tag type="green" size="sm" style={{ flexShrink: 0 }}>
                                      <CheckmarkFilled size={12} style={{ marginRight: '0.25rem' }} />
                                      FIXED in optimized code
                                    </Tag>
                                  </div>
                                ))}
                              </div>
                            </div>
                          )}
                          
                          {/* Warnings with Fix Status */}
                          {analysis?.warnings && analysis.warnings.length > 0 && (
                            <div style={{ marginBottom: analysis?.suggestions?.length > 0 ? '2rem' : '0' }}>
                              <h5 style={{
                                fontSize: '0.875rem',
                                fontWeight: '600',
                                marginBottom: '1rem',
                                color: 'var(--cds-support-warning)',
                                textTransform: 'uppercase',
                                letterSpacing: '0.5px',
                                display: 'flex',
                                alignItems: 'center',
                                gap: '0.5rem'
                              }}>
                                <WarningAlt size={20} /> Warnings
                              </h5>
                              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                                {analysis.warnings.map((warning, idx) => (
                                  <div key={idx} style={{
                                    padding: '1rem',
                                    backgroundColor: 'var(--cds-layer-01)',
                                    borderRadius: '4px',
                                    borderLeft: '3px solid var(--cds-support-success)',
                                    display: 'flex',
                                    justifyContent: 'space-between',
                                    alignItems: 'flex-start',
                                    gap: '1rem'
                                  }}>
                                    <div style={{ flex: 1 }}>
                                      <div style={{ fontSize: '0.875rem', color: 'var(--cds-text-primary)', marginBottom: '0.25rem' }}>
                                        {warning}
                                      </div>
                                    </div>
                                    <Tag type="green" size="sm" style={{ flexShrink: 0 }}>
                                      <CheckmarkFilled size={12} style={{ marginRight: '0.25rem' }} />
                                      FIXED in optimized code
                                    </Tag>
                                  </div>
                                ))}
                              </div>
                            </div>
                          )}

                          {/* Suggestions with Implementation Status */}
                          {analysis?.suggestions && analysis.suggestions.length > 0 && (
                            <div>
                              <h5 style={{
                                fontSize: '0.875rem',
                                fontWeight: '600',
                                marginBottom: '1rem',
                                color: 'var(--cds-support-info)',
                                textTransform: 'uppercase',
                                letterSpacing: '0.5px',
                                display: 'flex',
                                alignItems: 'center',
                                gap: '0.5rem'
                              }}>
                                <Information size={20} /> Suggestions
                              </h5>
                              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                                {analysis.suggestions.map((suggestion, idx) => (
                                  <div key={idx} style={{
                                    padding: '1rem',
                                    backgroundColor: 'var(--cds-layer-01)',
                                    borderRadius: '4px',
                                    borderLeft: '3px solid var(--cds-support-success)',
                                    display: 'flex',
                                    justifyContent: 'space-between',
                                    alignItems: 'flex-start',
                                    gap: '1rem'
                                  }}>
                                    <div style={{ flex: 1 }}>
                                      <div style={{ fontSize: '0.875rem', color: 'var(--cds-text-primary)', marginBottom: '0.25rem' }}>
                                        {suggestion}
                                      </div>
                                    </div>
                                    <Tag type="green" size="sm" style={{ flexShrink: 0 }}>
                                      <CheckmarkFilled size={12} style={{ marginRight: '0.25rem' }} />
                                      IMPLEMENTED
                                    </Tag>
                                  </div>
                                ))}
                              </div>
                            </div>
                          )}
                        </>
                      )}
                    </Tile>
                  </Column>
                )}
              </Grid>
            )}
          </TabPanel>

          {/* AI Enhancement Tab */}
          <TabPanel>
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

              <Column sm={4} md={8} lg={16}>
                <Tile style={{ padding: '1.5rem', marginBottom: '1rem' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
                    <h3 style={{ fontSize: '1.25rem', fontWeight: '500', margin: 0 }}>
                      AI-Enhanced Script
                    </h3>
                    <Button
                      kind="primary"
                      renderIcon={Upload}
                      onClick={handleUpdateScript}
                      disabled={updating || !optimizationResult?.optimizedCode}
                    >
                      {updating ? 'Updating...' : 'Update in Maximo'}
                    </Button>
                  </div>
                  
                  {loadingOptimization ? (
                    <div style={{ padding: '2rem', textAlign: 'center' }}>
                      <Loading description="Generating AI enhancements..." withOverlay={false} />
                    </div>
                  ) : optimizationResult?.optimizedCode ? (
                    <>
                      <p style={{ fontSize: '0.875rem', color: 'var(--cds-text-secondary)', marginBottom: '1rem' }}>
                        Review the AI-enhanced code below and click "Update in Maximo" to apply the changes.
                      </p>
                      
                      <div style={{
                        maxHeight: '500px',
                        overflow: 'auto',
                        border: '2px solid var(--cds-support-success)',
                        borderRadius: '4px',
                        backgroundColor: '#1e1e1e',
                        padding: '0.75rem'
                      }}>
                        <pre style={{
                          margin: 0,
                          whiteSpace: 'pre',
                          fontFamily: 'monospace',
                          fontSize: '0.75rem',
                          color: '#d4d4d4',
                          lineHeight: '1.5'
                        }} dangerouslySetInnerHTML={{
                          __html: addLineNumbers(optimizationResult.optimizedCode.replace(/\\n/g, '\n').replace(/</g, '<').replace(/>/g, '>'))
                        }} />
                      </div>

                      {/* Key Improvements */}
                      {optimizationResult.improvements && optimizationResult.improvements.length > 0 && (
                        <div style={{ marginTop: '1.5rem' }}>
                          <h4 style={{ fontSize: '1rem', fontWeight: '500', marginBottom: '1rem' }}>
                            Key Improvements Applied
                          </h4>
                          <ul style={{
                            listStyle: 'none',
                            padding: 0,
                            margin: 0,
                            display: 'flex',
                            flexDirection: 'column',
                            gap: '0.5rem'
                          }}>
                            {optimizationResult.improvements.map((improvement, idx) => (
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
                        </div>
                      )}
                    </>
                  ) : (
                    <div style={{
                      padding: '3rem 2rem',
                      textAlign: 'center',
                      backgroundColor: 'var(--cds-layer-01)',
                      borderRadius: '4px'
                    }}>
                      <Rocket size={48} style={{ marginBottom: '1rem', opacity: 0.6 }} />
                      <p style={{ fontSize: '0.875rem', color: 'var(--cds-text-secondary)' }}>
                        No AI enhancements available. Please check the AI Analysis tab first.
                      </p>
                    </div>
                  )}
                </Tile>
              </Column>
            </Grid>
          </TabPanel>
        </TabPanels>
      </Tabs>
    </Modal>
  );
};

export default ScriptDetail;

// Made with Bob
