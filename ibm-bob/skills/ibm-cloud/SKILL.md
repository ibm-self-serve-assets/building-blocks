---
name: ibmcloud-cli
description: >-
  Work with IBM Cloud by using the stand-alone `ibmcloud` CLI or IBM Cloud Shell.
  Use this whenever the user mentions IBM Cloud CLI, `ibmcloud`, Cloud Shell,
  installing or updating the CLI, logging in with IBMid, SSO, federated ID, API
  key, targeting an account, region, or resource group, configuring CLI defaults,
  managing CLI plug-ins, getting command help, using JSON output, troubleshooting
  CLI authentication/targeting issues, or using classic infrastructure commands
  through `ibmcloud sl`.
metadata:
  enabled: true
  author: IBM (adapted)
  version: "1.0.0"
---

# IBM Cloud CLI (`ibmcloud`)

Authoritative, practical guide for using the IBM Cloud Command Line Interface.
This skill is intentionally focused on the high-value commands and workflows that
matter most: install, verify, log in, target the right account/region/resource
group, configure output/debugging, manage plug-ins, and know when to use CLI
help for deeper service-specific details.

This is a **single-file skill**. Do not assume a companion `references/` folder.

> **Source scope**: This skill is grounded in the IBM Cloud CLI getting-started
> page and IBM documentation linked from that page, especially:
> - Getting started with the IBM Cloud CLI:
>   https://cloud.ibm.com/docs/cli?topic=cli-getting-started
> - General IBM Cloud CLI commands:
>   https://cloud.ibm.com/docs/cli?topic=cli-ibmcloud_cli
> - Extending IBM Cloud CLI with plug-ins:
>   https://cloud.ibm.com/docs/cli?topic=cli-plug-ins
> - Logging in with a federated ID:
>   https://cloud.ibm.com/docs/iam?interface=ui&topic=iam-federated_id
> - Getting started with IBM Cloud Shell:
>   https://cloud.ibm.com/docs/cloud-shell?topic=cloud-shell-getting-started
> - Getting help and support:
>   https://cloud.ibm.com/docs/cli?topic=cli-getting-help
>
> Avoid wandering into unrelated internet sources. For service-specific command
> details, use `ibmcloud help`, `ibmcloud <namespace> -h`, plug-in help, or the
> relevant IBM Cloud docs explicitly requested by the user.

---

## 1. Mental model

| Concept | What it means in the CLI |
|---|---|
| **CLI binary** | The local `ibmcloud` command, or the preinstalled CLI in IBM Cloud Shell. |
| **API endpoint** | The IBM Cloud API endpoint the CLI talks to. Usually `cloud.ibm.com`; private endpoint workflows use `private.cloud.ibm.com`. |
| **Login/session** | Authentication state for the CLI. Login can be interactive, SSO/federated, API-key based, or compute-resource based. |
| **Target** | The active account, region, and resource group. Always verify it before creating, deleting, or modifying resources. |
| **Resource group** | A scope used by many IBM Cloud resources. Targeting the wrong resource group is a common cause of “missing” resources. |
| **Region** | The target location for regional commands, for example `us-south` or `eu-gb`. |
| **Namespace** | A command group, such as `plugin`, `sl`, or a service plug-in namespace. |
| **Plug-in** | An extension that adds service-specific commands to the base CLI. |
| **Global options** | Options available to many commands, especially `--output json` and `-q, --quiet`. |

> **Golden rule #1 — always check the target.** Many `ibmcloud` commands depend
> on the current account, region, and resource group. Before changing resources,
> run `ibmcloud target` and confirm that the CLI is pointed at the intended
> account, region, and resource group.

> **Golden rule #2 — SSO for humans, API keys for automation.** Federated login
> with `--sso` requires a one-time passcode and is not suitable for automation.
> For scripts, use `ibmcloud login --apikey @KEY_FILE` or another noninteractive
> auth method supported by the user's environment.

> **Golden rule #3 — do not memorize everything.** The CLI is designed for
> discovery. Use `ibmcloud help`, `ibmcloud help COMMAND`, `ibmcloud COMMAND -h`,
> `ibmcloud plugin`, and plug-in-specific help instead of guessing obscure flags.

---

## 2. Install, use Cloud Shell, and verify

### Use IBM Cloud Shell when local setup is unnecessary

IBM Cloud Shell is a browser-based shell workspace from the IBM Cloud console.
It is preconfigured with the full IBM Cloud CLI, many plug-ins, and other tools.
A Cloud Shell session automatically logs you in through the IBM Cloud CLI.

Use Cloud Shell when:

- The user wants to start quickly without installing the CLI locally.
- The local machine has installation restrictions.
- The user needs a clean IBM-managed shell with common IBM Cloud tooling already available.

### Install the stand-alone CLI locally

macOS:

```bash
curl -fsSL https://clis.cloud.ibm.com/install/osx | sh
```

Linux:

```bash
curl -fsSL https://clis.cloud.ibm.com/install/linux | sh
```

Windows PowerShell, run as Administrator:

```powershell
iex (New-Object Net.WebClient).DownloadString('https://clis.cloud.ibm.com/install/powershell')
```

WSL2 on Windows:

```bash
curl -fsSL https://clis.cloud.ibm.com/install/linux | sh
```

### Verify the install

```bash
ibmcloud help
ibmcloud version
```

`ibmcloud help` displays usage instructions, the current version, and supported
commands. `ibmcloud version` prints the CLI version.

### Update the CLI

```bash
ibmcloud update
ibmcloud update -f
```

Use `-f` only when you intentionally want to force an update without
confirmation. Root privilege is required for forced update.

---

## 3. First-run workflow

A safe baseline workflow is:

```bash
# 1. Set or view the API endpoint.
ibmcloud api cloud.ibm.com
ibmcloud api

# 2. Log in. Use the method appropriate for the user.
ibmcloud login
# or, for federated/corporate SSO:
ibmcloud login --sso
# or, for automation:
ibmcloud login --apikey @key_file_name

# 3. Check available regions if needed.
ibmcloud regions

# 4. Set the intended target context.
ibmcloud target -r us-south -g Default

# 5. Verify the active account, region, and resource group.
ibmcloud target

# 6. Discover available commands.
ibmcloud help
```

When a command behaves unexpectedly, first check:

```bash
ibmcloud api
ibmcloud target
ibmcloud plugin list
ibmcloud version
```

---

## 4. API endpoint commands

### View or set the API endpoint

```bash
ibmcloud api
ibmcloud api cloud.ibm.com
ibmcloud api https://cloud.ibm.com
```

### Clear the configured endpoint

```bash
ibmcloud api --unset
```

### Private endpoint login patterns

```bash
ibmcloud login -a private.cloud.ibm.com
ibmcloud login -a private.cloud.ibm.com --vpc
```

`--vpc` is used for a VPC connection to a private API endpoint.

### Avoid `--skip-ssl-validation`

The CLI supports:

```bash
ibmcloud api https://cloud.ibm.com --skip-ssl-validation
ibmcloud login --skip-ssl-validation
```

But IBM documents that bypassing SSL validation is **not recommended**. Do not
suggest it as a normal fix. Use it only when the user explicitly understands the
tradeoff and is troubleshooting a controlled environment.

---

## 5. Login and authentication

### Interactive login

```bash
ibmcloud login
```

If the account has multiple accounts or regions, the CLI may prompt the user to
select the account and region.

### Login and target an account, region, or resource group

```bash
ibmcloud login -c ACCOUNT_ID
ibmcloud login -r us-south
ibmcloud login -g RESOURCE_GROUP_NAME
ibmcloud login -c ACCOUNT_ID -r us-south -g RESOURCE_GROUP_NAME
```

Useful options:

| Option | Purpose |
|---|---|
| `-a API_ENDPOINT` | Set the API endpoint during login. |
| `-c ACCOUNT_ID` | Target an account during login. |
| `-r REGION` | Target a region during login. |
| `-g RESOURCE_GROUP` | Target a resource group during login. |
| `--no-region` | Login without targeting a region. |
| `--no-account` | Force login without an account; not recommended. |
| `--accept` | Accept an invitation to join the targeted account. |

### Federated ID / SSO login

For users with a corporate or enterprise single sign-on identity:

```bash
ibmcloud login --sso
```

With an account target:

```bash
ibmcloud login --sso -c ACCOUNT_ID
```

The CLI provides a URL and prompts for a one-time passcode. The user opens the
URL, authenticates, copies the passcode, and enters it in the terminal.

You can make SSO passcode handling more automatic:

```bash
ibmcloud config --sso-otp auto
```

The default SSO OTP mode is manual. The `auto` setting launches the default
browser automatically and accepts the token.

### API-key login for automation

For scripts and noninteractive workflows, use an IBM Cloud API key:

```bash
ibmcloud login --apikey API_KEY_STRING
ibmcloud login --apikey @key_file_name
```

Prefer the file form to avoid exposing secrets in shell history:

```bash
ibmcloud login --apikey @key_file_name
```

If the API key has no associated account, specify an account:

```bash
ibmcloud login --apikey @key_file_name -c ACCOUNT_ID
```

Important notes:

- The API key must be an IBM Cloud platform API key, not a classic
  infrastructure API key and not a service-specific API key.
- If an API key has an associated account, switching to another account is not
  supported in that login context.
- Federated one-time passcode login is not automation-friendly; use an API key
  for scripts.

### Create an API key

The linked federated-login documentation includes this command:

```bash
ibmcloud iam api-key-create NAME -d DESCRIPTION --file FILE
```

Use `--file` when possible so the key is written to a file instead of printed in
the terminal.

### Logout

```bash
ibmcloud logout
```

---

## 6. Target account, region, and resource group

### View current target

```bash
ibmcloud target
```

If no options are specified, `ibmcloud target` displays the current account and
region context.

### Set account, region, or resource group

```bash
ibmcloud target -c ACCOUNT_ID
ibmcloud target -r eu-gb
ibmcloud target -g RESOURCE_GROUP_NAME
ibmcloud target -c ACCOUNT_ID -r us-south -g RESOURCE_GROUP_NAME
```

### Clear target values

```bash
ibmcloud target --unset-region
ibmcloud target --unset-resource-group
```

### List regions

```bash
ibmcloud regions
```

`ibmcloud regions` requires an API endpoint to be set.

### Targeting checklist before destructive changes

Before commands that create, update, or delete resources:

```bash
ibmcloud api
ibmcloud target
```

Confirm:

- API endpoint is expected.
- Account is expected.
- Region is expected.
- Resource group is expected.

---

## 7. Help, discovery, and command syntax

### General help

```bash
ibmcloud help
```

### Help for a command or namespace

```bash
ibmcloud help COMMAND
ibmcloud help NAMESPACE
ibmcloud COMMAND -h
ibmcloud NAMESPACE -h
```

Examples:

```bash
ibmcloud help login
ibmcloud help target
ibmcloud plugin -h
ibmcloud sl help
ibmcloud sl vs -h
```

### AI assistant command

The CLI includes:

```bash
ibmcloud assist "How do I update the CLI?"
```

Alias:

```bash
ibmcloud ai "How do I update the CLI?"
```

Use this as a convenience, not as a source of truth. IBM notes that generated
assistant content might include mistakes or be incorrect. Prefer official help
output and IBM docs for exact command syntax.

### Escaping quotes and exclamation marks

If a query or string contains quotation marks or exclamation marks, escape them
with `\` when needed by the shell and CLI context.

---

## 8. Output and scripting basics

### JSON output

Many commands support the global option:

```bash
--output json
```

Example:

```bash
ibmcloud resource groups --output json
```

Only JSON is supported for the documented `--output FORMAT` global option.
Use JSON output for scripts, parsing, and agent workflows.

### Quiet mode

```bash
-q
--quiet
```

Example:

```bash
ibmcloud resource groups -q
```

Quiet mode suppresses verbose messages such as prompt-style informational text.
Use it when command output will be parsed or embedded in another workflow.

### Automation login pattern

```bash
ibmcloud login --apikey @key_file_name -r us-south -g RESOURCE_GROUP_NAME
ibmcloud target
```

Avoid:

```bash
ibmcloud login --sso
```

in automation, because SSO passcode retrieval requires user interaction.

---

## 9. CLI configuration and debugging

`ibmcloud config` writes default values to the CLI configuration file. Only one
configuration option can be specified at a time.

### HTTP timeout

```bash
ibmcloud config --http-timeout 30
```

The default timeout is 60 seconds. Increase this when slow network calls are
expected; lower it only when fast failure is desirable.

### Trace HTTP requests

```bash
ibmcloud config --trace true
ibmcloud config --trace /path/to/trace_file
ibmcloud config --trace false
```

Use trace mode to debug CLI/API interactions. Trace output can expose sensitive
request details, so do not share trace files without reviewing/redacting them.

### Color output

```bash
ibmcloud config --color false
ibmcloud config --color true
```

Disable color when output will be parsed or pasted into logs.

### Locale

```bash
ibmcloud config --locale zh_Hans
ibmcloud config --locale CLEAR
```

### Version checking

```bash
ibmcloud config --check-version true
ibmcloud config --check-version false
```

### SSO one-time passcode behavior

```bash
ibmcloud config --sso-otp manual
ibmcloud config --sso-otp auto
```

### Alphabetical uncategorized commands

```bash
ibmcloud config --alpha-commands true
```

---

## 10. Plug-ins

IBM Cloud CLI supports a plug-in framework. Use plug-ins for many service-specific
commands.

### Discover available plug-ins

```bash
ibmcloud plugin repo-plugins
```

This lists available plug-ins in the repository, including names, versions, and
descriptions.

### Install a plug-in

```bash
ibmcloud plugin install PLUGIN_NAME
```

Example from IBM docs:

```bash
ibmcloud plugin install code-engine
```

### Install a specific version

```bash
ibmcloud plugin install PLUGIN_NAME@VERSION
```

Example:

```bash
ibmcloud plugin install container-service@1.0.506 secrets-manager@0.1.25
```

### Install all latest repository plug-ins

```bash
ibmcloud plugin install -a
```

Use this only when the user really wants all plug-ins. For most workflows, install
only the plug-ins needed for the task.

### Confirm installed plug-ins

```bash
ibmcloud plugin list
```

The list includes plug-in name, current version, whether a newer version is
available, and whether the plug-in version supports private endpoint use.

### Update plug-ins

```bash
ibmcloud plugin update
```

### Get plug-in help

```bash
ibmcloud plugin
ibmcloud plugin -h
ibmcloud plugin show PLUGIN_NAME
```

For a service plug-in namespace, use:

```bash
ibmcloud NAMESPACE -h
ibmcloud NAMESPACE COMMAND -h
```

---

## 11. Classic infrastructure commands

Classic infrastructure commands are grouped under `ibmcloud sl`.

### View classic infrastructure help

```bash
ibmcloud sl help
ibmcloud sl [command] -h
```

Examples of classic infrastructure command groups include:

| Command group | Area |
|---|---|
| `block` | Classic infrastructure Block Storage |
| `file` | Classic infrastructure File Storage |
| `dns` | Classic infrastructure Domain Name System |
| `globalip` | Global IP addresses |
| `hardware` | Hardware servers |
| `image` | Compute images |
| `ipsec` | IPSEC VPN |
| `order` | Orders |
| `placement-group` | Placement groups |
| `security` | SSH keys and SSL certificates |
| `securitygroup` | Network security groups |
| `subnet` | Network subnets |
| `ticket` | Tickets |
| `user` | Users |
| `vlan` | Network VLANs |
| `vs` | Virtual servers |

Do not go deep on classic infrastructure unless the user specifically asks. Use
`ibmcloud sl [command] -h` to inspect exact syntax.

Important: `ibmcloud sl init` is no longer available as of CLI version `0.14`.

---

## 12. Critical command map

| Need | Command |
|---|---|
| Show general help | `ibmcloud help` |
| Show help for a command or namespace | `ibmcloud help COMMAND` / `ibmcloud COMMAND -h` |
| Show CLI version | `ibmcloud version` |
| Set API endpoint | `ibmcloud api cloud.ibm.com` |
| View API endpoint | `ibmcloud api` |
| Clear API endpoint | `ibmcloud api --unset` |
| Interactive login | `ibmcloud login` |
| Federated SSO login | `ibmcloud login --sso` |
| API-key login | `ibmcloud login --apikey @key_file_name` |
| Login and target account | `ibmcloud login -c ACCOUNT_ID` |
| Logout | `ibmcloud logout` |
| List regions | `ibmcloud regions` |
| View current target | `ibmcloud target` |
| Set account target | `ibmcloud target -c ACCOUNT_ID` |
| Set region target | `ibmcloud target -r REGION` |
| Set resource group target | `ibmcloud target -g RESOURCE_GROUP` |
| Clear region target | `ibmcloud target --unset-region` |
| Clear resource group target | `ibmcloud target --unset-resource-group` |
| Update CLI | `ibmcloud update` |
| Configure timeout | `ibmcloud config --http-timeout SECONDS` |
| Enable trace | `ibmcloud config --trace true` |
| Trace to file | `ibmcloud config --trace /path/to/file` |
| Disable color | `ibmcloud config --color false` |
| SSO OTP auto mode | `ibmcloud config --sso-otp auto` |
| JSON output | `COMMAND --output json` |
| Quiet output | `COMMAND -q` |
| List available plug-ins | `ibmcloud plugin repo-plugins` |
| Install plug-in | `ibmcloud plugin install PLUGIN_NAME` |
| List installed plug-ins | `ibmcloud plugin list` |
| Update installed plug-ins | `ibmcloud plugin update` |
| Classic infrastructure help | `ibmcloud sl help` |

---

## 13. Common workflows

### Install locally and log in with SSO

```bash
curl -fsSL https://clis.cloud.ibm.com/install/osx | sh
ibmcloud help
ibmcloud login --sso
ibmcloud target
```

Use the Linux or Windows install command instead of the macOS command when needed.

### Use Cloud Shell instead of local install

1. Open IBM Cloud console.
2. Click the Cloud Shell icon.
3. Start running `ibmcloud` commands; the session automatically logs in through
   the IBM Cloud CLI.

### Log in for automation with an API key file

```bash
ibmcloud login --apikey @key_file_name -c ACCOUNT_ID -r us-south -g RESOURCE_GROUP_NAME
ibmcloud target
```

### Switch region and verify

```bash
ibmcloud target -r eu-gb
ibmcloud target
```

### Install a needed service plug-in

```bash
ibmcloud plugin repo-plugins
ibmcloud plugin install PLUGIN_NAME
ibmcloud plugin list
ibmcloud PLUGIN_NAMESPACE -h
```

### Debug a failing command

```bash
ibmcloud version
ibmcloud api
ibmcloud target
ibmcloud plugin list
ibmcloud COMMAND -h
```

If the failure appears API-related:

```bash
ibmcloud config --trace /tmp/ibmcloud-trace.log
# run the failing command
ibmcloud config --trace false
```

Review and redact trace output before sharing it.

---

## 14. Troubleshooting playbook

| Symptom | Likely cause | First checks / fixes |
|---|---|---|
| Command says not logged in | No active CLI session or expired session | Run `ibmcloud login`, `ibmcloud login --sso`, or `ibmcloud login --apikey @key_file_name`. |
| Federated login fails in a script | `--sso` requires one-time passcode interaction | Use an IBM Cloud API key: `ibmcloud login --apikey @key_file_name`. |
| Resources seem missing | Wrong account, region, or resource group | Run `ibmcloud target`; then set `-c`, `-r`, or `-g` as needed. |
| Command targets wrong account | API key is associated with a specific account | Use the correct API key/account. IBM docs note that switching to another account is not supported when the API key has an associated account. |
| Region-specific command fails | Region not targeted or wrong region targeted | Run `ibmcloud regions`, then `ibmcloud target -r REGION`. |
| Service command not found | Required plug-in is not installed | Run `ibmcloud plugin repo-plugins`, install the needed plug-in, then run `ibmcloud plugin list`. |
| Plug-in command syntax unknown | Service-specific syntax is outside base CLI | Run `ibmcloud NAMESPACE -h` or `ibmcloud NAMESPACE COMMAND -h`. |
| Output parsing is brittle | Human-readable output includes prompts/status text | Use `--output json` where supported and `-q` for quieter output. |
| CLI/API behavior is unclear | Need request-level diagnostics | Use `ibmcloud config --trace /path/to/file`, then disable trace after testing. |
| SSL workaround suggested | `--skip-ssl-validation` bypasses SSL validation | Avoid unless explicitly debugging a controlled environment; IBM marks it as not recommended. |
| User asks for an obscure command | Not in this focused skill | Use CLI help and IBM docs: `ibmcloud help`, `ibmcloud COMMAND -h`, plug-in help. |

---

## 15. Safe handling of credentials

- Prefer `ibmcloud login --apikey @key_file_name` over passing raw API keys on the
  command line.
- Do not paste API keys into examples unless the user explicitly provides a dummy
  value.
- Do not print, log, or store real API keys in generated artifacts.
- Use `--file` when creating API keys so the key is written to a file rather than
  displayed in the terminal.
- Review trace files before sharing; HTTP trace output can include sensitive
  information.

---

## 16. When to use help instead of expanding the skill

This skill should not attempt to document every IBM Cloud service command or every
plug-in flag. Use built-in help when the user moves beyond the core CLI:

```bash
ibmcloud help
ibmcloud help COMMAND
ibmcloud COMMAND -h
ibmcloud plugin
ibmcloud plugin show PLUGIN_NAME
ibmcloud NAMESPACE -h
ibmcloud NAMESPACE COMMAND -h
ibmcloud sl [command] -h
```

For exact syntax, trust the installed CLI help because plug-in versions can differ
between environments.
