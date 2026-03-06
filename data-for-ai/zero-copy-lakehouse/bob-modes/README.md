# Bob Mode for Zero-Copy Lakehouse

Custom IBM Bob mode configuration for zero-copy lakehouse architecture and watsonx.data development.

---

## Overview

This Bob mode provides specialized assistance for:

- **Zero-Copy Architecture**: Querying across databases, warehouses, and object stores without data duplication
- **watsonx.data Setup**: Configuration and optimization of watsonx.data environments
- **Query Federation**: Implementing cross-source query capabilities
- **Data Virtualization**: Setting up virtual data layers
- **Performance Optimization**: Tuning query performance and resource utilization
- **Cost Reduction**: Eliminating data movement and storage duplication

---

## What's Included

- **[`base-modes/zero-copy-lakehouse.yaml`](base-modes/zero-copy-lakehouse.yaml)**: Bob mode configuration for lakehouse development

---

## Mode Capabilities

- watsonx.data configuration and setup
- Query federation across multiple data sources
- Presto/Trino query optimization
- Catalog and schema management
- Data source connector configuration
- Performance tuning and monitoring
- Cost optimization strategies
- Security and access control setup
- Metadata management

---

## When to Use This Mode

- Setting up watsonx.data environments
- Implementing zero-copy data access patterns
- Configuring query federation across data sources
- Optimizing lakehouse query performance
- Troubleshooting data access issues
- Planning lakehouse architecture
- Implementing data virtualization layers

---

## Installing Bob Modes

This section provides step-by-step instructions for installing the custom Bob mode.

---

### Installing the Custom Bob Mode

The custom Bob mode ([`base-modes/zero-copy-lakehouse.yaml`](base-modes/zero-copy-lakehouse.yaml)) defines the behavior, expertise, and capabilities of IBM Bob when working with zero-copy lakehouse tasks.

For detailed information about custom modes, see the [IBM Bob Custom Modes Documentation](https://internal.bob.ibm.com/docs/ide/features/custom-modes).

#### Method 1: Copy to Bob's Global Modes Directory (Recommended)

**Windows**

```powershell
Copy-Item base-modes/zero-copy-lakehouse.yaml "$env:APPDATA\IBM Bob\User\globalStorage\ibm.bob-code\modes\"
```

**Linux / macOS**

```bash
cp base-modes/zero-copy-lakehouse.yaml ~/.config/IBM\ Bob/User/globalStorage/ibm.bob-code/modes/
```

After copying, restart IBM Bob for the new mode to become available.

---

#### Method 2: Reference Modes from Current Repository

If you prefer not to copy files, you can configure IBM Bob to reference this directory directly.

1. Open IBM Bob configuration settings
2. Add the local directory path under custom modes
3. Restart IBM Bob

This approach is useful for development and version-controlled mode updates.