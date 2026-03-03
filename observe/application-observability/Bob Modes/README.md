# Bob Modes

This directory contains custom Bob mode configurations that extend IBM Bob's capabilities with domain-specific expertise.
**File:** [Application Observability](/Base Modes/application-observability.yaml)
---

## Available Modes

### Data for AI Mode
**File:** Application Observability
[Application Observability](/Base Modes/application-observability.yaml)

---

## Installing Bob Modes

### Method 1: Copy to Bob's Modes Directory

**Windows:**
```powershell
Copy-Item application-observability.yaml "$env:APPDATA\IBM Bob\User\globalStorage\ibm.bob-code\modes\"
```

**Linux/Mac:**
```bash
cp application-observability.yaml ~/.config/IBM\ Bob/User/globalStorage/ibm.bob-code/modes/
```

### Method 2: Reference from Current Location

Edit Bob's configuration to reference modes from this directory.

