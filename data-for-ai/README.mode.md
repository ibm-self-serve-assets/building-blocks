# Bob Modes Creation Plan

## Overview

This document outlines the plan for creating 4 new Bob modes to automate setup and configuration for capabilities that currently lack automation support.

## Proposed Bob Modes

### 1. Vector Search Builder Mode
**Location**: `vector-search/bob-modes/base-modes/vector-search-builder.zip`

**Purpose**: Automate vector database setup and data ingestion for Milvus and OpenSearch

**Key Features**:
- Interactive setup wizard for Milvus or OpenSearch
- Automated connection configuration
- Collection/index creation with optimal settings
- Embedding model selection and configuration
- Sample data ingestion workflow
- Integration with watsonx embeddings

**Product APIs Used**:
- Milvus Python SDK (`pymilvus`)
  - `connections.connect()` - Connect to Milvus
  - `Collection()` - Create/manage collections
  - `utility.create_index()` - Create vector indexes
  - `collection.insert()` - Insert vectors
  - `collection.search()` - Search vectors
- OpenSearch Python Client
  - `OpenSearch()` - Connect to OpenSearch
  - `indices.create()` - Create index with k-NN mapping
  - `index()` - Index documents with vectors
  - `search()` - Vector similarity search
- watsonx.ai Embeddings API
  - `generate_embeddings()` - Generate embeddings

**Workflow**:
1. Ask user: Milvus or OpenSearch?
2. Collect connection details (host, port, credentials)
3. Test connection
4. Ask for collection/index name and dimensions
5. Create collection/index with vector field
6. Configure embedding model (watsonx, HuggingFace, local)
7. Generate sample ingestion code
8. Provide search example code

**Integration with Other Modes**:
- Can be called from `rag-builder` mode for RAG setup
- Can be used with `data-ingestion` mode for automated vector ingestion

---

### 2. Lakehouse Setup Mode
**Location**: `federated-search/bob-modes/base-modes/lakehouse-setup.zip`

**Purpose**: Automate watsonx.data lakehouse setup with Iceberg and Presto

**Key Features**:
- Automated catalog creation
- Schema and table setup
- Sample data loading
- Presto engine configuration
- Query examples generation

**Product APIs Used**:
- watsonx.data REST API
  - `POST /catalogs` - Create Iceberg catalog
  - `POST /schemas` - Create schemas
  - `POST /tables` - Create tables
  - `GET /engines` - List Presto engines
- IBM Cloud Object Storage SDK
  - `create_bucket()` - Create COS bucket
  - `upload_file()` - Upload data files
- Presto Python Client (`presto-python-client`)
  - `connect()` - Connect to Presto
  - `cursor.execute()` - Execute SQL queries

**Workflow**:
1. Collect watsonx.data credentials (endpoint, API key, instance ID)
2. Collect COS details (bucket, endpoint, credentials)
3. Test connections
4. Ask for catalog, schema, and table names
5. Create Iceberg catalog pointing to COS
6. Create schema
7. Create sample tables (customer, account, etc.)
8. Load sample data from CSV
9. Generate SQL query examples
10. Provide connection string for BI tools

**Integration with Other Modes**:
- Can be used with `data-ingestion` mode for lakehouse data loading
- Can integrate with `text-to-sql` mode for natural language queries

---

### 3. Security Setup Mode
**Location**: `data-security-encryption/bob-modes/base-modes/security-setup.zip`

**Purpose**: Automate data protection, encryption, and access control setup

**Key Features**:
- IBM Cloud project creation
- Data catalog setup with protection rules
- Encryption key management
- Access control configuration
- Audit logging setup
- PII data classification

**Product APIs Used**:
- IBM Cloud Projects API
  - `POST /projects` - Create project
  - `POST /projects/{id}/configs` - Configure project settings
- watsonx.data Governance API
  - `POST /catalogs/{id}/policies` - Create data policies
  - `POST /catalogs/{id}/rules` - Create protection rules
- IBM Key Protect API
  - `POST /keys` - Create encryption keys
  - `POST /keys/{id}/actions/wrap` - Wrap data encryption keys
- IBM Cloud IAM API
  - `POST /roles` - Create custom roles
  - `POST /policies` - Create access policies

**Workflow**:
1. Collect IBM Cloud credentials
2. Collect watsonx.data instance details
3. Ask for project name and description
4. Create IBM Cloud project
5. Set up Key Protect instance
6. Create encryption keys
7. Configure data catalog with protection rules
8. Set up PII detection rules (email, SSN, credit card, etc.)
9. Configure access control policies
10. Enable audit logging
11. Generate compliance report template

**Integration with Other Modes**:
- Should be used before `lakehouse-setup` for secure data storage
- Can integrate with `data-ingestion` for secure data pipelines

---

### 4. NoSQL Setup Mode
**Location**: `nosql-database/bob-modes/base-modes/nosql-setup.zip`

**Purpose**: Automate DataStax Astra DB setup and configuration

**Key Features**:
- Astra DB database creation
- Keyspace and table setup
- Vector search configuration
- Sample data loading
- Connection string generation

**Product APIs Used**:
- Astra DB DevOps API
  - `POST /databases` - Create database
  - `GET /databases/{id}` - Get database status
- Astra DB Data API
  - `POST /api/rest/v2/keyspaces` - Create keyspace
  - `POST /api/rest/v2/keyspaces/{keyspace}/tables` - Create table
- AstraPy Python SDK
  - `AstraDB()` - Connect to Astra DB
  - `create_collection()` - Create collection
  - `insert_one()` - Insert document
  - `find()` - Query documents
  - `vector_find()` - Vector similarity search

**Workflow**:
1. Collect Astra DB credentials (token, database ID)
2. Ask: Create new database or use existing?
3. If new: Create database with region selection
4. Wait for database to be ready
5. Ask for keyspace name
6. Create keyspace
7. Ask: Regular table or vector-enabled collection?
8. Create table/collection with appropriate schema
9. If vector: Configure vector dimensions and similarity metric
10. Generate sample insert code
11. Generate sample query code
12. Provide connection details for applications

**Integration with Other Modes**:
- Can be used with `vector-search-builder` for vector storage
- Can integrate with `data-ingestion` for NoSQL data loading

---

## Common Features Across All Modes

### 1. Interactive Setup
- Step-by-step guided configuration
- Input validation and error handling
- Connection testing before proceeding
- Clear progress indicators

### 2. Code Generation
- Generate Python code for setup
- Generate configuration files (.env, config.json)
- Generate example usage code
- Generate deployment scripts (Docker, Kubernetes)

### 3. Documentation
- Generate README with setup instructions
- Generate API reference documentation
- Generate troubleshooting guide
- Generate best practices document

### 4. Testing
- Generate test scripts
- Provide sample data for testing
- Include health check commands
- Include validation queries

### 5. Integration
- Each mode can call other modes
- Shared configuration management
- Consistent error handling
- Unified logging

## Mode Architecture

### Mode Structure
```
mode-name.zip
├── mode.json (mode configuration)
├── instructions.md (mode instructions)
├── prompts/ (conversation prompts)
├── templates/ (code templates)
└── examples/ (example configurations)
```

### Mode Configuration (mode.json)
```json
{
  "name": "Mode Name",
  "slug": "mode-slug",
  "description": "Mode description",
  "version": "1.0.0",
  "capabilities": ["capability1", "capability2"],
  "dependencies": ["other-mode-slug"],
  "apis": ["api1", "api2"]
}
```

## Implementation Plan

### Phase 1: Vector Search Builder
1. Create mode structure
2. Implement Milvus setup workflow
3. Implement OpenSearch setup workflow
4. Add embedding configuration
5. Generate code templates
6. Test with sample data

### Phase 2: Lakehouse Setup
1. Create mode structure
2. Implement watsonx.data API integration
3. Implement COS integration
4. Add Presto configuration
5. Generate SQL templates
6. Test with sample tables

### Phase 3: Security Setup
1. Create mode structure
2. Implement IBM Cloud Projects API
3. Implement Key Protect integration
4. Add policy configuration
5. Generate compliance templates
6. Test with sample policies

### Phase 4: NoSQL Setup
1. Create mode structure
2. Implement Astra DB DevOps API
3. Implement Data API integration
4. Add vector search configuration
5. Generate connection templates
6. Test with sample collections

## Usage Examples

### Using Vector Search Builder
```
User: "I need to set up vector search for my documents"
Bob: "I'll help you set up vector search. Which vector database would you like to use?"
     1. Milvus (recommended for large-scale)
     2. OpenSearch (recommended for hybrid search)
User: "Milvus"
Bob: "Great! Let me collect some information..."
     [Guided setup follows]
```

### Chaining Modes
```
User: "Set up a complete RAG system with security"
Bob: [Calls security-setup mode]
     [Calls vector-search-builder mode]
     [Calls rag-builder mode]
     "Your secure RAG system is ready!"
```

## Success Criteria

1. Each mode completes setup in < 5 minutes
2. Generated code runs without modification
3. All connections are tested before completion
4. Clear error messages for any failures
5. Documentation is comprehensive and accurate

## Next Steps

1. Review and approve this plan
2. Create modes using mode-writer
3. Test each mode individually
4. Test mode integration
5. Create user documentation
6. Deploy to repository

---

**Approval Required**: Please review this plan and approve before proceeding with mode creation.