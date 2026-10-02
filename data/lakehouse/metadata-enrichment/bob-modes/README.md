# Meta Data Enrichment and Quality -- Bob Modes

Bob custom modes for IBM watsonx.data intelligence -- metadata enrichment, data quality, and data lineage.

## Available modes

Modes are provided by the capability sub-folders:

| Mode | ZIP | Description |
|---|---|---|
| Data Quality Builder | [`../data-quality/bob-modes/base-modes/data-quality-builder.zip`](../data-quality/bob-modes/base-modes/data-quality-builder.zip) | Data quality rule authoring and monitoring with watsonx.data intelligence. Helps define validation rules, configure profiling, set thresholds, and build compliance reports. |
| Data Lineage Builder | [`../data-lineage/bob-modes/base-modes/data-lineage-builder.zip`](../data-lineage/bob-modes/base-modes/data-lineage-builder.zip) | End-to-end lineage tracking with watsonx.data intelligence. Assists with OpenLineage instrumentation, impact analysis, compliance reporting, and lineage visualization. |

## Installing a mode

1. Download the `.zip` file.
2. Copy the mode folder to `~/.bob/modes` (global) or `<project>/.bob/modes` (project-level).
3. Reload IBM Bob -- the mode appears in the mode selector.
