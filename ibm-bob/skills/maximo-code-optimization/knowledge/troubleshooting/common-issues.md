# Common Maximo Scripting Issues and Solutions

## Overview

This document provides solutions to common issues encountered in Maximo automation scripts, organized by category.

## Security Issues

### Issue 1: SQL Injection Vulnerability

**Symptom**: User input is concatenated directly into WHERE clauses

**Example**:
```python
assetnum = mbo.getString("ASSETNUM")
mboSet.setWhere("assetnum='" + assetnum + "'")
```

**Problem**: Malicious input like `' OR '1'='1` can bypass security

**Solution**:
```python
assetnum = mbo.getString("ASSETNUM")
if assetnum:
    # Escape single quotes
    escaped = assetnum.replace("'", "''")
    mboSet.setWhere("assetnum='" + escaped + "'")
```

**Best Practice**:
```python
from psdi.mbo import SqlFormat

assetnum = mbo.getString("ASSETNUM")
if assetnum:
    sqlFormat = SqlFormat("assetnum = :1")
    sqlFormat.setObject(1, "ASSET", "ASSETNUM", assetnum)
    mboSet.setWhere(sqlFormat.format())
```

### Issue 2: Missing Input Validation

**Symptom**: Script fails with NullPointerException or invalid data

**Example**:
```python
priority = int(mbo.getString("PRIORITY"))
mbo.setValue("WOPRIORITY", priority)
```

**Problem**: No validation of input before use

**Solution**:
```python
from psdi.util import MXApplicationException

priorityStr = mbo.getString("PRIORITY")

# Validate not null/empty
if not priorityStr or not priorityStr.strip():
    raise MXApplicationException("system", "requiredfield", ["PRIORITY"])

# Validate data type
try:
    priority = int(priorityStr)
except ValueError:
    raise MXApplicationException("system", "invalidnumber", ["PRIORITY"])

# Validate range
if not (1 <= priority <= 5):
    raise MXApplicationException("system", "invalidrange", ["PRIORITY", "1", "5"])

mbo.setValue("WOPRIORITY", priority)
```

### Issue 3: Insufficient Access Control

**Symptom**: Unauthorized users can perform sensitive operations

**Example**:
```python
# No permission check
mbo.setValue("STATUS", "APPR")
```

**Solution**:
```python
from psdi.server import MXServer
from psdi.util import MXApplicationException

mx = MXServer.getMXServer()
ui = mx.getSystemUserInfo()

# Check application access
if not ui.hasApplicationAccess("WOTRACK"):
    raise MXApplicationException("system", "noaccess", ["WOTRACK"])

# Check user group
userGroups = ui.getUserGroups()
if "APPROVERS" not in userGroups:
    raise MXApplicationException("system", "insufficientprivileges")

# Now safe to proceed
mbo.setValue("STATUS", "APPR")
```

## Resource Management Issues

### Issue 4: MboSet Not Closed

**Symptom**: Memory leaks, connection pool exhaustion, slow system

**Example**:
```python
mboSet = mx.getMboSet("WORKORDER", ui)
mboSet.setWhere("status='WAPPR'")
mboSet.reset()
# Process records
# Missing close()
```

**Problem**: MboSet consumes resources until garbage collected

**Solution**:
```python
mboSet = None
try:
    mboSet = mx.getMboSet("WORKORDER", ui)
    mboSet.setWhere("status='WAPPR'")
    mboSet.reset()
    # Process records
finally:
    if mboSet is not None:
        mboSet.close()
```

### Issue 5: MboSet Created in Loop

**Symptom**: Severe performance degradation, resource exhaustion

**Example**:
```python
for assetnum in assetList:
    assetSet = mx.getMboSet("ASSET", ui)
    assetSet.setWhere("assetnum='" + assetnum + "'")
    assetSet.reset()
    # Process asset
    assetSet.close()
```

**Problem**: Creates N database connections and queries

**Solution**:
```python
# Build IN clause
inClause = "'" + "','".join(assetList) + "'"

assetSet = None
try:
    assetSet = mx.getMboSet("ASSET", ui)
    assetSet.setWhere("assetnum in (" + inClause + ")")
    assetSet.reset()
    
    # Process all assets
    for i in range(assetSet.count()):
        asset = assetSet.getMbo(i)
        # Process asset
finally:
    if assetSet is not None:
        assetSet.close()
```

### Issue 6: Multiple MboSets Not Closed in Order

**Symptom**: Deadlocks, connection issues

**Example**:
```python
parentSet = mx.getMboSet("WORKORDER", ui)
childSet = mx.getMboSet("WOACTIVITY", ui)
# Process
parentSet.close()  # Wrong order
childSet.close()
```

**Solution**:
```python
parentSet = None
childSet = None

try:
    parentSet = mx.getMboSet("WORKORDER", ui)
    childSet = mx.getMboSet("WOACTIVITY", ui)
    # Process
finally:
    # Close in reverse order of creation
    if childSet is not None:
        childSet.close()
    if parentSet is not None:
        parentSet.close()
```

## Error Handling Issues

### Issue 7: Missing Exception Handling

**Symptom**: Unhandled exceptions, poor error messages, no logging

**Example**:
```python
mboSet = mx.getMboSet("WORKORDER", ui)
mboSet.setWhere("status='WAPPR'")
mboSet.reset()
# No try-catch
```

**Solution**:
```python
from psdi.util.logging import MXLoggerFactory
from psdi.util import MXApplicationException

logger = MXLoggerFactory.getLogger("maximo.script.WOProcess")

mboSet = None
try:
    mboSet = mx.getMboSet("WORKORDER", ui)
    mboSet.setWhere("status='WAPPR'")
    mboSet.reset()
    
    logger.info("Processing " + str(mboSet.count()) + " work orders")
    
    # Process records
    
except MXApplicationException as e:
    # Re-raise Maximo exceptions
    raise e
except Exception as e:
    logger.error("Error processing work orders: " + str(e))
    raise MXApplicationException("system", "operationfailed")
finally:
    if mboSet is not None:
        mboSet.close()
```

### Issue 8: No Logging

**Symptom**: Difficult to troubleshoot issues, no audit trail

**Example**:
```python
# No logging
for i in range(woSet.count()):
    wo = woSet.getMbo(i)
    wo.setValue("STATUS", "APPR")
```

**Solution**:
```python
from psdi.util.logging import MXLoggerFactory

logger = MXLoggerFactory.getLogger("maximo.script.WOApproval")

logger.info("Starting work order approval process")
logger.info("Processing " + str(woSet.count()) + " work orders")

approved = 0
errors = 0

for i in range(woSet.count()):
    wo = woSet.getMbo(i)
    wonum = wo.getString("WONUM")
    
    try:
        wo.setValue("STATUS", "APPR")
        approved += 1
        logger.debug("Approved WO: " + wonum)
    except Exception as e:
        errors += 1
        logger.error("Error approving WO " + wonum + ": " + str(e))

logger.info("Approval complete. Approved: " + str(approved) + ", Errors: " + str(errors))
```

### Issue 9: Exposing System Details in Errors

**Symptom**: Security risk, information disclosure

**Example**:
```python
try:
    mboSet = mx.getMboSet("WORKORDER", ui)
except Exception as e:
    raise Exception("Database error: " + str(e))  # Exposes DB details
```

**Solution**:
```python
from psdi.util.logging import MXLoggerFactory
from psdi.util import MXApplicationException

logger = MXLoggerFactory.getLogger("maximo.script.WOProcess")

try:
    mboSet = mx.getMboSet("WORKORDER", ui)
except Exception as e:
    # Log detailed error for admins
    logger.error("Error accessing work orders: " + str(e))
    # Show generic error to users
    raise MXApplicationException("system", "operationfailed")
```

## Performance Issues

### Issue 10: N+1 Query Problem

**Symptom**: Slow performance, many database queries

**Example**:
```python
woSet = mx.getMboSet("WORKORDER", ui)
woSet.reset()

for i in range(woSet.count()):
    wo = woSet.getMbo(i)
    assetnum = wo.getString("ASSETNUM")
    
    # Separate query for each work order
    assetSet = mx.getMboSet("ASSET", ui)
    assetSet.setWhere("assetnum='" + assetnum + "'")
    assetSet.reset()
    # Use asset
    assetSet.close()
```

**Solution**:
```python
woSet = mx.getMboSet("WORKORDER", ui)
woSet.reset()

for i in range(woSet.count()):
    wo = woSet.getMbo(i)
    
    # Use relationship instead of new query
    assetSet = wo.getMboSet("ASSET")
    if assetSet.count() > 0:
        asset = assetSet.getMbo(0)
        # Use asset
```

### Issue 11: No WHERE Clause

**Symptom**: Loads all records, very slow, high memory usage

**Example**:
```python
woSet = mx.getMboSet("WORKORDER", ui)
woSet.reset()  # Loads ALL work orders

for i in range(woSet.count()):
    wo = woSet.getMbo(i)
    if wo.getString("STATUS") == "WAPPR":
        # Process
```

**Solution**:
```python
woSet = mx.getMboSet("WORKORDER", ui)
woSet.setWhere("status='WAPPR' and siteid='BEDFORD'")
woSet.setMaxRows(100)
woSet.reset()

for i in range(woSet.count()):
    wo = woSet.getMbo(i)
    # Process
```

### Issue 12: Inefficient String Operations

**Symptom**: Slow performance in loops

**Example**:
```python
message = ""
for i in range(100):
    message = message + "Item " + str(i) + ", "
```

**Solution**:
```python
items = []
for i in range(100):
    items.append("Item " + str(i))
message = ", ".join(items)
```

### Issue 13: Repeated Field Access

**Symptom**: Unnecessary overhead, slower execution

**Example**:
```python
for i in range(woSet.count()):
    wo = woSet.getMbo(i)
    if wo.getString("ASSETNUM"):
        logger.info("Asset: " + wo.getString("ASSETNUM"))
        mbo.setValue("PARENTASSET", wo.getString("ASSETNUM"))
```

**Solution**:
```python
for i in range(woSet.count()):
    wo = woSet.getMbo(i)
    assetnum = wo.getString("ASSETNUM")  # Cache value
    if assetnum:
        logger.info("Asset: " + assetnum)
        mbo.setValue("PARENTASSET", assetnum)
```

## Logic Issues

### Issue 14: Missing Null Checks

**Symptom**: NullPointerException at runtime

**Example**:
```python
assetnum = mbo.getString("ASSETNUM")
if assetnum.length() > 0:  # Fails if assetnum is null
    # Process
```

**Solution**:
```python
assetnum = mbo.getString("ASSETNUM")
if assetnum and assetnum.strip():  # Safe null check
    # Process
```

### Issue 15: Incorrect Condition Order

**Symptom**: Inefficient execution, unnecessary checks

**Example**:
```python
# Checks rare condition first
if wo.getString("STATUS") == "CANCELLED":
    # Rare case (1%)
elif wo.getString("STATUS") == "WAPPR":
    # Common case (80%)
```

**Solution**:
```python
# Check common condition first
if wo.getString("STATUS") == "WAPPR":
    # Common case (80%)
elif wo.getString("STATUS") == "CANCELLED":
    # Rare case (1%)
```

### Issue 16: Redundant Checks

**Symptom**: Unnecessary code, harder to maintain

**Example**:
```python
assetnum = mbo.getString("ASSETNUM")
if assetnum is not None:
    if assetnum:
        if len(assetnum) > 0:
            # Process
```

**Solution**:
```python
assetnum = mbo.getString("ASSETNUM")
if assetnum and assetnum.strip():
    # Process (single check)
```

## Common Error Messages

### "MboSet not closed"
**Cause**: MboSet created but not closed
**Solution**: Add try-finally block with close()

### "Too many open cursors"
**Cause**: Multiple MboSets not closed
**Solution**: Close all MboSets in finally blocks

### "NullPointerException"
**Cause**: Accessing null object or field
**Solution**: Add null checks before use

### "SQL Exception"
**Cause**: Invalid SQL in WHERE clause
**Solution**: Validate and escape user input

### "Access denied"
**Cause**: User lacks permissions
**Solution**: Add access control checks

### "Deadlock detected"
**Cause**: MboSets closed in wrong order
**Solution**: Close in reverse order of creation

### "Out of memory"
**Cause**: Loading too many records
**Solution**: Use setMaxRows() and process in chunks

## Debugging Tips

### Enable Debug Logging
```python
from psdi.util.logging import MXLoggerFactory

logger = MXLoggerFactory.getLogger("maximo.script.DEBUG")
logger.setLevel("DEBUG")

logger.debug("Variable value: " + str(value))
logger.debug("MboSet count: " + str(mboSet.count()))
```

### Log Execution Time
```python
import time

startTime = time.time()

# Script operations

endTime = time.time()
logger.info("Execution time: " + str(endTime - startTime) + " seconds")
```

### Log Query Details
```python
whereClause = "status='WAPPR' and siteid='BEDFORD'"
logger.debug("WHERE clause: " + whereClause)

mboSet.setWhere(whereClause)
mboSet.reset()

logger.debug("Records found: " + str(mboSet.count()))
```

### Catch Specific Exceptions
```python
try:
    # Operations
except MXApplicationException as e:
    logger.error("Maximo exception: " + e.getMessage())
    raise
except SQLException as e:
    logger.error("Database exception: " + str(e))
    raise
except Exception as e:
    logger.error("General exception: " + str(e))
    raise
```

## Prevention Checklist

Use this checklist to prevent common issues:

### Before Deployment
- [ ] All user inputs are validated
- [ ] All WHERE clauses use escaped input
- [ ] All MboSets are closed in finally blocks
- [ ] All exceptions are caught and logged
- [ ] Access control checks are present
- [ ] Performance testing completed
- [ ] Security testing completed

### Code Review
- [ ] No SQL injection vulnerabilities
- [ ] No resource leaks
- [ ] No missing error handling
- [ ] No N+1 query problems
- [ ] No missing null checks
- [ ] Logging is comprehensive
- [ ] Code is readable and documented

### Testing
- [ ] Test with null/empty inputs
- [ ] Test with invalid data types
- [ ] Test with malicious input
- [ ] Test with large data volumes
- [ ] Test with unauthorized users
- [ ] Test error scenarios
- [ ] Monitor resource usage

## Quick Fixes

### Fix SQL Injection
```python
# Before
mboSet.setWhere("field='" + input + "'")

# After
escaped = input.replace("'", "''")
mboSet.setWhere("field='" + escaped + "'")
```

### Fix Resource Leak
```python
# Before
mboSet = mx.getMboSet("OBJECT", ui)
# Use mboSet

# After
mboSet = None
try:
    mboSet = mx.getMboSet("OBJECT", ui)
    # Use mboSet
finally:
    if mboSet is not None:
        mboSet.close()
```

### Fix Missing Error Handling
```python
# Before
mboSet = mx.getMboSet("OBJECT", ui)

# After
try:
    mboSet = mx.getMboSet("OBJECT", ui)
except Exception as e:
    logger.error("Error: " + str(e))
    raise
```

### Fix N+1 Query
```python
# Before
for i in range(woSet.count()):
    wo = woSet.getMbo(i)
    assetSet = mx.getMboSet("ASSET", ui)
    assetSet.setWhere("assetnum='" + wo.getString("ASSETNUM") + "'")
    assetSet.reset()
    assetSet.close()

# After
for i in range(woSet.count()):
    wo = woSet.getMbo(i)
    assetSet = wo.getMboSet("ASSET")  # Use relationship
```

## References

- [Security Best Practices](../core/security-best-practices.md)
- [Performance Optimization](../core/performance-optimization.md)
- [Script Optimization Workflow](../procedures/script-optimization-workflow.md)
- [Quick Reference](../reference/quick-reference.md)