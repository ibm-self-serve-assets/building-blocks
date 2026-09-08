/**
 * Simple but effective Java to Python converter for Maximo automation scripts
 */

function convertJavaToPython(javaCode) {
  let pythonCode = `# Converted from Java to Python (Jython)
# Business logic preserved from original Java implementation

from psdi.mbo import MboConstants
from psdi.server import MXServer
from psdi.util import MXApplicationException
from java.util import Date

`;

  // Remove package and imports
  javaCode = javaCode.replace(/package\s+[\w.]+;\s*/g, '');
  javaCode = javaCode.replace(/import\s+[\w.]+;\s*/g, '');
  
  // Remove ALL class-related keywords and declarations
  javaCode = javaCode.replace(/public\s+class\s+\w+\s*\{/g, '');
  javaCode = javaCode.replace(/private\s+class\s+\w+\s*\{/g, '');
  javaCode = javaCode.replace(/static\s+class\s+\w+\s*\{/g, '');
  javaCode = javaCode.replace(/public\s+static\s+class\s+\w+\s*\{/g, '');
  
  // Remove method signatures but keep the body
  javaCode = javaCode.replace(/public\s+void\s+\w+\s*\([^)]*\)\s*throws\s+[^{]+\{/g, '');
  javaCode = javaCode.replace(/public\s+void\s+\w+\s*\([^)]*\)\s*\{/g, '');
  javaCode = javaCode.replace(/public\s+static\s+void\s+\w+\s*\([^)]*\)\s*\{/g, '');
  javaCode = javaCode.replace(/private\s+\w+\s+\w+\s*\([^)]*\)\s*\{/g, '');
  javaCode = javaCode.replace(/public\s+\w+\s+\w+\s*\([^)]*\)\s*\{/g, '');
  
  // Remove the last closing brace (from class)
  javaCode = javaCode.trim();
  if (javaCode.endsWith('}')) {
    javaCode = javaCode.substring(0, javaCode.lastIndexOf('}')).trim();
  }
  // Remove any additional trailing closing braces
  while (javaCode.endsWith('}') && javaCode.split('{').length - 1 < javaCode.split('}').length - 1) {
    javaCode = javaCode.substring(0, javaCode.lastIndexOf('}')).trim();
  }
  
  // Process line by line
  const lines = javaCode.split('\n');
  let indentLevel = 0;
  let skipNext = false;
  
  for (let i = 0; i < lines.length; i++) {
    let line = lines[i];
    const originalIndent = line.match(/^\s*/)[0];
    line = line.trim();
    
    // Convert comments
    if (line.startsWith('//')) {
      pythonCode += '    '.repeat(indentLevel) + line.replace('//', '#') + '\n';
      continue;
    }
    
    // Skip empty lines and block comments
    if (!line || line.startsWith('/**') || line.startsWith('*') || line === '*/') {
      continue;
    }
    
    // Skip lines that are just Java keywords
    if (line.match(/^(public|private|protected|static|final|abstract|class|interface|extends|implements)\s/)) {
      continue;
    }
    
    // Handle closing braces
    if (line === '}' || line === '};') {
      indentLevel = Math.max(0, indentLevel - 1);
      continue;
    }
    
    // Convert the line
    let pythonLine = convertLine(line);
    
    if (pythonLine) {
      const indent = '    '.repeat(indentLevel);
      pythonCode += indent + pythonLine + '\n';
      
      // Adjust indent for next line
      if (pythonLine.endsWith(':')) {
        indentLevel++;
      }
    }
  }
  
  return pythonCode;
}

function convertLine(line) {
  // Remove semicolons
  line = line.replace(/;$/, '');
  
  // Skip if it's just a closing brace
  if (line === '}') {
    return null;
  }
  
  // Skip lines with only Java keywords
  if (line.match(/^(public|private|protected|static|final|void|class)\s*$/)) {
    return null;
  }
  
  // Remove Java access modifiers and keywords from the start of lines
  line = line.replace(/^(public|private|protected|static|final|abstract)\s+/g, '');
  
  // Convert variable declarations
  line = line.replace(/^(String|int|double|float|boolean|MboRemote|MboSetRemote)\s+(\w+)\s*=\s*(.+)$/, (match, type, name, value) => {
    value = convertValue(value);
    return `${name} = ${value}`;
  });
  
  line = line.replace(/^(String|int|double|float|boolean|MboRemote|MboSetRemote)\s+(\w+)$/, '$2 = None');
  
  // Convert if statements - handle multi-line conditions
  if (line.startsWith('if (') || line.startsWith('if(')) {
    line = line.replace(/^if\s*\((.*)\)\s*\{?$/, (match, condition) => {
      condition = convertCondition(condition);
      return `if ${condition}:`;
    });
  }
  
  // Convert for loops
  if (line.startsWith('for (') || line.startsWith('for(')) {
    // Handle traditional for loop: for (int i = 0; i < count; i++)
    const forMatch = line.match(/for\s*\(\s*int\s+(\w+)\s*=\s*(\d+)\s*;\s*\1\s*<\s*([^;]+)\s*;\s*\1\+\+\s*\)/);
    if (forMatch) {
      const varName = forMatch[1];
      const start = forMatch[2];
      let end = forMatch[3].trim();
      end = end.replace(/\{$/, '').trim();
      end = convertValue(end);
      return `for ${varName} in range(${start}, ${end}):`;
    }
    
    // Handle enhanced for loop: for (Type var : collection)
    const enhancedForMatch = line.match(/for\s*\(\s*(\w+)\s+(\w+)\s*:\s*([^)]+)\s*\)/);
    if (enhancedForMatch) {
      const varName = enhancedForMatch[2];
      const collection = convertValue(enhancedForMatch[3].trim());
      return `for ${varName} in ${collection}:`;
    }
  }
  
  // Convert return - in Maximo scripts, we can't use return outside functions
  // Just skip early returns or convert to pass
  if (line === 'return') {
    return 'pass  # Early exit';
  }
  
  // Convert throw to raise (handle multi-line)
  if (line.startsWith('throw ')) {
    // Simple single-line throw
    if (line.includes(')')) {
      line = line.replace(/throw\s+new\s+(\w+)\s*\((.*)\)/, (match, exception, args) => {
        args = convertValue(args);
        return `raise ${exception}(${args})`;
      });
      return line;
    } else {
      // Multi-line throw - just convert the keyword for now
      line = line.replace(/throw\s+new\s+/, 'raise ');
      return line;
    }
  }
  
  // Handle continuation of multi-line statements
  if (line.match(/^(new\s+Object\[|'[^']*'|"[^"]*"|\d+)/)) {
    return convertValue(line);
  }
  
  // Convert regular statements
  line = convertValue(line);
  
  // Remove opening brace if present
  line = line.replace(/\s*\{\s*$/, '');
  
  return line;
}

function convertCondition(condition) {
  // Handle multi-line conditions
  condition = condition.replace(/\s+/g, ' ').trim();
  
  // Convert .equals()
  condition = condition.replace(/(\w+)\.equals\(([^)]+)\)/g, '$1 == $2');
  condition = condition.replace(/([^)]+)\.equals\(([^)]+)\)/g, '$1 == $2');
  
  // Convert logical operators
  condition = condition.replace(/&&/g, 'and');
  condition = condition.replace(/\|\|/g, 'or');
  condition = condition.replace(/!(\w)/g, 'not $1');
  
  // Convert values
  condition = convertValue(condition);
  
  return condition;
}

function convertValue(value) {
  // Convert null, true, false
  value = value.replace(/\bnull\b/g, 'None');
  value = value.replace(/\btrue\b/g, 'True');
  value = value.replace(/\bfalse\b/g, 'False');
  
  // Convert quotes
  value = value.replace(/"/g, "'");
  
  // Convert new Date()
  value = value.replace(/new\s+Date\(\)/g, 'MXServer.getMXServer().getDate()');
  
  // Convert Java arrays to Python lists
  value = value.replace(/new\s+Object\[\]\s*\{([^}]+)\}/g, '[$1]');
  value = value.replace(/new\s+\w+\[\]\s*\{([^}]+)\}/g, '[$1]');
  
  return value;
}

function convertJavaToJavaScript(javaCode) {
  let jsCode = `// Converted from Java to JavaScript
// Business logic preserved from original Java implementation

`;

  // Remove package and imports
  javaCode = javaCode.replace(/package\s+[\w.]+;\s*/g, '');
  javaCode = javaCode.replace(/import\s+[\w.]+;\s*/g, '');
  
  // Remove ALL class-related keywords and declarations
  javaCode = javaCode.replace(/public\s+class\s+\w+\s*\{/g, '');
  javaCode = javaCode.replace(/private\s+class\s+\w+\s*\{/g, '');
  javaCode = javaCode.replace(/static\s+class\s+\w+\s*\{/g, '');
  javaCode = javaCode.replace(/public\s+static\s+class\s+\w+\s*\{/g, '');
  
  // Remove method signatures but keep the body
  javaCode = javaCode.replace(/public\s+void\s+\w+\s*\([^)]*\)\s*throws\s+[^{]+\{/g, '');
  javaCode = javaCode.replace(/public\s+void\s+\w+\s*\([^)]*\)\s*\{/g, '');
  javaCode = javaCode.replace(/public\s+static\s+void\s+\w+\s*\([^)]*\)\s*\{/g, '');
  javaCode = javaCode.replace(/private\s+\w+\s+\w+\s*\([^)]*\)\s*\{/g, '');
  javaCode = javaCode.replace(/public\s+\w+\s+\w+\s*\([^)]*\)\s*\{/g, '');
  
  // Remove the last closing brace (from class)
  javaCode = javaCode.trim();
  if (javaCode.endsWith('}')) {
    javaCode = javaCode.substring(0, javaCode.lastIndexOf('}')).trim();
  }
  // Remove any additional trailing closing braces
  while (javaCode.endsWith('}') && javaCode.split('{').length - 1 < javaCode.split('}').length - 1) {
    javaCode = javaCode.substring(0, javaCode.lastIndexOf('}')).trim();
  }
  
  // Process line by line
  const lines = javaCode.split('\n');
  let indentLevel = 0;
  let inMultiLineStatement = false;
  let multiLineBuffer = '';
  let multiLineIndent = 0;
  
  for (let i = 0; i < lines.length; i++) {
    let line = lines[i];
    const originalIndent = line.match(/^\s*/)[0];
    line = line.trim();
    
    // Convert comments
    if (line.startsWith('//')) {
      jsCode += '    '.repeat(indentLevel) + line + '\n';
      continue;
    }
    
    // Skip empty lines and block comments
    if (!line || line.startsWith('/**') || line.startsWith('*') || line === '*/') {
      continue;
    }
    
    // Skip lines that are just Java keywords
    if (line.match(/^(public|private|protected|static|final|abstract|class|interface|extends|implements)\s/)) {
      continue;
    }
    
    // Handle closing braces
    if (line === '}' || line === '};') {
      indentLevel = Math.max(0, indentLevel - 1);
      jsCode += '    '.repeat(indentLevel) + '}\n';
      continue;
    }
    
    // Check if we're starting a multi-line statement (opening paren without closing)
    const openParens = (line.match(/\(/g) || []).length;
    const closeParens = (line.match(/\)/g) || []).length;
    const openBrackets = (line.match(/\[/g) || []).length;
    const closeBrackets = (line.match(/\]/g) || []).length;
    
    if (inMultiLineStatement) {
      // Continue building multi-line statement
      multiLineBuffer += ' ' + line;
      
      // Check if statement is complete
      const totalOpenParens = (multiLineBuffer.match(/\(/g) || []).length;
      const totalCloseParens = (multiLineBuffer.match(/\)/g) || []).length;
      
      if (totalOpenParens === totalCloseParens) {
        // Statement is complete
        let jsLine = convertLineToJS(multiLineBuffer);
        if (jsLine) {
          const indent = '    '.repeat(multiLineIndent);
          jsCode += indent + jsLine + '\n';
          
          if (jsLine.endsWith('{')) {
            indentLevel++;
          }
        }
        inMultiLineStatement = false;
        multiLineBuffer = '';
      }
    } else if (openParens > closeParens || openBrackets > closeBrackets) {
      // Starting a multi-line statement
      inMultiLineStatement = true;
      multiLineBuffer = line;
      multiLineIndent = indentLevel;
    } else {
      // Regular single-line statement
      let jsLine = convertLineToJS(line);
      
      if (jsLine) {
        const indent = '    '.repeat(indentLevel);
        jsCode += indent + jsLine + '\n';
        
        // Adjust indent for next line
        if (jsLine.endsWith('{')) {
          indentLevel++;
        }
      }
    }
  }
  
  return jsCode;
}

function convertLineToJS(line) {
  // Skip if it's just a closing brace
  if (line === '}') {
    return null;
  }
  
  // Skip lines with only Java keywords
  if (line.match(/^(public|private|protected|static|final|void|class)\s*$/)) {
    return null;
  }
  
  // Remove Java access modifiers and keywords from the start of lines
  line = line.replace(/^(public|private|protected|static|final|abstract)\s+/g, '');
  
  // Convert variable declarations
  line = line.replace(/^(String|int|double|float|boolean|MboRemote|MboSetRemote)\s+(\w+)\s*=\s*(.+);?$/, (match, type, name, value) => {
    value = convertValueToJS(value.replace(/;$/, '')); // Remove trailing semicolon from value
    return `var ${name} = ${value}`;  // Don't add semicolon here, will be added later if needed
  });
  
  line = line.replace(/^(String|int|double|float|boolean|MboRemote|MboSetRemote)\s+(\w+);?$/, 'var $2 = null');
  
  // Convert if statements
  if (line.startsWith('if (') || line.startsWith('if(')) {
    line = line.replace(/^if\s*\((.*)\)\s*\{?$/, (match, condition) => {
      condition = convertConditionToJS(condition);
      return `if (${condition}) {`;
    });
  }
  
  // Convert for loops
  if (line.startsWith('for (') || line.startsWith('for(')) {
    // Handle traditional for loop: for (int i = 0; i < count; i++)
    const forMatch = line.match(/for\s*\(\s*int\s+(\w+)\s*=\s*(\d+)\s*;\s*\1\s*<\s*([^;]+)\s*;\s*\1\+\+\s*\)/);
    if (forMatch) {
      const varName = forMatch[1];
      const start = forMatch[2];
      let end = forMatch[3].trim();
      end = end.replace(/\{$/, '').trim();
      end = convertValueToJS(end);
      return `for (var ${varName} = ${start}; ${varName} < ${end}; ${varName}++) {`;
    }
  }
  
  // Convert return statements - in Maximo scripts, return without value is not allowed
  // We need to wrap the script logic in a function or remove standalone returns
  if (line === 'return' || line === 'return;') {
    return '// Early exit - return statement removed for Maximo script compatibility';
  }
  
  // Convert throw statements
  if (line.startsWith('throw ')) {
    line = line.replace(/throw\s+new\s+(\w+)\s*\((.*)\);?/, (match, exception, args) => {
      args = convertValueToJS(args);
      return `throw new ${exception}(${args});`;
    });
    return line;
  }
  
  // Convert regular statements
  line = convertValueToJS(line);
  
  // Ensure semicolon at end if not a control structure or continuation line
  // Don't add semicolon if line ends with comma, opening paren, or is part of multi-line statement
  if (!line.endsWith('{') &&
      !line.endsWith(';') &&
      !line.endsWith(',') &&
      !line.endsWith('(') &&
      !line.endsWith('[') &&
      line.length > 0 &&
      !line.match(/^\s*(\/\/|#)/)) {  // Don't add to comments
    line += ';';
  }
  
  return line;
}

function convertConditionToJS(condition) {
  // Handle multi-line conditions
  condition = condition.replace(/\s+/g, ' ').trim();
  
  // Convert .equals() to ===
  condition = condition.replace(/(\w+)\.equals\(([^)]+)\)/g, '$1 === $2');
  condition = condition.replace(/([^)]+)\.equals\(([^)]+)\)/g, '$1 === $2');
  
  // Convert values
  condition = convertValueToJS(condition);
  
  return condition;
}

function convertValueToJS(value) {
  // Convert null (keep as is for JavaScript)
  // value = value.replace(/\bnull\b/g, 'null');
  
  // Convert true, false (keep as is for JavaScript)
  // value = value.replace(/\btrue\b/g, 'true');
  // value = value.replace(/\bfalse\b/g, 'false');
  
  // Convert new Date() (keep as is for JavaScript)
  // value = value.replace(/new\s+Date\(\)/g, 'new Date()');
  
  // Convert Java arrays to JavaScript arrays
  value = value.replace(/new\s+Object\[\]\s*\{([^}]+)\}/g, '[$1]');
  value = value.replace(/new\s+\w+\[\]\s*\{([^}]+)\}/g, '[$1]');
  
  return value;
}

module.exports = { convertJavaToPython, convertJavaToJavaScript };

// Made with Bob
