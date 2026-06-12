# Maximo Scripting Quick Reference

## Common Patterns

### Secure WHERE Clause
```python
# Input sanitization
userInput = mbo.getString("FIELDNAME")
if userInput:
    escaped = userInput.replace("'", "''")
    mboSet.setWhere("field='" + escaped + "'")
```

### MboSet Lifecycle
```python
mboSet = None
try:
    mboSet = mx.getMboSet("OBJECT", ui)
    mboSet.setWhere("condition")
    mboSet.reset()
    # Use mboSet
finally:
    if mboSet is not None:
        mboSet.close()
```

### Error Handling
```python
from psdi.util.logging import MXLoggerFactory

logger = MXLoggerFactory.getLogger("maximo.script.NAME")

try:
    # operations
except Exception as e:
    logger.error("Error: " + str(e))
    raise
```

### Input Validation
```python
value = mbo.getString("FIELDNAME")
if not value or not value.strip():
    from psdi.util import MXApplicationException
    raise MXApplicationException("system", "requiredfield", ["FIELDNAME"])
```

### Access Control
```python
from psdi.server import MXServer

mx = MXServer.getMXServer()
ui = mx.getSystemUserInfo()

if not ui.hasApplicationAccess("APPNAME"):
    from psdi.util import MXApplicationException
    raise MXApplicationException("system", "noaccess")
```

## Common APIs

### MBO Methods
```python
# Get values
value = mbo.getString("FIELD")
value = mbo.getInt("FIELD")
value = mbo.getDouble("FIELD")
value = mbo.getDate("FIELD")
value = mbo.getBoolean("FIELD")

# Set values
mbo.setValue("FIELD", value)
mbo.setValueNull("FIELD")

# Field flags
from psdi.mbo import MboConstants
mbo.setFieldFlag("FIELD", MboConstants.READONLY, True)
mbo.setFieldFlag("FIELD", MboConstants.REQUIRED, True)

# Relationships
relatedSet = mbo.getMboSet("RELATIONSHIP")

# Status checks
isNew = mbo.toBeAdded()
isModified = mbo.toBeSaved()
isDeleted = mbo.toBeDeleted()
```

### MboSet Methods
```python
# Get MboSet
from psdi.server import MXServer
mx = MXServer.getMXServer()
ui = mx.getSystemUserInfo()
mboSet = mx.getMboSet("OBJECT", ui)

# Query
mboSet.setWhere("condition")
mboSet.setMaxRows(100)
mboSet.reset()

# Count and iterate
count = mboSet.count()
isEmpty = mboSet.isEmpty()

for i in range(mboSet.count()):
    mbo = mboSet.getMbo(i)
    # Process

# Add/Delete
newMbo = mboSet.add()
mbo.delete()

# Save and close
mboSet.save()
mboSet.close()
```

### MXServer Methods
```python
from psdi.server import MXServer

mx = MXServer.getMXServer()
ui = mx.getSystemUserInfo()
currentDate = mx.getDate()
mboSet = mx.getMboSet("OBJECT", ui)
lookup = mx.lookup("DOMAINID")
```

### Logging
```python
from psdi.util.logging import MXLoggerFactory

logger = MXLoggerFactory.getLogger("maximo.script.NAME")

logger.debug("Debug message")
logger.info("Info message")
logger.warn("Warning message")
logger.error("Error message")
logger.error("Error with exception", exception)
```

## Security Patterns

### SQL Injection Prevention
```python
# VULNERABLE
mboSet.setWhere("field='" + userInput + "'")

# SECURE
escaped = userInput.replace("'", "''")
mboSet.setWhere("field='" + escaped + "'")

# BEST
from psdi.mbo import SqlFormat
sqlFormat = SqlFormat("field = :1")
sqlFormat.setObject(1, "OBJECT", "FIELD", userInput)
mboSet.setWhere(sqlFormat.format())
```

### Input Validation Patterns
```python
# Null/Empty check
if not value or not value.strip():
    raise MXApplicationException("system", "requiredfield")

# Type validation
try:
    num = int(value)
except ValueError:
    raise MXApplicationException("system", "invalidnumber")

# Range validation
if not (1 <= num <= 100):
    raise MXApplicationException("system", "invalidrange")

# Length validation
if len(value) > 100:
    raise MXApplicationException("system", "toolong")

# Format validation (email)
import re
if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
    raise MXApplicationException("system", "invalidemail")
```

## Performance Patterns

### Efficient Queries
```python
# BAD - No WHERE clause
mboSet = mx.getMboSet("WORKORDER", ui)
mboSet.reset()

# GOOD - Specific WHERE clause
mboSet = mx.getMboSet("WORKORDER", ui)
mboSet.setWhere("status='WAPPR' and siteid='BEDFORD'")
mboSet.setMaxRows(100)
mboSet.reset()
```

### Use Relationships
```python
# BAD - New MboSet
assetnum = mbo.getString("ASSETNUM")
assetSet = mx.getMboSet("ASSET", ui)
assetSet.setWhere("assetnum='" + assetnum + "'")
assetSet.reset()
# Use asset
assetSet.close()

# GOOD - Use relationship
assetSet = mbo.getMboSet("ASSET")
if assetSet.count() > 0:
    asset = assetSet.getMbo(0)
    # Use asset
```

### Batch Operations
```python
# BAD - Save in loop
for i in range(mboSet.count()):
    mbo = mboSet.getMbo(i)
    mbo.setValue("FIELD", value)
    mboSet.save()

# GOOD - Batch save
for i in range(mboSet.count()):
    mbo = mboSet.getMbo(i)
    mbo.setValue("FIELD", value)
mboSet.save()
```

### Caching
```python
# Cache frequently used objects
mx = MXServer.getMXServer()
ui = mx.getSystemUserInfo()
currentDate = mx.getDate()
lookup = mx.lookup("DOMAIN")

# Use cached objects in loop
for i in range(mboSet.count()):
    mbo = mboSet.getMbo(i)
    mbo.setValue("DATE", currentDate)
    mbo.setValue("USER", ui.getUserName())
```

## Common Anti-Patterns

### ❌ SQL Injection
```python
# NEVER DO THIS
mboSet.setWhere("field='" + userInput + "'")
```

### ❌ Resource Leak
```python
# NEVER DO THIS
mboSet = mx.getMboSet("OBJECT", ui)
# ... use mboSet ...
# Missing close()
```

### ❌ Query in Loop
```python
# NEVER DO THIS
for item in items:
    mboSet = mx.getMboSet("OBJECT", ui)
    mboSet.setWhere("field='" + item + "'")
    mboSet.reset()
    # Use mboSet
    mboSet.close()
```

### ❌ Missing Error Handling
```python
# NEVER DO THIS
mboSet = mx.getMboSet("OBJECT", ui)
mboSet.reset()
# No try-catch
```

### ❌ No Input Validation
```python
# NEVER DO THIS
value = mbo.getString("FIELD")
# Use value without checking null/empty
```

## Severity Levels

### Critical
- SQL injection vulnerabilities
- Hardcoded credentials
- Exposed sensitive data
- Major security flaws

### High
- Resource leaks (unclosed MboSets)
- Missing error handling
- Access control issues
- Performance bottlenecks (queries in loops)

### Medium
- Missing input validation
- Inefficient queries
- Poor error messages
- Missing logging

### Low
- Code readability issues
- Missing comments
- Inconsistent naming
- Minor optimizations

## Common Exceptions

### MXApplicationException
```python
from psdi.util import MXApplicationException

# With message group and key
raise MXApplicationException("system", "requiredfield", ["FIELDNAME"])

# With custom message
raise MXApplicationException("custom", "custommessage")
```

### MXException
```python
from psdi.util import MXException

# General Maximo exception
raise MXException("system", "error")
```

## Field Flags

```python
from psdi.mbo import MboConstants

# Common flags
MboConstants.READONLY
MboConstants.REQUIRED
MboConstants.HIDDEN
MboConstants.NOVALIDATION
MboConstants.NOACCESSCHECK

# Usage
mbo.setFieldFlag("FIELD", MboConstants.READONLY, True)
mbo.setFieldFlag("FIELD", MboConstants.REQUIRED, False)
```

## Date/Time Operations

```python
from psdi.server import MXServer
from java.util import Date, Calendar

# Get current date
mx = MXServer.getMXServer()
currentDate = mx.getDate()

# Date arithmetic
calendar = Calendar.getInstance()
calendar.setTime(currentDate)
calendar.add(Calendar.DAY_OF_MONTH, 7)  # Add 7 days
futureDate = calendar.getTime()

# Set date
mbo.setValue("DATEFIELD", currentDate)
```

## String Operations

```python
# Get string
value = mbo.getString("FIELD")

# Check null/empty
if value and value.strip():
    # Safe to use

# String methods
upper = value.upper()
lower = value.lower()
trimmed = value.strip()
replaced = value.replace("old", "new")

# String concatenation
result = "Value: " + str(value)

# String formatting
result = "Value: {0}, Count: {1}".format(value, count)
```

## Numeric Operations

```python
# Get numbers
intValue = mbo.getInt("FIELD")
doubleValue = mbo.getDouble("FIELD")

# Validation
try:
    num = int(mbo.getString("FIELD"))
    if 1 <= num <= 100:
        mbo.setValue("RESULT", num)
except ValueError:
    raise MXApplicationException("system", "invalidnumber")
```

## Boolean Operations

```python
# Get boolean
boolValue = mbo.getBoolean("FIELD")

# Set boolean
mbo.setValue("FIELD", True)
mbo.setValue("FIELD", False)

# Check conditions
if mbo.getBoolean("ACTIVE") and not mbo.getBoolean("DELETED"):
    # Process
```

## Lookup Operations

```python
from psdi.server import MXServer

mx = MXServer.getMXServer()

# Get lookup
lookup = mx.lookup("DOMAINID")

# Get description
description = lookup.getDescription(value)

# Get list
valueList = lookup.getList()
```

## User Context

```python
from psdi.server import MXServer

mx = MXServer.getMXServer()
ui = mx.getSystemUserInfo()

# User information
username = ui.getUserName()
personId = ui.getPersonId()
defaultSite = ui.getDefaultSite()

# Permissions
hasAccess = ui.hasApplicationAccess("APPNAME")
hasSiteAccess = ui.hasSiteAccess("SITEID")

# User groups
groups = ui.getUserGroups()
if "ADMINGROUP" in groups:
    # User is admin
```

## Transaction Management

```python
# Maximo handles transactions automatically
# Changes are committed when script completes successfully
# Changes are rolled back if exception is thrown

# Explicit save
mboSet.save()

# Explicit rollback (rare)
mboSet.rollback()
```

## Performance Metrics

### Query Optimization
- **Target**: < 100ms per query
- **Max Records**: Limit to 1000 with setMaxRows()
- **WHERE Clause**: Always use specific conditions

### Resource Management
- **MboSet Lifetime**: Close within 1 second
- **Max Open MboSets**: < 10 simultaneously
- **Memory**: < 100MB per script execution

### Execution Time
- **Object Scripts**: < 500ms
- **Attribute Scripts**: < 200ms
- **Action Scripts**: < 2 seconds
- **Escalation Scripts**: < 5 minutes

## Testing Checklist

### Security Testing
- [ ] Test with SQL injection patterns
- [ ] Test with null/empty inputs
- [ ] Test with invalid data types
- [ ] Test with unauthorized users
- [ ] Test with special characters

### Performance Testing
- [ ] Test with 10 records
- [ ] Test with 100 records
- [ ] Test with 1000 records
- [ ] Measure execution time
- [ ] Monitor resource usage

### Error Testing
- [ ] Test with missing required fields
- [ ] Test with invalid relationships
- [ ] Test with database errors
- [ ] Test with concurrent updates
- [ ] Verify error messages

## References

- [Maximo Scripting Fundamentals](../core/maximo-scripting-fundamentals.md)
- [Security Best Practices](../core/security-best-practices.md)
- [Performance Optimization](../core/performance-optimization.md)
- [Script Optimization Workflow](../procedures/script-optimization-workflow.md)