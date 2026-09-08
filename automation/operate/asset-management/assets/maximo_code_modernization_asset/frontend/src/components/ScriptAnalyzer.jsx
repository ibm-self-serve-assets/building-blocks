import React, { useState, useEffect } from 'react';
import {
  Grid,
  Column,
  Tile,
  Loading,
  InlineNotification,
  Button,
  Accordion,
  AccordionItem,
  Tag,
} from '@carbon/react';
import { Renew, CheckmarkFilled, WarningAlt, ErrorFilled, Information } from '@carbon/icons-react';
import { scriptAPI } from '../services/api';

const ScriptAnalyzer = () => {
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Check if Maximo configuration exists before analyzing
    const savedConfig = localStorage.getItem('maximoConfig');
    if (savedConfig) {
      analyzeAllScripts();
    } else {
      setLoading(false);
      setError('Please configure your Maximo connection in the Configuration tab first.');
    }
  }, []);

  const analyzeAllScripts = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await scriptAPI.analyzeAllScripts();
      setAnalysis(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Grid>
        <Column sm={4} md={8} lg={16}>
          <Loading description="Analyzing scripts..." withOverlay={false} />
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
            title="Error analyzing scripts"
            subtitle={error}
            lowContrast
          />
        </Column>
      </Grid>
    );
  }

  const { summary, analyses } = analysis || {};

  return (
    <Grid>
      {/* Header */}
      <Column sm={4} md={8} lg={16}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
          <h2 style={{ fontSize: '2rem', fontWeight: '400' }}>Script Analysis</h2>
          <Button
            kind="tertiary"
            renderIcon={Renew}
            onClick={analyzeAllScripts}
          >
            Re-analyze
          </Button>
        </div>
      </Column>

      {/* Summary Statistics */}
      <Column sm={4} md={4} lg={4}>
        <Tile style={{ padding: '1.5rem', height: '100%' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '1rem' }}>
            <Information size={32} />
            <div style={{ fontSize: '0.875rem', color: 'var(--cds-text-secondary)' }}>
              Total Analyzed
            </div>
          </div>
          <div style={{ fontSize: '2.5rem', fontWeight: '300' }}>
            {summary?.total || 0}
          </div>
        </Tile>
      </Column>

      <Column sm={4} md={4} lg={4}>
        <Tile style={{ padding: '1.5rem', height: '100%', borderLeft: '3px solid var(--cds-support-error)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '1rem' }}>
            <ErrorFilled size={32} style={{ fill: 'var(--cds-support-error)' }} />
            <div style={{ fontSize: '0.875rem', color: 'var(--cds-text-secondary)' }}>
              Critical Issues
            </div>
          </div>
          <div style={{ fontSize: '2.5rem', fontWeight: '300' }}>
            {summary?.critical || 0}
          </div>
        </Tile>
      </Column>

      <Column sm={4} md={4} lg={4}>
        <Tile style={{ padding: '1.5rem', height: '100%', borderLeft: '3px solid var(--cds-support-warning)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '1rem' }}>
            <WarningAlt size={32} style={{ fill: 'var(--cds-support-warning)' }} />
            <div style={{ fontSize: '0.875rem', color: 'var(--cds-text-secondary)' }}>
              Warnings
            </div>
          </div>
          <div style={{ fontSize: '2.5rem', fontWeight: '300' }}>
            {summary?.warnings || 0}
          </div>
        </Tile>
      </Column>

      <Column sm={4} md={4} lg={4}>
        <Tile style={{ padding: '1.5rem', height: '100%', borderLeft: '3px solid var(--cds-support-success)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '1rem' }}>
            <CheckmarkFilled size={32} style={{ fill: 'var(--cds-support-success)' }} />
            <div style={{ fontSize: '0.875rem', color: 'var(--cds-text-secondary)' }}>
              Clean Scripts
            </div>
          </div>
          <div style={{ fontSize: '2.5rem', fontWeight: '300' }}>
            {summary?.clean || 0}
          </div>
        </Tile>
      </Column>

      {/* Detailed Analysis */}
      {analyses && analyses.length > 0 && (
        <Column sm={4} md={8} lg={16}>
          <Tile style={{ padding: '1.5rem' }}>
            <h3 style={{ fontSize: '1.25rem', fontWeight: '400', marginBottom: '1.5rem' }}>
              Detailed Analysis Results
            </h3>
            <Accordion>
              {analyses.map((scriptAnalysis, index) => {
                const hasIssues = scriptAnalysis.issues.length > 0;
                const hasWarnings = scriptAnalysis.warnings.length > 0;
                const hasSuggestions = scriptAnalysis.suggestions.length > 0;

                if (!hasIssues && !hasWarnings && !hasSuggestions) {
                  return null;
                }

                return (
                  <AccordionItem
                    key={index}
                    title={
                      <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', width: '100%' }}>
                        <span style={{ fontWeight: '500' }}>{scriptAnalysis.scriptName}</span>
                        <div style={{ display: 'flex', gap: '0.5rem' }}>
                          <Tag type="blue" size="sm">{scriptAnalysis.language}</Tag>
                          <Tag type={scriptAnalysis.status === 'ACTIVE' ? 'green' : 'warm-gray'} size="sm">
                            {scriptAnalysis.status}
                          </Tag>
                          {hasIssues && <Tag type="red" size="sm">{scriptAnalysis.issues.length} Issues</Tag>}
                          {hasWarnings && <Tag type="yellow" size="sm">{scriptAnalysis.warnings.length} Warnings</Tag>}
                        </div>
                      </div>
                    }
                  >
                    <div style={{ padding: '1rem' }}>
                      {/* Metrics */}
                      <div style={{ display: 'flex', gap: '2rem', marginBottom: '1.5rem', fontSize: '0.875rem' }}>
                        <div>
                          <span style={{ color: 'var(--cds-text-secondary)' }}>Lines: </span>
                          <span>{scriptAnalysis.metrics?.lineCount || 0}</span>
                        </div>
                        <div>
                          <span style={{ color: 'var(--cds-text-secondary)' }}>Characters: </span>
                          <span>{scriptAnalysis.metrics?.characterCount || 0}</span>
                        </div>
                      </div>

                      {/* Issues */}
                      {hasIssues && (
                        <div style={{ marginBottom: '1rem' }}>
                          <h4 style={{ 
                            fontSize: '1rem', 
                            fontWeight: '500', 
                            marginBottom: '0.5rem',
                            color: 'var(--cds-support-error)',
                            display: 'flex',
                            alignItems: 'center',
                            gap: '0.5rem'
                          }}>
                            <ErrorFilled size={16} /> Critical Issues
                          </h4>
                          <ul style={{ listStyle: 'none', padding: 0, margin: 0 }}>
                            {scriptAnalysis.issues.map((issue, idx) => (
                              <li key={idx} style={{
                                padding: '0.75rem',
                                marginBottom: '0.5rem',
                                backgroundColor: 'var(--cds-notification-background-error)',
                                borderLeft: '3px solid var(--cds-support-error)',
                                borderRadius: '4px'
                              }}>
                                {issue}
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}

                      {/* Warnings */}
                      {hasWarnings && (
                        <div style={{ marginBottom: '1rem' }}>
                          <h4 style={{ 
                            fontSize: '1rem', 
                            fontWeight: '500', 
                            marginBottom: '0.5rem',
                            color: 'var(--cds-support-warning)',
                            display: 'flex',
                            alignItems: 'center',
                            gap: '0.5rem'
                          }}>
                            <WarningAlt size={16} /> Warnings
                          </h4>
                          <ul style={{ listStyle: 'none', padding: 0, margin: 0 }}>
                            {scriptAnalysis.warnings.map((warning, idx) => (
                              <li key={idx} style={{
                                padding: '0.75rem',
                                marginBottom: '0.5rem',
                                backgroundColor: 'var(--cds-notification-background-warning)',
                                borderLeft: '3px solid var(--cds-support-warning)',
                                borderRadius: '4px'
                              }}>
                                {warning}
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}

                      {/* Suggestions */}
                      {hasSuggestions && (
                        <div>
                          <h4 style={{ 
                            fontSize: '1rem', 
                            fontWeight: '500', 
                            marginBottom: '0.5rem',
                            color: 'var(--cds-support-info)',
                            display: 'flex',
                            alignItems: 'center',
                            gap: '0.5rem'
                          }}>
                            <Information size={16} /> Suggestions
                          </h4>
                          <ul style={{ listStyle: 'none', padding: 0, margin: 0 }}>
                            {scriptAnalysis.suggestions.map((suggestion, idx) => (
                              <li key={idx} style={{
                                padding: '0.75rem',
                                marginBottom: '0.5rem',
                                backgroundColor: 'var(--cds-notification-background-info)',
                                borderLeft: '3px solid var(--cds-support-info)',
                                borderRadius: '4px'
                              }}>
                                {suggestion}
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  </AccordionItem>
                );
              })}
            </Accordion>
          </Tile>
        </Column>
      )}
    </Grid>
  );
};

export default ScriptAnalyzer;

// Made with Bob
