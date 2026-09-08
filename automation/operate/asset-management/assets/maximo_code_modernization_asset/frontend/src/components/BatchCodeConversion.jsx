import React, { useState, useEffect, useRef } from 'react';
import {
  Grid,
  Column,
  Button,
  Dropdown,
  Loading,
  InlineNotification,
  Tabs,
  TabList,
  Tab,
  TabPanels,
  TabPanel,
  DataTable,
  TableContainer,
  Table,
  TableHead,
  TableRow,
  TableHeader,
  TableBody,
  TableCell,
  ProgressBar,
  Tag,
  Modal,
  FileUploader,
} from '@carbon/react';
import {
  Upload,
  Download,
  CheckmarkFilled,
  WarningAlt,
  ErrorFilled,
  Renew,
  DocumentMultiple_01,
} from '@carbon/icons-react';
import { conversionAPI } from '../services/api';

const BatchCodeConversion = () => {
  const [languages, setLanguages] = useState([]);
  const [targetLanguage, setTargetLanguage] = useState(null);
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [converting, setConverting] = useState(false);
  const [batchId, setBatchId] = useState(null);
  const [batchStatus, setBatchStatus] = useState(null);
  const [batchResults, setBatchResults] = useState(null);
  const [error, setError] = useState(null);
  const [conversionHistory, setConversionHistory] = useState([]);
  const [showHistoryModal, setShowHistoryModal] = useState(false);
  const fileInputRef = useRef(null);
  const pollIntervalRef = useRef(null);

  useEffect(() => {
    fetchLanguages();
    fetchHistory();
    
    return () => {
      if (pollIntervalRef.current) {
        clearInterval(pollIntervalRef.current);
      }
    };
  }, []);

  const fetchLanguages = async () => {
    try {
      const result = await conversionAPI.getSupportedLanguages();
      setLanguages(result.languages || []);
      // Set Python as default
      const defaultLang = result.languages?.find(l => l.id === 'python');
      if (defaultLang) setTargetLanguage(defaultLang);
    } catch (err) {
      setError('Failed to load supported languages: ' + err.message);
    }
  };

  const fetchHistory = async () => {
    try {
      const result = await conversionAPI.getConversionHistory();
      setConversionHistory(result.history || []);
    } catch (err) {
      console.error('Failed to load history:', err);
    }
  };

  const handleFileSelect = (event) => {
    const files = Array.from(event.target.files || []);
    const javaFiles = files.filter(f => f.name.endsWith('.java'));
    
    if (javaFiles.length === 0) {
      setError('Please select .java files only');
      return;
    }
    
    setSelectedFiles(javaFiles);
    setError(null);
  };

  const handleStartBatchConversion = async () => {
    if (selectedFiles.length === 0) {
      setError('Please select Java files to convert');
      return;
    }

    if (!targetLanguage) {
      setError('Please select a target language');
      return;
    }

    try {
      setConverting(true);
      setError(null);
      setBatchResults(null);

      // Read file contents
      const filePromises = selectedFiles.map(file => {
        return new Promise((resolve, reject) => {
          const reader = new FileReader();
          reader.onload = (e) => resolve({
            filename: file.name,
            content: e.target.result
          });
          reader.onerror = reject;
          reader.readAsText(file);
        });
      });

      const filesData = await Promise.all(filePromises);

      // Start batch conversion
      const result = await conversionAPI.startBatchConversion(filesData, targetLanguage.id);
      
      if (result.success) {
        setBatchId(result.batchId);
        startPolling(result.batchId);
      } else {
        setError(result.message || 'Failed to start batch conversion');
        setConverting(false);
      }
    } catch (err) {
      setError('Batch conversion failed: ' + err.message);
      setConverting(false);
    }
  };

  const startPolling = (id) => {
    // Poll every 2 seconds
    pollIntervalRef.current = setInterval(async () => {
      try {
        const status = await conversionAPI.getBatchStatus(id);
        setBatchStatus(status);

        if (status.status === 'completed' || status.status === 'failed') {
          clearInterval(pollIntervalRef.current);
          setConverting(false);
          
          if (status.status === 'completed') {
            const results = await conversionAPI.getBatchResults(id);
            setBatchResults(results);
            fetchHistory(); // Refresh history
          }
        }
      } catch (err) {
        console.error('Failed to poll status:', err);
        clearInterval(pollIntervalRef.current);
        setConverting(false);
        setError('Failed to get conversion status');
      }
    }, 2000);
  };

  const handleReset = () => {
    setSelectedFiles([]);
    setBatchId(null);
    setBatchStatus(null);
    setBatchResults(null);
    setError(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleDownloadResults = () => {
    if (!batchResults || !batchResults.results) return;

    const successfulResults = batchResults.results.filter(r => r.success);
    
    successfulResults.forEach(result => {
      const blob = new Blob([result.convertedCode], { type: 'text/plain' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = result.filename.replace('.java', `.${targetLanguage.id}`);
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    });
  };

  const getStatusIcon = (success) => {
    if (success) {
      return <CheckmarkFilled size={20} style={{ color: 'var(--cds-support-success)' }} />;
    }
    return <ErrorFilled size={20} style={{ color: 'var(--cds-support-error)' }} />;
  };

  const resultsHeaders = [
    { key: 'status', header: 'Status' },
    { key: 'filename', header: 'File Name' },
    { key: 'result', header: 'Result' },
  ];

  const resultsRows = batchResults?.results?.map((result, idx) => ({
    id: `${idx}`,
    status: getStatusIcon(result.success),
    filename: result.filename,
    result: result.success ? 'Converted successfully' : result.error || 'Conversion failed',
  })) || [];

  return (
    <Grid>
      <Column sm={4} md={8} lg={16}>
        <div style={{ padding: '0 2rem', marginBottom: '2rem' }}>
          <h2 style={{ marginBottom: '1rem' }}>
            <DocumentMultiple_01 size={32} style={{ marginRight: '0.5rem', verticalAlign: 'middle' }} />
            Batch Java to Automation Script Converter
          </h2>
          <p style={{ color: 'var(--cds-text-secondary)' }}>
            Convert multiple Maximo Java classes to automation scripts in bulk. Perfect for migrating 20+ custom Java files.
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
              <div style={{ marginBottom: '2rem' }}>
                <h4 style={{ marginBottom: '1rem' }}>1. Select Java Files</h4>
                <input
                  ref={fileInputRef}
                  type="file"
                  accept=".java"
                  multiple
                  onChange={handleFileSelect}
                  style={{ display: 'none' }}
                />
                <Button
                  kind="tertiary"
                  renderIcon={Upload}
                  onClick={() => fileInputRef.current?.click()}
                  disabled={converting}
                >
                  Choose Files
                </Button>
                {selectedFiles.length > 0 && (
                  <div style={{ marginTop: '1rem' }}>
                    <Tag type="blue">{selectedFiles.length} file(s) selected</Tag>
                    <div style={{ marginTop: '0.5rem', maxHeight: '150px', overflowY: 'auto' }}>
                      {selectedFiles.map((file, idx) => (
                        <div key={idx} style={{ fontSize: '0.875rem', padding: '0.25rem 0' }}>
                          • {file.name}
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </Column>

            <Column sm={4} md={4} lg={8}>
              <div style={{ marginBottom: '2rem' }}>
                <h4 style={{ marginBottom: '1rem' }}>2. Select Target Language</h4>
                <Dropdown
                  id="target-language"
                  titleText="Target Language"
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
              </div>
            </Column>
          </Grid>

          <div style={{ marginTop: '2rem', display: 'flex', gap: '1rem' }}>
            <Button
              kind="primary"
              renderIcon={Renew}
              onClick={handleStartBatchConversion}
              disabled={converting || selectedFiles.length === 0 || !targetLanguage}
            >
              {converting ? 'Converting...' : 'Start Batch Conversion'}
            </Button>
            <Button
              kind="secondary"
              onClick={handleReset}
              disabled={converting}
            >
              Reset
            </Button>
            <Button
              kind="tertiary"
              onClick={() => setShowHistoryModal(true)}
            >
              View History
            </Button>
          </div>
        </div>

        {converting && batchStatus && (
          <div style={{ padding: '0 2rem', marginTop: '2rem' }}>
            <h4 style={{ marginBottom: '1rem' }}>Conversion Progress</h4>
            <ProgressBar
              label={`Processing ${batchStatus.processedFiles} of ${batchStatus.totalFiles} files`}
              value={batchStatus.progress || 0}
              max={100}
            />
            <div style={{ marginTop: '1rem', display: 'flex', gap: '1rem' }}>
              <Tag type="green">Success: {batchStatus.successfulConversions}</Tag>
              <Tag type="red">Failed: {batchStatus.failedConversions}</Tag>
            </div>
          </div>
        )}

        {batchResults && batchResults.status === 'completed' && (
          <div style={{ padding: '0 2rem', marginTop: '3rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
              <h3>Conversion Results</h3>
              <Button
                kind="primary"
                size="sm"
                renderIcon={Download}
                onClick={handleDownloadResults}
                disabled={batchResults.summary.successful === 0}
              >
                Download All ({batchResults.summary.successful} files)
              </Button>
            </div>

            <div style={{ marginBottom: '2rem', display: 'flex', gap: '1rem' }}>
              <Tag type="blue">Total: {batchResults.summary.total}</Tag>
              <Tag type="green">Successful: {batchResults.summary.successful}</Tag>
              <Tag type="red">Failed: {batchResults.summary.failed}</Tag>
              <Tag type="gray">Duration: {Math.round(batchResults.summary.duration / 1000)}s</Tag>
            </div>

            <DataTable rows={resultsRows} headers={resultsHeaders}>
              {({ rows, headers, getTableProps, getHeaderProps, getRowProps }) => (
                <TableContainer>
                  <Table {...getTableProps()}>
                    <TableHead>
                      <TableRow>
                        {headers.map((header) => (
                          <TableHeader {...getHeaderProps({ header })}>
                            {header.header}
                          </TableHeader>
                        ))}
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {rows.map((row) => (
                        <TableRow {...getRowProps({ row })}>
                          {row.cells.map((cell) => (
                            <TableCell key={cell.id}>{cell.value}</TableCell>
                          ))}
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              )}
            </DataTable>
          </div>
        )}

        <Modal
          open={showHistoryModal}
          onRequestClose={() => setShowHistoryModal(false)}
          modalHeading="Conversion History"
          passiveModal
          size="lg"
        >
          <div style={{ padding: '1rem' }}>
            {conversionHistory.length === 0 ? (
              <p>No conversion history available</p>
            ) : (
              <div>
                {conversionHistory.map((item, idx) => (
                  <div key={idx} style={{ padding: '1rem', marginBottom: '1rem', backgroundColor: 'var(--cds-layer-01)', borderRadius: '4px' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                      <strong>Batch ID: {item.batchId}</strong>
                      <span style={{ fontSize: '0.875rem', color: 'var(--cds-text-secondary)' }}>
                        {new Date(item.timestamp).toLocaleString()}
                      </span>
                    </div>
                    <div style={{ display: 'flex', gap: '1rem' }}>
                      <Tag type="blue">Total: {item.totalFiles}</Tag>
                      <Tag type="green">Success: {item.successful}</Tag>
                      <Tag type="red">Failed: {item.failed}</Tag>
                      <Tag type="gray">{item.targetLanguage}</Tag>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </Modal>
      </Column>
    </Grid>
  );
};

export default BatchCodeConversion;

// Made with Bob
