# Comprehensive Statistics API Integration Guide

## Overview
The Application Statistics tab now includes comprehensive resource statistics using the Turbonomic `/stats` API endpoint. This provides detailed current metrics for CPU, Memory, Storage, Network, and other resources.

## What's New (Version 2.6.0)

### Enhanced Application Statistics Tab
After loading time-series charts for ResponseTime and Transaction, the dashboard now displays:

1. **Current Resource Statistics Section** - Real-time metrics organized by category
2. **CPU & Processor Statistics** - CPU usage, VCPU allocation, provisioned CPU
3. **Memory Statistics** - Memory usage, VMem, ballooning, swapping
4. **Storage & I/O Statistics** - Storage usage, IOPS, latency, disk metrics
5. **Network Statistics** - Network throughput, bandwidth utilization
6. **Other Statistics** - Additional metrics like price index, flow, cooling, power

### Visual Features
- **Utilization Bars**: Color-coded progress bars showing resource utilization
  - Green (< 60%): Healthy utilization
  - Yellow (60-80%): Moderate utilization
  - Red (> 80%): High utilization
- **Capacity Display**: Shows current value vs. capacity for each metric
- **Organized Categories**: Statistics grouped by resource type
- **Responsive Cards**: Up to 6 metrics per category in a 3-column grid

## API Integration

### New Method in turbo_client.py

```python
def get_entity_stats(self, entity_uuid: str, stat_names: Optional[List[str]] = None) -> List[Dict]:
    """
    Get detailed statistics for an entity using POST /stats/{uuid}.
    
    Args:
        entity_uuid: UUID of the entity
        stat_names: Optional list of specific statistics to retrieve.
                   If None, returns all available statistics.
    
    Returns:
        List of statistic dictionaries with structure:
        [{
            "name": "CPU",
            "displayName": "CPU/EntityName",
            "units": "MHz",
            "value": 123.45,
            "values": {"avg": 123.45, "max": 200.0, "min": 50.0},
            "capacity": {"avg": 1000.0, "max": 1000.0, "min": 1000.0},
            "relatedEntityType": "VirtualMachine",
            "filters": [{"type": "relation", "value": "sold"}]
        }]
    """
```

### API Endpoint Used
**POST** `/api/v3/stats/{entity_uuid}`

**Request Body** (optional):
```json
{
  "statistics": [
    {"name": "CPU"},
    {"name": "Mem"},
    {"name": "VMem"}
  ]
}
```

**Response Structure**:
```json
[
  {
    "displayName": "ApplicationName",
    "date": "2024-01-01T12:00:00Z",
    "statistics": [
      {
        "name": "CPU",
        "displayName": "CPU/ApplicationName",
        "units": "MHz",
        "value": 123.45,
        "values": {
          "avg": 123.45,
          "max": 200.0,
          "min": 50.0,
          "total": 123.45
        },
        "capacity": {
          "avg": 1000.0,
          "max": 1000.0,
          "min": 1000.0,
          "total": 1000.0
        },
        "relatedEntityType": "VirtualMachine",
        "filters": [
          {
            "type": "relation",
            "value": "sold"
          }
        ]
      }
    ]
  }
]
```

## Statistics Categories

### 1. CPU & Processor Statistics
**Metrics Included:**
- `CPU` - CPU utilization (MHz or %)
- `VCPU` - Virtual CPU allocation
- `CPUProvisioned` - Provisioned CPU capacity
- `Q1VCPU`, `Q2VCPU`, `Q4VCPU`, `Q8VCPU`, `Q16VCPU`, `Q32VCPU` - CPU queue depths

**Example Display:**
```
CPU/MyApp
1234.5 MHz
Capacity: 5200.0 MHz
[████████░░] 23.7% utilized
```

### 2. Memory Statistics
**Metrics Included:**
- `Mem` - Memory utilization (KB or MB)
- `VMem` - Virtual memory usage
- `MemProvisioned` - Provisioned memory capacity
- `Ballooning` - Memory ballooning (bit/sec)
- `Swapping` - Memory swapping (bit/sec)

**Example Display:**
```
VMem/MyApp
8388.6 KB
Capacity: 16777.2 KB
[█████░░░░░] 50.0% utilized
```

### 3. Storage & I/O Statistics
**Metrics Included:**
- `Storage` - Storage utilization (GB)
- `IOThroughput` - I/O throughput (IOPS)
- `Latency` - Storage latency (ms)
- `NumDisk` - Number of disks

**Example Display:**
```
Storage/MyApp
45.2 GB
Capacity: 100.0 GB
[████░░░░░░] 45.2% utilized
```

### 4. Network Statistics
**Metrics Included:**
- `NetThroughput` - Network throughput (Kb/s)
- `Flow` - Network flow
- `FlowAllocation` - Flow allocation

**Example Display:**
```
NetThroughput/MyApp
1024.0 Kb/s
Capacity: 10000.0 Kb/s
[█░░░░░░░░░] 10.2% utilized
```

### 5. Other Statistics
**Metrics Included:**
- `priceIndex` - Price index
- `Cooling` - Cooling requirements
- `Power` - Power consumption
- `Space` - Space utilization

## Implementation Details

### Data Processing Flow

1. **Fetch Statistics**
   ```python
   current_stats = client.get_entity_stats(app_uuid)
   ```

2. **Categorize Statistics**
   ```python
   for stat in current_stats:
       name = stat.get("name", "")
       if any(x in name.upper() for x in ["CPU", "VCPU", "PROCESSOR"]):
           cpu_stats.append(stat)
       elif any(x in name.upper() for x in ["MEM", "MEMORY", "VMEM"]):
           memory_stats.append(stat)
       # ... etc
   ```

3. **Calculate Utilization**
   ```python
   value = vals.get("avg", stat.get("value", 0))
   capacity = cap.get("avg", 0)
   utilization = (value / capacity) * 100 if capacity > 0 else 0
   ```

4. **Determine Color**
   ```python
   util_color = "#42be65"  # Green (< 60%)
   if utilization > 80:
       util_color = "#da1e28"  # Red
   elif utilization > 60:
       util_color = "#f1c21b"  # Yellow
   ```

5. **Create Stat Cards**
   - Display name (truncated if > 30 chars)
   - Current value with units
   - Capacity with units
   - Utilization bar (color-coded)
   - Utilization percentage

### Card Layout

Each statistic is displayed in a card with:
- **Header**: Statistic name (uppercase, small, muted)
- **Value**: Large, bold, color-coded number with units
- **Capacity**: Small text showing capacity
- **Progress Bar**: Visual representation of utilization
- **Percentage**: Numeric utilization percentage

### Responsive Grid
- **Desktop**: 3 columns (md=4)
- **Tablet**: 2 columns
- **Mobile**: 1 column
- **Max per category**: 6 statistics

## Color Scheme

### Utilization Colors
- **Green (#42be65)**: 0-60% - Healthy
- **Yellow (#f1c21b)**: 60-80% - Moderate
- **Red (#da1e28)**: 80-100% - High

### Category Colors
- **CPU**: Blue (#0072c3)
- **Memory**: Purple (#6929c4)
- **Storage**: Gold (#b28600)
- **Network**: Green (#198038)
- **Other**: Orange (#f1620a)

## Usage Example

### Step 1: Navigate to App Statistics Tab
Click on "📈 App Statistics" in the sidebar.

### Step 2: Search for Application
1. Enter application name (min 2 characters)
2. Click "Search Applications"
3. Select application from dropdown

### Step 3: Load Statistics
1. Select time range (24h, 7d, 30d, 90d)
2. Click "Load Statistics"

### Step 4: View Results
The page displays:
1. **Application Header**: Name and type
2. **Metric Cards**: ResponseTime, Transaction, Pending Actions
3. **Time-Series Charts**: Transaction and ResponseTime over time
4. **Current Statistics**: Comprehensive resource metrics by category

### Step 5: Interpret Statistics
- **Green bars**: Resources are healthy
- **Yellow bars**: Monitor these resources
- **Red bars**: Resources need attention
- **No capacity**: Metric doesn't have capacity limits

## Error Handling

### No Statistics Available
If no statistics are returned:
```python
current_stats = client.get_entity_stats(app_uuid)
# Returns empty list []
# No statistics section is displayed
```

### Missing Values
```python
vals = stat.get("values", {}) or {}  # Handle None
cap = stat.get("capacity", {}) or {}  # Handle None
value = vals.get("avg", stat.get("value", 0))  # Fallback to value field
```

### API Errors
```python
try:
    current_stats = client.get_entity_stats(app_uuid)
except Exception as exc:
    log.error("get_entity_stats failed: %s", exc)
    return []  # Returns empty list, no crash
```

## Performance Considerations

### Limiting Display
- Maximum 6 statistics per category
- Prevents overwhelming the UI
- Most important metrics shown first

### Efficient Categorization
```python
# Single pass through statistics
for stat in current_stats:
    name = stat.get("name", "")
    if "CPU" in name.upper():
        cpu_stats.append(stat)
    # ... etc
```

### Lazy Loading
- Statistics only loaded when "Load Statistics" clicked
- Not fetched on initial page load
- Reduces unnecessary API calls

## Testing

### Test Case 1: Application with Full Statistics
1. Select application with many metrics
2. Verify all categories display
3. Check utilization bars are color-coded correctly
4. Verify capacity values are shown

### Test Case 2: Application with Limited Statistics
1. Select application with few metrics
2. Verify only populated categories display
3. Check empty categories are hidden

### Test Case 3: High Utilization
1. Find application with > 80% utilization
2. Verify bars are red
3. Check percentage is accurate

### Test Case 4: No Capacity Metrics
1. Select application without capacity data
2. Verify "N/A" is shown for capacity
3. Check no utilization bar is displayed

## Troubleshooting

### Issue: No Statistics Displayed
**Possible Causes:**
- Entity has no statistics available
- API endpoint not supported in Turbonomic version
- Entity UUID is invalid

**Solution:**
- Check browser console for errors
- Verify entity exists in Turbonomic
- Check Turbonomic version supports /stats endpoint

### Issue: Wrong Categorization
**Cause:** Statistic name doesn't match category keywords

**Solution:**
- Statistics are categorized by name keywords
- If miscategorized, appears in "Other Statistics"
- This is expected behavior for custom metrics

### Issue: Utilization > 100%
**Cause:** Value exceeds capacity (overprovisioning)

**Solution:**
- This is valid - shows overutilization
- Bar is capped at 100% width
- Percentage shows actual value (e.g., 125%)

## API Documentation Reference

### Turbonomic API v3 - Statistics Endpoints

**GET** `/api/v3/stats`
- Returns utility links for statistics endpoints

**GET** `/api/v3/stats/{entity_uuid}`
- Gets all statistics for specified entity
- Returns current snapshot

**POST** `/api/v3/stats/{entity_uuid}`
- Gets filtered statistics for entity
- Accepts optional statistics list in body
- Returns current snapshot with requested stats

**POST** `/api/v3/stats`
- Gets statistics for multiple entities in scope
- Accepts scope and period parameters
- Returns historical data

## Version History

### Version 2.6.0 (2026-04-21)
- ✅ Added `get_entity_stats()` method to turbo_client.py
- ✅ Enhanced Application Statistics tab with current statistics
- ✅ Implemented statistics categorization (CPU, Memory, Storage, Network, Other)
- ✅ Added utilization bars with color coding
- ✅ Created responsive card layout for statistics
- ✅ Added capacity display for each metric
- ✅ Implemented automatic category detection
- ✅ Limited display to 6 stats per category for performance

### Version 2.5.0 (2026-04-21)
- Complete Application Statistics Tab with time-series charts
- Server-side application search with 5 fallback strategies
- Safe timestamp conversion for ISO 8601 and epoch milliseconds

## Summary

✅ **New API Method**: `get_entity_stats()` in turbo_client.py
✅ **Enhanced UI**: Current statistics section with categorized metrics
✅ **Visual Indicators**: Color-coded utilization bars
✅ **Organized Display**: Statistics grouped by resource type
✅ **Responsive Design**: Works on all screen sizes
✅ **Error Handling**: Graceful handling of missing data
✅ **Performance**: Limited display, efficient categorization
✅ **Documentation**: Complete guide with examples

**The Application Statistics tab now provides comprehensive resource monitoring!**

---

*Generated: 2026-04-21*
*Version: 2.6.0*
*Mode: Automated Resource Management*