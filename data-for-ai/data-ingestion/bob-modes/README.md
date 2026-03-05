# Bob Mode for Data Ingestion

Custom IBM Bob mode configuration for data ingestion workflows including IBM UDI (Unstructured Data Ingestion) and structured data ingestion.

---

## Overview

This Bob mode provides specialized assistance for:

- **IBM UDI (Unstructured Data Ingestion)**: Processing documents, PDFs, images, and unstructured content
- **Structured Data Ingestion**: Database connectors (DB2, PostgreSQL, MySQL, Oracle) with CDC support
- Data pipeline design and optimization
- ETL/ELT workflow implementation
- Data quality and validation strategies

---

## What's Included

- **[`base-modes/.bob/ingestion.yaml`](base-modes/.bob/ingestion.yaml)**: Bob mode configuration for data ingestion development

---

## Mode Capabilities

- IBM UDI configuration and troubleshooting
- Database connector setup and optimization
- CDC (Change Data Capture) implementation
- Data transformation logic
- Schema mapping and validation
- Error handling and retry strategies
- Performance tuning for ingestion pipelines
- Data quality checks and monitoring

---

## When to Use This Mode

- Setting up new data ingestion pipelines
- Configuring IBM UDI for unstructured data
- Implementing database connectors with CDC
- Troubleshooting ingestion issues
- Optimizing data pipeline performance
- Designing data validation strategies

---

## Installing Bob Modes

This section provides step-by-step instructions for installing the custom Bob mode.

---

### Installing the Custom Bob Mode

The custom Bob mode ([`base-modes/.bob/ingestion.yaml`](base-modes/.bob/ingestion.yaml)) defines the behavior, expertise, and capabilities of IBM Bob when working with data ingestion tasks.

For detailed information about custom modes, see the [IBM Bob Custom Modes Documentation](https://internal.bob.ibm.com/docs/ide/features/custom-modes).

#### Method 1: Copy to Bob's Global Modes Directory (Recommended)

**Windows**

```powershell
Copy-Item base-modes/.bob/ingestion.yaml "$env:APPDATA\IBM Bob\User\globalStorage\ibm.bob-code\modes\"
```

**Linux / macOS**

```bash
cp base-modes/.bob/ingestion.yaml ~/.config/IBM\ Bob/User/globalStorage/ibm.bob-code/modes/
```

After copying, restart IBM Bob for the new mode to become available.

---

#### Method 2: Reference Modes from Current Repository

If you prefer not to copy files, you can configure IBM Bob to reference this directory directly.

1. Open IBM Bob configuration settings
2. Add the local directory path under custom modes
3. Restart IBM Bob

This approach is useful for development and version-controlled mode updates.