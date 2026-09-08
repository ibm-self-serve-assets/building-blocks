# Application Statistics Tab - Complete Implementation

## Overview
The Application Statistics tab now includes full time-series visualization with charts, metric cards, and comprehensive data processing.

## Features Implemented

### 1. Search Interface
- **Application Name Input**: Text field with minimum 2 characters
- **Search Button**: Triggers server-side search with 5 fallback strategies
- **Status Messages**: Color-coded feedback (green=success, yellow=warning, red=error)

### 2. Application Selection
- **Dropdown**: Populated from search results
- **Format**: "App Name [ClassName]"
- **Value**: Entity UUID for API calls

### 3. Time Range Selection
- **Radio Buttons**: 24h, 7d, 30d, 90d
- **Default**: 7d (Last 7 Days)
- **Styling**: White text (#ffffff) for visibility in dark theme

### 4. Load Statistics Button
- **Triggers**: Time-series data loading
- **Validation**: Disabled if no application selected
- **Feedback**: Loading state during API calls

### 5. Metric Cards (3 cards)
- **ResponseTime Card**: Latest value with units (Blue #0072c3)
- **Transaction Card**: Latest value with units (Green #198038)
- **Pending Actions Card**: Count of pending actions (Orange #f1620a)

### 6. Time-Series Charts (2 charts side-by-side)

#### Transaction Chart (TPS)
- **Average Line**: Blue (#0072c3), solid, spline, area fill
- **Maximum Line**: Red (#da1e28), dotted, spline
- **Capacity Line**: Yellow (#f1c21b), dashed, spline
- **Height**: 320px
- **Hover Mode**: Unified (shows all metrics at once)

#### ResponseTime Chart (msec)
- **Average Line**: Blue (#0072c3), solid, spline, area fill
- **Maximum Line**: Red (#da1e28), dotted, spline
- **Capacity Line**: Yellow (#f1c21b), dashed, spline
- **Height**: 320px
- **Hover Mode**: Unified (shows all metrics at once)

## API Integration

### Endpoints Used
1. **POST /api/v3/search** - Server-side application filtering
2. **GET /api/v3/entities/{uuid}** - Get application details
3. **POST /api/v3/entities/{uuid}/stats** - Get time-series statistics
4. **POST /api/v3/entities/{uuid}/actions** - Get pending actions

### Fallback Strategies (5 levels)
1. POST /search with BusinessApplication
2. GET /businessapplications
3. POST /search for each APP_ENTITY_TYPES
4. GET /markets/Market/entities with app types
5. Client-side filtering as last resort

## Critical Fixes Implemented

### EC003: Safe Timestamp Conversion
Handles both ISO 8601 strings and epoch milliseconds:
```python
def safe_timestamp_to_datetime(ts_ms: Any) -> Optional[datetime]:
    try:
        if isinstance(ts_ms, str):
            if 'T' in ts_ms:
                # ISO 8601 format
                return datetime.fromisoformat(ts_ms.replace('Z', '+00:00'))
            else:
                # Epoch milliseconds as string
                ts_ms_int = int(ts_ms)
                return datetime.utcfromtimestamp(ts_ms_int / 1000)
        else:
            # Numeric epoch milliseconds
            ts_ms_int = int(ts_ms) if ts_ms else 0
            return datetime.utcfromtimestamp(ts_ms_int / 1000) if ts_ms_int else None
    except (ValueError, TypeError, OSError):
        return None
```

### EC006: None Value Handling
Uses 'or {}' pattern for nested dictionaries:
```python
vals = stat.get("values", {}) or {}
cap = stat.get("capacity", {}) or {}
```

## Callback Architecture

### Callback 1: Search Applications
- **Input**: btn-appstats-search (n_clicks)
- **State**: appstats-search-input (value)
- **Output**: appstats-app-dropdown (options), appstats-search-status (children)
- **Logic**: Server-side search with 5 fallback strategies

### Callback 2: Display Time Range Selector
- **Input**: appstats-app-dropdown (value)
- **Output**: appstats-results-container (children)
- **Logic**: Shows time range radio buttons and Load Stats button

### Callback 3: Load and Display Statistics
- **Input**: btn-load-appstats (n_clicks)
- **State**: appstats-app-dropdown (value), appstats-time-range (value)
- **Output**: appstats-charts-container (children, allow_duplicate=True)
- **Logic**: 
  - Fetches time-series data
  - Processes timestamps safely
  - Creates metric cards
  - Generates time-series charts
  - Handles all edge cases

## Data Processing

### Time-Series Data Structure
```python
stat_series = {
    "ResponseTime": {
        "dates": [datetime, ...],
        "avg": [float, ...],
        "max": [float, ...],
        "min": [float, ...],
        "cap_avg": [float, ...],
        "units": "ms"
    },
    "Transaction": {
        "dates": [datetime, ...],
        "avg": [float, ...],
        "max": [float, ...],
        "min": [float, ...],
        "cap_avg": [float, ...],
        "units": "tps"
    }
}
```

### Latest Value Extraction
```python
if "ResponseTime" in stat_series:
    avgs = [v for v in stat_series["ResponseTime"]["avg"] if v is not None]
    if avgs:
        units = stat_series["ResponseTime"]["units"]
        response_time_val = f"{avgs[-1]:.1f} {units}"
```

## Chart Styling

### Spline Interpolation
- **Shape**: "spline" for smooth curves
- **Area Fill**: Semi-transparent under average line
- **Line Widths**: Average=3px, Maximum=2px, Capacity=2px

### Color Scheme
- **Average**: Blue (#0072c3) - Primary metric
- **Maximum**: Red (#da1e28) - Peak values
- **Capacity**: Yellow (#f1c21b) - Threshold/limit

### Hover Configuration
- **Mode**: "x unified" - Shows all metrics at cursor position
- **Background**: #161b2e (dark)
- **Border**: #0072c3 (blue)
- **Font Size**: 12px

## Edge Cases Handled

1. **No Application Selected**: Shows warning alert
2. **Application Not Found**: Shows danger alert
3. **No Time-Series Data**: Shows empty charts gracefully
4. **Invalid Timestamps**: Skips invalid data points
5. **Missing Statistics**: Uses N/A for metric cards
6. **API Failures**: Shows error alert with details
7. **Empty Snapshots**: Returns empty stat_series
8. **None Values**: Filters out before aggregation

## Testing Checklist

✅ Search with 2+ characters returns results
✅ Search status shows color-coded messages
✅ Dropdown populates with search results
✅ Time range radio buttons are visible (white text)
✅ Load Stats button triggers data loading
✅ Metric cards display latest values
✅ Transaction chart shows with splines and fills
✅ ResponseTime chart shows with splines and fills
✅ Charts handle missing data gracefully
✅ Hover shows unified tooltips
✅ All edge cases handled without crashes

## Performance Considerations

- **Server-Side Filtering**: Reduces data transfer
- **Time Range Selection**: Limits data points fetched
- **Lazy Loading**: Charts only load when button clicked
- **Efficient Processing**: Single pass through snapshots
- **Memory Management**: Filters None values before aggregation

## Future Enhancements

1. **Additional Commodities**: Heap, CollectionTime, Connections
2. **Export Functionality**: Download chart data as CSV
3. **Comparison Mode**: Compare multiple applications
4. **Alert Thresholds**: Visual indicators for capacity breaches
5. **Historical Trends**: Week-over-week comparison

## Code Locations

- **Search Callback**: Lines 1037-1070
- **Time Range Display**: Lines 1074-1103
- **Load Statistics**: Lines 1107-1250
- **Safe Timestamp Function**: Lines 82-98
- **TurbonomicClient Methods**: turbo_client.py lines 400-450

## Documentation References

- **Complete Tab Implementations**: .bob/rules-automated-resource-mgmt/7_complete_tab_implementations.xml
- **API Reference**: .bob/rules-automated-resource-mgmt/6_api_reference.xml
- **Edge Cases**: .bob/rules-automated-resource-mgmt/2_edge_cases_and_fixes.xml