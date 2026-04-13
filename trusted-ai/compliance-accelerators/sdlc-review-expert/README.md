# Custom Modes for `SDLC-Review` and `Configuration Gap Detector` Usage Guide

## How do these modes fit into Trusted AI building block

This custom modes configuration provides a **robust, modular framework** for architecture reviews with **strong alignment (80%) to IBM's Trusted AI building block**. The skill-based approach ensures consistency, reusability, and extensibility, while the Configuration Gap Detector enables continuous adaptation to emerging requirements.

**For AI/ML Systems**: The current configuration provides excellent governance, documentation, security, and performance support. With targeted enhancements for AI-specific validation capabilities (bias, fairness, explainability) and integration with watsonx.governance, this framework can become a **comprehensive Trusted AI review system**.

**Next Steps**:
1. Use existing modes for immediate AI system reviews
2. Leverage Configuration Gap Detector to propose AI-specific skills
3. Integrate with watsonx.governance workflows
4. Continuously enhance based on AI governance requirements

---

**Document Version**: 1.0  
**Created**: 2026-04-13  
**Last Updated**: 2026-04-13  
**Modes Documented**: 10  
**Skills Referenced**: 7  
**Trusted AI Alignment**: ⭐⭐⭐⭐☆ (4/5 Stars - 80%)

## Overview

This guide provides comprehensive documentation for the custom modes configured in this Bob Code Assistant project, including detailed skill documentation and an analysis of their alignment with IBM's **Trusted AI** building block from watsonx.governance and watsonx.ai.

---

## Table of Contents

1. [Custom Modes Overview](#custom-modes-overview)
2. [Architecture Review Mode](#architecture-review-mode)
3. [Specialized Review Modes](#specialized-review-modes)
4. [Configuration Gap Detector Mode](#configuration-gap-detector-mode)
5. [Detailed Skills Documentation](#detailed-skills-documentation)
6. [Trusted AI Alignment Analysis](#trusted-ai-alignment-analysis)
7. [Usage Examples](#usage-examples)
8. [Best Practices](#best-practices)

---

## Custom Modes Overview

This project includes **10 custom modes** organized into three categories:

### 1. Comprehensive Review Mode
- **🏛️ Architecture Review** - Orchestrates comprehensive reviews using 7 specialized skills

### 2. Specialized Review Modes (7)
- **🔒 Security & Threat Modeling** - Security architecture and threat analysis
- **📈 Scalability & Performance** - System scalability and performance analysis
- **🎨 Architecture Patterns** - Architecture patterns and best practices
- **🔧 Maintainability & Technical Debt** - Code maintainability and technical debt
- **📚 Documentation Review** - Architecture documentation and diagrams
- **☁️ 12-Factor Compliance** - Cloud-native 12-factor app compliance
- **🎯 Business Alignment** - Business goals and quality attributes

### 3. Configuration Management Mode
- **🔍 Configuration Gap Detector** - Detects configuration gaps and proposes new modes/skills

---

## Architecture Review Mode

### Purpose
The **🏛️ Architecture Review** mode is the primary orchestrator that conducts comprehensive architecture reviews using specialized, reusable skills.

### Key Features
- **Skill-Based Architecture**: Uses 7 modular review skills from `.bob/skills/`
- **Flexible Scope**: Conduct complete or focused reviews
- **Consistent Methodology**: Same approach across all reviews
- **Extensible**: Easy to add new skills

### When to Use
- Complete comprehensive reviews (all 7 areas)
- Focused reviews (specific areas like security or performance)
- Pre-production validation
- Technical debt assessment
- Architecture board preparation
- Compliance checks

### Available Skills
1. **business-alignment-skill.md** - Business goals and quality attributes
2. **security-threat-modeling-skill.md** - Security gaps and threat analysis
3. **scalability-performance-skill.md** - System capacity and performance
4. **architecture-patterns-skill.md** - Patterns and best practices
5. **maintainability-technical-debt-skill.md** - Code quality and technical debt
6. **documentation-review-skill.md** - Documentation completeness
7. **twelve-factor-compliance-skill.md** - Cloud-native readiness

---

## Specialized Review Modes

Each specialized mode focuses on a specific aspect of architecture review. See the [Detailed Skills Documentation](#detailed-skills-documentation) section for complete information about each skill.

![](./images/architecture-review.png)

### 🔒 Security & Threat Modeling
- OWASP Top 10, STRIDE threat modeling
- Authentication, authorization, encryption
- Compliance (GDPR, HIPAA, PCI-DSS, SOC2)

### 📈 Scalability & Performance
- Horizontal/vertical scaling, load balancing
- Caching strategies, database optimization
- Performance benchmarking, capacity planning

### 🎨 Architecture Patterns
- Microservices, CQRS, Event Sourcing, DDD
- SOLID principles, design patterns
- API design (REST, GraphQL, gRPC)

### 🔧 Maintainability & Technical Debt
- Code complexity, coupling/cohesion analysis
- Test coverage, refactoring strategies
- Technical debt quantification

### 📚 Documentation Review
- ADRs, C4 Model diagrams, UML diagrams
- API documentation, runbooks
- Documentation-as-code practices

### ☁️ 12-Factor Compliance
- All 12 factors for cloud-native apps
- Configuration management, stateless design
- CI/CD, containerization

### 🎯 Business Alignment
- Strategic planning, quality attributes
- Stakeholder analysis, cost-benefit analysis
- Risk assessment, ROI evaluation

---

## Configuration Gap Detector Mode

The **🔍 Configuration Gap Detector** identifies when current configuration is insufficient and proposes new capabilities based on research from authoritative sources.

### Key Capabilities
- Gap detection in domain knowledge or workflows
- Research-backed proposals using browser capabilities
- Minimal, targeted additions without duplication
- Evidence-based recommendations

### When to Use
- Task outside scope of existing modes
- New domain requirements (IoT, blockchain, ML)
- Periodic configuration health checks
- Before complex, unfamiliar tasks

---

## Detailed Skills Documentation

![](./images/skills-review.png)

### Skill 1: Business Alignment Review

**File**: `.bob/skills/business-alignment-skill.md`

**Purpose**: Evaluate how architecture supports organizational goals and quality attributes.

**Key Review Areas**:
1. Business objectives identification
2. Architecture-to-capability mapping
3. Quality attribute evaluation (performance, security, availability, scalability, maintainability, usability, reliability)
4. Stakeholder concerns assessment
5. Cost-benefit analysis
6. Business risk identification

**Output Includes**:
- ✅ Achieved alignments
- ⚠️ Concerns needing attention
- ❌ Critical gaps
- 💡 Prioritized recommendations with business impact

---

### Skill 2: Security & Threat Modeling Review

**File**: `.bob/skills/security-threat-modeling-skill.md`

**Purpose**: Identify security gaps and provide actionable security recommendations.

**Key Review Areas**:
1. **Authentication & Authorization**: OAuth, SAML, JWT, MFA, RBAC, ABAC
2. **Data Protection**: Encryption at rest/transit, key management, data masking
3. **Network Security**: Segmentation, firewalls, DMZ, intrusion detection
4. **STRIDE Threat Modeling**:
   - Spoofing Identity
   - Tampering with Data
   - Repudiation
   - Information Disclosure
   - Denial of Service
   - Elevation of Privilege
5. **OWASP Top 10**: Broken access control, cryptographic failures, injection, etc.
6. **Compliance**: GDPR, HIPAA, PCI-DSS, SOC2, ISO 27001

**Output Includes**:
- Threat model summary table
- Risk ratings (Critical/High/Medium/Low)
- Specific remediation steps
- Security checklist

---

### Skill 3: Scalability & Performance Review

**File**: `.bob/skills/scalability-performance-skill.md`

**Purpose**: Evaluate system capacity and provide performance optimization recommendations.

**Key Review Areas**:
1. **Current Load Analysis**: Traffic volume, peak patterns, resource utilization
2. **Scaling Strategies**: Horizontal/vertical scaling, auto-scaling
3. **Load Balancing**: Round-robin, least connections, health checking
4. **Caching**: CDN, application cache (Redis/Memcached), database cache
5. **Database Performance**: Query optimization, indexing, read replicas, sharding
6. **Asynchronous Processing**: Message queues, background workers
7. **API Performance**: Rate limiting, throttling, bulk operations

**Performance Metrics**:
- Response time (p50, p95, p99, p99.9)
- Throughput (RPS, TPS)
- Resource utilization (CPU, memory, disk, network)
- Availability (uptime, MTBF, MTTR, error rate)

**Output Includes**:
- Performance metrics table
- Bottleneck identification
- Optimization recommendations with expected improvements

---

### Skill 4: Architecture Patterns Review

**File**: `.bob/skills/architecture-patterns-skill.md`

**Purpose**: Evaluate pattern usage and recommend appropriate architectural patterns.

**Key Review Areas**:
1. **Architecture Style**: Monolith vs. Microservices vs. Serverless
2. **CQRS**: Command/query separation, eventual consistency
3. **Event-Driven Architecture**: Event bus, schema management, event sourcing
4. **Domain-Driven Design**: Bounded contexts, aggregates, entities, value objects
5. **SOLID Principles**: SRP, OCP, LSP, ISP, DIP
6. **Design Patterns**:
   - Creational: Factory, Builder, Singleton, Prototype
   - Structural: Adapter, Decorator, Facade, Proxy
   - Behavioral: Strategy, Observer, Command, Template Method
   - Enterprise: Repository, Unit of Work, Service Layer, DTO
7. **API Design**: REST, GraphQL, gRPC best practices
8. **Integration Patterns**: Point-to-point, pub-sub, API gateway, BFF
9. **Resilience Patterns**: Circuit breaker, retry, bulkhead, timeout

**Output Includes**:
- Pattern analysis table
- Anti-pattern identification
- Pattern recommendations with trade-offs

**Common Anti-Patterns**:
- God Object, Spaghetti Code, Golden Hammer
- Big Ball of Mud, Distributed Monolith
- Anemic Domain Model, Shotgun Surgery

---

### Skill 5: Maintainability & Technical Debt Review

**File**: `.bob/skills/maintainability-technical-debt-skill.md`

**Purpose**: Identify maintainability issues and quantify technical debt.

**Key Review Areas**:
1. **Code Complexity**: Cyclomatic complexity, cognitive complexity, LOC
2. **Coupling & Cohesion**: Module coupling, circular dependencies, cohesion analysis
3. **Code Duplication**: DRY principle violations, duplication percentage
4. **Dependency Management**: Dependency count, outdated dependencies, vulnerabilities
5. **Test Coverage**: Overall coverage, branch coverage, test quality
6. **Code Smells**:
   - Bloaters: Long Method, Large Class, Long Parameter List
   - OO Abusers: Switch Statements, Temporary Field
   - Change Preventers: Divergent Change, Shotgun Surgery
   - Dispensables: Dead Code, Duplicate Code, Lazy Class
   - Couplers: Feature Envy, Inappropriate Intimacy
7. **Technical Debt Quantification**:
   - Code, Design, Test, Documentation, Infrastructure, Dependency debt
   - Time/cost to fix, interest, risk level
   - Prioritization matrix

**Maintainability Metrics**:
- Maintainability Index (0-100): >85 Good, 65-85 Moderate, <65 Difficult
- Technical Debt Ratio: Remediation cost / Development cost (target <10%)
- Code Churn: Frequency of changes

**Output Includes**:
- Technical debt assessment table
- Code quality metrics table
- Refactoring roadmap with priorities

---

### Skill 6: Documentation Review

**File**: `.bob/skills/documentation-review-skill.md`

**Purpose**: Evaluate documentation completeness, clarity, and currency.

**Key Review Areas**:
1. **Architecture Decision Records (ADRs)**:
   - Title, Status, Context, Decision, Consequences, Alternatives
   - Coverage: Technology, patterns, integration, data, security, performance
2. **C4 Model Diagrams**:
   - Level 1: System Context
   - Level 2: Container
   - Level 3: Component
   - Level 4: Code
3. **UML Diagrams**: Sequence, Class, Deployment, Activity
4. **API Documentation**:
   - REST: OpenAPI/Swagger, endpoints, examples, versioning
   - GraphQL: Schema, queries, mutations, subscriptions
   - gRPC: Protocol buffers, service definitions
5. **Runbooks**:
   - Deployment: Steps, rollback, configuration, checklists
   - Operational: Monitoring, incident response, troubleshooting
   - Maintenance: Backup/restore, database maintenance
6. **System Documentation**: README, architecture overview, system context
7. **Developer Documentation**: Setup guides, coding standards, testing docs
8. **Data Documentation**: ERD, schema, data dictionary, data flow
9. **Security Documentation**: Security architecture, procedures

**Documentation Best Practices**:
- Documentation as Code
- Living Documentation
- Automated Generation
- Consistent Format
- Searchable and Versioned

**Output Includes**:
- Documentation checklist table
- Gap identification
- Recommendations with templates

---

### Skill 7: 12-Factor Compliance Review

**File**: `.bob/skills/twelve-factor-compliance-skill.md`

**Purpose**: Evaluate cloud-native 12-factor app compliance.

**The 12 Factors**:

1. **Codebase**: One codebase in version control, many deploys
2. **Dependencies**: Explicitly declare and isolate dependencies
3. **Config**: Store config in environment variables
4. **Backing Services**: Treat as attached resources
5. **Build, Release, Run**: Strictly separate stages
6. **Processes**: Execute as stateless processes
7. **Port Binding**: Export services via port binding
8. **Concurrency**: Scale out via process model
9. **Disposability**: Fast startup, graceful shutdown
10. **Dev/Prod Parity**: Keep environments similar
11. **Logs**: Treat as event streams (stdout/stderr)
12. **Admin Processes**: Run as one-off processes

**Review Process**:
- Evaluate each factor systematically
- Provide compliance status (✅/⚠️/❌) and score (0-10)
- Identify specific violations
- Explain impact of non-compliance
- Provide remediation steps

**Cloud-Native Readiness Score**:
- 90-120 points (75-100%): Excellent - Cloud-native ready
- 72-89 points (60-74%): Good - Minor improvements needed
- 60-71 points (50-59%): Fair - Significant work required
- <60 points (<50%): Poor - Major refactoring needed

**Output Includes**:
- Factor compliance table with scores
- Overall readiness score
- Migration path recommendations

---

## Trusted AI Alignment Analysis

### IBM Trusted AI Building Block

**Definition**: Capabilities from watsonx.governance and watsonx.ai that support **model validation**, **guardrails**, and **governance workflows**.

### Alignment Assessment

#### ✅ Strong Alignment Areas (4/5 Stars - 80%)

**1. Model Validation Capabilities** ⭐⭐⭐⭐☆

The custom modes provide strong support for AI model validation:

- **🔒 Security Mode**: Validates AI/ML model security, data pipeline security, model API authentication, data privacy compliance
- **📈 Performance Mode**: Validates model inference performance, latency, throughput, scalability of model serving
- **🔧 Maintainability Mode**: Validates model code quality, ML pipeline technical debt, test coverage for models

**2. Governance Workflow Support** ⭐⭐⭐⭐⭐

Excellent support for AI governance:

- **📚 Documentation Mode**: Model cards, data sheets, ADRs for model decisions, API documentation for model endpoints
- **🎯 Business Alignment Mode**: Quality attributes (fairness, explainability, accuracy), stakeholder requirements, risk assessment
- **☁️ 12-Factor Mode**: Cloud-native model deployment, configuration management, logging/monitoring for AI systems

**3. Guardrails Implementation** ⭐⭐⭐⭐☆

Good architectural support for guardrails:

- **🎨 Patterns Mode**: Validates appropriate patterns for AI systems, identifies ML architecture anti-patterns
- **🔍 Gap Detector Mode**: Identifies missing AI capabilities, proposes new AI governance skills

#### ⚠️ Areas for Enhancement

**1. AI-Specific Validation Skills** (Current: ⭐⭐⭐☆☆, Potential: ⭐⭐⭐⭐⭐)

Recommended new skills:
- **ai-model-validation-skill.md**: Model quality metrics, bias/fairness testing, explainability validation, drift detection
- **ai-data-governance-skill.md**: Data quality, lineage, privacy compliance, sensitive data handling
- **ai-mlops-skill.md**: ML pipeline validation, model deployment, monitoring, retraining workflows
- **ai-ethics-compliance-skill.md**: Ethical AI principles, regulatory compliance (EU AI Act), risk frameworks

**2. Governance Workflow Integration** (Current: ⭐⭐⭐⭐☆, Potential: ⭐⭐⭐⭐⭐)

Enhancements:
- Integration with watsonx.governance workflows
- Model approval and promotion workflows
- Automated compliance reporting
- Risk scoring and mitigation tracking

**3. Guardrails Enforcement** (Current: ⭐⭐⭐☆☆, Potential: ⭐⭐⭐⭐⭐)

Enhancements:
- Automated guardrail enforcement
- Policy-as-code validation
- Real-time monitoring integration
- Input/output validation rules

### Trusted AI Fit Score: ⭐⭐⭐⭐☆ (4/5 Stars - 80%)

**Detailed Scoring**:

| Trusted AI Capability | Current | Enhancement Potential | Final |
|----------------------|---------|----------------------|-------|
| Model Security Validation | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐☆ | ⭐⭐⭐⭐⭐ |
| Model Performance Validation | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐☆ | ⭐⭐⭐⭐⭐ |
| Model Quality Validation | ⭐⭐⭐☆☆ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐☆ |
| Bias & Fairness Validation | ⭐⭐☆☆☆ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐☆☆ |
| Explainability Validation | ⭐⭐☆☆☆ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐☆☆ |
| Documentation & Governance | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐☆ | ⭐⭐⭐⭐⭐ |
| Compliance & Risk | ⭐⭐⭐⭐☆ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Architectural Guardrails | ⭐⭐⭐⭐☆ | ⭐⭐⭐⭐☆ | ⭐⭐⭐⭐☆ |
| Operational Monitoring | ⭐⭐⭐☆☆ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐☆ |
| MLOps & Deployment | ⭐⭐⭐☆☆ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐☆ |

**Conclusion**: The custom modes provide a **strong foundation** for Trusted AI capabilities, particularly in governance workflows, documentation, security, and performance validation. With targeted enhancements for AI-specific validation (bias, fairness, explainability) and guardrails enforcement, this configuration could become a **comprehensive Trusted AI review framework** fully aligned with IBM watsonx.governance capabilities.

**Key Strengths**:
- ✅ Excellent governance and documentation support
- ✅ Strong security and performance validation
- ✅ Comprehensive architecture review methodology
- ✅ Extensible through Configuration Gap Detector

**Enhancement Opportunities**:
- 💡 Add AI-specific validation skills (bias, fairness, explainability)
- 💡 Integrate with watsonx.governance workflows
- 💡 Enhance guardrails enforcement capabilities
- 💡 Add MLOps and model lifecycle management skills

---

## Usage Examples

### Example 1: Pre-Production AI Model Review
```
Mode: 🏛️ Architecture Review
Request: "Review security, scalability, and documentation for our AI model deployment"

Bob will:
1. Read security-threat-modeling-skill.md
2. Read scalability-performance-skill.md
3. Read documentation-review-skill.md
4. Analyze model serving infrastructure
5. Identify security vulnerabilities
6. Assess performance and scalability
7. Review model documentation
8. Provide prioritized recommendations
```

### Example 2: AI Governance Compliance Check
```
Mode: 🎯 Business Alignment
Request: "Validate our AI system aligns with business goals and quality attributes"

Bob will:
1. Read business-alignment-skill.md
2. Identify business objectives
3. Map AI capabilities to business needs
4. Evaluate quality attributes (fairness, accuracy, explainability)
5. Assess stakeholder concerns
6. Perform risk assessment
7. Provide alignment recommendations
```

### Example 3: Detecting AI-Specific Gaps
```
Mode: 🔍 Configuration Gap Detector
Request: "Check if current configuration supports AI model bias validation"

Bob will:
1. Review existing modes and skills
2. Identify gap in AI bias validation
3. Research industry best practices (NIST AI RMF, EU AI Act)
4. Propose new "ai-model-validation-skill.md"
5. Include bias testing methodology
6. Provide implementation guidance
```

### Example 4: Technical Debt in ML Pipeline
```
Mode: 🔧 Maintainability & Technical Debt
Request: "Analyze technical debt in our ML training pipeline"

Bob will:
1. Read maintainability-technical-debt-skill.md
2. Analyze pipeline code complexity
3. Identify coupling issues
4. Detect code duplication
5. Assess test coverage
6. Quantify technical debt
7. Provide refactoring roadmap
```

### Example 5: Complete Architecture Review
```
Mode: 🏛️ Architecture Review
Request: "Conduct comprehensive architecture review using all skills"

Bob will:
1. Read all 7 skill files
2. Apply each skill's methodology
3. Provide findings for each area
4. Create executive summary
5. Prioritize recommendations across all areas
6. Highlight critical issues
```

---

## Best Practices

### 1. Start with the Right Mode
- Use **🏛️ Architecture Review** for comprehensive reviews
- Use specialized modes for focused analysis
- Use **🔍 Configuration Gap Detector** when unsure or for new domains

### 2. Be Specific in Requests
- Clearly state the scope (complete vs. focused)
- Specify priority areas (security-first, performance-first)
- Mention specific components or concerns
- Provide context about the system

### 3. Leverage Skills Effectively
- Review skill files to understand methodology
- Request specific skills by name
- Combine multiple skills for comprehensive coverage
- Use skills iteratively for deep dives

### 4. Iterate and Refine
- Start with high-level review
- Deep-dive into specific areas based on findings
- Follow up on critical findings
- Schedule regular reviews

### 5. Document Findings
- Use provided templates and formats
- Track recommendations and action items
- Create follow-up tasks
- Schedule follow-up reviews

### 6. Continuous Improvement
- Use Configuration Gap Detector for new requirements
- Update skills based on lessons learned
- Share findings across teams
- Maintain skill documentation

### 7. For AI/ML Systems
- Always include security and documentation reviews
- Validate performance under realistic load
- Check business alignment and quality attributes
- Consider proposing AI-specific skills through Gap Detector
- Focus on model governance and auditability
- Validate bias, fairness, and explainability
- Ensure compliance with AI regulations

### 8. Integration with Trusted AI
- Document model decisions in ADRs
- Create model cards and data sheets
- Implement model monitoring and alerting
- Establish model approval workflows
- Track model lineage and versioning
- Validate against quality attributes
- Ensure stakeholder transparency
