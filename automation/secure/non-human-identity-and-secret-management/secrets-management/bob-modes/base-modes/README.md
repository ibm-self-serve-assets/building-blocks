# 🚀 Step 1: Import Secrets Management Custom Bob Mode (via Bob UI)

Before using IBM Bob with HashiCorp Vault, you need to import the **Secrets Management custom mode** into your project.

------------------------------------------------------------------------

## 🆕 For New Projects

When working with a **new project**, there are no existing custom modes.
You can directly add the Secrets Management mode.

### 📁 Add Mode Configuration

1. Download and extract the `vault-secret-migrator.zip` file from this folder.
2. Open your project in **Bob UI**.
3. Navigate to the project workspace (file explorer).
4. Copy the contents of the `.bob` folder extracted in Step 1:

```
.bob/
├── custom_modes.yaml
└── rules/
    └── vault-secret-migrator/
        └── [mode rules files]
```

5. Paste them into the `.bob/` directory of your project.

------------------------------------------------------------------------

### ▶️ Start Using the Mode

- Refresh or reload the Bob UI (if required).
- Navigate to **Modes / Custom Modes section**.
- Select **Secrets Management**.
- Start using it in your workflows.

------------------------------------------------------------------------

## 🔁 For Existing Projects

If your project already has custom modes configured, follow these steps
carefully to avoid breaking existing setups.

------------------------------------------------------------------------

### ⚠️ Do Not Overwrite Existing Configuration

- Do **not replace** the existing `.bob/custom_modes.yaml`.
- This file may already contain active modes used by your project.

------------------------------------------------------------------------

### ✏️ Append New Mode Configuration

1. Download and extract the `vault-secret-migrator.zip` file from this folder.
2. Open `.bob/custom_modes.yaml` in the Bob UI editor.
3. Add the Secrets Management mode at the end of the file.

#### Example:

```yaml
# Existing custom modes
- slug: existing-mode-1
  name: Existing Mode 1
  # ... existing configuration ...

- slug: existing-mode-2
  name: Existing Mode 2
  # ... existing configuration ...

# Add Secrets Management mode
- slug: vault-secret-migrator
  name: Secrets Management
  # ... new mode configuration ...
```

------------------------------------------------------------------------

### 📂 Maintain Rules Folder Structure

1. Navigate to `.bob/rules/`.
2. Add the new rules folder extracted from the zip:

```
vault-secret-migrator/
```

3. Ensure the final structure looks like:

```
.bob/
├── custom_modes.yaml
└── rules/
    ├── existing-mode-1/
    ├── existing-mode-2/
    └── vault-secret-migrator/
```

👉 Do **not modify or delete existing rule folders**.

------------------------------------------------------------------------

### ✅ Verify in Bob UI

After completing the setup:

- Go to **Modes / Custom Modes**.
- Confirm:
  - Existing modes are still available.
  - **Secrets Management** mode appears.
- Open the mode and ensure no configuration errors are shown.

------------------------------------------------------------------------

## 🧠 Best Practices

- Always **append**, never overwrite `custom_modes.yaml`.
- Keep each mode isolated under its own rules folder.
- Validate YAML formatting carefully (indentation matters).
- Reload the UI if changes are not reflected immediately.

------------------------------------------------------------------------

## 🎯 Outcome

After completing these steps:

- Secrets Management mode will be available in Bob UI.
- Existing modes will continue to function without disruption.
- You can start using the mode for **Secrets Management** workflows with HashiCorp Vault.
