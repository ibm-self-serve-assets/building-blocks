const express = require('express');
const router = express.Router();
const scriptController = require('../controllers/scriptController');

// Get all automation scripts
router.get('/scripts', scriptController.getAllScripts.bind(scriptController));

// Get script statistics
router.get('/scripts/statistics', scriptController.getStatistics.bind(scriptController));

// Analyze all scripts
router.get('/scripts/analyze', scriptController.analyzeAllScripts.bind(scriptController));

// Get specific script by name
router.get('/scripts/:scriptName', scriptController.getScriptByName.bind(scriptController));

// Analyze specific script
router.get('/scripts/:scriptName/analyze', scriptController.analyzeScript.bind(scriptController));

// Analyze specific script with detailed impact analysis
router.get('/scripts/:scriptName/impact', scriptController.analyzeScriptWithImpact.bind(scriptController));

// Optimize specific script - Generate AI-powered optimizations
router.get('/scripts/:scriptName/optimize', scriptController.optimizeScript.bind(scriptController));

// Update script in Maximo with optimized code
router.post('/scripts/:scriptName/update', scriptController.updateScript.bind(scriptController));

// Code conversion endpoints
// Get supported target languages for conversion
router.get('/conversion/languages', scriptController.getSupportedLanguages.bind(scriptController));

// Convert Java code to automation script
router.post('/conversion/convert', scriptController.convertJavaToScript.bind(scriptController));

// Test converted script
router.post('/conversion/test', scriptController.testConvertedScript.bind(scriptController));

// Create converted script in Maximo

// Batch conversion endpoints
// Start batch conversion of multiple Java files
router.post('/conversion/batch', scriptController.startBatchConversion.bind(scriptController));

// Get batch conversion status
router.get('/conversion/batch/:batchId/status', scriptController.getBatchStatus.bind(scriptController));

// Get batch conversion results
router.get('/conversion/batch/:batchId/results', scriptController.getBatchResults.bind(scriptController));

// Get conversion history
router.get('/conversion/history', scriptController.getConversionHistory.bind(scriptController));
router.post('/conversion/create', scriptController.createConvertedScript.bind(scriptController));

module.exports = router;

// Made with Bob
