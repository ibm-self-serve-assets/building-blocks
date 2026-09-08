import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  }
});

// Request interceptor - Add Maximo configuration headers
api.interceptors.request.use(
  (config) => {
    // Get saved Maximo configuration from localStorage
    const savedConfig = localStorage.getItem('maximoConfig');
    if (savedConfig) {
      try {
        const maximoConfig = JSON.parse(savedConfig);
        // Add Maximo URL and API key as custom headers
        if (maximoConfig.maximoUrl) {
          config.headers['x-maximo-url'] = maximoConfig.maximoUrl;
        }
        if (maximoConfig.apiKey) {
          config.headers['x-maximo-apikey'] = maximoConfig.apiKey;
        }
      } catch (e) {
        console.error('Failed to parse Maximo config:', e);
      }
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => {
    return response.data;
  },
  (error) => {
    const message = error.response?.data?.message || error.message || 'An error occurred';
    return Promise.reject(new Error(message));
  }
);

export const scriptAPI = {
  // Get all scripts
  getAllScripts: () => api.get('/scripts'),
  
  // Get script by name
  getScriptByName: (scriptName) => api.get(`/scripts/${scriptName}`),
  
  // Get statistics
  getStatistics: () => api.get('/scripts/statistics'),
  
  // Analyze all scripts
  analyzeAllScripts: () => api.get('/scripts/analyze'),
  
  // Analyze specific script
  analyzeScript: (scriptName) => api.get(`/scripts/${scriptName}/analyze`),
  
  // Analyze specific script with detailed impact analysis
  analyzeScriptWithImpact: (scriptName) => api.get(`/scripts/${scriptName}/impact`),
  
  // Optimize script - Generate AI-powered optimizations
  optimizeScript: (scriptName) => api.get(`/scripts/${scriptName}/optimize`),
  
  // Update script in Maximo with optimized code
  updateScript: (scriptName, optimizedCode) => api.post(`/scripts/${scriptName}/update`, { optimizedCode }),
};

export const conversionAPI = {
  // Get supported target languages
  getSupportedLanguages: () => api.get('/conversion/languages'),
  
  // Convert Java code to automation script
  convertCode: (javaCode, targetLanguage, scriptContext = {}) =>
    api.post('/conversion/convert', { javaCode, targetLanguage, scriptContext }),
  
  // Test converted script
  testScript: (scriptCode, language, testData = {}) =>
    api.post('/conversion/test', { scriptCode, language, testData }),
  
  // Create converted script in Maximo
  createScript: (scriptData) =>
    api.post('/conversion/create', { scriptData }),
  
  // Batch conversion endpoints
  // Start batch conversion of multiple files
  startBatchConversion: (files, targetLanguage) =>
    api.post('/conversion/batch', { files, targetLanguage }),
  
  // Get batch conversion status
  getBatchStatus: (batchId) =>
    api.get(`/conversion/batch/${batchId}/status`),
  
  // Get batch conversion results
  getBatchResults: (batchId) =>
    api.get(`/conversion/batch/${batchId}/results`),
  
  // Get conversion history
  getConversionHistory: () =>
    api.get('/conversion/history'),
};

export const connectionAPI = {
  // Test Maximo connection
  testConnection: (config) => api.post('/connection/test', config),
};

export const healthAPI = {
  // Check server health
  checkHealth: () => axios.get('http://localhost:5000/health'),
};

export default api;

// Made with Bob
