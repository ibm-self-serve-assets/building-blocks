import React from 'react';
import {
  Grid,
  Column,
  Tile,
  Accordion,
  AccordionItem,
  Tag,
} from '@carbon/react';
import { CheckmarkFilled, WarningAlt, ErrorFilled } from '@carbon/icons-react';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';

const ImpactAnalysisView = ({ impactAnalysis }) => {
  if (!impactAnalysis) return null;

  const { currentState, optimizations, impactComparison, riskAssessment, optimizedCode } = impactAnalysis;

  const getLanguageForHighlighter = (lang) => {
    const langMap = {
      'jython': 'python',
      'python': 'python',
      'javascript': 'javascript',
      'java': 'java'
    };
    return langMap[lang?.toLowerCase()] || 'javascript';
  };

  // Calculate overall script score
  const calculateOverallScore = () => {
    if (!currentState) return 0;
    const codeQuality = currentState.codeQuality?.score || 0;
    const maintainability = currentState.maintainability?.score || 0;
    const performance = currentState.performance?.score || 50;
    const security = currentState.security?.score || 50;
    
    return Math.round((codeQuality + maintainability + performance + security) / 4);
  };

  const overallScore = calculateOverallScore();

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

  return (
    <Grid narrow>
      {/* Script Scoring Section */}
      <Column sm={4} md={8} lg={16}>
        <Tile style={{ 
          padding: '2rem', 
          marginBottom: '1.5rem',
          borderLeft: `4px solid ${getScoreColor(overallScore)}`
        }}>
          <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
            <h3 style={{ fontSize: '1.5rem', fontWeight: '500', marginBottom: '0.5rem' }}>
              Overall Script Score
            </h3>
            <div style={{ 
              fontSize: '4rem', 
              fontWeight: '300',
              color: getScoreColor(overallScore),
              lineHeight: '1'
            }}>
              {overallScore}/100
            </div>
            <div style={{ 
              fontSize: '1rem', 
              color: 'var(--cds-text-secondary)',
              marginTop: '0.5rem'
            }}>
              {getScoreLabel(overallScore)}
            </div>
          </div>

          <Grid narrow>
            <Column sm={4} md={4} lg={4}>
              <div style={{ 
                padding: '1.5rem',
                backgroundColor: 'var(--cds-layer-01)',
                borderRadius: '8px',
                textAlign: 'center'
              }}>
                <div style={{ fontSize: '0.875rem', color: 'var(--cds-text-secondary)', marginBottom: '0.5rem' }}>
                  Code Quality
                </div>
                <div style={{ 
                  fontSize: '2rem', 
                  fontWeight: '300',
                  color: getScoreColor(currentState?.codeQuality?.score || 0)
                }}>
                  {currentState?.codeQuality?.score || 0}
                </div>
                <div style={{ fontSize: '0.75rem', marginTop: '0.5rem', color: 'var(--cds-text-secondary)' }}>
                  {currentState?.codeQuality?.issues || 0} issues, {currentState?.codeQuality?.warnings || 0} warnings
                </div>
              </div>
            </Column>

            <Column sm={4} md={4} lg={4}>
              <div style={{ 
                padding: '1.5rem',
                backgroundColor: 'var(--cds-layer-01)',
                borderRadius: '8px',
                textAlign: 'center'
              }}>
                <div style={{ fontSize: '0.875rem', color: 'var(--cds-text-secondary)', marginBottom: '0.5rem' }}>
                  Maintainability
                </div>
                <div style={{ 
                  fontSize: '2rem', 
                  fontWeight: '300',
                  color: getScoreColor(currentState?.maintainability?.score || 0)
                }}>
                  {currentState?.maintainability?.score || 0}
                </div>
                <div style={{ fontSize: '0.75rem', marginTop: '0.5rem', color: 'var(--cds-text-secondary)' }}>
                  {currentState?.maintainability?.readability || 'N/A'}
                </div>
              </div>
            </Column>

            <Column sm={4} md={4} lg={4}>
              <div style={{ 
                padding: '1.5rem',
                backgroundColor: 'var(--cds-layer-01)',
                borderRadius: '8px',
                textAlign: 'center'
              }}>
                <div style={{ fontSize: '0.875rem', color: 'var(--cds-text-secondary)', marginBottom: '0.5rem' }}>
                  Performance
                </div>
                <div style={{ 
                  fontSize: '2rem', 
                  fontWeight: '300',
                  color: getScoreColor(currentState?.performance?.score || 50)
                }}>
                  {currentState?.performance?.estimatedComplexity || 'N/A'}
                </div>
                <div style={{ fontSize: '0.75rem', marginTop: '0.5rem', color: 'var(--cds-text-secondary)' }}>
                  {currentState?.performance?.resourceUsage || 'N/A'}
                </div>
              </div>
            </Column>

            <Column sm={4} md={4} lg={4}>
              <div style={{ 
                padding: '1.5rem',
                backgroundColor: 'var(--cds-layer-01)',
                borderRadius: '8px',
                textAlign: 'center'
              }}>
                <div style={{ fontSize: '0.875rem', color: 'var(--cds-text-secondary)', marginBottom: '0.5rem' }}>
                  Security
                </div>
                <div style={{ 
                  fontSize: '2rem', 
                  fontWeight: '300',
                  color: currentState?.security?.riskLevel === 'Low' ? 'var(--cds-support-success)' : 
                         currentState?.security?.riskLevel === 'Medium' ? 'var(--cds-support-warning)' : 
                         'var(--cds-support-error)'
                }}>
                  {currentState?.security?.riskLevel || 'N/A'}
                </div>
                <div style={{ fontSize: '0.75rem', marginTop: '0.5rem', color: 'var(--cds-text-secondary)' }}>
                  {currentState?.security?.vulnerabilities?.length || 0} vulnerabilities
                </div>
              </div>
            </Column>
          </Grid>
        </Tile>
      </Column>

      {/* Side-by-Side Code Comparison */}
      {optimizedCode && (
        <Column sm={4} md={8} lg={16}>
          <Tile style={{ padding: '1.5rem', marginBottom: '1.5rem' }}>
            <h3 style={{ fontSize: '1.25rem', fontWeight: '500', marginBottom: '1.5rem' }}>
              Code Comparison: Current vs Optimized
            </h3>
            
            <Grid narrow>
              <Column sm={4} md={4} lg={8}>
                <div style={{ 
                  marginBottom: '0.75rem',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.5rem'
                }}>
                  <ErrorFilled size={20} style={{ fill: 'var(--cds-support-error)' }} />
                  <span style={{ fontSize: '1rem', fontWeight: '600' }}>Current Script</span>
                </div>
                <div style={{ 
                  maxHeight: '500px', 
                  overflow: 'auto',
                  border: '2px solid var(--cds-support-error)',
                  borderRadius: '4px'
                }}>
                  <SyntaxHighlighter
                    language={getLanguageForHighlighter(impactAnalysis.language)}
                    style={vscDarkPlus}
                    showLineNumbers
                    wrapLines
                    customStyle={{
                      margin: 0,
                      borderRadius: '4px',
                      fontSize: '0.875rem'
                    }}
                  >
                    {optimizedCode.current || '// Current code not available'}
                  </SyntaxHighlighter>
                </div>
              </Column>

              <Column sm={4} md={4} lg={8}>
                <div style={{ 
                  marginBottom: '0.75rem',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.5rem'
                }}>
                  <CheckmarkFilled size={20} style={{ fill: 'var(--cds-support-success)' }} />
                  <span style={{ fontSize: '1rem', fontWeight: '600' }}>Optimized Script</span>
                </div>
                <div style={{ 
                  maxHeight: '500px', 
                  overflow: 'auto',
                  border: '2px solid var(--cds-support-success)',
                  borderRadius: '4px'
                }}>
                  <SyntaxHighlighter
                    language={getLanguageForHighlighter(impactAnalysis.language)}
                    style={vscDarkPlus}
                    showLineNumbers
                    wrapLines
                    customStyle={{
                      margin: 0,
                      borderRadius: '4px',
                      fontSize: '0.875rem'
                    }}
                  >
                    {optimizedCode.optimized || '// Optimized code not available'}
                  </SyntaxHighlighter>
                </div>
              </Column>
            </Grid>
          </Tile>
        </Column>
      )}

      {/* Comparison Summary */}
      {impactComparison && (
        <Column sm={4} md={8} lg={16}>
          <Tile style={{ padding: '1.5rem', marginBottom: '1.5rem' }}>
            <h3 style={{ fontSize: '1.25rem', fontWeight: '500', marginBottom: '1.5rem' }}>
              Impact Comparison Summary
            </h3>

            <Grid narrow>
              {/* Without Improvements */}
              <Column sm={4} md={8} lg={8}>
                <div style={{ 
                  padding: '1.5rem',
                  backgroundColor: 'var(--cds-notification-background-error)',
                  borderRadius: '8px',
                  border: '1px solid var(--cds-support-error)',
                  height: '100%'
                }}>
                  <h4 style={{ 
                    fontSize: '1.125rem', 
                    fontWeight: '600', 
                    marginBottom: '1rem',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.5rem'
                  }}>
                    <ErrorFilled size={24} style={{ fill: 'var(--cds-support-error)' }} />
                    Without Improvements
                  </h4>
                  
                  <div style={{ fontSize: '0.875rem', lineHeight: '1.8' }}>
                    <div style={{ marginBottom: '1rem' }}>
                      <strong style={{ display: 'block', marginBottom: '0.5rem' }}>Performance:</strong>
                      <ul style={{ marginTop: '0.5rem', paddingLeft: '1.5rem' }}>
                        <li>Execution Time: {impactComparison.withoutImprovements?.performance?.executionTime || 'N/A'}</li>
                        <li>Memory Usage: {impactComparison.withoutImprovements?.performance?.memoryUsage || 'N/A'}</li>
                        <li>CPU Usage: {impactComparison.withoutImprovements?.performance?.cpuUsage || 'N/A'}</li>
                      </ul>
                    </div>

                    <div style={{ marginBottom: '1rem' }}>
                      <strong style={{ display: 'block', marginBottom: '0.5rem' }}>Reliability:</strong>
                      <ul style={{ marginTop: '0.5rem', paddingLeft: '1.5rem' }}>
                        <li>Error Rate: {impactComparison.withoutImprovements?.reliability?.errorRate || 'N/A'}</li>
                        <li>Crash Risk: {impactComparison.withoutImprovements?.reliability?.crashRisk || 'N/A'}</li>
                      </ul>
                    </div>

                    <div>
                      <strong style={{ display: 'block', marginBottom: '0.5rem' }}>Maintainability:</strong>
                      <ul style={{ marginTop: '0.5rem', paddingLeft: '1.5rem' }}>
                        <li>Code Complexity: High</li>
                        <li>Error Handling: Poor</li>
                        <li>Resource Management: Inefficient</li>
                      </ul>
                    </div>
                  </div>
                </div>
              </Column>

              {/* With Improvements */}
              <Column sm={4} md={8} lg={8}>
                <div style={{ 
                  padding: '1.5rem',
                  backgroundColor: 'var(--cds-notification-background-success)',
                  borderRadius: '8px',
                  border: '1px solid var(--cds-support-success)',
                  height: '100%'
                }}>
                  <h4 style={{ 
                    fontSize: '1.125rem', 
                    fontWeight: '600', 
                    marginBottom: '1rem',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.5rem'
                  }}>
                    <CheckmarkFilled size={24} style={{ fill: 'var(--cds-support-success)' }} />
                    With Improvements
                  </h4>
                  
                  <div style={{ fontSize: '0.875rem', lineHeight: '1.8' }}>
                    <div style={{ marginBottom: '1rem' }}>
                      <strong style={{ display: 'block', marginBottom: '0.5rem' }}>Performance:</strong>
                      <ul style={{ marginTop: '0.5rem', paddingLeft: '1.5rem' }}>
                        <li>Execution Time: {impactComparison.withImprovements?.performance?.executionTime || 'N/A'}</li>
                        <li>Memory Usage: {impactComparison.withImprovements?.performance?.memoryUsage || 'N/A'}</li>
                        <li>CPU Usage: {impactComparison.withImprovements?.performance?.cpuUsage || 'N/A'}</li>
                      </ul>
                    </div>

                    <div style={{ marginBottom: '1rem' }}>
                      <strong style={{ display: 'block', marginBottom: '0.5rem' }}>Reliability:</strong>
                      <ul style={{ marginTop: '0.5rem', paddingLeft: '1.5rem' }}>
                        <li>Error Rate: {impactComparison.withImprovements?.reliability?.errorRate || 'N/A'}</li>
                        <li>Crash Risk: {impactComparison.withImprovements?.reliability?.crashRisk || 'N/A'}</li>
                      </ul>
                    </div>

                    <div>
                      <strong style={{ display: 'block', marginBottom: '0.5rem' }}>Maintainability:</strong>
                      <ul style={{ marginTop: '0.5rem', paddingLeft: '1.5rem' }}>
                        <li>Code Complexity: Low</li>
                        <li>Error Handling: Robust</li>
                        <li>Resource Management: Optimized</li>
                      </ul>
                    </div>
                  </div>
                </div>
              </Column>

              {/* Net Benefit */}
              {impactComparison.netBenefit && (
                <Column sm={4} md={8} lg={16}>
                  <div style={{ 
                    padding: '1.5rem',
                    backgroundColor: 'var(--cds-layer-accent-01)',
                    borderRadius: '8px',
                    marginTop: '1rem',
                    borderLeft: '4px solid var(--cds-support-success)'
                  }}>
                    <h4 style={{ fontSize: '1.125rem', fontWeight: '600', marginBottom: '1rem' }}>
                      Expected Benefits
                    </h4>
                    <Grid narrow>
                      <Column sm={2} md={4} lg={4}>
                        <div style={{ textAlign: 'center', padding: '1rem' }}>
                          <div style={{ fontSize: '0.875rem', color: 'var(--cds-text-secondary)', marginBottom: '0.5rem' }}>
                            Performance Gain
                          </div>
                          <div style={{ fontSize: '2rem', fontWeight: '300', color: 'var(--cds-support-success)' }}>
                            {impactComparison.netBenefit.performanceGain || 'N/A'}
                          </div>
                        </div>
                      </Column>
                      <Column sm={2} md={4} lg={4}>
                        <div style={{ textAlign: 'center', padding: '1rem' }}>
                          <div style={{ fontSize: '0.875rem', color: 'var(--cds-text-secondary)', marginBottom: '0.5rem' }}>
                            Memory Savings
                          </div>
                          <div style={{ fontSize: '2rem', fontWeight: '300', color: 'var(--cds-support-success)' }}>
                            {impactComparison.netBenefit.costSavings || 'N/A'}
                          </div>
                        </div>
                      </Column>
                      <Column sm={2} md={4} lg={4}>
                        <div style={{ textAlign: 'center', padding: '1rem' }}>
                          <div style={{ fontSize: '0.875rem', color: 'var(--cds-text-secondary)', marginBottom: '0.5rem' }}>
                            Risk Reduction
                          </div>
                          <div style={{ fontSize: '2rem', fontWeight: '300', color: 'var(--cds-support-success)' }}>
                            {impactComparison.netBenefit.riskReduction || 'N/A'}
                          </div>
                        </div>
                      </Column>
                      <Column sm={2} md={4} lg={4}>
                        <div style={{ textAlign: 'center', padding: '1rem' }}>
                          <div style={{ fontSize: '0.875rem', color: 'var(--cds-text-secondary)', marginBottom: '0.5rem' }}>
                            Scalability
                          </div>
                          <div style={{ fontSize: '2rem', fontWeight: '300', color: 'var(--cds-support-success)' }}>
                            {impactComparison.netBenefit.roi || 'Improved'}
                          </div>
                        </div>
                      </Column>
                    </Grid>
                  </div>
                </Column>
              )}
            </Grid>
          </Tile>
        </Column>
      )}

      {/* Optimization Recommendations */}
      {optimizations && optimizations.length > 0 && (
        <Column sm={4} md={8} lg={16}>
          <Tile style={{ padding: '1.5rem', marginBottom: '1.5rem' }}>
            <h3 style={{ fontSize: '1.25rem', fontWeight: '500', marginBottom: '1.5rem' }}>
              Detailed Optimization Recommendations
            </h3>
            
            <Accordion>
              {optimizations.map((opt, index) => (
                <AccordionItem
                  key={index}
                  title={
                    <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', width: '100%' }}>
                      <span style={{ fontWeight: '500' }}>{opt.category}</span>
                      <Tag type={opt.priority === 'critical' ? 'red' : opt.priority === 'high' ? 'magenta' : opt.priority === 'medium' ? 'purple' : 'blue'} size="sm">
                        {opt.priority}
                      </Tag>
                    </div>
                  }
                >
                  <div style={{ padding: '1rem' }}>
                    {/* Issue Description */}
                    <div style={{ marginBottom: '1.5rem' }}>
                      <h4 style={{ fontSize: '0.875rem', fontWeight: '600', marginBottom: '0.5rem', color: 'var(--cds-text-secondary)' }}>
                        Issue
                      </h4>
                      <p>{opt.issue}</p>
                    </div>

                    {/* Recommendation */}
                    <div style={{ marginBottom: '1.5rem' }}>
                      <h4 style={{ fontSize: '0.875rem', fontWeight: '600', marginBottom: '0.5rem', color: 'var(--cds-text-secondary)' }}>
                        Recommendation
                      </h4>
                      <p>{opt.recommendation}</p>
                    </div>

                    {/* Expected Impact */}
                    {opt.impact && (
                      <div>
                        <h4 style={{ fontSize: '0.875rem', fontWeight: '600', marginBottom: '0.75rem', color: 'var(--cds-text-secondary)' }}>
                          Expected Impact
                        </h4>
                        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
                          {Object.entries(opt.impact).map(([key, value]) => (
                            <Tag key={key} type="green" size="sm">
                              {key}: {value}
                            </Tag>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </AccordionItem>
              ))}
            </Accordion>
          </Tile>
        </Column>
      )}

      {/* Risk Assessment */}
      {riskAssessment && riskAssessment.length > 0 && (
        <Column sm={4} md={8} lg={16}>
          <Tile style={{ padding: '1.5rem', borderLeft: '4px solid var(--cds-support-error)' }}>
            <h3 style={{ fontSize: '1.25rem', fontWeight: '500', marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <WarningAlt size={24} style={{ fill: 'var(--cds-support-error)' }} />
              Risk Assessment
            </h3>
            
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              {riskAssessment.map((risk, index) => (
                <div key={index} style={{
                  padding: '1rem',
                  backgroundColor: 'var(--cds-notification-background-error)',
                  borderRadius: '4px',
                  border: '1px solid var(--cds-support-error)'
                }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                    <strong>{risk.type} Risk</strong>
                    <Tag type="red" size="sm">{risk.impact}</Tag>
                  </div>
                  <p style={{ fontSize: '0.875rem', marginBottom: '0.5rem' }}>{risk.description}</p>
                  <div style={{ fontSize: '0.75rem', color: 'var(--cds-text-secondary)' }}>
                    <div>Probability: {risk.probability}</div>
                    <div>Mitigation: {risk.mitigation}</div>
                  </div>
                </div>
              ))}
            </div>
          </Tile>
        </Column>
      )}
    </Grid>
  );
};

export default ImpactAnalysisView;

// Made with Bob