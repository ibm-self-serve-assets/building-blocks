# Data Sync with IBM Aspera

**Core Capability**: Pipelines
**IBM Products**: IBM Aspera Sync
**Product Components**: IBM Aspera Sync; FASP transport protocol; unidirectional, bidirectional, and mesh synchronization topologies

## Overview

Use **IBM Aspera Sync** to replicate and synchronize large files and data repositories quickly and securely over wide-area networks (WAN). IBM Aspera Sync uses IBM's purpose-built **FASP** (Fast, Adaptive, and Secure Protocol) transport to maintain near-wire-speed transfer performance regardless of network distance, latency, or packet loss — making it practical to synchronize terabytes of data between data centres, clouds, and remote sites within predictable windows.

Conventional TCP-based file transfer (rsync, SFTP, FTP) degrades sharply over long distances and high-latency links. A transfer that takes minutes on a local network can take hours or days across a WAN. IBM Aspera Sync addresses this directly.

---

## When to Use

Use Aspera Sync when:

- You need to synchronize **file repositories or large data sets** across WAN links where conventional transfer is too slow.
- Engineering, media, scientific, genomics, backup, or AI training data must be distributed between geographically separated locations.
- Incremental synchronization — transmitting only changes, new files, and file-system operations — is required to avoid unnecessary full re-transfers.
- A **one-to-one, one-to-many, bidirectional, or mesh** synchronization topology is needed.
- Large repositories must be kept in sync between on-premises data centres and IBM Cloud or other cloud sites.

> **What Aspera Sync is not**: This is a file/data-set synchronization capability. For near-real-time replication of relational database changes, use a CDC/data-replication technology such as **watsonx.data integration Data Replication** or a streaming pattern with **[IBM Confluent](../../context/real-time-streaming/README.md)**.

---

## Business Value

| Outcome | What It Means |
|---|---|
| **Shorter synchronization windows** | Move large data sets across long-distance or high-latency networks far faster than conventional TCP |
| **Efficient change synchronization** | Recognize and transmit only changes and file-system operations — avoid unnecessary full re-transfers |
| **Hybrid and multi-site distribution** | Keep large repositories synchronized between data centres, clouds, and remote sites |
| **Support very large scale** | Handle many small files or large multi-terabyte files depending on the workload |

---

## Reference Pattern

```
On-premises / Site A                                    Cloud / Site B
(large file repository)                                 (data repository)
        │                                                       │
        └───────── IBM Aspera Sync (FASP transport) ───────────┘
                           │
                    AI / Analytics pipeline
                    (downstream consumption)
```

---

## Synchronization Topologies

| Topology | Description |
|---|---|
| **Unidirectional** | Source pushes changes to one or more destinations. No conflict risk. |
| **Bidirectional** | Both sides can update files. Requires explicit conflict resolution strategy. |
| **Mesh** | Multiple peers synchronize with each other. Used for multi-site distribution. |

---

## Getting Started

### Prerequisites

- **IBM Aspera Sync** licence and installation on source and destination hosts
- Network access between source and destination on the required FASP UDP port (default 33001)
- Firewall and security policy review for FASP transport

### Quick Setup Steps

1. Install IBM Aspera Sync on the source and destination hosts.
2. Configure a synchronization relationship — define source path, destination host, destination path, and topology (unidirectional, bidirectional, or mesh).
3. Run an initial full synchronization and observe transfer throughput versus conventional transfer.
4. Configure incremental mode — Aspera Sync detects and transmits only changed files on subsequent runs.
5. Schedule recurring synchronization using the built-in scheduler or an external orchestrator.
6. Validate the destination data and confirm downstream pipeline consumption.

### IBM Bob — Your Fellow Developer

**[IBM Bob](https://www.ibm.com/products/bob)** is IBM's AI coding assistant purpose-built for IBM Cloud and watsonx. The Data Sync building block ships a **Bob Mode** and **Bob Skills** that give Bob expert knowledge of IBM Aspera Sync configuration, topology design, FASP transport tuning, and integration with downstream analytics pipelines.

**Install the Bob Mode**:
```powershell
# Windows
Copy-Item bob-modes/base-modes/aspera-sync-builder.zip "$env:APPDATA\IBM Bob\User\globalStorage\ibm.bob-code\modes\"
```
```bash
# Linux / macOS
cp bob-modes/base-modes/aspera-sync-builder.zip ~/.config/IBM\ Bob/User/globalStorage/ibm.bob-code/modes/
```
Restart IBM Bob — **Aspera Sync Builder** mode appears in the mode selector.

**Install Bob Skills**:
```bash
unzip bob-skills/aspera-sync-configuration.zip
```
Open IBM Bob → Skills panel → enable the skill.

---

## Design Considerations

- **Choose topology based on ownership and conflict expectations** — unidirectional is the lowest-risk starting point.
- **Separate bulk file synchronization from transactional database replication** — Aspera Sync is designed for file sets, not row-level CDC.
- **Validate firewall and network policy for FASP UDP** before performance testing.
- **Test with realistic file counts and sizes** — many small files can behave differently from fewer very large files.
- **Define conflict and deletion handling explicitly** for bidirectional synchronization.
- **Encryption**: FASP uses AES-128 encryption in transit; verify requirements for data at rest at the destination.

---

## Bob Modes

- **[`bob-modes/`](./bob-modes/)**: AI mode for IBM Aspera Sync configuration, topology design, and integration
  - **Install**: copy [`bob-modes/base-modes/aspera-sync-builder.zip`](./bob-modes/base-modes/aspera-sync-builder.zip) to your Bob modes directory

## Bob Skills

| Skill | Zip | Capabilities |
|---|---|---|
| `aspera-sync-configuration` | [`bob-skills/aspera-sync-configuration.zip`](./bob-skills/aspera-sync-configuration.zip) | IBM Aspera Sync topology design, FASP transport configuration, synchronization scheduling, large-scale file set patterns |

See [`bob-skills/README.md`](./bob-skills/README.md) for installation instructions.

---

## IBM Products Used

| Product | Role |
|---|---|
| **[IBM Aspera Sync](https://www.ibm.com/products/aspera/sync)** | High-speed WAN file and repository synchronization using the FASP transport protocol |

---

## IBM Cloud References

- [IBM Aspera Sync Product Page](https://www.ibm.com/products/aspera/sync)
- [IBM Aspera Documentation](https://www.ibm.com/docs/en/ahte)
- [IBM Cloud IAM API Keys](https://cloud.ibm.com/iam/apikeys)
