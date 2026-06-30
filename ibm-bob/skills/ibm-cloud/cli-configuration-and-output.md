# CLI configuration, output, and debugging

Source scope:

- https://cloud.ibm.com/docs/cli?topic=cli-ibmcloud_cli
- https://cloud.ibm.com/docs/vpc?topic=vpc-vpc-reference

---

## Output

JSON examples:

```bash
ibmcloud resource groups --output json
ibmcloud resource service-instances --output json
ibmcloud is vpcs --output JSON
ibmcloud is instance INSTANCE --output JSON
```

Quiet mode:

```bash
ibmcloud resource groups -q
ibmcloud is vpcs -q
```

Use JSON for scripts. Do not parse table output when JSON is available.

---

## Help / discovery

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

## `ibmcloud config`

Only set one option per command.

```bash
# HTTP timeout.
ibmcloud config --http-timeout 30

# Trace.
ibmcloud config --trace true
ibmcloud config --trace /home/user/my_trace
ibmcloud config --trace false

# Color.
ibmcloud config --color false

# Locale.
ibmcloud config --locale zh_Hans
ibmcloud config --locale CLEAR

# SSO OTP behavior.
ibmcloud config --sso-otp auto

# Command display.
ibmcloud config --alpha-commands true

# Version checking.
ibmcloud config --check-version true
ibmcloud config --check-version false
```

Trace can expose sensitive request details. Disable after use.

---

## Script baseline

```bash
set -euo pipefail

ibmcloud login --apikey @key_file_name -r us-south -g Default
ibmcloud target
ibmcloud resource groups --output json
```

---

## Triage

| Symptom | Command/check |
|---|---|
| Noisy output | Add `-q` / `--quiet` if supported |
| Parsing failure | Use `--output json` / `--output JSON` |
| Timeout | `ibmcloud config --http-timeout SECONDS` |
| Need HTTP diagnostics | `ibmcloud config --trace true` or trace file |
| Color breaks parser | `ibmcloud config --color false` |
