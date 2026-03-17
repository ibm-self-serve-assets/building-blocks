# 🚀 Step 1: Import Application Resilience Custom Bob Mode (via Bob UI)

Before using IBM Bob with Instana, you need to import the **Application
Observability custom mode** into your project.

------------------------------------------------------------------------

## 🆕 For New Projects

When working with a **new project**, there are no existing custom modes.
You can directly add the Application Resilience mode.

### 📁 Add Mode Configuration

1.  Open your project in **Bob UI**
2.  Navigate to the project workspace (file explorer)
3.  Create the following structure if not already present:

```{=html}
<!-- -->
```
    .bob/
    ├── custom_modes.yaml
    └── rules/
        └── application-observability/
            └── [mode rules files]

4.  Copy the provided:
    -   `custom_modes.yaml`
    -   `rules/*/` folder
5.  Paste them into the `.bob/` directory

------------------------------------------------------------------------

### ▶️ Start Using the Mode

-   Refresh or reload the Bob UI (if required)
-   Navigate to **Modes / Custom Modes section**
-   Select **Application Resilience**
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

1.  Open `.bob/custom_modes.yaml` in the Bob UI editor\
2.  Add the Application Resilience mode at the end of the file

#### Example:

    # Existing custom modes
    - slug: existing-mode-1
      name: Existing Mode 1
      # ... existing configuration ...

    - slug: existing-mode-2
      name: Existing Mode 2
      # ... existing configuration ...

    # Add Application Resilience mode
    - slug: application-observability
      name: Application Resilience
      # ... new mode configuration ...

------------------------------------------------------------------------

### 📂 Maintain Rules Folder Structure

1.  Navigate to `.bob/rules/`
2.  Add the new rules folder:

```{=html}
<!-- -->
```
    application-observability/

3.  Ensure the final structure looks like:

```{=html}
<!-- -->
```
    .bob/
    ├── custom_modes.yaml
    └── rules/
        ├── existing-mode-1/
        ├── existing-mode-2/
        └── application-observability/

👉 Do **not modify or delete existing rule folders**

------------------------------------------------------------------------

### ✅ Verify in Bob UI

After completing the setup:

-   Go to **Modes / Custom Modes**
-   Confirm:
    -   Existing modes are still available
    -   **Application Resilience** mode appears
-   Open the mode and ensure no configuration errors are shown

------------------------------------------------------------------------

## 🧠 Best Practices

-   Always **append**, never overwrite `custom_modes.yaml`.
-   Keep each mode isolated under its own rules folder.
-   Validate YAML formatting carefully (indentation matters).
-   Reload the UI if changes are not reflected immediately.

------------------------------------------------------------------------

## 🎯 Outcome

After completing these steps:

-   Application Resilience mode will be available in Bob UI.
-   Existing modes will continue to function without disruption.
-   You can start using the mode for **Application Resilience**.
