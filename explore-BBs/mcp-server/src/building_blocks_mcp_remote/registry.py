"""
Static catalog of IBM Technology Building Blocks and documentation pages.

Hierarchy: 3 Core Capabilities -> 8 Groups -> 24 Building Blocks.

Enables instant responses for discovery tools (zero API calls).
Update this file when new building blocks are added to the repository.
"""

from __future__ import annotations

REPO_OWNER = "ibm-self-serve-assets"
REPO_NAME = "building-blocks"
DOCS_REPO_NAME = "building-blocks-docs"
DEFAULT_BRANCH = "main"

REPO_BASE_URL = f"https://github.com/{REPO_OWNER}/{REPO_NAME}"
DOCS_SITE_URL = "https://ibm-self-serve-assets.github.io/building-blocks-docs"

# ---------------------------------------------------------------------------
# Core Capabilities (top level)
# ---------------------------------------------------------------------------

CORE_CAPABILITIES: dict[str, dict] = {
    "ai": {
        "name": "AI",
        "description": "AI agents, multi-agent orchestration, AI trust, model evaluation, and governance",
    },
    "data": {
        "name": "Data",
        "description": "Data integration, intelligence, and retrieval capabilities for AI-powered applications",
    },
    "automation": {
        "name": "Automation",
        "description": "Build and deploy, secure, and optimize enterprise applications and infrastructure",
    },
}

# ---------------------------------------------------------------------------
# Groups (second level - each belongs to a capability)
# ---------------------------------------------------------------------------

GROUPS: dict[str, dict] = {
    "agents": {
        "name": "Agents",
        "capability": "ai",
        "description": "Build and orchestrate AI agents using watsonx Orchestrate ADK, multi-agent patterns, and agentic SDLC",
    },
    "ai-trust": {
        "name": "AI Trust",
        "capability": "ai",
        "description": "Model evaluation, agent operations monitoring, real-time guardrails, and AI compliance",
    },
    "integration": {
        "name": "Integration",
        "capability": "data",
        "description": "AI-generated data pipelines, data streaming, and data observability for ingestion and processing",
    },
    "intelligence": {
        "name": "Intelligence",
        "capability": "data",
        "description": "Data quality, lineage tracking, and natural-language to SQL query generation",
    },
    "retrieval": {
        "name": "Retrieval",
        "capability": "data",
        "description": "Vector search, NoSQL databases, and zero-copy lakehouse access for unified data retrieval",
    },
    "build": {
        "name": "Build and Deploy",
        "capability": "automation",
        "description": "iPaaS integration, Infrastructure as Code, and code modernization",
    },
    "secure": {
        "name": "Secure",
        "capability": "automation",
        "description": "Non-human identity management and quantum-safe cryptography",
    },
    "optimize": {
        "name": "Optimize",
        "capability": "automation",
        "description": "Automated resource management, FinOps cost optimization, and resilience/compliance",
    },
}

# ---------------------------------------------------------------------------
# Building Blocks
# ---------------------------------------------------------------------------

BUILDING_BLOCKS: dict[str, dict] = {
    # --- AI > Agents ---
    "agent-builder": {
        "name": "Agent Builder",
        "group": "agents",
        "capability": "ai",
        "description": "Build autonomous, task-driven AI agents using watsonx Orchestrate ADK",
        "repo_path": "agents/agent-builder",
        "docs_path": "ai-core/agents/agent-builder.md",
        "products": ["watsonx Orchestrate"],
        "tags": ["agents", "adk", "orchestration", "bob-modes"],
    },
    "multi-agent-orchestration": {
        "name": "Multi-Agent Orchestration",
        "group": "agents",
        "capability": "ai",
        "description": "Enable specialized agents to collaborate on complex workflows through context sharing, task routing, and feedback loops via MCP and A2A protocols",
        "repo_path": "agents/multi-agent-orchestration",
        "docs_path": "ai-core/agents/multi-agent-orchestration.md",
        "products": ["watsonx Orchestrate"],
        "tags": ["agents", "multi-agent", "orchestration", "mcp", "a2a"],
    },
    "agentic-sdlc": {
        "name": "Agentic SDLC",
        "group": "agents",
        "capability": "ai",
        "description": "Agentic software development lifecycle for building, testing, and deploying AI-powered applications",
        "repo_path": "agents/agentic-sdlc",
        "docs_path": "ai-core/agents/agentic-sdlc.md",
        "products": ["watsonx Orchestrate"],
        "tags": ["agents", "sdlc", "development", "agentic"],
    },
    # --- AI > AI Trust ---
    "model-evaluation": {
        "name": "Model Evaluation",
        "group": "ai-trust",
        "capability": "ai",
        "description": "Evaluation approaches for generative AI and predictive ML models measuring quality, retrieval, safety, and performance",
        "repo_path": "ai-trust/model-evaluation",
        "docs_path": "ai-core/ai-trust/model-evaluation.md",
        "products": ["watsonx.governance"],
        "tags": ["trust", "evaluation", "metrics", "safety", "quality"],
    },
    "agent-ops": {
        "name": "Agent Ops",
        "group": "ai-trust",
        "capability": "ai",
        "description": "Operational monitoring and management of AI agents in production environments",
        "repo_path": "ai-trust/agent-ops",
        "docs_path": "ai-core/ai-trust/agent-ops.md",
        "products": ["watsonx.governance"],
        "tags": ["trust", "monitoring", "agents", "operations", "production"],
    },
    "real-time-guardrails": {
        "name": "Real-Time Guardrails",
        "group": "ai-trust",
        "capability": "ai",
        "description": "Real-time validation and guardrails for AI model inputs and outputs in production",
        "repo_path": "ai-trust/real-time-guardrails",
        "docs_path": "ai-core/ai-trust/real-time-guardrails.md",
        "products": ["watsonx.governance"],
        "tags": ["trust", "guardrails", "real-time", "safety", "runtime"],
    },
    "ai-compliance": {
        "name": "AI Compliance",
        "group": "ai-trust",
        "capability": "ai",
        "description": "Streamline regulatory alignment and industry compliance standards for AI systems",
        "repo_path": "ai-trust/ai-compliance",
        "docs_path": "ai-core/ai-trust/ai-compliance.md",
        "products": ["watsonx.governance"],
        "tags": ["trust", "compliance", "regulation", "governance"],
    },
    # --- Data > Integration ---
    "data-pipeline-ai-generated": {
        "name": "Data Pipeline (AI Generated)",
        "group": "integration",
        "capability": "data",
        "description": "AI-assisted data pipeline generation for ingesting unstructured and structured data via batch, streaming, or hybrid patterns",
        "repo_path": "data/integration/data-pipeline-ai-generated",
        "docs_path": "data-core/integration/data-pipeline-ai-generated/index.md",
        "products": ["watsonx.data"],
        "tags": ["data", "ingestion", "pipeline", "etl", "streaming"],
    },
    "data-streaming": {
        "name": "Data Streaming",
        "group": "integration",
        "capability": "data",
        "description": "Real-time data streaming capabilities for continuous data processing and event-driven architectures",
        "repo_path": "data/integration/data-streaming",
        "docs_path": "data-core/integration/data-streaming/index.md",
        "products": ["watsonx.data"],
        "tags": ["data", "streaming", "real-time", "events"],
    },
    "data-observability": {
        "name": "Data Observability",
        "group": "integration",
        "capability": "data",
        "description": "Monitor, profile, and observe data pipelines for freshness, volume, schema drift, and quality in real time",
        "repo_path": "data/integration/data-observability",
        "docs_path": "data-core/integration/data-observability/index.md",
        "products": ["watsonx.data"],
        "tags": ["data", "observability", "monitoring", "profiling", "quality"],
    },
    # --- Data > Intelligence ---
    "data-quality": {
        "name": "Data Quality",
        "group": "intelligence",
        "capability": "data",
        "description": "Data quality management with automated validation, profiling, and rule-based checks across data sources",
        "repo_path": "data/intelligence/data-quality",
        "docs_path": "data-core/intelligence/data-quality/index.md",
        "products": ["watsonx.data"],
        "tags": ["data", "quality", "validation", "profiling", "intelligence"],
    },
    "data-lineage": {
        "name": "Data Lineage",
        "group": "intelligence",
        "capability": "data",
        "description": "Track end-to-end data lineage across pipelines, transformations, and consumption for governance and trust",
        "repo_path": "data/intelligence/data-lineage",
        "docs_path": "data-core/intelligence/data-lineage/index.md",
        "products": ["watsonx.data"],
        "tags": ["data", "lineage", "governance", "intelligence", "traceability"],
    },
    "text2sql": {
        "name": "Text2SQL",
        "group": "intelligence",
        "capability": "data",
        "description": "Natural language to SQL conversion using watsonx.data Intelligence with metadata enrichment for accurate query generation",
        "repo_path": "data/intelligence/text2sql",
        "docs_path": "data-core/intelligence/text2sql/index.md",
        "products": ["watsonx.data", "watsonx.ai"],
        "tags": ["data", "text-to-sql", "natural-language", "intelligence", "query"],
    },
    # --- Data > Retrieval ---
    "vector-search": {
        "name": "Vector Search",
        "group": "retrieval",
        "capability": "data",
        "description": "Semantic similarity search with Milvus, OpenSearch, and DataStax Astra DB for unstructured data retrieval",
        "repo_path": "data/retrieval/vector-search",
        "docs_path": "data-core/retrieval/vector-search/index.md",
        "products": ["watsonx.ai"],
        "tags": ["data", "vector", "search", "milvus", "opensearch", "embeddings", "rag"],
    },
    "no-sql-database": {
        "name": "No SQL Database",
        "group": "retrieval",
        "capability": "data",
        "description": "NoSQL database capabilities for flexible, scalable data storage and retrieval",
        "repo_path": "data/retrieval/no-sql-database",
        "docs_path": "data-core/retrieval/no-sql-database/index.md",
        "products": [],
        "tags": ["data", "nosql", "database", "astradb", "retrieval"],
    },
    "zero-copy": {
        "name": "Zero Copy",
        "group": "retrieval",
        "capability": "data",
        "description": "Query across data sources without duplication using open table formats and federated query engines for lakehouse access",
        "repo_path": "data/retrieval/zero-copy",
        "docs_path": "data-core/retrieval/zero-copy/index.md",
        "products": ["watsonx.data"],
        "tags": ["data", "zero-copy", "lakehouse", "iceberg", "federated", "retrieval"],
    },
    # --- Automation > Build and Deploy ---
    "ipaas": {
        "name": "iPaaS",
        "group": "build",
        "capability": "automation",
        "description": "Cloud-native integration with 600+ pre-built connectors, low-code model, API lifecycle management, and event-driven integration via IBM webMethods",
        "repo_path": "build-and-deploy/ipaas",
        "docs_path": "automation-core/build/ipaas.md",
        "products": ["IBM webMethods"],
        "tags": ["integration", "ipaas", "api", "connectors"],
    },
    "infrastructure-as-code": {
        "name": "Infrastructure as Code",
        "group": "build",
        "capability": "automation",
        "description": "Terraform and Ansible for automated, consistent environment provisioning and deployment",
        "repo_path": "build-and-deploy/Iaas",
        "docs_path": "automation-core/build/infrastructure-as-code.md",
        "products": ["Terraform", "Ansible"],
        "tags": ["iac", "terraform", "ansible", "deployment", "infrastructure"],
    },
    "code-modernization": {
        "name": "Code Modernization",
        "group": "build",
        "capability": "automation",
        "description": "Modernize legacy middleware and application code for cloud-native architectures",
        "repo_path": "build-and-deploy/code-modernisation",
        "docs_path": "automation-core/build/middleware-modernization.md",
        "products": [],
        "tags": ["modernize", "middleware", "migration", "cloud-native", "legacy"],
    },
    # --- Automation > Secure ---
    "non-human-identity": {
        "name": "Non-Human Identity",
        "group": "secure",
        "capability": "automation",
        "description": "Identity and secrets management for non-human entities including service accounts, APIs, and machine identities, with HashiCorp Vault integration",
        "repo_path": "secure/non-human-identity",
        "docs_path": "automation-core/secure/authentication-management.md",
        "products": ["IBM Verify", "HashiCorp Vault"],
        "tags": ["identity", "auth", "non-human", "security", "machine-identity", "secrets"],
    },
    "quantum-safe": {
        "name": "Quantum-Safe Cryptography",
        "group": "secure",
        "capability": "automation",
        "description": "Quantum-safe cryptographic algorithms and migration tools for post-quantum security",
        "repo_path": "secure/quantum-safe",
        "docs_path": "automation-core/secure/quantum-safe.md",
        "products": [],
        "tags": ["quantum", "cryptography", "security", "post-quantum"],
    },
    # --- Automation > Optimize ---
    "automated-resource-mgmt": {
        "name": "Automated Resource Management",
        "group": "optimize",
        "capability": "automation",
        "description": "Real-time resource scaling, workload placement, bottleneck prevention, SLA protection, and cost-performance optimization via IBM Turbonomic",
        "repo_path": "optimize/automated-resource-mgmt",
        "docs_path": "automation-core/optimize/automated-resource-management.md",
        "products": ["IBM Turbonomic"],
        "tags": ["resources", "scaling", "turbonomic", "workload", "optimization"],
    },
    "finops": {
        "name": "FinOps",
        "group": "optimize",
        "capability": "automation",
        "description": "Cost visibility across teams, budget forecasting, spend anomaly detection, cost allocation, and ROI evaluation via Apptio",
        "repo_path": "optimize/finops",
        "docs_path": "automation-core/optimize/finops.md",
        "products": ["Apptio"],
        "tags": ["finops", "cost", "budget", "optimization", "apptio"],
    },
    "automated-resilience": {
        "name": "Automated Resilience & Compliance",
        "group": "optimize",
        "capability": "automation",
        "description": "CVE monitoring, compliance drift detection, certificate lifecycle management, and security posture assessment via IBM Concert",
        "repo_path": "optimize/automated-resilience-and-compliance",
        "docs_path": "automation-core/optimize/automated-resilience.md",
        "products": ["IBM Concert"],
        "tags": ["resilience", "compliance", "cve", "security", "concert"],
    },
}

# ---------------------------------------------------------------------------
# Documentation Pages (from mkdocs.yml nav)
# ---------------------------------------------------------------------------

DOCS_PAGES: list[dict] = [
    # Home
    {"title": "Home", "section": "Home", "path": "index.md"},
    # AI > Agents
    {"title": "Agents Overview", "section": "AI > Agents", "path": "ai-core/agents/index.md"},
    {"title": "Agent Builder", "section": "AI > Agents", "path": "ai-core/agents/agent-builder.md"},
    {"title": "Multi-Agent Orchestration", "section": "AI > Agents", "path": "ai-core/agents/multi-agent-orchestration.md"},
    {"title": "Agentic SDLC", "section": "AI > Agents", "path": "ai-core/agents/agentic-sdlc.md"},
    # AI > AI Trust
    {"title": "AI Trust Overview", "section": "AI > AI Trust", "path": "ai-core/ai-trust/index.md"},
    {"title": "Model Evaluation", "section": "AI > AI Trust", "path": "ai-core/ai-trust/model-evaluation.md"},
    {"title": "Agent Ops", "section": "AI > AI Trust", "path": "ai-core/ai-trust/agent-ops.md"},
    {"title": "Real-Time Guardrails", "section": "AI > AI Trust", "path": "ai-core/ai-trust/real-time-guardrails.md"},
    {"title": "AI Compliance", "section": "AI > AI Trust", "path": "ai-core/ai-trust/ai-compliance.md"},
    # Data
    {"title": "Data Overview", "section": "Data", "path": "data-core/index.md"},
    # Data > Integration
    {"title": "Integration Overview", "section": "Data > Integration", "path": "data-core/integration/index.md"},
    {"title": "Data Pipeline (AI Generated)", "section": "Data > Integration", "path": "data-core/integration/data-pipeline-ai-generated/index.md"},
    {"title": "Data Streaming", "section": "Data > Integration", "path": "data-core/integration/data-streaming/index.md"},
    {"title": "Data Observability", "section": "Data > Integration", "path": "data-core/integration/data-observability/index.md"},
    # Data > Intelligence
    {"title": "Intelligence Overview", "section": "Data > Intelligence", "path": "data-core/intelligence/index.md"},
    {"title": "Data Quality", "section": "Data > Intelligence", "path": "data-core/intelligence/data-quality/index.md"},
    {"title": "Data Lineage", "section": "Data > Intelligence", "path": "data-core/intelligence/data-lineage/index.md"},
    {"title": "Text2SQL", "section": "Data > Intelligence", "path": "data-core/intelligence/text2sql/index.md"},
    # Data > Retrieval
    {"title": "Retrieval Overview", "section": "Data > Retrieval", "path": "data-core/retrieval/index.md"},
    {"title": "Vector Search Overview", "section": "Data > Retrieval > Vector Search", "path": "data-core/retrieval/vector-search/index.md"},
    {"title": "Vector Search (Milvus)", "section": "Data > Retrieval > Vector Search", "path": "data-core/retrieval/vector-search/milvus.md"},
    {"title": "Vector Search (OpenSearch)", "section": "Data > Retrieval > Vector Search", "path": "data-core/retrieval/vector-search/opensearch.md"},
    {"title": "Vector Search (DataStax Astra DB)", "section": "Data > Retrieval > Vector Search", "path": "data-core/retrieval/vector-search/datastax-astra-db.md"},
    {"title": "No SQL Database", "section": "Data > Retrieval", "path": "data-core/retrieval/no-sql-database/index.md"},
    {"title": "Zero Copy", "section": "Data > Retrieval", "path": "data-core/retrieval/zero-copy/index.md"},
    # Automation > Build and Deploy
    {"title": "Build and Deploy Overview", "section": "Automation > Build and Deploy", "path": "automation-core/build/index.md"},
    {"title": "iPaaS", "section": "Automation > Build and Deploy", "path": "automation-core/build/ipaas.md"},
    {"title": "Infrastructure as Code", "section": "Automation > Build and Deploy", "path": "automation-core/build/infrastructure-as-code.md"},
    {"title": "Code Modernization", "section": "Automation > Build and Deploy", "path": "automation-core/build/middleware-modernization.md"},
    # Automation > Secure
    {"title": "Secure Overview", "section": "Automation > Secure", "path": "automation-core/secure/index.md"},
    {"title": "Authentication Management", "section": "Automation > Secure", "path": "automation-core/secure/authentication-management.md"},
    {"title": "Quantum-Safe Cryptography", "section": "Automation > Secure", "path": "automation-core/secure/quantum-safe.md"},
    # Automation > Optimize
    {"title": "Optimize Overview", "section": "Automation > Optimize", "path": "automation-core/optimize/index.md"},
    {"title": "Automated Resilience & Compliance", "section": "Automation > Optimize", "path": "automation-core/optimize/automated-resilience.md"},
    {"title": "FinOps", "section": "Automation > Optimize", "path": "automation-core/optimize/finops.md"},
    {"title": "Automated Resource Management", "section": "Automation > Optimize", "path": "automation-core/optimize/automated-resource-management.md"},
    # Call to Action
    {"title": "IBM Bob and Building Blocks", "section": "IBM Bob", "path": "ibm-bob/index.md"},
    {"title": "Build with Bob Workshops", "section": "IBM Bob", "path": "workshop/index.md"},
    {"title": "Build with Bob Webinars", "section": "IBM Bob", "path": "build-with-bob/index.md"},
]


def get_block(block_id: str) -> dict | None:
    """Return a building block entry by ID, or None if not found."""
    return BUILDING_BLOCKS.get(block_id)


def get_group(group_id: str) -> dict | None:
    """Return a group entry by ID, or None if not found."""
    return GROUPS.get(group_id)


def get_capability(capability_id: str) -> dict | None:
    """Return a core capability entry by ID, or None if not found."""
    return CORE_CAPABILITIES.get(capability_id)


def blocks_for_group(group_id: str) -> list[dict]:
    """Return all building blocks belonging to a group."""
    return [
        {"id": bid, **b}
        for bid, b in BUILDING_BLOCKS.items()
        if b["group"] == group_id
    ]


def blocks_for_capability(capability_id: str) -> list[dict]:
    """Return all building blocks belonging to a core capability."""
    return [
        {"id": bid, **b}
        for bid, b in BUILDING_BLOCKS.items()
        if b["capability"] == capability_id
    ]
