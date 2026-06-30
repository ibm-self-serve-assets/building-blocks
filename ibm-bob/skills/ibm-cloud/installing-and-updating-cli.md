# Installing and updating the IBM Cloud CLI

Source scope:

- https://cloud.ibm.com/docs/cli?topic=cli-getting-started
- https://cloud.ibm.com/docs/cloud-shell?topic=cloud-shell-getting-started
- https://cloud.ibm.com/docs/cli?topic=cli-ibmcloud_cli

---

## Cloud Shell

Use when local installation is unnecessary:

```bash
ibmcloud help
ibmcloud version
ibmcloud target
```

Notes:

- IBM Cloud Shell includes the IBM Cloud CLI and common tooling.
- Cloud Shell sessions started from the console are already authenticated.
- Availability depends on account settings/permissions.

---

## Local install

macOS:

```bash
curl -fsSL https://clis.cloud.ibm.com/install/osx | sh
```

Linux:

```bash
curl -fsSL https://clis.cloud.ibm.com/install/linux | sh
```

WSL2:

```bash
curl -fsSL https://clis.cloud.ibm.com/install/linux | sh
```

Windows PowerShell, run as Administrator:

```powershell
iex (New-Object Net.WebClient).DownloadString('https://clis.cloud.ibm.com/install/powershell')
```

---

## Verify

```bash
ibmcloud help
ibmcloud version
```

---

## Update base CLI

```bash
ibmcloud update
ibmcloud update -f
```

Use `-f` only when confirmation bypass is explicitly requested.

---

## Post-install baseline

```bash
ibmcloud api cloud.ibm.com
ibmcloud login --sso
ibmcloud target -r us-south -g Default
ibmcloud plugin list
```

Automation baseline:

```bash
ibmcloud login --apikey @key_file_name -r us-south -g Default
ibmcloud target
```

---

## Install service plug-ins only when needed

```bash
ibmcloud plugin repo-plugins
ibmcloud plugin install PLUGIN_NAME
ibmcloud plugin update PLUGIN_NAME
ibmcloud plugin list
```

VPC:

```bash
ibmcloud plugin install vpc-infrastructure
ibmcloud is help
```
