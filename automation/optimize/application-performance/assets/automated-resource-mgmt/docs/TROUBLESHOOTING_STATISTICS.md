# Troubleshooting: No Statistics Displayed

## Issue: "No detailed statistics available for this application"

If you see this message in the Application Statistics tab, it means the `/stats` API endpoint returned no data. Here's how to diagnose and fix it.

## Quick Diagnosis Steps

### Step 1: Check Browser Console
1. Open browser Developer Tools (F12)
2. Go to Console tab
3. Look for error messages when clicking "Load Statistics"
4. Look for log message: `Retrieved X statistics for app {uuid}`

### Step 2: Check Application Logs
Look in the terminal where the app is running for:
```
INFO: Retrieved X statistics for app {uuid}
```

If you see `Retrieved 0 statistics`, the API returned empty data.

### Step 3: Test API Directly

#### Test 1: Check if entity exists
```bash
curl -k -u username:password \
  https://your-turbonomic/api/v3/entities/{app_uuid}
```

**Expected**: JSON with entity details
**If fails**: Entity UUID is invalid

#### Test 2: Get all statistics
```bash
curl -k -u username:password \
  -X POST \
  https://your-turbonomic/api/v3/stats/{app_uuid}
```

**Expected**: JSON array with statistics
**If empty**: Entity has no statistics available

#### Test 3: Get specific statistics
```bash
curl -k -u username:password \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"statistics":[{"name":"CPU"},{"name":"Mem"}]}' \
  https://your-turbonomic/api/v3/stats/{app_uuid}
```

**Expected**: JSON with CPU and Mem statistics
**If empty**: These specific stats aren't available

## Common Causes and Solutions

### Cause 1: Application Type Doesn't Support Statistics

**Symptoms:**
- API returns empty array `[]`
- No error messages in logs
- Other applications work fine

**Explanation:**
Not all application types provide detailed statistics. For example:
- `BusinessApplication` entities may not have CPU/Memory stats
- Some application types only have ResponseTime/Transaction
- Custom application types may not be instrumented

**Solution:**
This is expected behavior. The application will show:
- ✅ Time-series charts (ResponseTime, Transaction) - if available
- ✅ Pending Actions count
- ℹ️ Info message about no detailed statistics

**Workaround:**
Try selecting a different application type:
- Look for `Application` entities (not `BusinessApplication`)
- Try `VirtualMachine` entities (they have full statistics)
- Check `Container` or `Pod` entities

### Cause 2: Turbonomic Version Doesn't Support /stats Endpoint

**Symptoms:**
- API returns 404 Not Found
- Error in console: `HTTPError: 404`
- Logs show: `Failed to get entity stats: 404`

**Explanation:**
The `/stats` endpoint was added in Turbonomic v7.x. Older versions don't support it.

**Solution:**
1. Check Turbonomic version:
   ```bash
   curl -k https://your-turbonomic/api/v3/about
   ```

2. If version < 7.0, the statistics feature won't work

**Workaround:**
- Upgrade Turbonomic to v7.x or later
- Or use only time-series charts (which use different endpoint)

### Cause 3: Insufficient Permissions

**Symptoms:**
- API returns 403 Forbidden
- Error in console: `HTTPError: 403`
- Logs show: `Failed to get entity stats: 403`

**Explanation:**
The user account doesn't have permission to view statistics.

**Solution:**
1. Check user role in Turbonomic
2. Ensure user has at least "Observer" role
3. Try with administrator account to confirm

### Cause 4: Entity Has No Data Yet

**Symptoms:**
- API returns empty array `[]`
- Entity was recently discovered
- Other entities of same type work

**Explanation:**
Newly discovered entities may not have statistics yet. Turbonomic needs time to collect data.

**Solution:**
- Wait 5-10 minutes for data collection
- Refresh the page and try again
- Check if entity is in "ACTIVE" state

### Cause 5: API Response Format Changed

**Symptoms:**
- No error messages
- Logs show: `Retrieved 0 statistics`
- API returns data but it's not parsed correctly

**Explanation:**
The `_to_list()` method might not be handling the response format.

**Solution:**
1. Check raw API response:
   ```python
   # In turbo_client.py, add debug logging
   result = self._post(f"/stats/{entity_uuid}", payload=payload)
   log.debug(f"Raw stats response: {result}")
   ```

2. Check if response has unexpected wrapper:
   ```json
   {
     "someWrapper": {
       "statistics": [...]
     }
   }
   ```

3. Update `_to_list()` method to handle new format

## Debugging Code

### Add Debug Logging to turbo_client.py

```python
def get_entity_stats(self, entity_uuid: str, stat_names: Optional[List[str]] = None) -> List[Dict]:
    try:
        payload: Dict[str, Any] = {}
        if stat_names:
            payload["statistics"] = [{"name": name} for name in stat_names]
        
        # POST request
        result = self._post(f"/stats/{entity_uuid}", payload=payload if payload else None)
        
        # DEBUG: Log raw response
        log.debug(f"Raw stats response type: {type(result)}")
        log.debug(f"Raw stats response: {result}")
        
        # Normalize response
        snapshots = self._to_list(result, f"stats_{entity_uuid}")
        log.debug(f"Snapshots after _to_list: {len(snapshots)} items")
        
        if not snapshots:
            log.warning(f"No statistics snapshots for {entity_uuid}")
            return []
        
        # Extract statistics
        snapshot = snapshots[0] if isinstance(snapshots, list) else snapshots
        log.debug(f"First snapshot type: {type(snapshot)}")
        log.debug(f"First snapshot keys: {snapshot.keys() if isinstance(snapshot, dict) else 'not a dict'}")
        
        statistics = snapshot.get("statistics", []) if isinstance(snapshot, dict) else []
        log.debug(f"Statistics count: {len(statistics)}")
        
        return statistics
        
    except Exception as exc:
        log.error(f"get_entity_stats failed for {entity_uuid}: {exc}")
        import traceback
        log.error(traceback.format_exc())
        return []
```

### Add Debug Logging to app.py

```python
# In load_app_statistics callback
try:
    current_stats = client.get_entity_stats(app_uuid)
    log.info(f"Retrieved {len(current_stats)} statistics for app {app_uuid}")
    
    # DEBUG: Log first few statistics
    if current_stats:
        log.debug(f"First stat: {current_stats[0]}")
        log.debug(f"Stat names: {[s.get('name') for s in current_stats[:5]]}")
    else:
        log.warning(f"No statistics returned for app {app_uuid}")
        
except Exception as exc:
    log.error(f"Failed to get entity stats: {exc}")
    import traceback
    log.error(traceback.format_exc())
    current_stats = []
```

## Testing with Different Entity Types

### Test with VirtualMachine (Most Reliable)

VirtualMachines typically have the most complete statistics:

```python
# In Application Statistics tab, manually test with a VM UUID
vm_uuid = "your-vm-uuid-here"
stats = client.get_entity_stats(vm_uuid)
print(f"VM has {len(stats)} statistics")
for stat in stats[:10]:
    print(f"  - {stat.get('name')}: {stat.get('value')} {stat.get('units')}")
```

Expected output:
```
VM has 25 statistics
  - CPU: 1234.5 MHz
  - Mem: 8388608 KB
  - VMem: 4194304 KB
  - Storage: 50.0 GB
  - NetThroughput: 1024.0 Kb/s
  ...
```

### Test with BusinessApplication

BusinessApplications may have limited statistics:

```python
app_uuid = "your-app-uuid-here"
stats = client.get_entity_stats(app_uuid)
print(f"App has {len(stats)} statistics")
```

Expected output (may be empty):
```
App has 0 statistics
```

Or:
```
App has 5 statistics
  - ResponseTime: 123.4 msec
  - Transaction: 45.6 TPS
  - VMem: 1048576 KB
  - VCPU: 2.0
  - priceIndex: 1.01
```

## Verification Checklist

- [ ] Browser console shows no errors
- [ ] Application logs show `Retrieved X statistics`
- [ ] Direct API call returns data
- [ ] Entity UUID is correct
- [ ] Turbonomic version >= 7.0
- [ ] User has sufficient permissions
- [ ] Entity is in ACTIVE state
- [ ] Entity type supports statistics
- [ ] Waited for data collection (if new entity)

## Expected Behavior

### When Statistics Are Available
You should see:
1. **Time-series charts** for ResponseTime and Transaction
2. **Metric cards** showing latest values
3. **📊 Current Resource Statistics** section with:
   - CPU & PROCESSOR STATISTICS (if available)
   - MEMORY STATISTICS (if available)
   - STORAGE & I/O STATISTICS (if available)
   - NETWORK STATISTICS (if available)
   - OTHER STATISTICS (if available)

### When Statistics Are NOT Available
You should see:
1. **Time-series charts** for ResponseTime and Transaction (if available)
2. **Metric cards** showing latest values
3. **Info message**: "No detailed statistics available for this application"
   - With explanation of possible causes
   - This is normal for some application types

## Still Not Working?

If you've tried all the above and statistics still don't show:

1. **Check Turbonomic API documentation** for your version
2. **Contact Turbonomic support** to verify /stats endpoint availability
3. **Try with a known-good entity** (like a VirtualMachine)
4. **Check Turbonomic UI** - can you see statistics there?
5. **Review Turbonomic logs** for any backend errors

## Alternative: Use Time-Series Endpoint

If `/stats` doesn't work, you can still get historical data using the time-series endpoint (which is already working):

```python
# This endpoint works for ResponseTime and Transaction
commodities = ["ResponseTime", "Transaction", "CPU", "Mem"]
snapshots = client.get_entity_time_series(app_uuid, commodities, start_ms, end_ms)
```

This provides historical data but not the current snapshot with capacity information.

---

*Last Updated: 2026-04-21*
*Version: 2.6.0*