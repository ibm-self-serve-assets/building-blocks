---
name: ibmcloud-cli
description: >-
  Use this skill to learn hot to use the IBM Cloud CLI (`ibmcloud`) commands, flags, command patterns, or troubleshooting guidance. 
  Covers core CLI workflows: install/verify/update, login with SSO or API keys, select account/region/resource group targets, 
  inspect and configure CLI output, manage plug-ins (e.g. `vpc-infrastructure` / `ibmcloud is ...` for VPC infrastructure.).
metadata:
  enabled: true
  author: IBM (adapted)
  version: "1.2.0"
---

# IBM Cloud CLI (`ibmcloud`)

Command-focused router skill for senior engineers. Keep this file lightweight;
load companion `.md` files for specific command families.

Source scope:

- https://cloud.ibm.com/docs/cli?topic=cli-getting-started
- https://cloud.ibm.com/docs/cli?topic=cli-ibmcloud_cli
- https://cloud.ibm.com/docs/cli?topic=cli-plug-ins
- https://cloud.ibm.com/docs/cli?topic=cli-ibmcloud_commands_settings
- https://cloud.ibm.com/docs/iam?interface=ui&topic=iam-federated_id
- https://cloud.ibm.com/docs/cloud-shell?topic=cloud-shell-getting-started
- https://cloud.ibm.com/media/docs/downloads/IBM%20Cloud%20CLI%20quick%20reference.pdf
- https://cloud.ibm.com/docs/vpc?topic=vpc-vpc-reference

Do not add service-specific command catalogs here. Add/maintain a focused
companion `.md` file instead.

---

## Critical defaults

```bash
ibmcloud help
ibmcloud version
ibmcloud api
ibmcloud target
ibmcloud plugin list
```

Rules:

- Verify `ibmcloud target` before create/update/delete.
- Use `ibmcloud login --sso` for federated humans.
- Use `ibmcloud login --apikey @key_file_name` for automation.
- Use `--output json` / `--output JSON` for scripting when supported.
- Do not use `-f` / `--force` unless explicitly requested.
- Use exact command help instead of guessing flags: `ibmcloud COMMAND -h`.

---

## Minimal workflow

```bash
# Install locally or use IBM Cloud Shell.
ibmcloud help
ibmcloud version

# Endpoint.
ibmcloud api cloud.ibm.com
ibmcloud api

# Login.
ibmcloud login
ibmcloud login --sso
ibmcloud login --apikey @key_file_name

# Targeting.
ibmcloud regions
ibmcloud target -r us-south -g Default
ibmcloud target

# Plug-ins.
ibmcloud plugin list
ibmcloud plugin repo-plugins
```

VPC infrastructure:

```bash
ibmcloud plugin install vpc-infrastructure
ibmcloud plugin update vpc-infrastructure
ibmcloud plugin list
ibmcloud is help
```

---

## Load companion files

| File | Use for |
|---|---|
| `installing-and-updating-cli.md` | Install, verify, version, update, Cloud Shell. |
| `logging-in-and-targeting.md` | API endpoint, login, SSO, API keys, compute-resource login, target, logout. |
| `cli-configuration-and-output.md` | Global options, JSON output, quiet mode, trace, timeout, color, locale, config. |
| `plugin-management.md` | Plug-in repos, install, update, show, list, download, uninstall. |
| `resource-groups-and-account-context.md` | Resource groups, catalog, service instances, tags, IAM/API keys, users, billing basics. |
| `vpc-infrastructure-plugin.md` | `vpc-infrastructure` plug-in and `ibmcloud is ...` VPC infrastructure commands. |

---

## Command discovery

```bash
ibmcloud help
ibmcloud help login
ibmcloud help target
ibmcloud COMMAND -h
ibmcloud plugin
ibmcloud plugin show PLUGIN_NAME
ibmcloud is help
ibmcloud is instance-create -h
```

---

## Failure triage

```bash
ibmcloud version
ibmcloud api
ibmcloud target
ibmcloud plugin list
ibmcloud help COMMAND
```

| Symptom | Check |
|---|---|
| Resource missing | Account, region, resource group: `ibmcloud target`. |
| Login fails for enterprise user | Use `ibmcloud login --sso` or API-key login. |
| Script hangs at login | Replace SSO/passcode login with API-key login. |
| Namespace missing | Install/update the required plug-in. |
| Output parsing fails | Use JSON output where available. |
| Delete prompts | Do not add `-f` unless explicitly approved. |
