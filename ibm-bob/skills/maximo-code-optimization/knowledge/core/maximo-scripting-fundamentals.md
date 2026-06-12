# Maximo Scripting Fundamentals

## Overview

This document covers the fundamental concepts of IBM Maximo automation scripting, including script types, execution contexts, and core APIs.

## Script Types

### 1. Object Launch Point Scripts
- **Trigger**: Object lifecycle events (Add, Update, Delete, Initialize)
- **Context**: Runs on MBO (Maximo Business Object)
- **Access**: Full access to current MBO and related objects
- **Use Cases**: Data validation, field calculations, workflow automation

**Example**:
```python
# Object script on WORKORDER - runs on Save
assetnum = mbo.getString("ASSETNUM")
if assetnum:
    mbo.setValue("DESCRIPTION", "Work on asset: " + assetnum)
```

### 2. Attribute Launch Point Scripts
- **Trigger**: Attribute value changes
- **Context**: Runs when specific field is modified
- **Access**: Current MBO and the changed attribute
- **Use Cases**: Field validation, dependent field updates, calculations

**Example**:
```python
# Attribute script on WORKORDER.ASSETNUM
assetnum = mbo.getString("ASSETNUM")
if assetnum:
    # Auto-populate location from asset
    assetSet = mbo.getMboSet("ASSET")
    if assetSet.count() > 0:
        asset = assetSet.getMbo(0)
        location = asset.getString("LOCATION")
        mbo.setValue("LOCATION", location)
```

### 3. Action Launch Point Scripts
- **Trigger**: Custom actions invoked by users or workflows
- **Context**: Runs on demand
- **Access**: Current MBO or MboSet
- **Use Cases**: Custom business logic, integrations, batch operations

**Example**:
```python
# Action script to approve multiple work orders
from psdi.mbo import MboConstants

for i in range(mboSet.count()):
    wo = mboSet.getMbo(i)
    if wo.getString("STATUS") == "WAPPR":
        wo.setValue("STATUS", "APPR")
        wo.setValue("STATUSDATE", MXServer.getMXServer().getDate())
```

### 4. Escalation Scripts
- **Trigger**: Time-based conditions
- **Context**: Runs on schedule
- **Access**: Query results based on escalation WHERE clause
- **Use Cases**: Notifications, status updates, data cleanup

### 5. Custom Condition Scripts
- **Trigger**: Evaluated for conditional logic
- **Context**: Returns boolean result
- **Access**: Current MBO
- **Use Cases**: Conditional visibility, workflow routing, validation

## Core Maximo APIs

### MBO (Maximo Business Object)

The MBO represents a single record in Maximo.

**Common Methods**:
```python
# Get field values
value = mbo.getString("FIELDNAME")
value = mbo.getInt("FIELDNAME")
value = mbo.getDouble("FIELDNAME")
value = mbo.getDate("FIELDNAME")
value = mbo.getBoolean("FIELDNAME")

# Set field values
mbo.setValue("FIELDNAME", value)
mbo.setValueNull("FIELDNAME")

# Field flags
from psdi.mbo import MboConstants
mbo.setFieldFlag("FIELDNAME", MboConstants.READONLY, True)
mbo.setFieldFlag("FIELDNAME", MboConstants.REQUIRED, True)

# Get related MboSets
relatedSet = mbo.getMboSet("RELATIONSHIPNAME")

# Check if new record
isNew = mbo.toBeAdded()
isModified = mbo.toBeSaved()
isDeleted = mbo.toBeDeleted()
```

### MboSet (Collection of MBOs)

The MboSet represents a collection of records.

**Common Methods**:
```python
# Get MboSet
from psdi.server import MXServer
mx = MXServer.getMXServer()
ui = mx.getSystemUserInfo()
mboSet = mx.getMboSet("OBJECTNAME", ui)

# Set WHERE clause
mboSet.setWhere("status='WAPPR' and siteid='BEDFORD'")
mboSet.reset()

# Get count
count = mboSet.count()

# Iterate records
for i in range(mboSet.count()):
    record = mboSet.getMbo(i)
    # Process record

# Add new record
newMbo = mboSet.add()
newMbo.setValue("FIELDNAME", value)

# Delete record
mbo.delete()

# Save changes
mboSet.save()

# Close MboSet (CRITICAL!)
mboSet.close()
```

### MXServer

The MXServer provides access to system-level functions.

**Common Methods**:
```python
from psdi.server import MXServer

mx = MXServer.getMXServer()

# Get system user info
ui = mx.getSystemUserInfo()

# Get current date/time
currentDate = mx.getDate()

# Get MboSet
mboSet = mx.getMboSet("OBJECTNAME", ui)

# Lookup values
lookup = mx.lookup("DOMAINID")
```

### MXLoggerFactory

The logging framework for Maximo scripts.

**Usage**:
```python
from psdi.util.logging import MXLoggerFactory

logger = MXLoggerFactory.getLogger("maximo.script.SCRIPTNAME")

logger.debug("Debug level message")
logger.info("Info level message")
logger.warn("Warning level message")
logger.error("Error level message")

# Log with exception
try:
    # operations
except Exception as e:
    logger.error("Error occurred: " + str(e), e)
```

## Script Variables

Scripts have access to implicit variables:

### Common Variables
- `mbo` - Current Maximo Business Object
- `mboSet` - Current MboSet (for action scripts)
- `scriptName` - Name of the current script
- `service` - Script service object

### Getting Script Variables
```python
# Access script variables (configured in Automation Scripts app)
from psdi.common.context import ScriptDriverFactory

driver = ScriptDriverFactory.getScriptDriver()
varValue = driver.getScriptVariable("VARIABLENAME")
```

## Execution Context

### User Context
Scripts run in the context of the user who triggered them:
```python
from psdi.server import MXServer

mx = MXServer.getMXServer()
ui = mx.getSystemUserInfo()

# Get current user
username = ui.getUserName()
personId = ui.getPersonId()

# Check user permissions
hasAccess = ui.hasApplicationAccess("APPNAME")
```

### Transaction Context
Scripts run within database transactions:
- Changes are committed when the transaction completes
- Errors can rollback the entire transaction
- Use `mboSet.save()` to commit changes explicitly

## Best Practices

### 1. Always Close MboSets
```python
mboSet = None
try:
    mboSet = mx.getMboSet("WORKORDER", ui)
    # Use mboSet
finally:
    if mboSet is not None:
        mboSet.close()
```

### 2. Check for Null/Empty
```python
assetnum = mbo.getString("ASSETNUM")
if assetnum and assetnum.strip():
    # Safe to use assetnum
```

### 3. Use Logging
```python
from psdi.util.logging import MXLoggerFactory

logger = MXLoggerFactory.getLogger("maximo.script.SCRIPTNAME")
logger.info("Script started for WONUM: " + mbo.getString("WONUM"))
```

### 4. Handle Errors
```python
try:
    # Script logic
except Exception as e:
    logger.error("Error in script: " + str(e))
    # Don't re-raise unless necessary
```

### 5. Validate Inputs
```python
assetnum = mbo.getString("ASSETNUM")
if not assetnum:
    from psdi.util import MXApplicationException
    raise MXApplicationException("system", "requiredfield", ["ASSETNUM"])
```

## Common Patterns

### Pattern 1: Update Related Records
```python
# Update all child work orders when parent status changes
taskSet = mbo.getMboSet("WOACTIVITY")
for i in range(taskSet.count()):
    task = taskSet.getMbo(i)
    task.setValue("STATUS", mbo.getString("STATUS"))
```

### Pattern 2: Conditional Field Updates
```python
# Set priority based on asset criticality
assetnum = mbo.getString("ASSETNUM")
if assetnum:
    assetSet = mbo.getMboSet("ASSET")
    if assetSet.count() > 0:
        asset = assetSet.getMbo(0)
        criticality = asset.getString("CRITICALITY")
        if criticality == "HIGH":
            mbo.setValue("PRIORITY", 1)
```

### Pattern 3: Validation
```python
# Validate work order can be approved
status = mbo.getString("STATUS")
if status == "WAPPR":
    # Check required fields
    if not mbo.getString("ASSETNUM"):
        from psdi.util import MXApplicationException
        raise MXApplicationException("workorder", "assetrequired")
```

## Performance Considerations

### 1. Minimize Database Queries
```python
# BAD - Multiple queries
for i in range(100):
    assetSet = mx.getMboSet("ASSET", ui)
    assetSet.setWhere("assetnum='" + assetnum + "'")
    assetSet.reset()
    # Use assetSet
    assetSet.close()

# GOOD - Single query
assetSet = mx.getMboSet("ASSET", ui)
assetSet.setWhere("assetnum in ('ASSET1','ASSET2','ASSET3')")
assetSet.reset()
# Process all assets
assetSet.close()
```

### 2. Use Efficient WHERE Clauses
```python
# BAD - No WHERE clause, loads all records
woSet = mx.getMboSet("WORKORDER", ui)
woSet.reset()

# GOOD - Specific WHERE clause
woSet = mx.getMboSet("WORKORDER", ui)
woSet.setWhere("status='WAPPR' and siteid='BEDFORD'")
woSet.reset()
```

### 3. Limit Result Sets
```python
# Set maximum rows
mboSet.setWhere("status='WAPPR'")
mboSet.setMaxRows(100)
mboSet.reset()
```

## Security Considerations

### 1. SQL Injection Prevention
```python
# VULNERABLE
assetnum = mbo.getString("ASSETNUM")
mboSet.setWhere("assetnum='" + assetnum + "'")

# SECURE
assetnum = mbo.getString("ASSETNUM")
if assetnum:
    escaped = assetnum.replace("'", "''")
    mboSet.setWhere("assetnum='" + escaped + "'")
```

### 2. Access Control
```python
# Check user has permission
from psdi.server import MXServer

mx = MXServer.getMXServer()
ui = mx.getSystemUserInfo()

if not ui.hasApplicationAccess("WOTRACK"):
    from psdi.util import MXApplicationException
    raise MXApplicationException("system", "noaccess")
```

## References

- Source: Maximo Automation Scripts Quick Reference (Pages 1-15)
- Source: Scripting with Maximo Guide (Pages 1-50)
- Related: [Security Best Practices](security-best-practices.md)
- Related: [Performance Optimization](performance-optimization.md)