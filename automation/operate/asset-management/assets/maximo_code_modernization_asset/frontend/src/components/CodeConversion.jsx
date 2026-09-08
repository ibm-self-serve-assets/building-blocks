import React, { useState, useEffect, useRef } from 'react';
import {
  Grid,
  Column,
  TextArea,
  Button,
  Dropdown,
  Loading,
  InlineNotification,
  Tabs,
  TabList,
  Tab,
  TabPanels,
  TabPanel,
  Modal,
  TextInput,
  Form,
  FormGroup,
  CodeSnippet,
  Tag,
  FileUploader,
} from '@carbon/react';
import {
  ArrowRight,
  CheckmarkFilled,
  WarningAlt,
  Code,
  Play,
  Save,
  DocumentAdd,
  Download
} from '@carbon/icons-react';
import { conversionAPI } from '../services/api';

const CodeConversion = () => {
  const [javaCode, setJavaCode] = useState('');
  const [targetLanguage, setTargetLanguage] = useState(null);
  const [languages, setLanguages] = useState([]);
  const [converting, setConverting] = useState(false);
  const [testing, setTesting] = useState(false);
  const [creating, setCreating] = useState(false);
  const [conversionResult, setConversionResult] = useState(null);
  const [testResult, setTestResult] = useState(null);
  const [error, setError] = useState(null);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [scriptName, setScriptName] = useState('');
  const [scriptDescription, setScriptDescription] = useState('');
  const [launchPoint, setLaunchPoint] = useState('');
  const [launchPointType, setLaunchPointType] = useState('OBJECT');
  const [objectName, setObjectName] = useState('WORKORDER');
  const [uploadedFileName, setUploadedFileName] = useState('');
  const fileInputRef = useRef(null);
  const resultsRef = useRef(null);

  useEffect(() => {
    fetchSupportedLanguages();
  }, []);

  const fetchSupportedLanguages = async () => {
    try {
      const data = await conversionAPI.getSupportedLanguages();
      const languageList = data.languages || [];
      setLanguages(languageList);
      
      // Set Python (Jython) as default selection
      const pythonLanguage = languageList.find(lang => lang.id === 'python');
      if (pythonLanguage) {
        setTargetLanguage(pythonLanguage);
      }
    } catch (err) {
      console.error('Failed to load languages from backend:', err);
      // Fallback to hardcoded languages if backend is not available
      const fallbackLanguages = [
        { id: 'python', name: 'Python (Jython)', engine: 'Jython', version: '2.7.4' },
        { id: 'javascript', name: 'JavaScript', engine: 'Nashorn', version: '15.6' },
        { id: 'nashorn', name: 'Nashorn', engine: 'Nashorn', version: '15.6' },
        { id: 'ecmascript', name: 'ECMAScript', engine: 'Nashorn', version: '15.6' },
        { id: 'mbr', name: 'Maximo Business Rules', engine: 'MBR', version: '1.0' }
      ];
      setLanguages(fallbackLanguages);
      setTargetLanguage(fallbackLanguages[0]); // Default to Python
      setError('Backend server not available. Using offline mode. Please start the backend server for full functionality.');
    }
  };

  const handleConvert = async () => {
    if (!javaCode.trim()) {
      setError('Please enter Java code to convert');
      return;
    }

    if (!targetLanguage) {
      setError('Please select a target language');
      return;
    }

    try {
      setConverting(true);
      setError(null);
      setConversionResult(null);
      setTestResult(null);

      const result = await conversionAPI.convertCode(javaCode, targetLanguage.id);

      if (result.success) {
        setConversionResult(result);
        // Scroll to results after a short delay to ensure DOM is updated
        setTimeout(() => {
          resultsRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }, 100);
      } else {
        setError(result.error || 'Conversion failed');
      }
    } catch (err) {
      setError('Conversion failed: ' + err.message);
    } finally {
      setConverting(false);
    }
  };

  const handleTestScript = async () => {
    if (!conversionResult || !conversionResult.convertedCode) {
      setError('No converted code to test');
      return;
    }

    try {
      setTesting(true);
      setError(null);

      const result = await conversionAPI.testScript(
        conversionResult.convertedCode,
        targetLanguage.id
      );

      setTestResult(result.testResult);
    } catch (err) {
      setError('Test failed: ' + err.message);
    } finally {
      setTesting(false);
    }
  };

  const handleCreateScript = async () => {
    if (!scriptName.trim()) {
      setError('Please enter a script name');
      return;
    }

    try {
      setCreating(true);
      setError(null);

      const scriptData = {
        scriptName: scriptName.trim(),
        scriptCode: conversionResult.convertedCode,
        description: scriptDescription.trim() || `Converted from Java - ${scriptName.trim()}`,
        language: targetLanguage.id,
        scriptLanguage: targetLanguage.id
      };

      const result = await conversionAPI.createScript(scriptData);

      if (result.success) {
        setShowCreateModal(false);
        setError(null);
        
        // Show Maximo-themed success modal
        const successModal = document.createElement('div');
        successModal.style.cssText = `
          position: fixed;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background: rgba(0, 0, 0, 0.7);
          display: flex;
          align-items: center;
          justify-content: center;
          z-index: 10000;
          animation: fadeIn 0.2s ease-in;
          cursor: pointer;
        `;
        
        // Close modal when clicking on overlay
        successModal.addEventListener('click', (e) => {
          if (e.target === successModal) {
            successModal.remove();
          }
        });
        
        // Extract a brief functionality description from the script
        const getFunctionality = () => {
          const code = conversionResult.convertedCode.toLowerCase();
          if (code.includes('labor') && code.includes('validate')) return 'Validates labor transactions';
          if (code.includes('workorder') || code.includes('work order')) return 'Manages work order operations';
          if (code.includes('asset')) return 'Handles asset management';
          if (code.includes('location')) return 'Manages location data';
          if (code.includes('inventory')) return 'Controls inventory operations';
          if (code.includes('purchase')) return 'Processes purchase orders';
          if (code.includes('service request')) return 'Handles service requests';
          return 'Automation script logic';
        };
        
        successModal.innerHTML = `
          <div style="
            background: #262626;
            border: 1px solid #393939;
            border-radius: 4px;
            padding: 2rem;
            max-width: 500px;
            width: 90%;
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.5);
            animation: slideUp 0.3s ease-out;
            cursor: default;
            font-family: 'IBM Plex Sans', sans-serif;
          " onclick="event.stopPropagation()">
            <div style="text-align: center;">
              <!-- Success Icon -->
              <div style="
                width: 64px;
                height: 64px;
                background: #24a148;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                margin: 0 auto 1.5rem;
              ">
                <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="3" stroke-linecap="round" stroke-linejoin="round">
                  <polyline points="20 6 9 17 4 12"></polyline>
                </svg>
              </div>
              
              <!-- Title -->
              <h2 style="
                font-size: 1.5rem;
                font-weight: 400;
                color: #f4f4f4;
                margin-bottom: 0.5rem;
              ">Script Created Successfully</h2>
              
              <!-- Subtitle -->
              <p style="
                color: #c6c6c6;
                margin-bottom: 1.5rem;
                font-size: 0.875rem;
              ">The automation script has been created in Maximo</p>
              
              <!-- Details -->
              <div style="
                background: #161616;
                border: 1px solid #393939;
                padding: 1.25rem;
                border-radius: 4px;
                margin-bottom: 1.5rem;
                text-align: left;
              ">
                <div style="margin-bottom: 1rem;">
                  <div style="color: #8d8d8d; font-size: 0.75rem; margin-bottom: 0.25rem;">SCRIPT NAME</div>
                  <div style="color: #f4f4f4; font-weight: 600; font-size: 1rem;">${scriptName.trim()}</div>
                </div>
                
                <div style="margin-bottom: 1rem;">
                  <div style="color: #8d8d8d; font-size: 0.75rem; margin-bottom: 0.25rem;">LANGUAGE</div>
                  <div style="color: #78a9ff; font-weight: 500;">${targetLanguage.name}</div>
                </div>
                
                <div>
                  <div style="color: #8d8d8d; font-size: 0.75rem; margin-bottom: 0.25rem;">FUNCTIONALITY</div>
                  <div style="color: #c6c6c6; font-size: 0.875rem;">${getFunctionality()}</div>
                </div>
              </div>
              
              <!-- Action Button -->
              <button onclick="this.closest('div').parentElement.remove()" style="
                background: #0f62fe;
                color: white;
                border: none;
                padding: 0.875rem 2rem;
                border-radius: 4px;
                font-size: 0.875rem;
                font-weight: 400;
                cursor: pointer;
                transition: background 0.1s ease;
                width: 100%;
              "
              onmouseover="this.style.background='#0353e9'"
              onmouseout="this.style.background='#0f62fe'">
                OK
              </button>
            </div>
          </div>
          <style>
            @keyframes fadeIn {
              from { opacity: 0; }
              to { opacity: 1; }
            }
            @keyframes slideUp {
              from { transform: translateY(10px); opacity: 0; }
              to { transform: translateY(0); opacity: 1; }
            }
          </style>
        `;
        
        document.body.appendChild(successModal);
        
        // Reset form after a delay
        setTimeout(() => {
          setJavaCode('');
          setConversionResult(null);
          setTestResult(null);
          setScriptName('');
          setScriptDescription('');
          setUploadedFileName('');
        }, 500);
      } else {
        setError(result.message || 'Failed to create script');
      }
    } catch (err) {
      setError('Failed to create script: ' + err.message);
    } finally {
      setCreating(false);
    }
  };

  const handleFileUpload = (event) => {
    const file = event.target.files[0];
    if (file) {
      // Check if file is a Java file
      if (!file.name.endsWith('.java')) {
        setError('Please upload a Java (.java) file');
        return;
      }

      const reader = new FileReader();
      reader.onload = (e) => {
        const content = e.target.result;
        setJavaCode(content);
        setUploadedFileName(file.name);
        setError(null);
      };
      reader.onerror = () => {
        setError('Failed to read file');
      };
      reader.readAsText(file);
    }
  };

  const handleReset = () => {
    setJavaCode('');
    setTargetLanguage(null);
    setConversionResult(null);
    setTestResult(null);
    setError(null);
    setScriptName('');
    setScriptDescription('');
    setLaunchPoint('');
    setLaunchPointType('OBJECT');
    setObjectName('WORKORDER');
    setUploadedFileName('');
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <Grid>
      <Column sm={4} md={8} lg={16}>
        <div style={{ padding: '0 2rem', marginBottom: '2rem' }}>
          <h2 style={{ marginBottom: '1rem' }}>Java to Automation Script Converter</h2>
          <p style={{ color: 'var(--cds-text-secondary)' }}>
            Convert Maximo Java classes to automation scripts while preserving business logic and functionality.
          </p>
        </div>

        {error && (
          <div style={{ padding: '0 2rem' }}>
            <InlineNotification
              kind="error"
              title="Error"
              subtitle={error}
              onCloseButtonClick={() => setError(null)}
              lowContrast
              style={{ marginBottom: '1rem' }}
            />
          </div>
        )}

        <div style={{ padding: '0 2rem' }}>
          <Grid narrow>
          <Column sm={4} md={4} lg={8}>
            <FormGroup legendText="Java Code Input">
              <div style={{ marginBottom: '1rem' }}>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                  <Button
                    kind="primary"
                    size="lg"
                    renderIcon={DocumentAdd}
                    onClick={() => fileInputRef.current?.click()}
                    disabled={converting}
                    style={{ width: '100%' }}
                  >
                    Choose Java File
                  </Button>
                  {uploadedFileName && (
                    <div style={{
                      padding: '1rem',
                      backgroundColor: 'var(--cds-layer-01)',
                      borderRadius: '4px',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '0.5rem'
                    }}>
                      <Tag type="blue">{uploadedFileName}</Tag>
                      <span style={{ fontSize: '0.875rem', color: 'var(--cds-text-secondary)' }}>
                        File loaded successfully
                      </span>
                    </div>
                  )}
                  {javaCode && (
                    <div style={{
                      padding: '1rem',
                      backgroundColor: 'var(--cds-layer-01)',
                      borderRadius: '4px',
                      fontSize: '0.875rem',
                      color: 'var(--cds-text-secondary)'
                    }}>
                      <strong>Lines of code:</strong> {javaCode.split('\n').length}
                    </div>
                  )}
                </div>
                <input
                  ref={fileInputRef}
                  type="file"
                  accept=".java"
                  onChange={handleFileUpload}
                  style={{ display: 'none' }}
                />
              </div>
            </FormGroup>
          </Column>

          <Column sm={4} md={4} lg={8}>
            <FormGroup legendText="Target Language">
              <Dropdown
                id="target-language"
                titleText="Select Target Language"
                label="Choose scripting language"
                items={languages}
                itemToString={(item) => (item ? item.name : '')}
                selectedItem={targetLanguage}
                onChange={({ selectedItem }) => setTargetLanguage(selectedItem)}
                disabled={converting}
              />
              
              {targetLanguage && (
                <div style={{ marginTop: '1rem', padding: '1rem', backgroundColor: 'var(--cds-layer-01)', borderRadius: '4px' }}>
                  <p style={{ fontSize: '0.875rem', marginBottom: '0.5rem' }}>
                    <strong>Engine:</strong> {targetLanguage.engine}
                  </p>
                  <p style={{ fontSize: '0.875rem' }}>
                    <strong>Version:</strong> {targetLanguage.version}
                  </p>
                </div>
              )}

              <div style={{ marginTop: '2rem' }}>
                <Button
                  kind="primary"
                  renderIcon={ArrowRight}
                  onClick={handleConvert}
                  disabled={converting || !javaCode.trim() || !targetLanguage}
                >
                  {converting ? 'Converting...' : 'Convert Code'}
                </Button>
                <Button
                  kind="secondary"
                  onClick={handleReset}
                  disabled={converting}
                  style={{ marginLeft: '1rem' }}
                >
                  Reset
                </Button>
              </div>
            </FormGroup>
          </Column>
          </Grid>
        </div>

        {converting && (
          <div style={{ padding: '0 2rem', marginTop: '2rem' }}>
            <Loading description="Converting Java code to automation script..." withOverlay={false} />
          </div>
        )}

        {conversionResult && conversionResult.success && (
          <div ref={resultsRef} style={{ padding: '0 2rem', marginTop: '3rem' }}>
            <div style={{ padding: '1rem', backgroundColor: 'var(--cds-layer-01)', borderRadius: '4px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
                <div>
                  <h3 style={{ marginBottom: '0.5rem' }}>Converted {conversionResult.language} Code</h3>
                  <p style={{ color: 'var(--cds-text-secondary)', fontSize: '0.875rem' }}>
                    Review the converted automation script below. Test it before creating in Maximo.
                  </p>
                </div>
                <div style={{ display: 'flex', gap: '0.5rem' }}>
                  <Button
                    kind="tertiary"
                    size="md"
                    renderIcon={Play}
                    onClick={handleTestScript}
                    disabled={testing}
                  >
                    {testing ? 'Testing...' : 'Test Script'}
                  </Button>
                  <Button
                    kind="secondary"
                    size="md"
                    renderIcon={Download}
                    onClick={() => {
                      const blob = new Blob([conversionResult.convertedCode], { type: 'text/plain' });
                      const url = URL.createObjectURL(blob);
                      const a = document.createElement('a');
                      a.href = url;
                      a.download = `${scriptName || 'converted_script'}.${targetLanguage.id === 'python' ? 'py' : 'js'}`;
                      document.body.appendChild(a);
                      a.click();
                      document.body.removeChild(a);
                      URL.revokeObjectURL(url);
                    }}
                  >
                    Download Script
                  </Button>
                  <Button
                    kind="primary"
                    size="md"
                    renderIcon={Save}
                    onClick={() => setShowCreateModal(true)}
                    disabled={!testResult || !testResult.passed}
                  >
                    Create in Maximo
                  </Button>
                </div>
              </div>

              {testResult && (
                <InlineNotification
                  kind={testResult.passed ? 'success' : 'error'}
                  title={testResult.passed ? 'Test Passed' : 'Test Failed'}
                  subtitle={testResult.message}
                  lowContrast
                  hideCloseButton
                  style={{ marginBottom: '1rem' }}
                />
              )}

              <div style={{ marginBottom: '1.5rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                  <h4 style={{ margin: 0 }}>Converted Script</h4>
                  <Button
                    kind="ghost"
                    size="sm"
                    onClick={() => {
                      navigator.clipboard.writeText(conversionResult.convertedCode);
                    }}
                  >
                    Copy to clipboard
                  </Button>
                </div>
                <div style={{
                  border: '1px solid var(--cds-border-subtle)',
                  borderRadius: '4px',
                  backgroundColor: 'var(--cds-layer-01)',
                  maxHeight: '500px',
                  minHeight: '300px',
                  overflow: 'auto',
                  fontFamily: '"Courier New", Courier, monospace',
                  fontSize: '13px',
                  lineHeight: '1.6'
                }}>
                  <pre style={{
                    margin: 0,
                    padding: '1rem',
                    display: 'grid',
                    gridTemplateColumns: 'auto 1fr',
                    gap: '1rem'
                  }}>
                    <code style={{
                      color: 'var(--cds-text-secondary)',
                      textAlign: 'right',
                      userSelect: 'none',
                      paddingRight: '1rem',
                      borderRight: '1px solid var(--cds-border-subtle)',
                      fontFamily: '"Courier New", Courier, monospace'
                    }}>
                      {conversionResult.convertedCode.split('\n').map((_, i) => (
                        <div key={i}>{i + 1}</div>
                      ))}
                    </code>
                    <code style={{
                      color: 'var(--cds-text-primary)',
                      whiteSpace: 'pre',
                      fontFamily: '"Courier New", Courier, monospace'
                    }}>
                      {conversionResult.convertedCode}
                    </code>
                  </pre>
                </div>
              </div>

              {conversionResult.analysis && (
                <div style={{ marginTop: '2rem', paddingTop: '1.5rem', borderTop: '1px solid var(--cds-border-subtle)' }}>
                  <h4 style={{ marginBottom: '1rem' }}>Code Analysis & Optimizations</h4>
                    
                  {conversionResult.analysis.optimizations && conversionResult.analysis.optimizations.length > 0 && (
                    <div style={{ marginBottom: '1.5rem' }}>
                      <h5 style={{ marginBottom: '0.75rem', fontSize: '0.875rem', fontWeight: 600, display: 'flex', alignItems: 'center' }}>
                        <CheckmarkFilled size={20} style={{ marginRight: '0.5rem', color: 'var(--cds-support-success)' }} />
                        Applied Optimizations
                      </h5>
                      {conversionResult.analysis.optimizations.map((opt, idx) => (
                        <div key={idx} style={{ marginBottom: '0.75rem', padding: '1rem', backgroundColor: 'var(--cds-layer-02)', borderRadius: '4px', borderLeft: '3px solid var(--cds-support-success)' }}>
                          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: '0.5rem' }}>
                            <strong style={{ fontSize: '0.875rem', color: 'var(--cds-text-primary)' }}>{opt.category}</strong>
                            <Tag type="green" size="sm">Optimized</Tag>
                          </div>
                          <p style={{ fontSize: '0.875rem', color: 'var(--cds-text-secondary)', marginBottom: '0.5rem' }}>
                            {opt.description}
                          </p>
                          <p style={{ fontSize: '0.75rem', color: 'var(--cds-text-secondary)', fontStyle: 'italic' }}>
                            ✓ {opt.benefit}
                          </p>
                        </div>
                      ))}
                    </div>
                  )}

                  {(!conversionResult.analysis.optimizations || conversionResult.analysis.optimizations.length === 0) && (
                    <InlineNotification
                      kind="success"
                      title="Conversion Complete"
                      subtitle="The code was converted successfully without any warnings."
                    hideCloseButton
                  />
                )}
              </div>
            )}
          </div>
          </div>
        )}

        <Modal
          open={showCreateModal}
          onRequestClose={() => setShowCreateModal(false)}
          onRequestSubmit={handleCreateScript}
          modalHeading="Create Script in Maximo"
          primaryButtonText={creating ? 'Creating...' : 'Create Script'}
          secondaryButtonText="Cancel"
          primaryButtonDisabled={creating || !scriptName.trim()}
        >
          <Form>
            <div style={{ marginBottom: '1rem' }}>
              <TextInput
                id="script-name"
                labelText="Script Name"
                placeholder="Enter script name (e.g., MY_CONVERTED_SCRIPT)"
                value={scriptName}
                onChange={(e) => setScriptName(e.target.value)}
                disabled={creating}
                required
              />
            </div>
            
            <div style={{ marginBottom: '1rem' }}>
              <TextArea
                id="script-description"
                labelText="Description"
                placeholder="Enter script description"
                rows={3}
                value={scriptDescription}
                onChange={(e) => setScriptDescription(e.target.value)}
                disabled={creating}
              />
            </div>
            
            <div style={{ padding: '1rem', backgroundColor: 'var(--cds-layer-01)', borderRadius: '4px' }}>
              <p style={{ fontSize: '0.875rem', marginBottom: '0.5rem' }}>
                <strong>Script Language:</strong> {targetLanguage?.name}
              </p>
              <p style={{ fontSize: '0.875rem', margin: 0 }}>
                <strong>Engine:</strong> {targetLanguage?.engine} {targetLanguage?.version}
              </p>
            </div>
          </Form>
        </Modal>
      </Column>
    </Grid>
  );
};

export default CodeConversion;

// Made with Bob