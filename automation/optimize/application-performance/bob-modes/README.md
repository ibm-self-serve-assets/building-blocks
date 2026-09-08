# IBM Turbonomic Resource Management Dashboard

A production-ready IBM Turbonomic dashboard built with Dash and Plotly using a dark IBM Carbon-inspired theme.

## Features

- 8 dashboard tabs
- Turbonomic REST API v3 integration
- Real-time market data retrieval
- Action execution with confirmation
- Application statistics with time-series charts
- Responsive dark theme UI
- Defensive programming for API edge cases

## Tabs Included

1. Overview
2. Pending Actions
3. Entities
4. App Statistics
5. Targets
6. Groups
7. Kubernetes
8. Policies

## Critical Fixes Implemented

### EC001
Uses [`/api/v3/markets/Market/entities`](turbo_client.py) instead of bare [`/api/v3/entities`](turbo_client.py) for real entity retrieval.

### EC002
Implements response normalization in [`_to_list()`](turbo_client.py:97) to safely handle list and wrapped dict responses.

### EC003
Implements safe timestamp handling in [`safe_dt()`](app.py:82) for both ISO 8601 strings and epoch millisecond values.

### EC004
Uses server-side filtering through [`POST /api/v3/search`](turbo_client.py) in [`search_applications()`](turbo_client.py:253).

### EC005
Includes full dropdown visibility overrides in [`assets/custom.css`](assets/custom.css) for dark theme readability.

### EC006
Uses safe dict fallback patterns like [`or {}`](app.py:522) when processing statistics payloads.

## Project Structure

- [`app.py`](app.py) - Main Dash application
- [`turbo_client.py`](turbo_client.py) - Turbonomic API client
- [`assets/custom.css`](assets/custom.css) - UI theme and component styles
- [`requirements.txt`](requirements.txt) - Python dependencies
- [`scripts/start.sh`](scripts/start.sh) - Environment setup and start
- [`scripts/stop.sh`](scripts/stop.sh) - Stop running dashboard
- [`README.md`](README.md) - Project documentation

## Prerequisites

- Python 3.10+
- Network access to Turbonomic
- Valid Turbonomic credentials
- Optional SSL certificate trust if using verification

## Installation

```bash
cd Turbonomic_BB
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

## Quick Start

1. Run [`scripts/start.sh`](scripts/start.sh)
2. Open `http://localhost:8050`
3. Enter Turbonomic host, username, and password
4. Browse data across all 8 tabs

## Architecture

### Frontend
Built using Dash, Bootstrap components, and Plotly.

### Backend
Uses session-based authentication via [`TurbonomicClient`](turbo_client.py:11).

### Data Flow
- Login creates session credentials in browser session store
- Interval callbacks pull fresh data
- Render callbacks map data to cards, charts, and tables
- Execute flow posts action acceptance back to Turbonomic

## API Integration

Primary API methods:
- [`get_entities()`](turbo_client.py:167)
- [`get_pending_actions()`](turbo_client.py:226)
- [`execute_action()`](turbo_client.py:242)
- [`search_applications()`](turbo_client.py:253)
- [`get_targets()`](turbo_client.py:337)
- [`get_groups()`](turbo_client.py:346)
- [`get_clusters()`](turbo_client.py:355)
- [`get_policies()`](turbo_client.py:364)

## Turbonomic API Endpoints Used

This dashboard integrates with the following Turbonomic REST API v3 endpoints:

### Authentication
**POST** `/api/v3/login`
- **Purpose**: Authenticate and establish session
- **Method**: Form-encoded POST
- **Parameters**:
  - `username` (string, required): Turbonomic username
  - `password` (string, required): Turbonomic password
- **Response**: Sets `JSESSIONID` cookie for subsequent requests
- **Used in**: [`_login()`](turbo_client.py:48)

### Markets & Entities
**GET** `/api/v3/markets/Market/entities`
- **Purpose**: Fetch entities from real-time market (PRIMARY ENDPOINT)
- **Parameters**:
  - `types` (string, optional): Entity type filter (e.g., "VirtualMachine")
  - `limit` (integer, optional): Maximum results (default: 500)
- **Response**: List of entity objects or dict with "entities" wrapper
- **Used in**: [`get_entities()`](turbo_client.py:167)
- **Tabs**: Overview, Entities, Kubernetes
- **Critical Fix**: EC001 - Use this instead of bare `/api/v3/entities`

**GET** `/api/v3/entities/{uuid}`
- **Purpose**: Get single entity by UUID
- **Parameters**: None (UUID in path)
- **Response**: Single entity object
- **Used in**: [`get_entity()`](turbo_client.py:209)
- **Tabs**: App Statistics

**POST** `/api/v3/entities/{uuid}/stats`
- **Purpose**: Get time-series statistics for an entity
- **Request Body**:
  ```json
  {
    "statistics": [{"name": "ResponseTime"}, {"name": "Transaction"}],
    "startDate": 1704110400000,
    "endDate": 1704196800000
  }
  ```
- **Response**: Array of snapshot objects with statistics
- **Used in**: [`get_entity_time_series()`](turbo_client.py:217)
- **Tabs**: App Statistics
- **Critical Fix**: EC003 - Handles both string and int timestamps

**POST** `/api/v3/entities/{uuid}/actions`
- **Purpose**: Get actions for a specific entity
- **Request Body**:
  ```json
  {
    "actionStateList": ["READY", "QUEUED"],
    "actionModeList": ["RECOMMEND"],
    "relatedEntityTypes": []
  }
  ```
- **Parameters**:
  - `limit` (integer, optional): Maximum results
- **Response**: List of action objects
- **Used in**: [`get_entity_actions()`](turbo_client.py:234)
- **Tabs**: App Statistics

### Actions
**POST** `/api/v3/markets/Market/actions`
- **Purpose**: Get all pending actions from real-time market
- **Request Body**:
  ```json
  {
    "actionStateList": ["READY", "QUEUED", "IN_PROGRESS", "ACCEPTED"],
    "actionModeList": ["RECOMMEND", "EXTERNAL_APPROVAL", "MANUAL", "AUTOMATIC"]
  }
  ```
- **Parameters**:
  - `limit` (integer, optional): Maximum results
- **Response**: List of action objects or dict with "actions"/"actionsList" wrapper
- **Used in**: [`get_pending_actions()`](turbo_client.py:226)
- **Tabs**: Overview, Pending Actions

**POST** `/api/v3/actions/{uuid}`
- **Purpose**: Execute/accept an action (PRIMARY METHOD)
- **Parameters**:
  - `accept=true` (query parameter): Accept the action
- **Response**: Action execution result
- **Used in**: [`execute_action()`](turbo_client.py:242)
- **Tabs**: Pending Actions
- **Fallback Strategy**:
  1. Try `POST /actions/{uuid}?accept=true`
  2. Try `POST /actions/{uuid}` with payload `{"actionState": "ACCEPTED"}`
  3. Try `POST /actions/{uuid}/accept` (legacy)

### Search
**POST** `/api/v3/search`
- **Purpose**: Server-side entity search with filtering (RECOMMENDED)
- **Request Body**:
  ```json
  {
    "criteria": {
      "expType": "RXEQ",
      "expVal": ".*search_term.*",
      "filterType": "displayName",
      "caseSensitive": false
    },
    "className": "BusinessApplication"
  }
  ```
- **Parameters**:
  - `limit` (integer, optional): Maximum results
- **Response**: List of matching entities
- **Used in**: [`search_applications()`](turbo_client.py:253)
- **Tabs**: App Statistics
- **Critical Fix**: EC004 - Server-side filtering prevents missing results beyond limit

### Targets
**GET** `/api/v3/targets`
- **Purpose**: Get all configured targets
- **Parameters**: None
- **Response**: List of target objects or dict with "targets" wrapper
- **Used in**: [`get_targets()`](turbo_client.py:337)
- **Tabs**: Overview, Targets

### Groups
**GET** `/api/v3/groups`
- **Purpose**: Get all groups
- **Parameters**:
  - `group_type` (string, optional): Filter by group type
- **Response**: List of group objects or dict with "groups" wrapper
- **Used in**: [`get_groups()`](turbo_client.py:346)
- **Tabs**: Groups

### Kubernetes
**GET** `/api/v3/clusters`
- **Purpose**: Get Kubernetes clusters
- **Parameters**: None
- **Response**: List of cluster objects
- **Used in**: [`get_clusters()`](turbo_client.py:355)
- **Tabs**: Kubernetes

### Policies
**GET** `/api/v3/settingspolicies`
- **Purpose**: Get automation policies
- **Parameters**: None
- **Response**: List of policy objects
- **Used in**: [`get_policies()`](turbo_client.py:364)
- **Tabs**: Policies

### Response Normalization
All API responses are normalized using [`_to_list()`](turbo_client.py:97) which handles:
- Direct list responses: `[{...}, {...}]`
- Wrapped dict responses: `{"entities": [{...}], "links": [...]}`
- Empty responses with only links: `{"links": [...]}`
- None responses: `null`

**Critical Fix EC002**: This ensures consistent data handling across different Turbonomic versions.

### Common Response Wrappers
The API may wrap responses in these keys:
- `entities` - Entity lists
- `actions` or `actionsList` - Action lists
- `groups` - Group lists
- `targets` - Target lists
- `items`, `results`, `content`, `data` - Generic wrappers
- `links` - Navigation links (when alone, indicates empty result)

### Error Handling
All API calls include:
- Try-except blocks for network errors
- Response status validation with `raise_for_status()`
- Fallback strategies for version compatibility
- Detailed logging for debugging
- Graceful degradation on failures

## App Statistics Notes

The App Statistics tab uses:
- initial render callback pattern
- duplicate output callback pattern
- safe timestamp conversion
- Average, Maximum, and Capacity lines
- spline interpolation and unified hover

## Edge Cases Covered

- Empty API responses
- Missing fields
- None values
- Unexpected wrapper objects
- String timestamps
- API request failures
- empty charts
- no dropdown options
- no matching filters

## Troubleshooting

### Imports not resolved in editor
Install dependencies from [`requirements.txt`](requirements.txt). Static analysis warnings are expected before environment setup.

### No entities returned
Ensure Turbonomic has discovered targets and that the real-time market contains inventory.

### Search returns no applications
Check application naming and permissions. The dashboard already uses server-side search fallbacks.

### Dropdown text invisible
Confirm [`assets/custom.css`](assets/custom.css) is loading and clear browser cache if necessary.

### SSL errors
Disable SSL verification on login for lab environments or install trusted certificates.

## Performance Notes

- Entity loading uses capped limits
- tables use pagination
- app search uses server-side filtering first
- graphs are built only for active datasets

## Security Notes

- Credentials are stored in Dash session storage for the current browser session
- No secrets are written to disk by default
- Use HTTPS and verified certificates in production

## Production Deployment

### Local
Run [`python app.py`](app.py)

### Gunicorn
```bash
gunicorn app:server --bind 0.0.0.0:8050
```

### Reverse Proxy
Deploy behind NGINX or OpenShift route with TLS termination.

## Start and Stop

Start:
```bash
./scripts/start.sh
```

Stop:
```bash
./scripts/stop.sh
```

## Verification Checklist

- Login page loads
- all 8 tabs appear in sidebar
- dashboard connects to Turbonomic
- charts render with dark theme
- dropdown text is visible
- actions can be executed
- application search uses server-side filtering

## Notes

This implementation is designed to be robust and extensible. Additional charts, export features, and caching can be added on top of the current structure.