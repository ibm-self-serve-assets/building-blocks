# Bob Skills for Data Sync with IBM Aspera

Bob skills for **IBM Aspera Sync** — high-speed WAN file and repository synchronization using the FASP transport protocol.

## Overview

This skill gives IBM Bob expert knowledge of IBM Aspera Sync configuration, topology design, FASP transport parameters, large-scale file handling, and integration with downstream analytics and AI pipelines.

## Available Skills

> **Coming soon** — `aspera-sync-configuration.zip` is not yet committed to this repository. The documentation below describes the intended skill capabilities. Check this directory for availability.

| Skill | Zip | Use When |
|---|---|---|
| `aspera-sync-configuration` | `aspera-sync-configuration.zip` | Configuring IBM Aspera Sync for WAN file repository synchronization |

---

### `aspera-sync-configuration`

A comprehensive skill for IBM Aspera Sync deployments:

- IBM Aspera Sync synchronization relationship setup and configuration
- FASP transport protocol — bandwidth control, encryption (AES-128 in transit), UDP port configuration
- Synchronization topology selection: unidirectional, bidirectional, mesh
- Incremental synchronization — change detection, transmitting only modified files and operations
- File filtering — include/exclude patterns for large repositories
- Scheduler configuration for recurring synchronization runs
- Conflict and deletion handling for bidirectional topologies
- Performance tuning — target rate, minimum rate, adaptive rate control
- Network prerequisites — FASP UDP port requirements, firewall rules
- Integration of the synchronized destination with downstream analytics or AI pipelines

---

## Installation

### Step 1 — Install the skill

```bash
# From the root of your Bob workspace project
unzip aspera-sync-configuration.zip
```

This will create:
```
.bob/skills/aspera-sync-configuration/SKILL.md
```

### Step 2 — Enable in IBM Bob

Open IBM Bob → Skills panel → enable the skill. Bob will use it as active context for every prompt in this workspace.

### Step 3 — Verify

Ask Bob: *"What IBM Aspera Sync skills do you have active?"*

---

## Usage Examples

- *"Configure an IBM Aspera Sync relationship to synchronize a 10 TB repository from an on-premises server to IBM Cloud"*
- *"What topology should I use to keep two data centres synchronized when both sides can write new files?"*
- *"How do I set up incremental synchronization so that only changed files are transmitted after the initial full sync?"*
- *"What firewall rules and ports does IBM Aspera Sync require for FASP UDP transport?"*
- *"Design a synchronization pattern for distributing AI training data from a central repository to three regional sites"*

---

## Prerequisites

Before using this skill, ensure you have:

- IBM Aspera Sync licence
- Network access between source and destination hosts on the FASP UDP port (default 33001)
- Administrative access to configure IBM Aspera Sync on source and destination hosts

---

## Related

- [`../bob-modes/`](../bob-modes/) — Aspera Sync Builder Bob Mode
- [`../README.md`](../README.md) — Data Sync building block overview
