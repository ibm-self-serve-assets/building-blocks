# 🚀 Step 1: Import Quantum Safe Explorer Custom Bob Mode (via Bob UI)

Before using IBM Bob with IBM Quantum Safe Explorer (QSE), you need to import the **Quantum Safe Explorer custom mode** into your project.

------------------------------------------------------------------------

## 🆕 For New Projects

When working with a **new project**, there are no existing custom modes.
You can directly add the Quantum Safe Explorer mode.

### 📁 Add Mode Configuration

1. Download and extract `quantum-safe.zip` file in the bob-modes folder.
2. Open your project in **Bob UI**
3. Navigate to the project workspace (file explorer)
4. Copy the content of the extracted folder into the `.bob/` directory:

```
.bob/
├── custom_modes.yaml
```

5.  Copy the provided:
    -   `custom_modes.yaml`
6.  Paste it into the `.bob/` directory

------------------------------------------------------------------------

### ▶️ Start Using the Mode

-   Refresh or reload the Bob UI (if required)
-   Navigate to **Modes / Custom Modes section**
-   Select **🔐 Quantum Safe Explorer**
-   Start using it in your workflows

------------------------------------------------------------------------

## 🔁 For Existing Projects

If your project already has custom modes configured, follow these steps
carefully to avoid breaking existing setups.

------------------------------------------------------------------------

### ⚠️ Do Not Overwrite Existing Configuration

-   Do **not replace** the existing `.bob/custom_modes.yaml`
-   This file may already contain active modes used by your project

------------------------------------------------------------------------

### ✏️ Append New Mode Configuration

1. Download and extract `quantum-safe.zip` file.
2. Open `.bob/custom_modes.yaml` in the Bob UI editor
3. Add the Quantum Safe Explorer mode at the end of the file

#### Example:

    # Existing custom modes
    - slug: existing-mode-1
      name: Existing Mode 1
      # ... existing configuration ...

    - slug: existing-mode-2
      name: Existing Mode 2
      # ... existing configuration ...

    # Add Quantum Safe Explorer mode
    - slug: qse
      name: 🔐 Quantum Safe Explorer
      # ... new mode configuration ...

------------------------------------------------------------------------

### ✅ Verify in Bob UI

After completing the setup:

-   Go to **Modes / Custom Modes**
-   Confirm:
    -   Existing modes are still available
    -   **🔐 Quantum Safe Explorer** mode appears
-   Open the mode and ensure no configuration errors are shown

------------------------------------------------------------------------

## 🧠 Best Practices

-   Always **append**, never overwrite `custom_modes.yaml`.
-   Validate YAML formatting carefully (indentation matters).
-   Reload the UI if changes are not reflected immediately.
-   Ensure QSE CLI is installed at `/usr/local/bin/qse-cli-artifacts` before running scans.
-   For QCM upload functionality, configure the `gcm-mcp-server` MCP tool with valid IBM Guardium credentials.

------------------------------------------------------------------------

## 🎯 Outcome

After completing these steps:

-   **🔐 Quantum Safe Explorer** mode will be available in Bob UI.
-   Existing modes will continue to function without disruption.
-   You can start using the mode to **scan codebases for quantum-vulnerable cryptographic APIs**, run Cryptographic Analytics (Java), execute API Discovery scans, and upload findings to IBM Guardium Cryptographic Manager.
