# IBM Cloud CLI plug-in management

Source scope:

- https://cloud.ibm.com/docs/cli?topic=cli-plug-ins
- https://cloud.ibm.com/docs/cli?topic=cli-ibmcloud_commands_settings
- https://cloud.ibm.com/docs/vpc?topic=vpc-vpc-reference

---

## Repositories

```bash
ibmcloud plugin repos
ibmcloud plugin repo-plugins
ibmcloud plugin repo-plugins -r REPO_NAME
ibmcloud plugin repo-plugin PLUGIN_NAME
ibmcloud plugin repo-plugin PLUGIN_NAME -r REPO_NAME
```

Official IBM Cloud plug-in repository URL:

```text
https://plugins.cloud.ibm.com
```

Add/remove repo:

```bash
ibmcloud plugin repo-add REPO_NAME REPO_URL
ibmcloud plugin repo-remove REPO_NAME
```

---

## Install

```bash
ibmcloud plugin install PLUGIN_NAME
ibmcloud plugin install PLUGIN_NAME -r "IBM Cloud"
ibmcloud plugin install PLUGIN_NAME -v VERSION
ibmcloud plugin install container-service@1.0.506 secrets-manager@0.1.25
ibmcloud plugin install --all
ibmcloud plugin install --all -f
```

Local/URL install only from trusted sources:

```bash
ibmcloud plugin install /path/to/plugin
ibmcloud plugin install https://example.com/path/to/plugin
```

---

## List/show

```bash
ibmcloud plugin list
ibmcloud plugin show PLUGIN_NAME
```

`plugin list` shows installed version, available updates, and private-endpoint
support information.

---

## Update

```bash
ibmcloud plugin update
ibmcloud plugin update PLUGIN_NAME
ibmcloud plugin update PLUGIN_NAME -v VERSION
ibmcloud plugin update --all
```

---

## Download / uninstall

```bash
ibmcloud plugin download PLUGIN_NAME
ibmcloud plugin download PLUGIN_NAME -v VERSION -d ~/downloads
ibmcloud plugin download --all
ibmcloud plugin uninstall PLUGIN_NAME
```

---

## VPC infrastructure plug-in

```bash
ibmcloud plugin install vpc-infrastructure
ibmcloud plugin update vpc-infrastructure
ibmcloud plugin list
ibmcloud is help
```

VPC command namespace: `ibmcloud is ...`.

Load `vpc-infrastructure-plugin.md` for VPC commands.

---

## Triage

| Symptom | Command/check |
|---|---|
| Namespace missing | `ibmcloud plugin list`; install plug-in |
| Syntax differs | `ibmcloud plugin update PLUGIN_NAME`; `ibmcloud PLUGIN_NAMESPACE help` |
| Need command list | `ibmcloud plugin show PLUGIN_NAME` |
| Private endpoint issue | Check private endpoint support in `ibmcloud plugin list` |
