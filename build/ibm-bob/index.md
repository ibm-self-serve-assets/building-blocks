# Customizing IBM Bob to work with the Building Blocks

IBM Bob custom modes allow developers to tailor Bob's behavior by combining reusable Building Blocks. Numerous modes are available to support work in these areas to address specific operational needs and development workflows.

- Builidng agents 
- MCP creation and integration
- Vector Search & Document Processing
- Data Engineering & Knowledge Pipelines
- Application Observability & Monitoring
- Security, Risk & Trust Intelligence

This composable approach enables teams to design highly contextual assistants optimized for specialized tasks and domain-specific scenarios.
      
## Code Repositories
Instructions and related files for these custom modes can be found in their respective repository.

### Agents Code Repository
- [Agent Builder](https://github.com/ibm-self-serve-assets/building-blocks/tree/main/agents/ibm-bob/modes): Bob uses wxo's ADK and documentation MCP servers to build custom agents.
- [MCP Builder](https://github.com/ibm-self-serve-assets/building-blocks/tree/main/agents/ibm-bob/modes): Expands on the Agent Builder mode to build and deploy MCP servers on wxo.
- [Domain Agent Builder](https://github.com/ibm-self-serve-assets/building-blocks/tree/main/agents/ibm-bob/modes/domain-agent-builder): Bob builds a tool-augmented RAG agent for partner's custom specific domain.

### Data
- [Data for AI](https://github.com/ibm-self-serve-assets/building-blocks/tree/main/data-for-ai/ibm-bob/base-mode): Specialized for data engineering, architecture, and data operations
- [RAG Ingestion](https://github.com/ibm-self-serve-assets/building-blocks/tree/main/data-for-ai/ibm-bob/rag-ingestion-sse-mcp-server): Ingest IBM Cloud Object Storage (COS) into vector databases.
- [RAG Retrieval](https://github.com/ibm-self-serve-assets/building-blocks/tree/main/data-for-ai/ibm-bob/rag-retrieval-sse-mcp-server): Retrieve from OpenSearch or Milvus.
- [RAG Builder](https://github.com/ibm-self-serve-assets/building-blocks/tree/main/data-for-ai/ibm-bob/advance-mode/rag-builder-mode): IBM Bob: Intelligence for Vector Search and Document Processing.

### Automation
- [Application monitoring and observability expert](https://github.com/ibm-self-serve-assets/building-blocks/tree/main/observe/application-observability/ibm-bob/base-mode): Connect Bob with the Instana MCP server.
- [Automated Resilience & Compliance](https://github.com/ibm-self-serve-assets/building-blocks/blob/main/optimize/automated-resilience-and-compliance/ibm-bob/base-mode/application-resilience.yaml): Unified Vulnerability and Certificate Intelligence via IBM Concert.