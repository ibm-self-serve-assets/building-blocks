# Namespace Column Debugging Guide

## Issue: Namespace Column Shows "—" Instead of Actual Namespaces

If the Namespace column is empty (showing "—") when it should show values like `retail-dev`, `robot-shop`, `turbonomic`, follow these steps to debug and fix it.

## Step 1: Check Application Logs

When you load the Pending Actions tab, check the terminal where the app is running for debug messages:

```bash
# Look for lines like this:
DEBUG: Action abc-123: target keys = ['uuid', 'displayName', 'className', ...], namespace = —
DEBUG: Action def-456: target keys = ['uuid', 'displayName', 'className', ...], namespace = retail-dev
```

The `target keys` will show you what fields are available in the API response.

## Step 2: Inspect Raw API Response

Use curl to see the actual API response structure:

```bash
curl -k -u username:password \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"actionStateList":["READY","QUEUED","IN_PROGRESS","ACCEPTED"],"actionModeList":["RECOMMEND","EXTERNAL_APPROVAL","MANUAL","AUTOMATIC"]}' \
  https://your-turbonomic/api/v3/markets/Market/actions?limit=5 | jq '.'
```

Look for namespace in the response. It might be in:
- `target.namespace`
- `target.aspects.namespace`
- `target.environment.namespace`
- `target.providers[].namespace`
- `target.discoveredBy.namespace`

## Step 3: Common Namespace Locations

### Location 1: Direct Field (Most Common)
```json
{
  "target": {
    "uuid": "abc-123",
    "displayName": "my-pod",
    "namespace": "retail-dev"  ← HERE
  }
}
```

### Location 2: In Aspects
```json
{
  "target": {
    "uuid": "abc-123",
    "displayName": "my-pod",
    "aspects": {
      "namespace": "robot-shop"  ← HERE
    }
  }
}
```

### Location 3: In Environment
```json
{
  "target": {
    "uuid": "abc-123",
    "displayName": "my-pod",
    "environment": {
      "namespace": "turbonomic"  ← HERE
    }
  }
}
```

### Location 4: In Providers Array
```json
{
  "target": {
    "uuid": "abc-123",
    "displayName": "my-pod",
    "providers": [
      {
        "uuid": "def-456",
        "displayName": "namespace-obj",
        "namespace": "retail-dev"  ← HERE
      }
    ]
  }
}
```

### Location 5: In DiscoveredBy
```json
{
  "target": {
    "uuid": "abc-123",
    "displayName": "my-pod",
    "discoveredBy": {
      "uuid": "cluster-123",
      "displayName": "OpenShift-Cluster",
      "namespace": "default"  ← HERE
    }
  }
}
```

## Step 4: Update Code Based on Findings

Once you identify where the namespace is located, update the code in `app.py`:

### If namespace is in a different location:

```python
# Add a new strategy before the existing ones
# Example: If namespace is in target.metadata.namespace
if namespace == "—":
    metadata = target.get("metadata", {}) or {}
    if isinstance(metadata, dict) and "namespace" in metadata:
        namespace = metadata["namespace"]
```

### If namespace is in a nested array:

```python
# Example: If namespace is in target.consumers[0].namespace
if namespace == "—":
    consumers = target.get("consumers", []) or []
    if consumers and len(consumers) > 0:
        consumer = consumers[0]
        if isinstance(consumer, dict):
            namespace = consumer.get("namespace", "—")
```

## Step 5: Common Issues and Solutions

### Issue 1: Namespace is null/empty in API
**Symptom:** API returns `"namespace": null` or `"namespace": ""`
**Solution:** This means Turbonomic doesn't have namespace data for these entities
**Workaround:** Check if entities are properly discovered from Kubernetes/OpenShift

### Issue 2: Namespace is in a custom field
**Symptom:** Namespace exists but in a non-standard location
**Solution:** Add custom extraction logic based on your Turbonomic version
**Example:**
```python
# For custom field location
if namespace == "—":
    custom_data = target.get("customData", {}) or {}
    namespace = custom_data.get("k8sNamespace", "—")
```

### Issue 3: Different field name
**Symptom:** Field is called something else (e.g., "k8sNamespace", "namespaceName")
**Solution:** Check all fields that contain "namespace" in the name
**Example:**
```python
# Try variations
for key in target.keys():
    if "namespace" in key.lower() and target[key]:
        namespace = target[key]
        break
```

## Step 6: Enable Detailed Logging

Add more detailed logging to see all target fields:

```python
# In app.py, in the load_actions_data function
for a in actions[:3]:  # First 3 actions only
    target = a.get("target", {}) or {}
    log.info(f"Full target structure: {json.dumps(target, indent=2)}")
```

This will print the complete target structure to help identify where namespace is.

## Step 7: Test with Specific Entity Types

Different entity types may have namespace in different locations:

### For Pods:
```python
# Pods usually have direct namespace field
namespace = target.get("namespace", "—")
```

### For Containers:
```python
# Containers might get namespace from parent Pod
providers = target.get("providers", [])
for provider in providers:
    if provider.get("className") == "ContainerPod":
        namespace = provider.get("namespace", "—")
        break
```

### For Services:
```python
# Services might have namespace in aspects
aspects = target.get("aspects", {})
namespace = aspects.get("namespace", "—")
```

## Step 8: Verify Entity Types

Check what entity types are in your actions:

```python
# Add this logging
entity_types = {}
for a in actions:
    target = a.get("target", {})
    entity_type = target.get("className", "Unknown")
    entity_types[entity_type] = entity_types.get(entity_type, 0) + 1

log.info(f"Entity types in actions: {entity_types}")
```

This shows which entity types have actions, helping focus debugging.

## Step 9: Manual Test

Test namespace extraction manually in Python:

```python
# In Python console or script
import requests
import json

# Get actions
response = requests.post(
    "https://your-turbonomic/api/v3/markets/Market/actions",
    auth=("username", "password"),
    json={"actionStateList": ["READY"]},
    verify=False
)

actions = response.json()

# Check first action
if actions:
    first_action = actions[0] if isinstance(actions, list) else actions.get("actionsList", [{}])[0]
    target = first_action.get("target", {})
    
    print("Target keys:", list(target.keys()))
    print("Namespace field:", target.get("namespace"))
    print("Aspects:", target.get("aspects", {}))
    print("Environment:", target.get("environment", {}))
    print("Providers:", target.get("providers", []))
```

## Step 10: Contact Support

If namespace still doesn't appear after trying all strategies:

1. **Document your findings:**
   - Turbonomic version
   - Entity types affected
   - Sample API response (sanitized)
   - Strategies tried

2. **Check Turbonomic documentation:**
   - API version differences
   - Entity schema changes
   - Namespace field availability

3. **Verify Kubernetes/OpenShift integration:**
   - Is namespace data being collected?
   - Check target configuration
   - Verify discovery is working

## Expected Result

After fixing, you should see:

```
| Action Type | Namespace    | Entity              | Description      |
|-------------|--------------|---------------------|------------------|
| RESIZE      | retail-dev   | web-pod-abc123      | Increase CPU     |
| MOVE        | robot-shop   | cart-pod-def456     | Move to node-02  |
| SCALE       | turbonomic   | api-pod-ghi789      | Scale replicas   |
```

## Quick Fix Template

If you find the namespace location, here's a template to add:

```python
# In app.py, load_actions_data function, after line 505

# CUSTOM NAMESPACE EXTRACTION
# Replace 'YOUR_PATH_HERE' with actual path
if namespace == "—":
    # Example: target.customField.namespace
    custom_field = target.get("YOUR_PATH_HERE", {}) or {}
    if isinstance(custom_field, dict):
        namespace = custom_field.get("namespace", "—")
```

---

*Last Updated: 2026-04-22*
*Version: 2.9.2*