/**
 * Maximo Scripting Best Practices Optimizer
 * Implements actual code modifications based on IBM Maximo best practices
 */

class MaximoBestPractices {
  /**
   * Apply Maximo best practices to Python/Jython scripts
   * Actually modifies the code to implement best practices
   */
  applyPythonBestPractices(source, analysis, improvements) {
    let optimized = source;
    const appliedOptimizations = [];
    
    // Best Practice 1: Cache count() calls
    if ((source.match(/\.count\(\)/g) || []).length > 1) {
      optimized = this.cacheCountCalls(optimized);
      appliedOptimizations.push('Cached count() results');
    }
    
    // Best Practice 2: Add proper MboSet cleanup
    if (source.includes('getMboSet') && !source.includes('finally')) {
      optimized = this.addProperMboSetCleanup(optimized);
      appliedOptimizations.push('Added MboSet cleanup');
    }
    
    // Best Practice 3: Add error handling
    if (!source.includes('try') && !source.includes('except')) {
      optimized = this.addErrorHandling(optimized);
      appliedOptimizations.push('Added error handling');
    }
    
    // Best Practice 4: Add logging level check
    if (source.includes('service.log(') && !source.includes('isLoggingEnabled')) {
      optimized = this.addLoggingLevelCheck(optimized);
      appliedOptimizations.push('Added logging level check');
    }
    
    // Update improvements array
    improvements.push(...appliedOptimizations);
    
    // Add header
    if (appliedOptimizations.length > 0) {
      const header = `# Optimized by IBM Bob\n# Optimizations: ${appliedOptimizations.join(', ')}\n\n`;
      optimized = header + optimized;
    }
    
    return optimized;
  }

  /**
   * Cache count() calls to avoid multiple SQL queries
   */
  cacheCountCalls(source) {
    const lines = source.split('\n');
    const result = [];
    const countVars = new Map(); // varName -> cachedVarName
    let modified = false;
    
    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];
      const countMatches = [...line.matchAll(/(\w+)\.count\(\)/g)];
      
      if (countMatches.length > 0) {
        let modifiedLine = line;
        
        for (const match of countMatches) {
          const varName = match[1];
          
          if (!countVars.has(varName)) {
            // First occurrence - cache it
            const indent = line.match(/^\s*/)[0];
            const cachedVar = `${varName}_count`;
            result.push(`${indent}${cachedVar} = ${varName}.count()  # Cache to avoid multiple SQL queries`);
            countVars.set(varName, cachedVar);
            modified = true;
          }
          
          // Replace in current line
          const cachedVar = countVars.get(varName);
          modifiedLine = modifiedLine.replace(new RegExp(`${varName}\\.count\\(\\)`, 'g'), cachedVar);
        }
        
        result.push(modifiedLine);
      } else {
        result.push(line);
      }
    }
    
    return modified ? result.join('\n') : source;
  }

  /**
   * Add proper MboSet cleanup with try-finally
   */
  addProperMboSetCleanup(source) {
    const lines = source.split('\n');
    const mboSetVars = [];
    
    // Find all MboSet variables
    for (const line of lines) {
      const match = line.match(/(\w+)\s*=.*getMboSet/);
      if (match) {
        mboSetVars.push(match[1]);
      }
    }
    
    if (mboSetVars.length === 0) {
      return source;
    }
    
    // Get base indentation
    const baseIndent = lines.find(l => l.trim().length > 0)?.match(/^\s*/)[0] || '';
    const indent = '    ';
    
    // Wrap in try-finally
    const result = [];
    
    // Initialize MboSet variables
    for (const varName of mboSetVars) {
      result.push(`${baseIndent}${varName} = None`);
    }
    
    result.push(`${baseIndent}try:`);
    
    // Indent all original lines
    for (const line of lines) {
      if (line.trim().length > 0) {
        result.push(`${indent}${line}`);
      } else {
        result.push(line);
      }
    }
    
    result.push(`${baseIndent}finally:`);
    result.push(`${indent}# Always close MboSets to prevent memory leaks`);
    
    for (const varName of mboSetVars) {
      result.push(`${indent}if ${varName} is not None:`);
      result.push(`${indent}${indent}${varName}.close()`);
    }
    
    return result.join('\n');
  }

  /**
   * Add comprehensive error handling
   */
  addErrorHandling(source) {
    const lines = source.split('\n');
    const baseIndent = lines.find(l => l.trim().length > 0)?.match(/^\s*/)[0] || '';
    const indent = '    ';
    
    const result = [];
    result.push(`${baseIndent}try:`);
    
    // Indent all original lines
    for (const line of lines) {
      if (line.trim().length > 0) {
        result.push(`${indent}${line}`);
      } else {
        result.push(line);
      }
    }
    
    result.push(`${baseIndent}except Exception as e:`);
    result.push(`${indent}from psdi.util.logging import MXLoggerFactory`);
    result.push(`${indent}logger = MXLoggerFactory.getLogger("maximo.script")`);
    result.push(`${indent}logger.error("Script error: " + str(e))`);
    result.push(`${indent}raise`);
    
    return result.join('\n');
  }

  /**
   * Add logging level check before logging
   */
  addLoggingLevelCheck(source) {
    const lines = source.split('\n');
    const result = [];
    let loggerAdded = false;
    
    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];
      
      if (line.includes('service.log(')) {
        const indent = line.match(/^\s*/)[0];
        
        if (!loggerAdded) {
          // Add logger import at the beginning
          result.unshift('from psdi.util.logging import MXLoggerFactory');
          result.unshift('logger = MXLoggerFactory.getLogger("maximo.script")');
          result.unshift('');
          loggerAdded = true;
        }
        
        // Wrap log call with level check
        result.push(`${indent}if logger.isDebugEnabled():`);
        result.push(`${indent}    ${line.trim()}`);
      } else {
        result.push(line);
      }
    }
    
    return result.join('\n');
  }

  /**
   * Apply best practices to JavaScript scripts
   */
  applyJavaScriptBestPractices(source, analysis, improvements) {
    let optimized = source;
    const appliedOptimizations = [];
    
    // Replace var with let/const
    if (source.includes('var ')) {
      optimized = optimized.replace(/\bvar\b/g, 'let');
      appliedOptimizations.push('Replaced var with let');
    }
    
    // Replace == with ===
    if (/[^=!]==[^=]/.test(source)) {
      optimized = optimized.replace(/([^=!])==([^=])/g, '$1===$2');
      appliedOptimizations.push('Replaced == with ===');
    }
    
    // Add try-catch if missing
    if (!source.includes('try') && !source.includes('catch')) {
      optimized = this.addJavaScriptErrorHandling(optimized);
      appliedOptimizations.push('Added error handling');
    }
    
    // Update improvements array
    improvements.push(...appliedOptimizations);
    
    // Add header
    if (appliedOptimizations.length > 0) {
      const header = `// Optimized by IBM Bob\n// Optimizations: ${appliedOptimizations.join(', ')}\n\n`;
      optimized = header + optimized;
    }
    
    return optimized;
  }

  /**
   * Add JavaScript error handling
   */
  addJavaScriptErrorHandling(source) {
    const lines = source.split('\n');
    const baseIndent = lines.find(l => l.trim().length > 0)?.match(/^\s*/)[0] || '';
    const indent = '    ';
    
    const result = [];
    result.push(`${baseIndent}try {`);
    
    // Indent all original lines
    for (const line of lines) {
      if (line.trim().length > 0) {
        result.push(`${indent}${line}`);
      } else {
        result.push(line);
      }
    }
    
    result.push(`${baseIndent}} catch (error) {`);
    result.push(`${indent}var logger = MXLoggerFactory.getLogger("maximo.script");`);
    result.push(`${indent}logger.error("Script error: " + error.message);`);
    result.push(`${indent}throw error;`);
    result.push(`${baseIndent}}`);
    
    return result.join('\n');
  }
}

module.exports = new MaximoBestPractices();

// Made with Bob
