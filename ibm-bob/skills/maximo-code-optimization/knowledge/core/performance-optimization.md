# Maximo Scripting Performance Optimization

## Overview

Performance is critical in Maximo automation scripts, especially in high-volume environments. This document covers performance best practices and optimization techniques.

## Performance Principles

### 1. Minimize Database Queries
Database operations are the primary performance bottleneck in Maximo scripts.

#### Anti-Pattern: Multiple Queries in Loop
```python
# BAD - Creates 100 database queries
for i in range(100):
    assetSet = mx.getMboSet("ASSET", ui)
    assetSet.setWhere("assetnum='" + assetList[i] + "'")
    assetSet.reset()
    if assetSet.count() > 0:
        asset = assetSet.getMbo(0)
        # Process asset
    assetSet.close()
```

#### Optimized: Single Query with IN Clause
```python
# GOOD - Single database query
assetList = ["ASSET1", "ASSET2", "ASSET3"]
inClause = "'" + "','".join(assetList) + "'"

assetSet = mx.getMboSet("ASSET", ui)
assetSet.setWhere("assetnum in (" + inClause + ")")
assetSet.reset()

for i in range(assetSet.count()):
    asset = assetSet.getMbo(i)
    # Process asset

assetSet.close()
```

### 2. Use Efficient WHERE Clauses

#### Inefficient WHERE Clause
```python
# BAD - No WHERE clause, loads ALL work orders
woSet = mx.getMboSet("WORKORDER", ui)
woSet.reset()

for i in range(woSet.count()):
    wo = woSet.getMbo(i)
    if wo.getString("STATUS") == "WAPPR":
        # Process work order
```

#### Efficient WHERE Clause
```python
# GOOD - Filters at database level
woSet = mx.getMboSet("WORKORDER", ui)
woSet.setWhere("status='WAPPR' and siteid='BEDFORD'")
woSet.reset()

for i in range(woSet.count()):
    wo = woSet.getMbo(i)
    # Process work order
```

### 3. Limit Result Sets

Always limit the number of records retrieved when possible.

```python
# Set maximum rows to prevent loading too many records
woSet = mx.getMboSet("WORKORDER", ui)
woSet.setWhere("status='WAPPR'")
woSet.setMaxRows(100)  # Limit to 100 records
woSet.reset()
```

### 4. Use Relationships Instead of New MboSets

Leverage existing relationships rather than creating new MboSets.

#### Inefficient: New MboSet
```python
# BAD - Creates new MboSet
assetnum = mbo.getString("ASSETNUM")
assetSet = mx.getMboSet("ASSET", ui)
assetSet.setWhere("assetnum='" + assetnum + "'")
assetSet.reset()
if assetSet.count() > 0:
    asset = assetSet.getMbo(0)
    location = asset.getString("LOCATION")
assetSet.close()
```

#### Efficient: Use Relationship
```python
# GOOD - Uses existing relationship
assetSet = mbo.getMboSet("ASSET")  # Uses WORKORDER->ASSET relationship
if assetSet.count() > 0:
    asset = assetSet.getMbo(0)
    location = asset.getString("LOCATION")
# No need to close - managed by parent MBO
```

### 5. Avoid Unnecessary Field Access

Accessing fields triggers lazy loading and can cause performance issues.

```python
# BAD - Accesses field multiple times
for i in range(woSet.count()):
    wo = woSet.getMbo(i)
    if wo.getString("ASSETNUM"):
        logger.info("Asset: " + wo.getString("ASSETNUM"))
        mbo.setValue("PARENTASSET", wo.getString("ASSETNUM"))

# GOOD - Cache field value
for i in range(woSet.count()):
    wo = woSet.getMbo(i)
    assetnum = wo.getString("ASSETNUM")
    if assetnum:
        logger.info("Asset: " + assetnum)
        mbo.setValue("PARENTASSET", assetnum)
```

## Resource Management

### 1. Always Close MboSets

Unclosed MboSets cause memory leaks and database connection exhaustion.

#### Pattern: Try-Finally Block
```python
mboSet = None
try:
    mboSet = mx.getMboSet("WORKORDER", ui)
    mboSet.setWhere("status='WAPPR'")
    mboSet.reset()
    
    # Process records
    for i in range(mboSet.count()):
        wo = mboSet.getMbo(i)
        # Process work order
        
finally:
    if mboSet is not None:
        mboSet.close()
```

### 2. Close MboSets in Correct Order

When working with multiple MboSets, close them in reverse order of creation.

```python
parentSet = None
childSet = None

try:
    parentSet = mx.getMboSet("WORKORDER", ui)
    parentSet.setWhere("status='WAPPR'")
    parentSet.reset()
    
    childSet = mx.getMboSet("WOACTIVITY", ui)
    childSet.setWhere("parent in (select wonum from workorder where status='WAPPR')")
    childSet.reset()
    
    # Process records
    
finally:
    # Close in reverse order
    if childSet is not None:
        childSet.close()
    if parentSet is not None:
        parentSet.close()
```

### 3. Reuse MboSets When Possible

```python
# BAD - Creates new MboSet for each lookup
for assetnum in assetList:
    assetSet = mx.getMboSet("ASSET", ui)
    assetSet.setWhere("assetnum='" + assetnum + "'")
    assetSet.reset()
    # Process
    assetSet.close()

# GOOD - Reuse single MboSet
assetSet = mx.getMboSet("ASSET", ui)
try:
    for assetnum in assetList:
        assetSet.setWhere("assetnum='" + assetnum + "'")
        assetSet.reset()
        # Process
finally:
    assetSet.close()
```

## Loop Optimization

### 1. Minimize Work Inside Loops

Move invariant operations outside loops.

```python
# BAD - Gets date in every iteration
for i in range(woSet.count()):
    wo = woSet.getMbo(i)
    wo.setValue("STATUSDATE", mx.getDate())

# GOOD - Get date once
currentDate = mx.getDate()
for i in range(woSet.count()):
    wo = woSet.getMbo(i)
    wo.setValue("STATUSDATE", currentDate)
```

### 2. Break Early When Possible

```python
# BAD - Continues checking after found
found = False
for i in range(woSet.count()):
    wo = woSet.getMbo(i)
    if wo.getString("WONUM") == targetWO:
        found = True
        # Process

# GOOD - Breaks when found
found = False
for i in range(woSet.count()):
    wo = woSet.getMbo(i)
    if wo.getString("WONUM") == targetWO:
        found = True
        # Process
        break
```

### 3. Use Range Instead of While

```python
# BAD - While loop with manual counter
i = 0
while i < woSet.count():
    wo = woSet.getMbo(i)
    # Process
    i += 1

# GOOD - For loop with range
for i in range(woSet.count()):
    wo = woSet.getMbo(i)
    # Process
```

## String Operations

### 1. Use String Concatenation Efficiently

```python
# BAD - Multiple string concatenations
message = ""
for i in range(100):
    message = message + "Item " + str(i) + ", "

# GOOD - Use list and join
items = []
for i in range(100):
    items.append("Item " + str(i))
message = ", ".join(items)
```

### 2. Avoid Repeated String Operations

```python
# BAD - Repeated upper() calls
for i in range(woSet.count()):
    wo = woSet.getMbo(i)
    if wo.getString("STATUS").upper() == "WAPPR":
        logger.info(wo.getString("STATUS").upper())

# GOOD - Cache result
for i in range(woSet.count()):
    wo = woSet.getMbo(i)
    status = wo.getString("STATUS").upper()
    if status == "WAPPR":
        logger.info(status)
```

## Conditional Logic Optimization

### 1. Order Conditions by Likelihood

```python
# BAD - Checks rare condition first
if wo.getString("STATUS") == "CANCELLED":
    # Rare case
elif wo.getString("STATUS") == "WAPPR":
    # Common case

# GOOD - Checks common condition first
if wo.getString("STATUS") == "WAPPR":
    # Common case
elif wo.getString("STATUS") == "CANCELLED":
    # Rare case
```

### 2. Use Short-Circuit Evaluation

```python
# BAD - Always evaluates both conditions
if isValid(wo) and isApproved(wo):
    # Process

# GOOD - Short-circuits if first is false
if isValid(wo) and isApproved(wo):
    # Process (isApproved not called if isValid is false)
```

### 3. Avoid Redundant Checks

```python
# BAD - Redundant null check
assetnum = mbo.getString("ASSETNUM")
if assetnum is not None:
    if assetnum:
        # Process

# GOOD - Single check
assetnum = mbo.getString("ASSETNUM")
if assetnum:
    # Process (empty string is falsy)
```

## Batch Processing

### 1. Batch Database Operations

```python
# BAD - Saves after each update
for i in range(woSet.count()):
    wo = woSet.getMbo(i)
    wo.setValue("STATUS", "APPR")
    woSet.save()  # Saves after each record

# GOOD - Batch save
for i in range(woSet.count()):
    wo = woSet.getMbo(i)
    wo.setValue("STATUS", "APPR")
woSet.save()  # Single save for all records
```

### 2. Process in Chunks

For very large datasets, process in chunks to avoid memory issues.

```python
CHUNK_SIZE = 100
offset = 0

while True:
    woSet = mx.getMboSet("WORKORDER", ui)
    woSet.setWhere("status='WAPPR'")
    woSet.setMaxRows(CHUNK_SIZE)
    woSet.setOffset(offset)
    woSet.reset()
    
    if woSet.count() == 0:
        woSet.close()
        break
    
    try:
        for i in range(woSet.count()):
            wo = woSet.getMbo(i)
            # Process work order
        
        woSet.save()
        offset += CHUNK_SIZE
        
    finally:
        woSet.close()
```

## Caching Strategies

### 1. Cache Lookup Values

```python
# BAD - Looks up domain value repeatedly
for i in range(woSet.count()):
    wo = woSet.getMbo(i)
    priority = wo.getString("PRIORITY")
    priorityDesc = mx.lookup("WOPRIORITY").getDescription(priority)

# GOOD - Cache lookup
priorityLookup = mx.lookup("WOPRIORITY")
for i in range(woSet.count()):
    wo = woSet.getMbo(i)
    priority = wo.getString("PRIORITY")
    priorityDesc = priorityLookup.getDescription(priority)
```

### 2. Cache Frequently Used Objects

```python
# Cache MXServer and UserInfo
mx = MXServer.getMXServer()
ui = mx.getSystemUserInfo()
currentDate = mx.getDate()

# Use cached objects
for i in range(woSet.count()):
    wo = woSet.getMbo(i)
    wo.setValue("STATUSDATE", currentDate)
    wo.setValue("CHANGEUSER", ui.getUserName())
```

## Performance Monitoring

### 1. Add Performance Logging

```python
from psdi.util.logging import MXLoggerFactory
import time

logger = MXLoggerFactory.getLogger("maximo.script.Performance")

startTime = time.time()

# Script operations

endTime = time.time()
duration = endTime - startTime
logger.info("Script completed in " + str(duration) + " seconds")
```

### 2. Log Record Counts

```python
logger.info("Processing " + str(woSet.count()) + " work orders")

processed = 0
errors = 0

for i in range(woSet.count()):
    try:
        # Process record
        processed += 1
    except Exception as e:
        errors += 1
        logger.error("Error processing record: " + str(e))

logger.info("Processed: " + str(processed) + ", Errors: " + str(errors))
```

## Performance Anti-Patterns

### 1. N+1 Query Problem

```python
# BAD - N+1 queries (1 for work orders + N for assets)
woSet = mx.getMboSet("WORKORDER", ui)
woSet.setWhere("status='WAPPR'")
woSet.reset()

for i in range(woSet.count()):
    wo = woSet.getMbo(i)
    assetnum = wo.getString("ASSETNUM")
    
    # Separate query for each asset
    assetSet = mx.getMboSet("ASSET", ui)
    assetSet.setWhere("assetnum='" + assetnum + "'")
    assetSet.reset()
    # Process asset
    assetSet.close()

# GOOD - Use relationship
woSet = mx.getMboSet("WORKORDER", ui)
woSet.setWhere("status='WAPPR'")
woSet.reset()

for i in range(woSet.count()):
    wo = woSet.getMbo(i)
    assetSet = wo.getMboSet("ASSET")  # Uses relationship
    if assetSet.count() > 0:
        asset = assetSet.getMbo(0)
        # Process asset
```

### 2. Loading Unnecessary Data

```python
# BAD - Loads all fields for all records
woSet = mx.getMboSet("WORKORDER", ui)
woSet.reset()  # No WHERE clause

# GOOD - Specific WHERE clause and field selection
woSet = mx.getMboSet("WORKORDER", ui)
woSet.setWhere("status='WAPPR' and siteid='BEDFORD'")
woSet.setMaxRows(100)
woSet.reset()
```

### 3. Inefficient Existence Checks

```python
# BAD - Loads all records just to check existence
assetSet = mx.getMboSet("ASSET", ui)
assetSet.setWhere("assetnum='" + assetnum + "'")
assetSet.reset()
exists = assetSet.count() > 0
assetSet.close()

# GOOD - Use isEmpty()
assetSet = mx.getMboSet("ASSET", ui)
assetSet.setWhere("assetnum='" + assetnum + "'")
exists = not assetSet.isEmpty()
assetSet.close()
```

## Performance Checklist

Use this checklist when optimizing scripts:

### Database Operations
- [ ] WHERE clauses are specific and indexed
- [ ] Result sets are limited with setMaxRows()
- [ ] Relationships are used instead of new MboSets
- [ ] Batch operations are used instead of individual saves
- [ ] IN clauses are used instead of multiple queries

### Resource Management
- [ ] All MboSets are closed in finally blocks
- [ ] MboSets are closed in reverse order of creation
- [ ] MboSets are reused when possible
- [ ] No MboSets are created inside loops unnecessarily

### Loop Optimization
- [ ] Invariant operations are moved outside loops
- [ ] Early breaks are used when possible
- [ ] Field values are cached instead of repeated access
- [ ] String operations are minimized

### Caching
- [ ] Lookup values are cached
- [ ] MXServer and UserInfo are cached
- [ ] Frequently used objects are cached
- [ ] Date/time values are cached

### Monitoring
- [ ] Performance logging is added
- [ ] Record counts are logged
- [ ] Error counts are tracked
- [ ] Execution time is measured

## Performance Testing

### Test with Realistic Data Volumes
```python
# Test with different data volumes
TEST_VOLUMES = [10, 100, 1000, 10000]

for volume in TEST_VOLUMES:
    startTime = time.time()
    
    woSet = mx.getMboSet("WORKORDER", ui)
    woSet.setWhere("status='WAPPR'")
    woSet.setMaxRows(volume)
    woSet.reset()
    
    # Process records
    
    endTime = time.time()
    logger.info("Volume: " + str(volume) + ", Time: " + str(endTime - startTime))
    woSet.close()
```

### Measure Query Performance
```python
# Log query execution time
startTime = time.time()
woSet.setWhere("status='WAPPR' and siteid='BEDFORD'")
woSet.reset()
queryTime = time.time() - startTime
logger.info("Query time: " + str(queryTime) + " seconds")
```

## References

- Source: Scripting Best Practices for Performance (Pages 1-20)
- Source: Maximo Performance Tuning Guide
- Related: [Maximo Scripting Fundamentals](maximo-scripting-fundamentals.md)
- Related: [Resource Management](../procedures/resource-management.md)