# Maximo Script Optimization Workflow

## Overview

This document provides a step-by-step workflow for analyzing and optimizing Maximo automation scripts. Follow this systematic approach to ensure comprehensive script review and optimization.

## Workflow Phases

### Phase 1: Initial Assessment

#### Step 1.1: Gather Script Information
```
- Script name and launch point type
- Trigger conditions (object, attribute, action, etc.)
- Expected execution frequency
- Current performance metrics (if available)
- Known issues or complaints
```

#### Step 1.2: Read and Understand Script
```
- Read entire script from top to bottom
- Identify main purpose and business logic
- Note any complex or unclear sections
- Document dependencies on other scripts or systems
```

#### Step 1.3: Create Baseline Documentation
```
- Document current script behavior
- Note current line count
- Identify all external dependencies
- List all MboSets created
- List all database queries
```

### Phase 2: Security Analysis

#### Step 2.1: SQL Injection Check
**For each WHERE clause in the script:**

1. Identify all `setWhere()` calls
2. Check if user input is concatenated directly
3. Verify input sanitization is present
4. Test with malicious input patterns

**Example Check:**
```python
# FIND patterns like:
mboSet.setWhere("field='" + userInput + "'")

# VERIFY it should be:
escaped = userInput.replace("'", "''")
mboSet.setWhere("field='" + escaped + "'")
```

#### Step 2.2: Input Validation Check
**For each user input:**

1. Identify all input sources (mbo.getString(), parameters, etc.)
2. Check for null/empty validation
3. Check for data type validation
4. Check for range/length validation
5. Check for format validation

**Checklist:**
```
[ ] Null checks present
[ ] Empty string checks present
[ ] Data type validation present
[ ] Range validation present (for numbers)
[ ] Length validation present (for strings)
[ ] Format validation present (for emails, phones, etc.)
```

#### Step 2.3: Access Control Check
**For sensitive operations:**

1. Identify operations that modify critical data
2. Check for permission verification
3. Check for application access validation
4. Check for site access validation

**Example Check:**
```python
# VERIFY permission checks exist:
if not ui.hasApplicationAccess("APPNAME"):
    raise MXApplicationException("system", "noaccess")
```

#### Step 2.4: Sensitive Data Check
**Review logging and error handling:**

1. Check if passwords/credentials are logged
2. Check if sensitive data is exposed in errors
3. Verify error messages are generic
4. Check if stack traces are exposed

### Phase 3: Resource Management Analysis

#### Step 3.1: MboSet Lifecycle Check
**For each MboSet created:**

1. Identify where MboSet is created
2. Verify try-finally block exists
3. Verify close() is called in finally
4. Check for proper error handling

**Pattern to Verify:**
```python
mboSet = None
try:
    mboSet = mx.getMboSet("OBJECT", ui)
    # operations
finally:
    if mboSet is not None:
        mboSet.close()
```

#### Step 3.2: Resource Leak Detection
**Check for these common leaks:**

```
[ ] MboSets not closed
[ ] MboSets created in loops without closing
[ ] Multiple MboSets not closed in reverse order
[ ] MboSets created but never used
[ ] Nested MboSets without proper cleanup
```

#### Step 3.3: Connection Management
**Verify:**

1. No direct JDBC connections (use Maximo APIs)
2. No connection pooling issues
3. No long-running transactions

### Phase 4: Error Handling Analysis

#### Step 4.1: Exception Handling Check
**For each code block:**

1. Identify operations that can throw exceptions
2. Verify try-catch blocks exist
3. Check if exceptions are logged
4. Verify proper error messages

**Required Pattern:**
```python
from psdi.util.logging import MXLoggerFactory

logger = MXLoggerFactory.getLogger("maximo.script.NAME")

try:
    # operations
except Exception as e:
    logger.error("Error: " + str(e))
    # Handle or re-raise
```

#### Step 4.2: Logging Check
**Verify:**

```
[ ] Logger is initialized at script start
[ ] Appropriate log levels used (debug, info, warn, error)
[ ] Key operations are logged
[ ] Errors are logged with context
[ ] No sensitive data in logs
```

#### Step 4.3: Error Recovery Check
**For each error scenario:**

1. Verify graceful degradation
2. Check if partial success is handled
3. Verify transaction rollback if needed
4. Check if user is notified appropriately

### Phase 5: Performance Analysis

#### Step 5.1: Database Query Analysis
**For each database query:**

1. Count total queries in script
2. Identify queries in loops
3. Check WHERE clause specificity
4. Verify result set limits
5. Check for N+1 query problems

**Optimization Checklist:**
```
[ ] WHERE clauses are specific
[ ] setMaxRows() is used
[ ] Queries are not in loops
[ ] Relationships used instead of new MboSets
[ ] IN clauses used for multiple values
```

#### Step 5.2: Loop Optimization
**For each loop:**

1. Identify invariant operations
2. Check for early break opportunities
3. Verify efficient iteration method
4. Check for nested loops

**Optimization Pattern:**
```python
# Move invariants outside loop
currentDate = mx.getDate()
ui = mx.getSystemUserInfo()

for i in range(mboSet.count()):
    mbo = mboSet.getMbo(i)
    # Use cached values
    mbo.setValue("DATE", currentDate)
```

#### Step 5.3: String Operation Analysis
**Check for:**

```
[ ] Repeated string concatenations in loops
[ ] Repeated string operations (upper(), lower())
[ ] Inefficient string building
[ ] Unnecessary string conversions
```

#### Step 5.4: Caching Opportunities
**Identify cacheable items:**

1. Lookup values
2. MXServer instance
3. UserInfo instance
4. Date/time values
5. Frequently accessed objects

### Phase 6: Code Quality Analysis

#### Step 6.1: Null Safety Check
**For each field access:**

1. Verify null checks before use
2. Check for empty string handling
3. Verify safe navigation

**Pattern:**
```python
assetnum = mbo.getString("ASSETNUM")
if assetnum and assetnum.strip():
    # Safe to use assetnum
```

#### Step 6.2: Logic Validation
**Review business logic:**

1. Check for logical errors
2. Verify condition ordering
3. Check for redundant conditions
4. Verify edge case handling

#### Step 6.3: Code Readability
**Assess:**

```
[ ] Variable names are descriptive
[ ] Comments explain complex logic
[ ] Code is properly indented
[ ] Functions are single-purpose
[ ] Magic numbers are avoided
```

## Optimization Report Template

### Report Structure

```markdown
# Script Optimization Report: [SCRIPT_NAME]

## Executive Summary
- Total Issues Found: [COUNT]
- Critical: [COUNT]
- High: [COUNT]
- Medium: [COUNT]
- Low: [COUNT]

## Script Information
- **Script Name**: [NAME]
- **Launch Point**: [TYPE]
- **Current Lines**: [COUNT]
- **Analysis Date**: [DATE]

## Issues Found

### 1. Security Issues

#### Issue 1.1: SQL Injection Vulnerability
- **Severity**: Critical
- **Line**: [LINE_NUMBER]
- **Description**: User input concatenated directly into WHERE clause
- **Current Code**:
```python
[VULNERABLE CODE]
```
- **Recommended Fix**:
```python
[SECURE CODE]
```
- **Impact**: Potential data breach, unauthorized access

[Repeat for each security issue]

### 2. Resource Management Issues

#### Issue 2.1: MboSet Not Closed
- **Severity**: High
- **Line**: [LINE_NUMBER]
- **Description**: MboSet created but not closed in finally block
- **Current Code**:
```python
[PROBLEMATIC CODE]
```
- **Recommended Fix**:
```python
[FIXED CODE]
```
- **Impact**: Memory leak, connection exhaustion

[Repeat for each resource issue]

### 3. Error Handling Issues

#### Issue 3.1: Missing Exception Handling
- **Severity**: High
- **Line**: [LINE_NUMBER]
- **Description**: Database operation without try-catch
- **Current Code**:
```python
[PROBLEMATIC CODE]
```
- **Recommended Fix**:
```python
[FIXED CODE]
```
- **Impact**: Unhandled exceptions, poor error messages

[Repeat for each error handling issue]

### 4. Performance Issues

#### Issue 4.1: Query in Loop
- **Severity**: High
- **Line**: [LINE_NUMBER]
- **Description**: Database query executed inside loop
- **Current Code**:
```python
[INEFFICIENT CODE]
```
- **Recommended Fix**:
```python
[OPTIMIZED CODE]
```
- **Impact**: Slow execution, database load

[Repeat for each performance issue]

### 5. Code Quality Issues

#### Issue 5.1: Missing Null Check
- **Severity**: Medium
- **Line**: [LINE_NUMBER]
- **Description**: Field accessed without null check
- **Current Code**:
```python
[PROBLEMATIC CODE]
```
- **Recommended Fix**:
```python
[FIXED CODE]
```
- **Impact**: Potential NullPointerException

[Repeat for each quality issue]

## Optimization Summary

### Changes Made
1. [Change description]
2. [Change description]
3. [Change description]

### Performance Improvements
- Reduced database queries from [X] to [Y]
- Eliminated [X] resource leaks
- Added [X] security validations
- Improved error handling in [X] locations

### Testing Recommendations
1. Test with malicious input for SQL injection
2. Test with null/empty values
3. Test with large data volumes
4. Test error scenarios
5. Monitor resource usage

## Conclusion

[Summary of optimization results and recommendations]
```

## Optimization Workflow Example

### Example: Optimizing a Work Order Script

#### Original Script (Problematic)
```python
# Get work orders
woSet = mx.getMboSet("WORKORDER", ui)
woSet.setWhere("status='" + status + "'")  # SQL injection risk
woSet.reset()

# Process each work order
for i in range(woSet.count()):
    wo = woSet.getMbo(i)
    assetnum = wo.getString("ASSETNUM")
    
    # Get asset for each work order (N+1 problem)
    assetSet = mx.getMboSet("ASSET", ui)
    assetSet.setWhere("assetnum='" + assetnum + "'")
    assetSet.reset()
    
    if assetSet.count() > 0:
        asset = assetSet.getMbo(0)
        location = asset.getString("LOCATION")
        wo.setValue("LOCATION", location)
    
    # No close() - resource leak
```

#### Optimized Script
```python
from psdi.util.logging import MXLoggerFactory
from psdi.server import MXServer

logger = MXLoggerFactory.getLogger("maximo.script.WOUpdate")

# Validate input
status = mbo.getString("STATUS")
if not status:
    from psdi.util import MXApplicationException
    raise MXApplicationException("system", "requiredfield", ["STATUS"])

# Sanitize input
escaped_status = status.replace("'", "''")

# Cache frequently used objects
mx = MXServer.getMXServer()
ui = mx.getSystemUserInfo()

woSet = None
try:
    # Get work orders with specific WHERE clause
    woSet = mx.getMboSet("WORKORDER", ui)
    woSet.setWhere("status='" + escaped_status + "'")
    woSet.setMaxRows(100)  # Limit results
    woSet.reset()
    
    logger.info("Processing " + str(woSet.count()) + " work orders")
    
    # Process each work order
    for i in range(woSet.count()):
        wo = woSet.getMbo(i)
        
        # Use relationship instead of new MboSet
        assetSet = wo.getMboSet("ASSET")
        if assetSet.count() > 0:
            asset = assetSet.getMbo(0)
            location = asset.getString("LOCATION")
            if location:
                wo.setValue("LOCATION", location)
    
    # Batch save
    woSet.save()
    logger.info("Work orders updated successfully")
    
except Exception as e:
    logger.error("Error updating work orders: " + str(e))
    raise
    
finally:
    # Always close MboSet
    if woSet is not None:
        woSet.close()
```

#### Issues Fixed
1. **SQL Injection**: Input sanitized before use in WHERE clause
2. **N+1 Query**: Used relationship instead of creating new MboSet in loop
3. **Resource Leak**: Added try-finally block with close()
4. **Error Handling**: Added exception handling and logging
5. **Performance**: Added setMaxRows() and batch save
6. **Input Validation**: Added null check for status

## Best Practices Checklist

Use this checklist for every script optimization:

### Security
- [ ] All user inputs are sanitized
- [ ] SQL injection vulnerabilities are fixed
- [ ] Input validation is comprehensive
- [ ] Access control is verified
- [ ] Sensitive data is protected

### Resource Management
- [ ] All MboSets are closed
- [ ] Try-finally blocks are used
- [ ] Resources are closed in reverse order
- [ ] No resource leaks exist

### Error Handling
- [ ] All exceptions are caught
- [ ] Errors are logged appropriately
- [ ] Error messages are user-friendly
- [ ] Logging framework is used

### Performance
- [ ] Database queries are minimized
- [ ] WHERE clauses are specific
- [ ] Result sets are limited
- [ ] Loops are optimized
- [ ] Caching is implemented

### Code Quality
- [ ] Null checks are present
- [ ] Code is readable
- [ ] Logic is correct
- [ ] Comments explain complex sections
- [ ] Variable names are descriptive

## References

- Related: [Security Best Practices](../core/security-best-practices.md)
- Related: [Performance Optimization](../core/performance-optimization.md)
- Related: [Maximo Scripting Fundamentals](../core/maximo-scripting-fundamentals.md)