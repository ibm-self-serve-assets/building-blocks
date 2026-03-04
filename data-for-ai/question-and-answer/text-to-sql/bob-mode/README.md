# Bob Mode for Text-to-SQL

Custom IBM Bob mode configuration for Text-to-SQL development using watsonx.data Intelligence.

---

## Overview

This Bob mode provides specialized assistance for:

- **Text-to-SQL Implementation**: Converting natural language to SQL queries
- **watsonx.data Intelligence**: Leveraging IBM's Text2SQL capabilities
- **Metadata Enrichment**: Enhancing database metadata for better query generation
- **Query Optimization**: Improving generated SQL performance
- **Schema Understanding**: Analyzing and documenting database schemas
- **Natural Language Processing**: Handling complex user queries

---

## What's Included

- **[`base-mode/text-to-sql.yaml`](base-mode/text-to-sql.yaml)**: Bob mode configuration for Text-to-SQL development

---

## Mode Capabilities

- watsonx.data Intelligence Text2SQL configuration
- Metadata enrichment strategies
- Database schema analysis and documentation
- Natural language query interpretation
- SQL query generation and optimization
- Connection setup (DB2, MySQL, PostgreSQL, Presto)
- Error handling and query validation
- Performance tuning for generated queries
- Integration with watsonx.ai models

---

## When to Use This Mode

- Implementing Text-to-SQL applications
- Configuring watsonx.data Intelligence Text2SQL
- Enriching database metadata for better results
- Troubleshooting query generation issues
- Optimizing Text-to-SQL performance
- Setting up database connections
- Designing natural language interfaces
- Evaluating and improving query accuracy

---

## Installing Bob Modes

This section provides step-by-step instructions for installing the custom Bob mode.

---

### Installing the Custom Bob Mode

The custom Bob mode ([`base-mode/text-to-sql.yaml`](base-mode/text-to-sql.yaml)) defines the behavior, expertise, and capabilities of IBM Bob when working with Text-to-SQL tasks.

For detailed information about custom modes, see the [IBM Bob Custom Modes Documentation](https://internal.bob.ibm.com/docs/ide/features/custom-modes).

#### Method 1: Copy to Bob's Global Modes Directory (Recommended)

**Windows**

```powershell
Copy-Item base-mode/text-to-sql.yaml "$env:APPDATA\IBM Bob\User\globalStorage\ibm.bob-code\modes\"
```

**Linux / macOS**

```bash
cp base-mode/text-to-sql.yaml ~/.config/IBM\ Bob/User/globalStorage/ibm.bob-code/modes/
```

After copying, restart IBM Bob for the new mode to become available.

---

#### Method 2: Reference Modes from Current Repository

If you prefer not to copy files, you can configure IBM Bob to reference this directory directly.

1. Open IBM Bob configuration settings
2. Add the local directory path under custom modes
3. Restart IBM Bob

This approach is useful for development and version-controlled mode updates.