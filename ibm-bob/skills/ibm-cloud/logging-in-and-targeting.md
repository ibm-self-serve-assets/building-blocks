# Logging in and targeting IBM Cloud

Source scope:

- https://cloud.ibm.com/docs/cli?topic=cli-getting-started
- https://cloud.ibm.com/docs/cli?topic=cli-ibmcloud_cli
- https://cloud.ibm.com/docs/iam?interface=ui&topic=iam-federated_id

---

## API endpoint

```bash
ibmcloud api
ibmcloud api cloud.ibm.com
ibmcloud api https://cloud.ibm.com
ibmcloud api --unset
```

Private endpoint patterns:

```bash
ibmcloud login -a private.cloud.ibm.com
ibmcloud login -a private.cloud.ibm.com --vpc
```

Avoid `--skip-ssl-validation` unless explicitly requested.

---

## Interactive login

```bash
ibmcloud login
ibmcloud login -c ACCOUNT_ID -r us-south -g Default
```

---

## Federated / SSO login

```bash
ibmcloud login --sso
ibmcloud login --sso -c ACCOUNT_ID
```

SSO/passcode login is interactive. Do not use for unattended scripts.

---

## API-key login

Create API key:

```bash
ibmcloud iam api-key-create NAME -d DESCRIPTION --file key_file_name
```

Login:

```bash
ibmcloud login --apikey API_KEY_STRING
ibmcloud login --apikey @key_file_name
ibmcloud login --apikey @key_file_name -r us-south -g Default
```

PowerShell file reference:

```powershell
ibmcloud login --apikey '@key_file_name'
```

Environment variable:

```bash
export IBMCLOUD_API_KEY=api_key_string
ibmcloud login
```

Use IBM Cloud platform API keys for CLI login.

---

## Compute-resource login

VPC VSI compute resource identity:

```bash
ibmcloud login --vpc-cri
ibmcloud login --vpc-cri --profile trusted_profile_id_or_crn
IBMCLOUD_CR_PROFILE=trusted_profile_id_or_crn ibmcloud login --vpc-cri
```

Compute resource token:

```bash
ibmcloud login --cr-token token-string --profile trusted_profile_name_id_or_crn
ibmcloud login --cr-token @filename --profile trusted_profile_name_id_or_crn
IBMCLOUD_CR_TOKEN=@filename ibmcloud login --profile trusted_profile_name_id_or_crn
```

---

## Targeting

Show current context:

```bash
ibmcloud target
```

Set context:

```bash
ibmcloud target -c ACCOUNT_ID
ibmcloud target -r us-south
ibmcloud target -g Default
ibmcloud target -r us-south -g Default
```

Unset context:

```bash
ibmcloud target --unset-region
ibmcloud target --unset-resource-group
```

List regions:

```bash
ibmcloud regions
```

Logout:

```bash
ibmcloud logout
```

---

## Triage

| Symptom | Command/check |
|---|---|
| Wrong/missing resources | `ibmcloud target` |
| Corporate login fails | `ibmcloud login --sso` |
| Script login blocks | `ibmcloud login --apikey @key_file_name` |
| Private endpoint issue | Check endpoint and `--vpc` requirement |
| API key rejected | Confirm platform API key |
