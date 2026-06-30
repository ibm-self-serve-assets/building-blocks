# IBM Cloud VPC infrastructure plug-in (`vpc-infrastructure`, `ibmcloud is`)

Source scope:

- https://cloud.ibm.com/docs/vpc?topic=vpc-vpc-reference
- https://cloud.ibm.com/docs/cli?topic=cli-getting-started
- https://cloud.ibm.com/docs/cli?topic=cli-plug-ins
- https://cloud.ibm.com/docs/cli?topic=cli-ibmcloud_commands_settings

---

## Install / verify

```bash
ibmcloud plugin install vpc-infrastructure
ibmcloud plugin update vpc-infrastructure
ibmcloud plugin list
ibmcloud is help
```

Namespace: `ibmcloud is ...`.

---

## Operating rules

```bash
ibmcloud target -r REGION -g RESOURCE_GROUP
ibmcloud target
ibmcloud is help
ibmcloud is COMMAND -h
```

Rules:

- VPC resources are regional/zonal; target region first.
- Discover IDs/names before create/update/delete.
- Prefer IDs in automation.
- Use `--output JSON` for scripts where supported.
- Avoid `-f` / `--force` unless explicitly approved.

---

## Discovery baseline

```bash
ibmcloud is regions --output JSON
ibmcloud is zones --output JSON
ibmcloud is vpcs --output JSON
ibmcloud is subnets --output JSON
ibmcloud is security-groups --output JSON
ibmcloud is images --output JSON
ibmcloud is instance-profiles --output JSON
ibmcloud is keys --output JSON
```

---

## Command families

| Resource | Commands |
|---|---|
| Regions/zones | `regions`, `region`, `zones`, `zone` |
| VPCs | `vpcs`, `vpc`, `vpc-create`, `vpc-update`, `vpc-delete` |
| Address prefixes | `vpc-address-prefixes`, `vpc-address-prefix-create`, `vpc-address-prefix-delete` |
| Subnets | `subnets`, `subnet`, `subnet-create`, `subnet-update`, `subnet-delete` |
| Security groups | `security-groups`, `security-group`, `security-group-create`, `security-group-rule-add` |
| Floating IPs | `floating-ips`, `floating-ip`, `floating-ip-reserve`, `floating-ip-release` |
| Public gateways | `public-gateways`, `public-gateway`, create/update/delete family |
| Images/OS | `images`, `image`, `operating-systems`, `operating-system` |
| Profiles | `instance-profiles`, `instance-profile` |
| SSH keys | `keys`, `key`, key create/update/delete family |
| VSIs | `instances`, `instance`, `instance-create`, start/stop/reboot/delete family |
| Volumes | `volumes`, `volume`, create/update/delete/attach family |
| File shares | `shares`, `share`, `share-create`, `share-delete`, `share-profiles` |

Use exact help for arguments:

```bash
ibmcloud is vpc-create -h
ibmcloud is subnet-create -h
ibmcloud is instance-create -h
ibmcloud is security-group-rule-add -h
```

---

## Regions / zones

```bash
ibmcloud is regions
ibmcloud is regions --output JSON
ibmcloud is region REGION_NAME
ibmcloud is zones
ibmcloud is zones --output JSON
ibmcloud is zone ZONE_NAME
```

---

## VPCs / address prefixes

```bash
# Create VPC.
ibmcloud is vpc-create VPC_NAME
ibmcloud is vpc-create VPC_NAME --address-prefix-management auto
ibmcloud is vpc-create VPC_NAME --address-prefix-management manual
ibmcloud is vpc-create VPC_NAME --resource-group-name Default --output JSON

# List/show.
ibmcloud is vpcs
ibmcloud is vpcs --output JSON
ibmcloud is vpc VPC
ibmcloud is vpc VPC --output JSON

# Address prefixes.
ibmcloud is vpc-address-prefixes VPC
ibmcloud is vpc-address-prefix-create PREFIX_NAME VPC ZONE_NAME CIDR
ibmcloud is vpc-address-prefix-delete VPC PREFIX

# Delete.
ibmcloud is vpc-delete VPC
```

`--address-prefix-management auto | manual` controls default address prefix
creation.

---

## Subnets

```bash
# CIDR-based.
ibmcloud is subnet-create SUBNET_NAME VPC --ipv4-cidr-block 10.10.10.0/24

# Address-count-based.
ibmcloud is subnet-create SUBNET_NAME VPC --ipv4-address-count 256 --zone us-south-2

# List/show.
ibmcloud is subnets
ibmcloud is subnets --output JSON
ibmcloud is subnet SUBNET
ibmcloud is subnet SUBNET --vpc VPC --show-attached --output JSON

# Update/delete.
ibmcloud is subnet-update SUBNET [OPTIONS]
ibmcloud is subnet-delete SUBNET
```

`--ipv4-cidr-block` and `--ipv4-address-count` are mutually exclusive. If using
address count, specify `--zone`.

---

## Security groups

```bash
# Create/list/show.
ibmcloud is security-group-create GROUP_NAME VPC
ibmcloud is security-group-create GROUP_NAME VPC --resource-group-name Default --output JSON
ibmcloud is security-groups
ibmcloud is security-groups --output JSON
ibmcloud is security-group GROUP --vpc VPC --output JSON

# Inbound TCP, for example SSH.
ibmcloud is security-group-rule-add GROUP inbound tcp \
  --port-min 22 \
  --port-max 22 \
  --remote CIDR_BLOCK \
  --vpc VPC

# Inbound ICMP echo request.
ibmcloud is security-group-rule-add GROUP inbound icmp \
  --icmp-type 8 \
  --icmp-code 0 \
  --remote CIDR_BLOCK \
  --vpc VPC
```

Do not default to `0.0.0.0/0`; require explicit user intent.

---

## Floating IPs / public gateways

```bash
# Floating IPs.
ibmcloud is floating-ips
ibmcloud is floating-ips --output JSON
ibmcloud is floating-ip FLOATING_IP --output JSON
ibmcloud is floating-ip-reserve FLOATING_IP_NAME --zone us-south-1
ibmcloud is floating-ip-reserve FLOATING_IP_NAME --nic TARGET_INTERFACE --in TARGET_INSTANCE
ibmcloud is floating-ip-release FLOATING_IP

# Public gateways.
ibmcloud is public-gateways
ibmcloud is public-gateway PUBLIC_GATEWAY
ibmcloud is public-gateway PUBLIC_GATEWAY --output JSON
ibmcloud is public-gateway-create -h
ibmcloud is public-gateway-delete -h
```

Releasing floating IPs can lose the address.

---

## Images / OS / profiles / keys

```bash
# Operating systems.
ibmcloud is operating-systems --output JSON
ibmcloud is operating-system OPERATING_SYSTEM_NAME --output JSON

# Images.
ibmcloud is images --output JSON
ibmcloud is images --visibility public --output JSON
ibmcloud is image IMAGE --output JSON

# Profiles.
ibmcloud is instance-profiles --output JSON
ibmcloud is instance-profile PROFILE_NAME --output JSON

# SSH keys.
ibmcloud is keys --output JSON
ibmcloud is key KEY --output JSON
ibmcloud is key-create -h
```

Resolve image/profile/key before `instance-create`.

---

## Virtual server instances

```bash
# List/show.
ibmcloud is instances
ibmcloud is instances --output JSON
ibmcloud is instance INSTANCE
ibmcloud is instance INSTANCE --output JSON

# Create.
ibmcloud is instance-create INSTANCE_NAME VPC ZONE PROFILE SUBNET --image IMAGE
ibmcloud is instance-create my-instance my-vpc us-south-1 bx2-2x8 my-subnet \
  --image ibm-ubuntu-20-04-2-minimal-amd64-1 \
  --output JSON

# Exact syntax for advanced inputs.
ibmcloud is instance-create -h
```

Before delete, check attached volumes, floating IPs, and auto-delete settings.

```bash
ibmcloud is instance-delete INSTANCE
```

---

## Volumes / file shares

```bash
# Volumes.
ibmcloud is volumes
ibmcloud is volumes --output JSON
ibmcloud is volumes --zone us-south-1 --output JSON
ibmcloud is volumes --attachment-state unattached --output JSON
ibmcloud is volume VOLUME --output JSON
ibmcloud is volume-create -h
ibmcloud is volume-attach -h
ibmcloud is volume-delete -h

# File shares.
ibmcloud is shares --output JSON
ibmcloud is share SHARE --output JSON
ibmcloud is share-profiles --output JSON
ibmcloud is share-create -h
ibmcloud is share-delete -h
```

File share deletion cannot be undone.

---

## Basic VSI create sequence

```bash
# 1. Context.
ibmcloud target -r us-south -g Default
ibmcloud target

# 2. Plug-in.
ibmcloud plugin list
ibmcloud is help

# 3. Discovery.
ibmcloud is zones --output JSON
ibmcloud is images --output JSON
ibmcloud is instance-profiles --output JSON
ibmcloud is keys --output JSON

# 4. Network.
ibmcloud is vpc-create my-vpc --resource-group-name Default --output JSON
ibmcloud is subnet-create my-subnet my-vpc --ipv4-address-count 256 --zone us-south-1 --output JSON
ibmcloud is security-group-create my-sg my-vpc --output JSON

# 5. Security group rule.
ibmcloud is security-group-rule-add my-sg inbound tcp \
  --port-min 22 \
  --port-max 22 \
  --remote YOUR_CIDR \
  --vpc my-vpc

# 6. Instance.
ibmcloud is instance-create my-instance my-vpc us-south-1 bx2-2x8 my-subnet \
  --image IMAGE \
  --output JSON

# 7. Optional floating IP.
ibmcloud is floating-ip-reserve my-ip --zone us-south-1 --output JSON
```

Replace `IMAGE`, `YOUR_CIDR`, region, zone, profile, and names with discovered
values.

---

## Triage

| Symptom | Command/check |
|---|---|
| `ibmcloud is` missing | `ibmcloud plugin install vpc-infrastructure`; `ibmcloud plugin list` |
| Resource not found | `ibmcloud target`; use IDs; add `--vpc` where needed |
| Invalid zone/profile | `ibmcloud is zones`; `ibmcloud is instance-profiles` |
| Invalid image | `ibmcloud is images --output JSON` |
| Subnet failure | VPC, zone, CIDR/address count, address-prefix mode |
| SG rule too broad | Narrow protocol, ports, remote CIDR/security group |
| Delete prompts | Do not use `-f` without approval |
| Complex JSON unclear | Use `ibmcloud is COMMAND -h`; prefer `@file` where supported |
