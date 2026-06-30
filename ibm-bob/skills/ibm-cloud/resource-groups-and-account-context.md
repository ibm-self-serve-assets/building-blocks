# Resource groups, catalog, service instances, account, IAM, and billing commands

Source scope:

- https://cloud.ibm.com/docs/cli?topic=cli-ibmcloud_cli
- https://cloud.ibm.com/media/docs/downloads/IBM%20Cloud%20CLI%20quick%20reference.pdf
- https://cloud.ibm.com/docs/iam?interface=ui&topic=iam-federated_id

---

## Context

```bash
ibmcloud api
ibmcloud login --sso
ibmcloud login --apikey @key_file_name
ibmcloud target
ibmcloud target -c ACCOUNT_ID
ibmcloud target -r us-south
ibmcloud target -g Default
ibmcloud target -r us-south -g Default
```

---

## Resource groups

```bash
ibmcloud resource groups
ibmcloud resource groups --output json
ibmcloud resource group create GROUP_NAME
ibmcloud target -g GROUP_NAME
```

---

## Catalog

```bash
ibmcloud catalog search QUERY
ibmcloud catalog search "kube"
ibmcloud catalog service NAME
ibmcloud catalog service containers-kubernetes
```

---

## Service instances

Create:

```bash
ibmcloud resource service-instance-create NAME SERVICE_NAME PLAN_NAME LOCATION
ibmcloud resource service-instance-create myKubeCluster containers-kubernetes lite us-south
```

List:

```bash
ibmcloud resource service-instances
ibmcloud resource service-instances -g GROUP_NAME
ibmcloud resource service-instances --output json
```

Before create, resolve exact `SERVICE_NAME`, `PLAN_NAME`, `LOCATION`, and target
resource group.

---

## Tags

```bash
ibmcloud resource tags
ibmcloud resource tag-attach --tag-names TAG --resource-name NAME
ibmcloud resource tag-attach --tag-names myTeamTag --resource-name myKubeCluster
```

Tags organize resources; do not treat tags as IAM enforcement.

---

## Account users / billing

```bash
ibmcloud account user-invite USER_EMAIL
ibmcloud account users
ibmcloud billing account-usage
ibmcloud billing account-usage -d YYYY-MM
```

`ibmcloud account users` can require account-owner permissions.

---

## IAM / API keys / access

```bash
# API keys.
ibmcloud iam api-key-create NAME -d DESCRIPTION
ibmcloud iam api-key-create NAME -d DESCRIPTION --file key_file_name
ibmcloud login --apikey @key_file_name

# User policy.
ibmcloud iam user-policy-create USER_NAME [OPTIONS]
ibmcloud iam user-policy-create user@example.com --roles Editor

# Access group.
ibmcloud iam access-group-create NAME
ibmcloud iam access-group-create myAdminGroup
```

Rules:

- Prefer file-based API-key handling: `--file`, `--apikey @file`.
- Keep IAM roles/scope explicit.
- Do not generate broad grants unless requested.

---

## Project plug-in note

```bash
ibmcloud project list
```

Requires the `project` plug-in.

```bash
ibmcloud plugin list
ibmcloud plugin repo-plugins
```

---

## Triage

| Symptom | Command/check |
|---|---|
| Service instance missing | `ibmcloud target`; resource group |
| Unknown service/plan | `ibmcloud catalog search`; `ibmcloud catalog service` |
| Permission failure | IAM role/scope; target account/resource group |
| API key exposed | Use `--file` and `--apikey @file` |
| Billing/account failure | Account owner/admin permissions |
