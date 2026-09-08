# Data Sync

**IBM product**: IBM Aspera Sync

Use this building block for high-speed synchronization of **large files, file repositories, and directories** across data centers, edge locations, and cloud environments.

## When to use

Good fits include:

- synchronizing large engineering/media/scientific repositories;
- distributing AI training or reference data to multiple locations;
- keeping file trees synchronized across WAN links;
- moving large numbers of small files or very large files efficiently;
- feeding downstream analytics/AI pipelines after file synchronization.

This is **not relational database CDC**. For structured near-real-time database replication, use IBM watsonx.data integration Data Replication.

## Typical flow

```text
On-prem / edge / data center
          |
          | IBM Aspera Sync / FASP
          v
Cloud / remote file repository
          |
          v
analytics / AI / archive / downstream pipeline
```

Actual throughput depends on network capacity, endpoint/storage performance, workload characteristics, and configuration.

## Repository status

This folder currently contains developer guidance under:

- [`bob-modes/`](bob-modes/)
- [`bob-skills/`](bob-skills/)

The Bob ZIP implementation is currently marked **Coming soon**. There is no runnable `assets/` implementation in this building block yet.

## Developer checklist

Before implementing an Aspera Sync topology, decide:

1. Source and destination file-system locations.
2. Unidirectional, bidirectional, or mesh topology.
3. Conflict/deletion behavior.
4. Include/exclude patterns.
5. FASP network/firewall requirements.
6. Target/minimum transfer rates and operational windows.
7. How synchronized content is consumed downstream.

## IBM references

- IBM Aspera Sync: https://www.ibm.com/products/aspera/sync
- IBM Aspera: https://www.ibm.com/products/aspera
