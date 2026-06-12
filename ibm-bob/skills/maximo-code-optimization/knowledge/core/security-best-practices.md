# Maximo Scripting Security Best Practices

## Overview

Security is paramount in Maximo automation scripts. This document covers critical security vulnerabilities and how to prevent them.

## Critical Security Issues

### 1. SQL Injection Vulnerabilities

SQL injection is the **#1 security risk** in Maximo scripts. It occurs when user input is directly concatenated into SQL WHERE clauses.

#### Vulnerable Pattern
```python
# CRITICAL VULNERABILITY - DO NOT USE
assetnum = mbo.getString("ASSETNUM")
assetSet = mbo.getMboSet("ASSET")
assetSet.setWhere("assetnum='" + assetnum + "'")
assetSet.reset()
```

**Attack Example**:
If `assetnum` contains `' OR '1'='1`, the WHERE clause becomes:
```sql
assetnum='' OR '1'='1'
```
This returns ALL assets, bypassing security.

#### Secure Pattern
```python
# SECURE - Input sanitization
assetnum = mbo.getString("ASSETNUM")
if assetnum:
    # Escape single quotes by doubling them
    escaped_assetnum = assetnum.replace("'", "''")
    assetSet = mbo.getMboSet("ASSET")
    assetSet.setWhere("assetnum='" + escaped_assetnum + "'")
    assetSet.reset()
```

#### Best Practice: Use Parameterized Queries
```python
# BEST - Use SqlFormat for parameterized queries
from psdi.mbo import SqlFormat

assetnum = mbo.getString("ASSETNUM")
if assetnum:
    sqlFormat = SqlFormat("assetnum = :1")
    sqlFormat.setObject(1, "ASSET", "ASSETNUM", assetnum)
    assetSet = mbo.getMboSet("ASSET")
    assetSet.setWhere(sqlFormat.format())
    assetSet.reset()
```

### 2. Input Validation

Always validate user input before processing.

#### Validation Checklist
```python
# Check for null/empty
value = mbo.getString("FIELDNAME")
if not value or not value.strip():
    from psdi.util import MXApplicationException
    raise MXApplicationException("system", "requiredfield", ["FIELDNAME"])

# Check data type
try:
    priority = int(mbo.getString("PRIORITY"))
    if priority < 1 or priority > 5:
        raise MXApplicationException("system", "invalidvalue", ["PRIORITY"])
except ValueError:
    raise MXApplicationException("system", "invalidvalue", ["PRIORITY"])

# Check length
description = mbo.getString("DESCRIPTION")
if len(description) > 100:
    raise MXApplicationException("system", "toolong", ["DESCRIPTION", "100"])

# Check format (e.g., email)
import re
email = mbo.getString("EMAIL")
if email and not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
    raise MXApplicationException("system", "invalidemail")
```

### 3. Access Control

Verify user permissions before performing sensitive operations.

```python
from psdi.server import MXServer

mx = MXServer.getMXServer()
ui = mx.getSystemUserInfo()

# Check application access
if not ui.hasApplicationAccess("WOTRACK"):
    from psdi.util import MXApplicationException
    raise MXApplicationException("system", "noaccess", ["WOTRACK"])

# Check security group
userGroups = ui.getUserGroups()
if "ADMINGROUP" not in userGroups:
    raise MXApplicationException("system", "insufficientprivileges")

# Check site access
siteid = mbo.getString("SITEID")
if not ui.hasSiteAccess(siteid):
    raise MXApplicationException("system", "nositeaccess", [siteid])
```

### 4. Sensitive Data Protection

Protect sensitive information in scripts.

```python
# DO NOT log sensitive data
logger.debug("Processing user: " + username)  # OK
logger.debug("Password: " + password)  # NEVER DO THIS

# Mask sensitive fields
def maskCreditCard(cardNumber):
    if cardNumber and len(cardNumber) > 4:
        return "****" + cardNumber[-4:]
    return "****"

# Use secure storage for credentials
# Never hardcode passwords or API keys in scripts
# Use Maximo's encryption services or external key management
```

### 5. Error Message Information Disclosure

Avoid exposing system details in error messages.

```python
# BAD - Exposes internal details
try:
    mboSet = mx.getMboSet("WORKORDER", ui)
except Exception as e:
    raise Exception("Database error: " + str(e))  # Exposes DB structure

# GOOD - Generic error message
try:
    mboSet = mx.getMboSet("WORKORDER", ui)
except Exception as e:
    logger.error("Error accessing work orders: " + str(e))
    from psdi.util import MXApplicationException
    raise MXApplicationException("system", "operationfailed")
```

## Common Vulnerability Patterns

### Pattern 1: Dynamic WHERE Clause Construction

**Vulnerable**:
```python
status = mbo.getString("STATUS")
siteid = mbo.getString("SITEID")
whereClause = "status='" + status + "' and siteid='" + siteid + "'"
mboSet.setWhere(whereClause)
```

**Secure**:
```python
status = mbo.getString("STATUS")
siteid = mbo.getString("SITEID")

if status and siteid:
    escaped_status = status.replace("'", "''")
    escaped_siteid = siteid.replace("'", "''")
    whereClause = "status='" + escaped_status + "' and siteid='" + escaped_siteid + "'"
    mboSet.setWhere(whereClause)
```

### Pattern 2: User Input in Field Names

**Vulnerable**:
```python
# NEVER allow user input to determine field names
fieldName = mbo.getString("USERFIELDNAME")
value = mbo.getString(fieldName)  # DANGEROUS
```

**Secure**:
```python
# Use whitelist of allowed fields
ALLOWED_FIELDS = ["ASSETNUM", "LOCATION", "DESCRIPTION"]
fieldName = mbo.getString("USERFIELDNAME")

if fieldName in ALLOWED_FIELDS:
    value = mbo.getString(fieldName)
else:
    raise MXApplicationException("system", "invalidfield")
```

### Pattern 3: Unvalidated Numeric Input

**Vulnerable**:
```python
# Direct conversion without validation
priority = int(mbo.getString("PRIORITY"))
mbo.setValue("WOPRIORITY", priority)
```

**Secure**:
```python
try:
    priority = int(mbo.getString("PRIORITY"))
    if 1 <= priority <= 5:
        mbo.setValue("WOPRIORITY", priority)
    else:
        raise MXApplicationException("system", "invalidrange", ["PRIORITY", "1", "5"])
except ValueError:
    raise MXApplicationException("system", "invalidnumber", ["PRIORITY"])
```

## Security Checklist

Use this checklist when reviewing scripts:

### Input Validation
- [ ] All user inputs are validated before use
- [ ] Null/empty checks are performed
- [ ] Data types are validated
- [ ] Value ranges are checked
- [ ] String lengths are validated
- [ ] Format validation (email, phone, etc.) is applied

### SQL Injection Prevention
- [ ] No direct string concatenation in WHERE clauses
- [ ] All user inputs in WHERE clauses are escaped
- [ ] SqlFormat or parameterized queries are used where possible
- [ ] Field names are not derived from user input

### Access Control
- [ ] User permissions are checked before sensitive operations
- [ ] Application access is verified
- [ ] Site access is validated
- [ ] Security group membership is checked where needed

### Data Protection
- [ ] Sensitive data is not logged
- [ ] Passwords/credentials are not hardcoded
- [ ] Error messages don't expose system details
- [ ] Sensitive fields are masked in logs

### Error Handling
- [ ] All exceptions are caught and logged
- [ ] Generic error messages are shown to users
- [ ] Detailed errors are logged for administrators
- [ ] No stack traces are exposed to end users

## Secure Coding Examples

### Example 1: Secure Asset Lookup
```python
from psdi.util.logging import MXLoggerFactory
from psdi.util import MXApplicationException

logger = MXLoggerFactory.getLogger("maximo.script.AssetLookup")

assetnum = mbo.getString("ASSETNUM")

# Validate input
if not assetnum or not assetnum.strip():
    raise MXApplicationException("asset", "assetrequired")

# Check length
if len(assetnum) > 12:
    raise MXApplicationException("asset", "assetnumtoolong")

# Sanitize input
escaped_assetnum = assetnum.replace("'", "''")

assetSet = None
try:
    from psdi.server import MXServer
    mx = MXServer.getMXServer()
    ui = mx.getSystemUserInfo()
    
    assetSet = mx.getMboSet("ASSET", ui)
    assetSet.setWhere("assetnum='" + escaped_assetnum + "'")
    assetSet.reset()
    
    if assetSet.count() == 0:
        raise MXApplicationException("asset", "notfound", [assetnum])
    
    asset = assetSet.getMbo(0)
    location = asset.getString("LOCATION")
    mbo.setValue("LOCATION", location)
    
except MXApplicationException as e:
    raise e
except Exception as e:
    logger.error("Error in asset lookup: " + str(e))
    raise MXApplicationException("system", "operationfailed")
finally:
    if assetSet is not None:
        assetSet.close()
```

### Example 2: Secure Status Update with Access Control
```python
from psdi.util.logging import MXLoggerFactory
from psdi.util import MXApplicationException
from psdi.server import MXServer

logger = MXLoggerFactory.getLogger("maximo.script.StatusUpdate")

# Get user context
mx = MXServer.getMXServer()
ui = mx.getSystemUserInfo()

# Check permissions
if not ui.hasApplicationAccess("WOTRACK"):
    logger.warn("User " + ui.getUserName() + " attempted unauthorized status update")
    raise MXApplicationException("system", "noaccess", ["WOTRACK"])

# Validate new status
newStatus = mbo.getString("NEWSTATUS")
VALID_STATUSES = ["WAPPR", "APPR", "INPRG", "COMP", "CLOSE"]

if newStatus not in VALID_STATUSES:
    raise MXApplicationException("workorder", "invalidstatus", [newStatus])

# Check business rules
currentStatus = mbo.getString("STATUS")
if currentStatus == "CLOSE" and newStatus != "CLOSE":
    raise MXApplicationException("workorder", "cannotreopenclose")

# Update status
try:
    mbo.setValue("STATUS", newStatus)
    mbo.setValue("STATUSDATE", mx.getDate())
    mbo.setValue("CHANGEUSER", ui.getUserName())
    logger.info("Status updated to " + newStatus + " by " + ui.getUserName())
except Exception as e:
    logger.error("Error updating status: " + str(e))
    raise MXApplicationException("system", "operationfailed")
```

### Example 3: Secure Batch Processing
```python
from psdi.util.logging import MXLoggerFactory
from psdi.server import MXServer

logger = MXLoggerFactory.getLogger("maximo.script.BatchProcess")

mx = MXServer.getMXServer()
ui = mx.getSystemUserInfo()

# Check permissions
if not ui.hasApplicationAccess("WOTRACK"):
    raise MXApplicationException("system", "noaccess", ["WOTRACK"])

# Validate input parameters
siteid = mbo.getString("SITEID")
if not siteid:
    raise MXApplicationException("system", "requiredfield", ["SITEID"])

# Verify site access
if not ui.hasSiteAccess(siteid):
    raise MXApplicationException("system", "nositeaccess", [siteid])

# Sanitize input
escaped_siteid = siteid.replace("'", "''")

woSet = None
try:
    woSet = mx.getMboSet("WORKORDER", ui)
    woSet.setWhere("status='WAPPR' and siteid='" + escaped_siteid + "'")
    woSet.reset()
    
    count = woSet.count()
    logger.info("Processing " + str(count) + " work orders for site " + siteid)
    
    for i in range(count):
        wo = woSet.getMbo(i)
        try:
            wo.setValue("STATUS", "APPR")
            wo.setValue("STATUSDATE", mx.getDate())
        except Exception as e:
            logger.error("Error processing WO " + wo.getString("WONUM") + ": " + str(e))
            # Continue processing other records
    
    woSet.save()
    logger.info("Batch processing completed for site " + siteid)
    
except Exception as e:
    logger.error("Error in batch processing: " + str(e))
    raise MXApplicationException("system", "operationfailed")
finally:
    if woSet is not None:
        woSet.close()
```

## Security Testing

### Test Cases for SQL Injection
Test your scripts with these malicious inputs:

1. `' OR '1'='1`
2. `'; DROP TABLE WORKORDER; --`
3. `' UNION SELECT * FROM MAXUSER --`
4. `admin'--`
5. `' OR 1=1 --`

**Expected Result**: All should be safely escaped or rejected.

### Test Cases for Input Validation
1. Empty strings
2. Null values
3. Very long strings (>1000 characters)
4. Special characters: `<>'"&;`
5. Unicode characters
6. Numeric overflow values

## References

- Source: Scripting Best Practices for Performance (Pages 8-12)
- Source: Maximo Security Guide
- Related: [Maximo Scripting Fundamentals](maximo-scripting-fundamentals.md)
- Related: [Common Vulnerabilities](../troubleshooting/common-vulnerabilities.md)