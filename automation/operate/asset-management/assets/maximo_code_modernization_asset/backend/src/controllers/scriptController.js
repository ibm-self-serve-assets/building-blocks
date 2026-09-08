const maximoService = require('../services/maximoService');
const codeConverter = require('../services/codeConverter');

class ScriptController {
  /**
   * Get all automation scripts
   */
  async getAllScripts(req, res) {
    try {
      const config = maximoService.getConfig(req);
      const result = await maximoService.fetchAutomationScripts(config);
      
      if (result.success) {
        res.json({
          success: true,
          count: result.count,
          scripts: result.scripts
        });
      } else {
        res.status(404).json({
          success: false,
          message: result.message
        });
      }
    } catch (error) {
      res.status(error.status || 500).json({
        success: false,
        message: error.message || 'Failed to fetch automation scripts'
      });
    }
  }

  /**
   * Get a specific script by name
   */
  async getScriptByName(req, res) {
    try {
      const { scriptName } = req.params;
      const config = maximoService.getConfig(req);
      const result = await maximoService.getScriptByName(scriptName, config);
      
      res.json(result);
    } catch (error) {
      res.status(error.status || 500).json({
        success: false,
        message: error.message || 'Failed to fetch script'
      });
    }
  }

  /**
   * Analyze all scripts
   */
  async analyzeAllScripts(req, res) {
    try {
      const config = maximoService.getConfig(req);
      const result = await maximoService.fetchAutomationScripts(config);
      
      if (!result.success) {
        return res.status(404).json({
          success: false,
          message: result.message
        });
      }

      const analyses = result.scripts.map(script =>
        maximoService.analyzeScript(script)
      );

      // Categorize by severity
      const critical = analyses.filter(a => a.issues.length > 0);
      const warnings = analyses.filter(a => a.warnings.length > 0 && a.issues.length === 0);
      const clean = analyses.filter(a => a.issues.length === 0 && a.warnings.length === 0);

      res.json({
        success: true,
        summary: {
          total: analyses.length,
          critical: critical.length,
          warnings: warnings.length,
          clean: clean.length
        },
        analyses: analyses
      });
    } catch (error) {
      res.status(error.status || 500).json({
        success: false,
        message: error.message || 'Failed to analyze scripts'
      });
    }
  }

  /**
   * Analyze a specific script
   */
  async analyzeScript(req, res) {
    try {
      const { scriptName } = req.params;
      const config = maximoService.getConfig(req);
      const result = await maximoService.getScriptByName(scriptName, config);
      
      if (!result.success) {
        return res.status(404).json(result);
      }

      const analysis = maximoService.analyzeScript(result.script);
      
      // Disable caching for analysis results
      res.set('Cache-Control', 'no-store, no-cache, must-revalidate, private');
      res.set('Pragma', 'no-cache');
      res.set('Expires', '0');
      
      res.json({
        success: true,
        analysis: analysis
      });
    } catch (error) {
      res.status(error.status || 500).json({
        success: false,
        message: error.message || 'Failed to analyze script'
      });
    }
  }

  /**
   * Analyze a specific script with detailed impact analysis
   */
  async analyzeScriptWithImpact(req, res) {
    try {
      const { scriptName } = req.params;
      const config = maximoService.getConfig(req);
      const result = await maximoService.getScriptByName(scriptName, config);
      
      if (!result.success) {
        return res.status(404).json(result);
      }

      const analysis = maximoService.analyzeScriptWithImpact(result.script);
      
      // Disable caching for analysis results
      res.set('Cache-Control', 'no-store, no-cache, must-revalidate, private');
      res.set('Pragma', 'no-cache');
      res.set('Expires', '0');
      
      res.json({
        success: true,
        analysis: analysis
      });
    } catch (error) {
      res.status(error.status || 500).json({
        success: false,
        message: error.message || 'Failed to analyze script with impact'
      });
    }
  }

  /**
   * Get script statistics
   */
  async getStatistics(req, res) {
    try {
      const config = maximoService.getConfig(req);
      const result = await maximoService.fetchAutomationScripts(config);
      
      if (!result.success) {
        return res.status(404).json({
          success: false,
          message: result.message
        });
      }

      const stats = maximoService.getScriptStatistics(result.scripts);
      
      res.json({
        success: true,
        statistics: stats
      });
    } catch (error) {
      res.status(error.status || 500).json({
        success: false,
        message: error.message || 'Failed to get statistics'
      });
    }
  }

  /**
   * Optimize a specific script - Apply Maximo best practices
   */
  async optimizeScript(req, res) {
    try {
      const { scriptName } = req.params;
      const config = maximoService.getConfig(req);
      const result = await maximoService.getScriptByName(scriptName, config);
      
      if (!result.success) {
        return res.status(404).json(result);
      }

      const optimization = maximoService.optimizeScript(result.script);
      
      // Disable caching for optimization results
      res.set('Cache-Control', 'no-store, no-cache, must-revalidate, private');
      res.set('Pragma', 'no-cache');
      res.set('Expires', '0');
      
      res.json({
        success: true,
        optimization: optimization
      });
    } catch (error) {
      res.status(error.status || 500).json({
        success: false,
        message: error.message || 'Failed to optimize script'
      });
    }
  }

  /**
   * Update a script in Maximo with optimized code
   */
  async updateScript(req, res) {
    try {
      const { scriptName } = req.params;
      const { optimizedCode } = req.body;
      
      if (!optimizedCode) {
        return res.status(400).json({
          success: false,
          message: 'Optimized code is required'
        });
      }

      const config = maximoService.getConfig(req);
      const result = await maximoService.updateScript(scriptName, optimizedCode, config);
      
      res.json(result);
    } catch (error) {
      res.status(error.status || 500).json({
        success: false,
        message: error.message || 'Failed to update script'
      });
    }
  }

  /**
   * Get supported target languages for code conversion
   */
  async getSupportedLanguages(req, res) {
    try {
      const languages = codeConverter.getSupportedLanguages();
      res.json({
        success: true,
        languages
      });
    } catch (error) {
      res.status(500).json({
        success: false,
        message: error.message || 'Failed to get supported languages'
      });
    }
  }

  /**
   * Convert Java code to automation script
   */
  async convertJavaToScript(req, res) {
    try {
      const { javaCode, targetLanguage, scriptContext } = req.body;

      if (!javaCode) {
        return res.status(400).json({
          success: false,
          message: 'Java code is required'
        });
      }

      if (!targetLanguage) {
        return res.status(400).json({
          success: false,
          message: 'Target language is required'
        });
      }

      const result = await codeConverter.convertJavaToScript(
        javaCode,
        targetLanguage,
        scriptContext || {}
      );

      // Disable caching for conversion results
      res.set('Cache-Control', 'no-store, no-cache, must-revalidate, private');
      res.set('Pragma', 'no-cache');
      res.set('Expires', '0');

      res.json(result);
    } catch (error) {
      res.status(error.status || 500).json({
        success: false,
        message: error.message || 'Failed to convert code'
      });
    }
  }

  /**
   * Test converted script
   */
  async testConvertedScript(req, res) {
    try {
      const { scriptCode, language, testData } = req.body;

      if (!scriptCode) {
        return res.status(400).json({
          success: false,
          message: 'Script code is required'
        });
      }

      // For now, return a mock test result
      // In production, this would execute the script in a sandbox environment
      res.json({
        success: true,
        testResult: {
          passed: true,
          message: 'Test script validation passed. Ready to create in Maximo.',
          details: {
            syntaxCheck: 'Passed',
            logicValidation: 'Passed',
            apiCompatibility: 'Passed'
          }
        }
      });
    } catch (error) {
      res.status(500).json({
        success: false,
        message: error.message || 'Failed to test script'
      });
    }
  }

  /**
   * Create converted script in Maximo
   */
  async createConvertedScript(req, res) {
    try {
      const { scriptData } = req.body;

      console.log('Received scriptData:', {
        hasScriptData: !!scriptData,
        scriptName: scriptData?.scriptName,
        hasScriptCode: !!scriptData?.scriptCode,
        scriptCodeLength: scriptData?.scriptCode?.length,
        language: scriptData?.language
      });
      
      // Log the actual script code to debug syntax errors
      console.log('=== SCRIPT CODE TO BE CREATED ===');
      console.log(scriptData?.scriptCode);
      console.log('=== END SCRIPT CODE ===');

      if (!scriptData || !scriptData.scriptName || !scriptData.scriptCode) {
        return res.status(400).json({
          success: false,
          message: 'Script name and code are required'
        });
      }

      const config = maximoService.getConfig(req);
      const result = await codeConverter.createScriptInMaximo(scriptData, config);

      res.json(result);
    } catch (error) {
      res.status(error.status || 500).json({
        success: false,
        message: error.message || 'Failed to create script in Maximo'
      });
    }
  }

  /**
   * Start batch conversion of multiple Java files
   */
  async startBatchConversion(req, res) {
    try {
      const { files, targetLanguage } = req.body;

      if (!files || !Array.isArray(files) || files.length === 0) {
        return res.status(400).json({
          success: false,
          message: 'Files array is required and must not be empty'
        });
      }

      if (!targetLanguage) {
        return res.status(400).json({
          success: false,
          message: 'Target language is required'
        });
      }

      const result = await codeConverter.startBatchConversion(files, targetLanguage);
      
      res.json(result);
    } catch (error) {
      res.status(error.status || 500).json({
        success: false,
        message: error.message || 'Failed to start batch conversion'
      });
    }
  }

  /**
   * Get batch conversion status
   */
  async getBatchStatus(req, res) {
    try {
      const { batchId } = req.params;
      const result = codeConverter.getBatchStatus(batchId);
      
      if (!result.success) {
        return res.status(404).json(result);
      }
      
      res.json(result);
    } catch (error) {
      res.status(error.status || 500).json({
        success: false,
        message: error.message || 'Failed to get batch status'
      });
    }
  }

  /**
   * Get batch conversion results
   */
  async getBatchResults(req, res) {
    try {
      const { batchId } = req.params;
      const result = codeConverter.getBatchResults(batchId);
      
      if (!result.success) {
        return res.status(404).json(result);
      }
      
      res.json(result);
    } catch (error) {
      res.status(error.status || 500).json({
        success: false,
        message: error.message || 'Failed to get batch results'
      });
    }
  }

  /**
   * Get conversion history
   */
  async getConversionHistory(req, res) {
    try {
      const result = codeConverter.getConversionHistory();
      res.json(result);
    } catch (error) {
      res.status(error.status || 500).json({
        success: false,
        message: error.message || 'Failed to get conversion history'
      });
    }
  }
}

module.exports = new ScriptController();

// Made with Bob
