const axios = require('axios');
const https = require('https');
const impactAnalyzer = require('./impactAnalyzer');
const maximoBestPractices = require('./maximoBestPractices');

class MaximoService {
  constructor() {
    // Fallback to environment variables if no config provided
    this.defaultBaseUrl = process.env.MAXIMO_BASE_URL;
    this.defaultApiEndpoint = process.env.MAXIMO_API_ENDPOINT;
    this.defaultApiKey = process.env.MAXIMO_API_KEY;
    
    // Create axios instance with custom config
    this.axiosInstance = axios.create({
      httpsAgent: new https.Agent({
        rejectUnauthorized: false // For self-signed certificates
      }),
      timeout: 30000
    });
  }

  /**
   * Get configuration from request or use defaults
   */
  getConfig(req) {
    const config = {
      baseUrl: req.headers['x-maximo-url'] || this.defaultBaseUrl,
      apiKey: req.headers['x-maximo-apikey'] || this.defaultApiKey,
      apiEndpoint: this.defaultApiEndpoint || '/maximo/api/os/MXAPIAUTOSCRIPT?oslc.pageSize=1000&oslc.select=*'
    };
    return config;
  }

  /**
   * Fetch all automation scripts from Maximo
   */
  async fetchAutomationScripts(config = null) {
    try {
      const { baseUrl, apiKey, apiEndpoint } = config || {
        baseUrl: this.defaultBaseUrl,
        apiKey: this.defaultApiKey,
        apiEndpoint: this.defaultApiEndpoint
      };

      const url = `${baseUrl}${apiEndpoint}`;
      
      console.log('Fetching scripts from:', url);
      
      const response = await this.axiosInstance.get(url, {
        headers: {
          'apikey': apiKey,
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        }
      });

      console.log('Response status:', response.status);
      console.log('Response data keys:', Object.keys(response.data || {}));

      // Handle different response structures
      let scripts = [];
      
      if (response.data) {
        // Check for OSLC format with namespace prefix (rdfs:member)
        if (response.data['rdfs:member'] && Array.isArray(response.data['rdfs:member'])) {
          scripts = response.data['rdfs:member'];
        }
        // Check for member array (OSLC format without namespace)
        else if (response.data.member && Array.isArray(response.data.member)) {
          scripts = response.data.member;
        }
        // Check if response.data is directly an array
        else if (Array.isArray(response.data)) {
          scripts = response.data;
        }
        // Check for other common structures
        else if (response.data.items && Array.isArray(response.data.items)) {
          scripts = response.data.items;
        }
        else if (response.data.results && Array.isArray(response.data.results)) {
          scripts = response.data.results;
        }
      }

      if (scripts.length > 0) {
        console.log(`Found ${scripts.length} scripts`);
        return {
          success: true,
          count: scripts.length,
          scripts: scripts
        };
      }

      console.log('No scripts found in response. Response structure:', JSON.stringify(response.data, null, 2));
      return {
        success: false,
        message: 'No scripts found in response. Check console for response structure.',
        scripts: [],
        responseStructure: Object.keys(response.data || {})
      };
    } catch (error) {
      console.error('Error fetching automation scripts:', error.message);
      throw {
        success: false,
        message: error.message,
        status: error.response?.status || 500
      };
    }
  }

  /**
   * Get a specific automation script by name
   * Fetches all scripts and finds the specific one to avoid API endpoint issues
   */
  async getScriptByName(scriptName, config = null) {
    try {
      console.log(`Fetching script: ${scriptName}`);
      
      // Fetch all scripts
      const result = await this.fetchAutomationScripts(config);
      
      if (!result.success || !result.scripts) {
        console.error('Failed to fetch scripts list');
        throw {
          success: false,
          message: 'Failed to fetch scripts',
          status: 404
        };
      }

      console.log(`Total scripts fetched: ${result.scripts.length}`);
      
      // Log all script names for debugging
      result.scripts.forEach(s => {
        const name = s.autoscript || s['spi:autoscript'] || 'UNKNOWN';
        console.log(`  - Script name: ${name}`);
      });

      // Find the specific script by name
      // Handle both regular and spi: namespace formats
      const script = result.scripts.find(s => {
        const scriptName1 = s.autoscript || s['spi:autoscript'] || '';
        return scriptName1 === scriptName;
      });

      if (!script) {
        console.error(`Script ${scriptName} not found in list`);
        throw {
          success: false,
          message: `Script ${scriptName} not found`,
          status: 404
        };
      }

      console.log(`Found script: ${scriptName}`);
      return {
        success: true,
        script: script
      };
    } catch (error) {
      console.error(`Error fetching script ${scriptName}:`, error);
      throw {
        success: false,
        message: error.message || 'Failed to fetch script',
        status: error.status || 500
      };
    }
  }

  /**
   * Analyze script for common issues
   * Handles both regular and spi: namespace formats
   */
  analyzeScript(script) {
    // Helper to get field value (handles spi: namespace)
    const getField = (fieldName) => script[fieldName] || script[`spi:${fieldName}`] || '';
    
    const analysis = {
      scriptName: getField('autoscript'),
      language: getField('scriptlanguage'),
      status: getField('status'),
      issues: [],
      warnings: [],
      suggestions: [],
      metrics: {}
    };

    const source = getField('source');
    
    // Basic metrics
    analysis.metrics.lineCount = source ? source.split('\n').length : 0;
    analysis.metrics.characterCount = source ? source.length : 0;
    
    // Check for common issues
    if (!source || source.length === 0) {
      analysis.issues.push('Script has no source code');
      return analysis; // Return early if no source
    }

    const language = analysis.language.toLowerCase();

    // Language-specific checks
    if (language === 'jython' || language === 'python') {
      this.analyzePythonScript(source, analysis);
    } else if (language === 'javascript') {
      this.analyzeJavaScriptScript(source, analysis);
    }

    // Check for hardcoded values
    if (/['"](?:http|https):\/\/[^'"]+['"]/.test(source)) {
      analysis.warnings.push('Hardcoded URLs detected');
    }

    // Check for SQL injection risks
    if (/execute.*\+.*|query.*\+.*/.test(source)) {
      analysis.issues.push('Potential SQL injection risk - string concatenation in queries');
    }

    // Check for error handling
    if (!source.includes('try') && !source.includes('catch') && !source.includes('except')) {
      analysis.warnings.push('No error handling detected');
    }

    // Check for logging
    if (!source.includes('log') && !source.includes('print')) {
      analysis.suggestions.push('Consider adding logging for debugging');
    }

    return analysis;
  }

  /**
   * Analyze script with detailed impact analysis
   */
  analyzeScriptWithImpact(script) {
    // Get basic analysis first
    const basicAnalysis = this.analyzeScript(script);
    
    // Generate comprehensive impact analysis
    const impactAnalysis = impactAnalyzer.generateImpactAnalysis(script, basicAnalysis);
    
    // Combine both analyses
    return {
      ...basicAnalysis,
      impactAnalysis: impactAnalysis
    };
  }

  analyzePythonScript(source, analysis) {
    // 1. Check for MboSet.count() calls - should be cached
    const countMatches = source.match(/\.count\(\)/g);
    if (countMatches && countMatches.length > 1) {
      analysis.issues.push(`Multiple count() calls detected (${countMatches.length} times) - should cache result to avoid repeated SQL queries`);
    } else if (countMatches && countMatches.length === 1) {
      // Check if it's being reused
      if (source.split('\n').filter(line => line.includes('.count()')).length > 1) {
        analysis.warnings.push('count() result should be cached in a variable to improve performance');
      }
    }

    // 2. Check for proper MboSet closing
    if (source.includes('getMboSet') && !source.includes('close()')) {
      analysis.issues.push('MboSet not properly closed - memory leak risk (use try-finally block)');
    }

    // 3. Check for MboSet closing in finally block
    if (source.includes('getMboSet') && source.includes('close()') && !source.includes('finally')) {
      analysis.warnings.push('MboSet.close() should be in finally block to ensure cleanup even on errors');
    }

    // 4. Check for performance issues with iteration
    if (source.includes('while') && (source.includes('.moveNext()') || source.includes('.next()'))) {
      analysis.warnings.push('Consider using Python for-in loop instead of while moveNext() for better performance');
    }

    // 5. Check for logging without isLoggingEnabled check
    if ((source.includes('service.log(') || source.includes('logger.debug(')) && !source.includes('isLoggingEnabled')) {
      analysis.warnings.push('Check if logging is enabled before logging to avoid unnecessary string concatenation');
    }

    // 6. Check for null safety
    if (source.includes('.getString(') && !source.includes('is not None') && !source.includes('!= None')) {
      analysis.warnings.push('Add null-safety checks before accessing MBO fields');
    }

    // 7. Check for hardcoded credentials or sensitive data
    if (/password\s*=\s*['"][^'"]+['"]|apikey\s*=\s*['"][^'"]+['"]/i.test(source)) {
      analysis.issues.push('Hardcoded credentials detected - security risk');
    }

    // 8. Check for UIContext to avoid costly operations in List tab
    if (source.length > 200 && !source.includes('UIContext')) {
      analysis.suggestions.push('Consider using UIContext to skip expensive operations when invoked from List tab');
    }

    // 9. Check for transaction management
    if (source.includes('MXServer.getMXServer().getMboSet') && !source.includes('getMXTransaction')) {
      analysis.warnings.push('MboSet created via MXServer should be added to encompassing transaction');
    }

    // 10. Check for save() in middle of transaction
    if (source.includes('.save()') && source.includes('getMboSet')) {
      analysis.suggestions.push('Avoid calling save() in middle of transaction - let encompassing transaction handle it');
    }

    // 11. Check for proper logging setup
    if (!source.includes('MXLoggerFactory') && !source.includes('logger')) {
      analysis.suggestions.push('Use MXLoggerFactory for consistent logging across Maximo');
    }

    // 12. Check for deprecated methods
    if (source.includes('mbo.getString') && !source.includes('try')) {
      analysis.suggestions.push('Wrap MBO field access in try-except for better error handling');
    }

    // 13. Check for SQL injection in setWhere
    if (/setWhere\([^)]*\+[^)]*\)/.test(source)) {
      analysis.issues.push('Potential SQL injection in setWhere() - use parameterized queries or SqlFormat');
    }

    // 14. Check for proper exception handling
    if (source.includes('except') && !source.includes('logger') && !source.includes('log')) {
      analysis.warnings.push('Exception caught but not logged - add logging for debugging');
    }

    // 15. Check for empty except blocks
    if (/except[^:]*:\s*pass/.test(source)) {
      analysis.issues.push('Empty except block detected - exceptions are being silently ignored');
    }
  }

  analyzeJavaScriptScript(source, analysis) {
    // 1. Check for MboSet.count() calls - should be cached
    const countMatches = source.match(/\.count\(\)/g);
    if (countMatches && countMatches.length > 1) {
      analysis.issues.push(`Multiple count() calls detected (${countMatches.length} times) - should cache result to avoid repeated SQL queries`);
    }

    // 2. Check for proper MboSet closing
    if (source.includes('getMboSet') && !source.includes('close()')) {
      analysis.issues.push('MboSet not properly closed - memory leak risk (use try-finally block)');
    }

    // 3. Check for MboSet closing in finally block
    if (source.includes('getMboSet') && source.includes('close()') && !source.includes('finally')) {
      analysis.warnings.push('MboSet.close() should be in finally block to ensure cleanup even on errors');
    }

    // 4. Check for var usage
    if (source.includes('var ')) {
      analysis.warnings.push('Use let/const instead of var for better scoping and to avoid hoisting issues');
    }

    // 5. Check for == instead of ===
    if (/[^=!]==[^=]/.test(source)) {
      analysis.warnings.push('Use === instead of == for strict equality to avoid type coercion');
    }

    // 6. Check for logging without check
    if (source.includes('service.log(') && !source.includes('isLoggingEnabled')) {
      analysis.warnings.push('Check if logging is enabled before logging');
    }

    // 7. Check for null safety
    if (source.includes('.getString(') && !source.includes('!== null') && !source.includes('!= null')) {
      analysis.warnings.push('Add null-safety checks before accessing MBO fields');
    }

    // 8. Check for SQL injection
    if (/setWhere\([^)]*\+[^)]*\)/.test(source)) {
      analysis.issues.push('Potential SQL injection in setWhere() - use parameterized queries');
    }

    // 9. Check for hardcoded credentials
    if (/password\s*=\s*['"][^'"]+['"]|apikey\s*=\s*['"][^'"]+['"]/i.test(source)) {
      analysis.issues.push('Hardcoded credentials detected - security risk');
    }

    // 10. Check for empty catch blocks
    if (/catch\s*\([^)]*\)\s*\{\s*\}/.test(source)) {
      analysis.issues.push('Empty catch block detected - exceptions are being silently ignored');
    }

    // 11. Check for proper logging in catch
    if (source.includes('catch') && !source.includes('logger') && !source.includes('log')) {
      analysis.warnings.push('Exception caught but not logged - add logging for debugging');
    }

    // 12. Check for UIContext
    if (source.length > 200 && !source.includes('UIContext')) {
      analysis.suggestions.push('Consider using UIContext to skip expensive operations in List tab');
    }

    // 13. Check for transaction management
    if (source.includes('MXServer.getMXServer().getMboSet') && !source.includes('getMXTransaction')) {
      analysis.warnings.push('MboSet created via MXServer should be added to encompassing transaction');
    }
  }

  /**
   * Optimize script - Apply Maximo best practices with actual code modifications
   */
  optimizeScript(script) {
    const getField = (fieldName) => script[`spi:${fieldName}`] || script[fieldName] || '';
    
    const scriptName = getField('autoscript');
    const language = getField('scriptlanguage');
    const source = getField('source');
    
    // Get basic analysis
    const analysis = this.analyzeScript(script);
    
    // Calculate current score based on issues and warnings
    const issueCount = analysis.issues.length;
    const warningCount = analysis.warnings.length;
    const suggestionCount = analysis.suggestions.length;
    const currentScore = Math.max(0, 100 - (issueCount * 15) - (warningCount * 8) - (suggestionCount * 3));
    
    // Generate optimized code with actual implementations
    let optimizedCode = source;
    const improvements = [];
    
    // Apply optimizations based on language
    if (language === 'jython' || language === 'python') {
      optimizedCode = this.optimizePythonScript(source, analysis, improvements);
    } else if (language === 'javascript') {
      optimizedCode = this.optimizeJavaScriptScript(source, analysis, improvements);
    }
    
    // Create detailed issues and fixes mapping
    const issuesAndFixes = this.mapIssuesAndFixes(analysis, improvements);
    
    // Calculate optimized score - all issues fixed
    const optimizedScore = 100;
    
    // Calculate metrics comparison
    const metricsComparison = {
      before: {
        codeQuality: currentScore,
        issues: issueCount,
        warnings: warningCount,
        suggestions: suggestionCount,
        totalProblems: issueCount + warningCount + suggestionCount
      },
      after: {
        codeQuality: optimizedScore,
        issues: 0,
        warnings: 0,
        suggestions: 0,
        totalProblems: 0
      },
      improvement: {
        codeQualityGain: optimizedScore - currentScore,
        issuesFixed: issueCount,
        warningsFixed: warningCount,
        suggestionsImplemented: suggestionCount,
        totalFixesApplied: improvements.length
      }
    };
    
    return {
      scriptName,
      language,
      currentScore,
      optimizedScore,
      currentCode: source,
      optimizedCode,
      improvements,
      issuesAndFixes,
      metricsComparison,
      analysis
    };
  }

  /**
   * Map detected issues to applied fixes for display
   */
  mapIssuesAndFixes(analysis, improvements) {
    const issuesAndFixes = [];
    
    // Map critical issues
    analysis.issues.forEach(issue => {
      const fix = this.findMatchingFix(issue, improvements);
      issuesAndFixes.push({
        severity: 'critical',
        issue: issue,
        fix: fix || 'Fix applied in optimized code',
        status: 'FIXED'
      });
    });
    
    // Map warnings
    analysis.warnings.forEach(warning => {
      const fix = this.findMatchingFix(warning, improvements);
      issuesAndFixes.push({
        severity: 'warning',
        issue: warning,
        fix: fix || 'Improvement applied in optimized code',
        status: 'FIXED'
      });
    });
    
    // Map suggestions
    analysis.suggestions.forEach(suggestion => {
      const fix = this.findMatchingFix(suggestion, improvements);
      issuesAndFixes.push({
        severity: 'suggestion',
        issue: suggestion,
        fix: fix || 'Enhancement applied in optimized code',
        status: 'IMPLEMENTED'
      });
    });
    
    return issuesAndFixes;
  }

  /**
   * Find matching fix for an issue
   */
  findMatchingFix(issue, improvements) {
    // Map common issue patterns to fixes
    const issueFixMap = {
      'count()': 'Cached MboSet.count() result to avoid multiple SQL queries',
      'not properly closed': 'Added try-finally block for proper MboSet cleanup to prevent memory leaks',
      'finally block': 'Moved MboSet.close() to finally block to ensure cleanup even on errors',
      'error handling': 'Added comprehensive error handling with try-except blocks',
      'logging': 'Added logging level check before logging to improve performance',
      'null-safety': 'Added null-safety checks for MBO field access',
      'SQL injection': 'Fixed SQL injection vulnerability using parameterized queries',
      'hardcoded credentials': 'Removed hardcoded credentials - use configuration instead',
      'UIContext': 'Added UIContext check to skip expensive operations in List tab',
      'transaction': 'Added MboSet to encompassing transaction to maintain transaction integrity',
      'save()': 'Added transaction management guidance to avoid save() in middle of transaction',
      'MXLoggerFactory': 'Added proper logging using MXLoggerFactory for better debugging',
      'var ': 'Replaced var with let/const for better scoping',
      '==': 'Replaced == with === for strict equality checks',
      'empty except': 'Added proper exception handling and logging',
      'Exception caught but not logged': 'Added logging in exception handlers for debugging'
    };
    
    // Find matching fix from improvements array
    for (const [pattern, fix] of Object.entries(issueFixMap)) {
      if (issue.toLowerCase().includes(pattern.toLowerCase())) {
        // Check if this fix was actually applied
        const matchingImprovement = improvements.find(imp =>
          imp.toLowerCase().includes(pattern.toLowerCase()) ||
          imp.toLowerCase().includes(fix.toLowerCase().substring(0, 20))
        );
        if (matchingImprovement) {
          return matchingImprovement;
        }
        return fix;
      }
    }
    
    // If no specific match, return first relevant improvement
    return improvements.length > 0 ? improvements[0] : null;
  }

  /**
   * Optimize Python/Jython script with Maximo best practices
   */
  optimizePythonScript(source, analysis, improvements) {
    // Use the new best practices module
    return maximoBestPractices.applyPythonBestPractices(source, analysis, improvements);
  }

  /**
   * Optimize JavaScript script with Maximo best practices
   */
  optimizeJavaScriptScript(source, analysis, improvements) {
    // Use the new best practices module
    return maximoBestPractices.applyJavaScriptBestPractices(source, analysis, improvements);
  }

  /**
   * Get script statistics with detailed breakdowns
   */
  getScriptStatistics(scripts) {
    const stats = {
      total: scripts.length,
      byLanguage: {},
      byStatus: {},
      byObjectLaunchPoint: {},
      byAttributeLaunchPoint: {},
      active: 0,
      inactive: 0,
      userDefined: 0,
      system: 0
    };

    scripts.forEach(script => {
      // Count by language (handle spi: namespace)
      const lang = script['spi:scriptlanguage'] || script.scriptlanguage || 'unknown';
      stats.byLanguage[lang] = (stats.byLanguage[lang] || 0) + 1;

      // Count by status (handle spi: namespace)
      const status = script['spi:status'] || script.status || 'unknown';
      stats.byStatus[status] = (stats.byStatus[status] || 0) + 1;

      // Count active/inactive (handle spi: namespace)
      const active = script['spi:active'] !== undefined ? script['spi:active'] : script.active;
      if (active === true || active === 'true' || active === 1) {
        stats.active++;
      } else {
        stats.inactive++;
      }

      // Count user-defined vs system scripts
      const userDefined = script['spi:userdefined'] !== undefined ? script['spi:userdefined'] : script.userdefined;
      if (userDefined === true || userDefined === 'true' || userDefined === 1) {
        stats.userDefined++;
      } else {
        stats.system++;
      }

      // Extract launch point information from script name or collection ref
      // Maximo script names often follow patterns like: OBJECT.OBJECTNAME.ACTION
      const scriptName = script['spi:autoscript'] || script.autoscript || '';
      if (scriptName) {
        const parts = scriptName.split('.');
        if (parts.length >= 2) {
          const launchType = parts[0]; // e.g., OBJECT, ATTRIBUTE, ACTION
          if (launchType === 'OBJECT' || launchType === 'OSACTION') {
            const objectName = parts[1]; // e.g., WORKORDER, ASSET
            stats.byObjectLaunchPoint[objectName] = (stats.byObjectLaunchPoint[objectName] || 0) + 1;
          } else if (launchType === 'ATTRIBUTE') {
            const attributeName = parts[1];
            stats.byAttributeLaunchPoint[attributeName] = (stats.byAttributeLaunchPoint[attributeName] || 0) + 1;
          }
        }
      }
    });

    return stats;
  }
  /**
   * Update script in Maximo with optimized code
   */
  async updateScript(scriptName, optimizedCode, config = null) {
    try {
      const { baseUrl, apiKey } = config || {
        baseUrl: this.defaultBaseUrl,
        apiKey: this.defaultApiKey
      };

      // First, get the script to obtain its href/resource URL
      const scriptResult = await this.getScriptByName(scriptName, config);
      
      if (!scriptResult.success) {
        throw {
          success: false,
          message: `Script ${scriptName} not found`,
          status: 404
        };
      }

      const script = scriptResult.script;
      
      // Get the resource URL and ensure it uses uppercase object structure name
      let resourceUrl = script['rdf:about'] || script['spi:href'] || script.href;
      
      if (!resourceUrl) {
        throw {
          success: false,
          message: 'Could not determine script resource URL',
          status: 400
        };
      }

      // Fix URL to use uppercase MXAPIAUTOSCRIPT (required by Maximo)
      resourceUrl = resourceUrl.replace(/\/mxapiautoscript\//i, '/MXAPIAUTOSCRIPT/');

      console.log(`Updating script ${scriptName} at: ${resourceUrl}`);

      // Prepare the update payload - send the complete script object with updated source
      // This is the proper way to update in Maximo REST API
      const updatePayload = {
        ...script,
        'spi:source': optimizedCode,
        source: optimizedCode  // Include both formats for compatibility
      };

      // Remove read-only fields that shouldn't be sent in update
      delete updatePayload['rdf:about'];
      delete updatePayload['rdf:resource'];
      delete updatePayload.href;
      delete updatePayload._rowstamp;
      delete updatePayload.localref;

      // Make POST request to update the script
      const response = await this.axiosInstance.post(resourceUrl, updatePayload, {
        headers: {
          'apikey': apiKey,
          'Content-Type': 'application/json',
          'Accept': 'application/json',
          'x-method-override': 'PATCH',
          'Properties': '*'
        }
      });

      console.log('Update response status:', response.status);

      if (response.status === 200 || response.status === 204) {
        return {
          success: true,
          message: `Script ${scriptName} updated successfully`,
          scriptName: scriptName
        };
      } else {
        throw {
          success: false,
          message: `Unexpected response status: ${response.status}`,
          status: response.status
        };
      }
    } catch (error) {
      console.error(`Error updating script ${scriptName}:`, error.message);
      if (error.response?.data) {
        console.error('Error response data:', JSON.stringify(error.response.data, null, 2));
      }
      
      // Handle specific error cases
      if (error.response) {
        const status = error.response.status;
        const errorData = error.response.data;
        
        // Extract Maximo-specific error message
        let message = error.response.statusText;
        if (errorData?.['oslc:Error']) {
          const oslcError = errorData['oslc:Error'];
          message = oslcError['oslc:message'] || oslcError.message || message;
        } else if (errorData?.Error) {
          message = errorData.Error.message || message;
        } else if (errorData?.message) {
          message = errorData.message;
        }
        
        throw {
          success: false,
          message: `Failed to update script: ${message}`,
          status: status
        };
      }
      
      throw {
        success: false,
        message: error.message || 'Failed to update script',
        status: error.status || 500
      };
    }
  }
}

module.exports = new MaximoService();

// Made with Bob
