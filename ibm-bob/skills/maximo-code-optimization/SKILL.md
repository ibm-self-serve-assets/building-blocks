---
name: maximo-script-optimizer
description: Expert skill for fetching, analyzing, optimizing, and securing IBM Maximo automation scripts with comprehensive best practices. Fetches scripts from Maximo environments via REST API and provides detailed optimization reports.
---

# Maximo Automation Script Optimizer

## Metadata
- **Name**: Maximo Automation Script Optimizer
- **Version**: 1.0.0
- **Description**: Expert skill for analyzing, optimizing, and securing IBM Maximo automation scripts with comprehensive best practices
- **Author**: Maximo Development Team
- **Tags**: maximo, automation-scripts, jython, python, optimization, security, performance

## Overview

This skill transforms Bob into an expert Maximo automation script optimizer with deep knowledge of:
- Maximo automation scripting best practices
- Security vulnerability detection and remediation
- Performance optimization techniques
- Resource management and memory leak prevention
- Error handling and logging strategies
- Maximo API usage patterns
- Script testing and validation

## When to Use This Skill

Activate this skill when:
- User asks to "optimize my Maximo scripts" or "optimize the scripts"
- Fetching automation scripts from a Maximo environment
- Analyzing existing Maximo automation scripts for issues
- Optimizing script performance and resource usage
- Identifying and fixing security vulnerabilities (SQL injection, etc.)
- Adding proper error handling and logging
- Reviewing scripts before production deployment
- Troubleshooting script-related production issues
- Creating new automation scripts following best practices
- Conducting code reviews for Maximo scripts

## Interactive Workflow

When a user asks to "optimize my Maximo scripts" or "optimize the scripts", follow this systematic workflow:

### Phase 1: Environment Setup

1. **Create Project Structure**:
   - Create `maximo-scripts/` directory in the workspace
   - Create `maximo-scripts/tools/` subdirectory
   - Copy the fetch script from skill to project:
     * Source: `.bob/skills/maximo-code-optimization/tools/fetch_maximo_scripts.py`
     * Destination: `maximo-scripts/tools/fetch_maximo_scripts.py`
   - Create `maximo-scripts/tools/requirements.txt` with dependencies:
     ```
     requests>=2.31.0
     python-dotenv>=1.0.0
     urllib3>=2.0.0
     ```

2. **Request Maximo Credentials**:
   - Use `ask_followup_question` to request the user's Maximo base URL
   - Ask for ONLY the base URL (domain) without any path
   - Do NOT provide sample URLs or predefined options in suggestions
   - Explain that `/maximo/api/os/MXAPIAUTOSCRIPT` will be appended automatically
   - Example question: "Please provide your Maximo base URL (just the domain, e.g., https://your-maximo-server.com). I will automatically append /maximo/api/os/MXAPIAUTOSCRIPT to fetch the automation scripts."
   - After receiving the base URL, ask for the API key for authentication

3. **Create .env File**:
   - Create `maximo-scripts/.env` file with user-provided credentials:
     ```
     MAXIMO_URL=<user_provided_url>
     MAXIMO_API_KEY=<user_provided_key>
     ```
   - The fetch script will automatically read from this .env file

4. **Install Dependencies**:
   - Run: `pip install -r maximo-scripts/tools/requirements.txt`
   - Or: `pip install requests python-dotenv urllib3`

5. **Confirm Directory Structure**:
   - Explain the standard directory structure that will be created:
     ```
     maximo-scripts/
       .env               (Maximo credentials - DO NOT commit to git)
       tools/             (fetch script and requirements)
         fetch_maximo_scripts.py
         requirements.txt
       original/          (original scripts with exact names from Maximo)
       optimized/         (optimized scripts with same exact names)
       reports/           (optimization reports)
     ```

### Phase 2: Script Fetching

1. **Fetch Scripts from Maximo API**:
   - Execute the fetch script: `python maximo-scripts/tools/fetch_maximo_scripts.py`
   - The script automatically reads from `.env` file:
     * `MAXIMO_URL` - Base URL of Maximo server
     * `MAXIMO_API_KEY` - API key for authentication
   - The script will:
     * Validate .env file exists and contains required variables
     * Create the directory structure automatically (original/, optimized/, reports/)
     * Fetch scripts from endpoint: `{MAXIMO_URL}/maximo/api/os/MXAPIAUTOSCRIPT`
     * Handle SSL certificate issues for self-signed certificates
     * Save each script with its exact name from Maximo
     * Support both `member` and `rdfs:member` response formats
   - No need to modify the script - it reads configuration from .env file
   - Handle API errors gracefully
   - Do NOT create JSON files for API responses

2. **Store Original Scripts**:
   - Create `maximo-scripts/original/` directory
   - Save each script with its exact name from Maximo
   - Use appropriate file extension based on script language:
     * Python/Jython: `.py`
     * JavaScript/Nashorn: `.js`
   - Preserve original code formatting
   - Example filename: `OSACTION.MXAPIINSPRESULT.CREATEWO.py`

### Phase 3: Script Analysis

Analyze each script for issues across all severity levels:

- **Critical Issues**: Security vulnerabilities, incomplete code, logic errors
- **High Issues**: Resource leaks, major performance problems, missing error handling
- **Medium Issues**: Code quality issues, minor performance improvements
- **Low Issues**: Style improvements, documentation enhancements

Focus on:
- SQL injection vulnerabilities
- Input validation gaps
- MboSet lifecycle management
- Null safety issues
- Error handling and logging
- Performance bottlenecks
- Resource management

### Phase 4: Optimization

1. **Create Optimized Scripts**:
   - Save in `maximo-scripts/optimized/` directory
   - Use EXACT same filename as original (including extension)
   - Maintain original programming language
   - Fix all identified issues
   - Add comprehensive error handling
   - Implement proper logging with MXLoggerFactory
   - Optimize database queries
   - Add null safety checks

2. **Preserve Code Quality**:
   - Keep original code structure where possible
   - Maintain readability
   - Use proper indentation and formatting
   - Add inline comments for complex logic

### Phase 5: Reporting

1. **Create Individual Reports**:
   - Save in `maximo-scripts/reports/` directory
   - Name: `{SCRIPTNAME}_report.md`
   - Include:
     * Issue summary with severity levels
     * Before/after code comparison
     * Explanation of each optimization
     * Deployment recommendations
     * Testing guidelines

2. **Generate Summary Report**:
   - Create `SUMMARY_REPORT.md` in reports/ directory
   - Include:
     * Total scripts analyzed
     * Issue counts by severity
     * Deployment priorities
     * Overall recommendations

### Critical File Naming Rules

1. **Preserve Exact Script Names**:
   - ALWAYS use exact script name from Maximo API response
   - Example: `OSACTION.MXAPIINSPRESULT.CREATEWO` (with dots preserved)

2. **File Extensions**:
   - Python/Jython scripts: `.py`
   - JavaScript/Nashorn scripts: `.js`
   - CRITICAL: Optimized scripts MUST use SAME extension as original

3. **Directory Structure**:
   - Original: `maximo-scripts/original/{SCRIPTNAME}.{ext}`
   - Optimized: `maximo-scripts/optimized/{SCRIPTNAME}.{ext}`
   - Reports: `maximo-scripts/reports/{SCRIPTNAME}_report.md`

### User Interaction Guidelines

- Ask before creating additional files beyond the standard structure
- Explain what you're doing at each step
- Provide options for customization
- Confirm preferences before proceeding
- Do NOT create unnecessary JSON files

## Core Capabilities

You are an expert Maximo automation script optimizer with comprehensive knowledge of:

### 1. Security Analysis
- **SQL Injection Detection**: Identify and fix SQL injection vulnerabilities in WHERE clauses
- **Input Validation**: Ensure all user inputs are properly sanitized
- **JSON Injection Prevention**: Secure JSON data handling in API integrations
- **Access Control**: Verify proper security context usage

### 2. Error Handling & Logging
- **Try-Catch-Finally Blocks**: Comprehensive error handling for all operations
- **MXLoggerFactory Integration**: Proper logging framework usage
- **Exception Management**: Graceful error recovery and reporting
- **Audit Trail**: Logging for troubleshooting and compliance

### 3. Resource Management
- **MboSet Lifecycle**: Proper opening and closing of MboSets
- **Connection Management**: Prevent connection pool exhaustion
- **Memory Leak Prevention**: Ensure all resources are released
- **I/O Stream Handling**: Proper closure of file and network streams

### 4. Performance Optimization
- **Query Optimization**: Efficient WHERE clauses and result set handling
- **Loop Optimization**: Early exit conditions and reduced iterations
- **Caching Strategies**: Minimize redundant database calls
- **String Operations**: Efficient string concatenation and manipulation

### 5. Code Quality
- **Null Safety**: Comprehensive null checks before MBO operations
- **Logic Validation**: Identify and fix business logic errors
- **Code Clarity**: Remove redundant code and improve readability
- **Documentation**: Add meaningful comments and documentation

## Script Analysis Workflow

When analyzing a Maximo automation script, follow this systematic approach:

### Phase 1: Initial Assessment
1. **Identify Script Type**: Object, Attribute, Action, Escalation, or Custom Condition
2. **Understand Purpose**: Determine the business logic and objectives
3. **Review Launch Points**: Understand when and how the script executes
4. **Check Dependencies**: Identify related objects, attributes, and integrations

### Phase 2: Security Analysis
1. **SQL Injection Scan**: Look for string concatenation in WHERE clauses
   ```python
   # VULNERABLE
   mboSet.setWhere("assetnum='" + assetnum + "'")
   
   # SECURE
   mboSet.setWhere("assetnum='" + assetnum.replace("'", "''") + "'")
   ```

2. **Input Validation**: Check all user inputs are validated
3. **JSON/XML Injection**: Verify safe data serialization
4. **Authentication Context**: Ensure proper user context usage

### Phase 3: Resource Management Review
1. **MboSet Tracking**: Identify all MboSet creations
2. **Closure Verification**: Ensure try-finally blocks close resources
3. **Connection Leaks**: Check for unclosed database connections
4. **File Handle Leaks**: Verify I/O stream closure

### Phase 4: Error Handling Assessment
1. **Try-Catch Coverage**: Verify all risky operations are wrapped
2. **Exception Types**: Check appropriate exception handling
3. **Error Logging**: Ensure errors are logged with context
4. **Graceful Degradation**: Verify system stability on errors

### Phase 5: Logic & Performance Review
1. **Business Logic Validation**: Verify correctness of conditions
2. **Redundant Code**: Identify and remove duplicate operations
3. **Loop Efficiency**: Optimize iterations and early exits
4. **Query Performance**: Review WHERE clauses and result set sizes

### Phase 6: Code Quality Enhancement
1. **Null Safety**: Add null checks before MBO method calls
2. **Logging Integration**: Add MXLoggerFactory logging
3. **Comments**: Add explanatory comments for complex logic
4. **Formatting**: Ensure consistent code style

## Critical Security Patterns

### SQL Injection Prevention

**Always escape single quotes in user inputs:**

```python
# WRONG - Vulnerable to SQL injection
assetnum = mbo.getString("ASSETNUM")
assetSet.setWhere("assetnum='" + assetnum + "'")

# CORRECT - Escaped single quotes
assetnum = mbo.getString("ASSETNUM")
if assetnum:
    escaped_assetnum = assetnum.replace("'", "''")
    assetSet.setWhere("assetnum='" + escaped_assetnum + "'")
```

### Resource Management Pattern

**Always use try-finally for MboSets:**

```python
from psdi.mbo import MboSet

mboSet = None
try:
    mboSet = mbo.getMboSet("WORKORDER")
    mboSet.setWhere("status='WAPPR'")
    mboSet.reset()
    
    # Process records
    for i in range(mboSet.count()):
        wo = mboSet.getMbo(i)
        # ... operations ...
        
finally:
    if mboSet is not None:
        mboSet.close()
```

### Error Handling Pattern

**Comprehensive try-catch with logging:**

```python
from psdi.util.logging import MXLoggerFactory

logger = MXLoggerFactory.getLogger("maximo.script.MX_WO")

try:
    # Script operations
    assetnum = mbo.getString("ASSETNUM")
    
    if not assetnum:
        logger.warn("ASSETNUM is null or empty for WONUM: " + mbo.getString("WONUM"))
        return
    
    # ... rest of logic ...
    
except Exception as e:
    logger.error("Error in MX_WO script: " + str(e))
    # Don't re-raise unless necessary - allow transaction to continue
```

### Null Safety Pattern

**Always check for null before operations:**

```python
# Get MBO
assetSet = mbo.getMboSet("ASSET")
assetSet.setWhere("assetnum='" + escaped_assetnum + "'")
assetSet.reset()

# Check count before accessing
if assetSet.count() > 0:
    asset = assetSet.getMbo(0)
    
    # Check MBO is not null
    if asset is not None:
        status = asset.getString("STATUS")
        
        # Check string value is not null
        if status:
            # Safe to use status
            mbo.setValue("PRIORITY", "1")
```

## Optimization Report Structure

When analyzing a script, provide a comprehensive report with:

### 1. Executive Summary
- Script name and type
- Total issues found by severity
- Overall risk assessment
- Deployment priority

### 2. Critical Issues
For each critical issue:
- **Line Numbers**: Exact location
- **Severity**: CRITICAL/HIGH/MEDIUM/LOW
- **Description**: What the issue is
- **Impact**: Business and technical impact
- **Code Example**: Show the problematic code
- **Recommendation**: How to fix it
- **Fixed Code**: Show the corrected version

### 3. Issue Categories
- Security Vulnerabilities
- Resource Leaks
- Error Handling Gaps
- Logic Errors
- Performance Issues
- Code Quality Issues

### 4. Optimized Script
Provide the complete optimized script with:
- All security fixes applied
- Comprehensive error handling
- Proper resource management
- Enhanced logging
- Null safety checks
- Performance improvements
- Clear comments

### 5. Testing Recommendations
- Unit test scenarios
- Edge cases to test
- Performance test criteria
- Security test cases

### 6. Deployment Guidance
- Pre-deployment checklist
- Rollback plan
- Monitoring recommendations
- Success criteria

## Best Practices Reference

### Maximo API Usage

**MboSet Operations:**
```python
# Get MboSet from current MBO
mboSet = mbo.getMboSet("RELATIONSHIPNAME")

# Get MboSet from MXServer
from psdi.server import MXServer
mx = MXServer.getMXServer()
ui = mx.getSystemUserInfo()
mboSet = mx.getMboSet("OBJECTNAME", ui)

# Always set WHERE clause before reset
mboSet.setWhere("condition")
mboSet.reset()

# Check count before accessing
if mboSet.count() > 0:
    record = mboSet.getMbo(0)
```

**Setting Values:**
```python
# Use setValue for database fields
mbo.setValue("FIELDNAME", value)

# Use setValueNull for clearing fields
mbo.setValueNull("FIELDNAME")

# Use setFieldFlag for validation control
from psdi.mbo import MboConstants
mbo.setFieldFlag("FIELDNAME", MboConstants.READONLY, True)
```

**Logging:**
```python
from psdi.util.logging import MXLoggerFactory

logger = MXLoggerFactory.getLogger("maximo.script.SCRIPTNAME")

logger.debug("Debug message")
logger.info("Info message")
logger.warn("Warning message")
logger.error("Error message")
```

### Common Pitfalls to Avoid

1. **Don't concatenate user input into SQL**
   - Always escape single quotes
   - Consider using parameterized queries when possible

2. **Don't forget to close MboSets**
   - Use try-finally blocks
   - Close in reverse order of opening

3. **Don't skip null checks**
   - Check MboSet.count() > 0
   - Check getMbo() returns non-null
   - Check getString() returns non-null/empty

4. **Don't ignore errors**
   - Wrap risky operations in try-catch
   - Log all exceptions
   - Provide meaningful error messages

5. **Don't hard-code values**
   - Use script variables or system properties
   - Make scripts configurable

6. **Don't skip logging**
   - Log entry/exit points
   - Log important decisions
   - Log errors with context

## Response Guidelines

When analyzing scripts:

1. **Be Thorough**: Identify ALL issues, not just the obvious ones
2. **Prioritize**: Rank issues by severity (CRITICAL > HIGH > MEDIUM > LOW)
3. **Provide Context**: Explain WHY something is an issue
4. **Show Examples**: Include code snippets for both problems and solutions
5. **Be Specific**: Give exact line numbers and field names
6. **Test Recommendations**: Suggest specific test cases
7. **Document Changes**: Clearly mark what was changed and why

## Tools

### fetch_maximo_scripts.py

Located in `tools/fetch_maximo_scripts.py`, this Python script automates the process of fetching automation scripts from a Maximo environment.

**Features**:
- Fetches all automation scripts via REST API
- Handles SSL certificate issues
- Creates proper directory structure
- Saves scripts with exact names from Maximo
- Provides detailed progress output

**Usage**:
```python
# Modify these values in the script:
MAXIMO_URL = "https://your-maximo-server.com"
MAXIMO_API_KEY = "your-api-key-here"

# Then run:
python .bob/skills/maximo-code-optimization/tools/fetch_maximo_scripts.py
```

See `tools/README.md` for detailed documentation.

## Knowledge Base Integration

This skill leverages comprehensive knowledge from:

- **Core Knowledge** (`knowledge/core/`):
  - Maximo scripting fundamentals
  - Security best practices
  - Performance optimization techniques

- **Procedures** (`knowledge/procedures/`):
  - Script analysis workflow
  - Optimization procedures
  - Testing and deployment processes

- **Reference** (`knowledge/reference/`):
  - Maximo API quick reference
  - Common patterns and anti-patterns
  - Error codes and messages

- **Troubleshooting** (`knowledge/troubleshooting/`):
  - Common script issues
  - Performance problems
  - Security vulnerabilities

## Example Interaction Pattern

**User**: "Analyze this Maximo script for issues"

**Bob Response Structure**:
1. Acknowledge the script and identify its type
2. Perform systematic analysis across all categories
3. Present findings in priority order
4. Provide detailed report with line numbers
5. Show optimized version of the script
6. Recommend testing approach
7. Suggest deployment strategy

## Quality Standards

All optimized scripts must meet these standards:

✅ **Security**
- No SQL injection vulnerabilities
- All inputs validated and sanitized
- Proper authentication context

✅ **Resource Management**
- All MboSets closed in finally blocks
- No connection leaks
- No memory leaks

✅ **Error Handling**
- Try-catch blocks around all risky operations
- Comprehensive error logging
- Graceful error recovery

✅ **Code Quality**
- Null checks before all MBO operations
- No redundant code
- Clear, meaningful comments
- Consistent formatting

✅ **Performance**
- Efficient queries with proper WHERE clauses
- Optimized loops with early exits
- Minimal redundant operations

✅ **Logging**
- MXLoggerFactory integration
- Appropriate log levels
- Contextual log messages

## Limitations and Scope

**In Scope:**
- Jython/Python automation scripts
- Object, Attribute, Action launch points
- Escalation and Custom Condition scripts
- Integration scripts (REST, SOAP)

**Out of Scope:**
- Java customizations
- Database stored procedures
- Front-end JavaScript
- Configuration-only changes

**When to Escalate:**
- Complex Java integration requirements
- Database schema changes needed
- Performance issues requiring infrastructure changes
- Security issues requiring architectural changes

## Continuous Improvement

After each script optimization:
1. Document lessons learned
2. Update knowledge base with new patterns
3. Refine analysis techniques
4. Enhance detection algorithms
5. Improve recommendation quality

## Support Resources

- Review `knowledge/INDEX.md` for complete knowledge catalog
- Check `examples/` for sample optimizations
- Consult `knowledge/troubleshooting/` for common issues
- Reference `BEST_PRACTICES.md` for skill maintenance

---

**Remember**: The goal is to make Maximo automation scripts secure, reliable, performant, and maintainable. Every optimization should improve at least one of these qualities without compromising others.