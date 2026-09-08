# Bob Mode for Data Sync with IBM Aspera

Custom IBM Bob mode configuration for **IBM Aspera Sync** — high-speed WAN file and repository synchronization using the FASP transport protocol.

---

## Overview

This Bob mode provides specialized assistance for:

- **Aspera Sync Configuration**: Setting up synchronization relationships, topology selection, and FASP transport parameters
- **Topology Design**: Choosing and configuring unidirectional, bidirectional, or mesh synchronization for specific use cases
- **Large-Scale File Operations**: Handling many small files or very large files depending on workload characteristics
- **Integration with Downstream Pipelines**: Connecting synchronized data at the destination to analytics or AI pipelines
- **Conflict and Deletion Handling**: Designing explicit strategies for bidirectional synchronization scenarios

---

## What's Included

- **[`base-modes/aspera-sync-builder.zip`](base-modes/aspera-sync-builder.zip)**: Bob mode configuration for IBM Aspera Sync development

---

## Mode Capabilities

- IBM Aspera Sync synchronization relationship configuration
- FASP transport protocol parameters — bandwidth, encryption, port configuration
- Topology selection — unidirectional, bidirectional, mesh
- Incremental synchronization — detecting and transmitting only changed files
- Scheduler configuration for recurring synchronization
- Conflict resolution strategy design for bidirectional topologies
- Network and firewall requirements for FASP UDP traffic
- Integration patterns for downstream analytics or AI pipeline consumption of synchronized data

---

## When to Use This Mode

- Designing an IBM Aspera Sync deployment for cross-WAN file repository synchronization
- Selecting the right synchronization topology for a multi-site or hybrid cloud use case
- Configuring FASP transport settings for a specific network profile
- Troubleshooting Aspera Sync configuration, connectivity, or performance issues
- Integrating a synchronized destination with a downstream data pipeline

---

## Installing the Bob Mode

**Windows**
```powershell
Copy-Item base-modes/aspera-sync-builder.zip "$env:APPDATA\IBM Bob\User\globalStorage\ibm.bob-code\modes\"
```

**Linux / macOS**
```bash
cp base-modes/aspera-sync-builder.zip ~/.config/IBM\ Bob/User/globalStorage/ibm.bob-code/modes/
```

After copying, restart IBM Bob for the new mode to become available in the mode selector.

---

## Related

- [`../bob-skills/`](../bob-skills/) — IBM Aspera Sync configuration skill
- [`../README.md`](../README.md) — Data Sync building block overview
