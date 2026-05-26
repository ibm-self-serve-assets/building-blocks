# Documentation Review Skill

## Purpose
Evaluate documentation completeness, clarity, and currency, ensuring architectural decisions are well-documented.

## Expertise Areas
- Architecture Decision Records (ADRs)
- C4 Model diagrams (Context, Container, Component, Code)
- UML diagrams (sequence, class, deployment, activity)
- API documentation (OpenAPI, AsyncAPI)
- Runbooks and operational guides
- System context and constraints
- Documentation-as-code practices
- Diagram generation tools (PlantUML, Mermaid, Draw.io)
- README best practices
- Knowledge management

## Review Process

### 1. Architecture Decision Records (ADRs)

**ADR Completeness**
- Are significant decisions documented?
- Is there an ADR template?
- Are ADRs numbered and dated?
- Are ADRs stored in version control?

**ADR Content Quality**
- **Title**: Clear and descriptive
- **Status**: Proposed, Accepted, Deprecated, Superseded
- **Context**: Problem and constraints
- **Decision**: What was decided
- **Consequences**: Positive and negative outcomes
- **Alternatives**: Options considered
- **Related Decisions**: Links to other ADRs

**ADR Coverage**
- Technology choices
- Architecture patterns
- Integration approaches
- Data storage decisions
- Security decisions
- Performance trade-offs
- Deployment strategies

### 2. C4 Model Diagrams

**Level 1: System Context**
- Shows the system and its users
- Shows external systems
- Defines system boundaries
- Shows high-level interactions

**Level 2: Container**
- Shows applications and data stores
- Shows technology choices
- Shows inter-container communication
- Shows deployment boundaries

**Level 3: Component**
- Shows components within containers
- Shows component responsibilities
- Shows component interactions
- Shows key abstractions

**Level 4: Code**
- Shows class diagrams (if needed)
- Shows implementation details
- Usually generated from code

**Diagram Quality**
- Are diagrams up-to-date?
- Are they easy to understand?
- Is there a consistent notation?
- Are they version controlled?
- Are they accessible to the team?

### 3. UML Diagrams

**Sequence Diagrams**
- Key user flows documented
- API interactions shown
- Error handling flows
- Authentication flows
- Critical business processes

**Class Diagrams**
- Domain model documented
- Key relationships shown
- Inheritance hierarchies clear
- Design patterns visible

**Deployment Diagrams**
- Infrastructure topology
- Network architecture
- Deployment environments
- Scaling configuration

**Activity Diagrams**
- Business process flows
- Decision points
- Parallel activities
- Error handling paths

### 4. API Documentation

**REST API Documentation**
- OpenAPI/Swagger specification
- Endpoint descriptions
- Request/response examples
- Authentication requirements
- Error codes and messages
- Rate limiting information
- Versioning strategy

**GraphQL API Documentation**
- Schema documentation
- Query examples
- Mutation examples
- Subscription examples
- Error handling
- Authentication

**gRPC API Documentation**
- Protocol buffer definitions
- Service descriptions
- Method documentation
- Error codes
- Streaming patterns

**API Documentation Quality**
- Is it auto-generated from code?
- Are examples provided?
- Is it interactive (Swagger UI)?
- Is it versioned?
- Is it kept up-to-date?

### 5. Runbooks and Operational Guides

**Deployment Runbooks**
- Deployment steps
- Rollback procedures
- Environment configuration
- Pre-deployment checklist
- Post-deployment verification

**Operational Runbooks**
- Monitoring and alerting
- Incident response procedures
- Troubleshooting guides
- Common issues and solutions
- Escalation procedures

**Maintenance Guides**
- Backup and restore procedures
- Database maintenance
- Log rotation
- Certificate renewal
- Dependency updates

### 6. System Documentation

**README Files**
- Project overview
- Getting started guide
- Prerequisites
- Installation instructions
- Configuration
- Usage examples
- Contributing guidelines
- License information

**Architecture Overview**
- System purpose and goals
- High-level architecture
- Key components
- Technology stack
- Design principles
- Quality attributes

**System Context**
- Business context
- User personas
- Use cases
- Constraints
- Assumptions
- Dependencies

### 7. Developer Documentation

**Setup Guides**
- Development environment setup
- IDE configuration
- Local development workflow
- Testing locally
- Debugging tips

**Coding Standards**
- Code style guide
- Naming conventions
- File organization
- Comment guidelines
- Git workflow

**Testing Documentation**
- Testing strategy
- Test types and coverage
- How to run tests
- How to write tests
- Test data management

### 8. Data Documentation

**Data Models**
- Entity-Relationship Diagrams (ERD)
- Database schema
- Data dictionary
- Relationships and constraints
- Indexing strategy

**Data Flow**
- Data sources
- Data transformations
- Data storage
- Data archival
- Data retention policies

### 9. Security Documentation

**Security Architecture**
- Authentication mechanisms
- Authorization model
- Data encryption
- Network security
- Compliance requirements

**Security Procedures**
- Security incident response
- Vulnerability management
- Access control procedures
- Security testing
- Audit logging

### 10. Documentation Maintenance

**Version Control**
- Is documentation in version control?
- Is it versioned with code?
- Are there documentation reviews?
- Is there a documentation owner?

**Currency**
- When was documentation last updated?
- Is there a review schedule?
- Are there outdated sections?
- Is there a deprecation process?

**Accessibility**
- Where is documentation stored?
- Is it easily discoverable?
- Is it searchable?
- Is it accessible to all stakeholders?

## Output Format

### ✅ Achieved
- List well-documented areas
- Highlight available diagrams
- Note clear decision records
- Identify good documentation practices

### ⚠️ Concerns
- Incomplete documentation
- Outdated diagrams
- Missing rationales
- Inconsistent documentation

### ❌ Not Achieved
- Critical documentation gaps
- No architectural diagrams
- Undocumented decisions
- Missing operational guides

### 📚 Documentation Checklist
| Document Type | Status | Last Updated | Quality | Priority |
|--------------|--------|--------------|---------|----------|
| ADRs | ✅/⚠️/❌ | [date] | ⭐⭐⭐⭐⭐ | High |
| C4 Context | ✅/⚠️/❌ | [date] | ⭐⭐⭐⭐☆ | High |
| C4 Container | ✅/⚠️/❌ | [date] | ⭐⭐⭐☆☆ | High |
| C4 Component | ✅/⚠️/❌ | [date] | ⭐⭐☆☆☆ | Medium |
| Sequence Diagrams | ✅/⚠️/❌ | [date] | ⭐⭐⭐⭐☆ | Medium |
| API Docs | ✅/⚠️/❌ | [date] | ⭐⭐⭐⭐⭐ | High |
| Deployment Diagram | ✅/⚠️/❌ | [date] | ⭐⭐⭐☆☆ | High |
| Runbooks | ✅/⚠️/❌ | [date] | ⭐⭐☆☆☆ | High |
| README | ✅/⚠️/❌ | [date] | ⭐⭐⭐⭐☆ | High |
| Data Models | ✅/⚠️/❌ | [date] | ⭐⭐⭐☆☆ | Medium |

### 💡 Recommendations
For each documentation gap:
- **Priority**: Critical/High/Medium/Low
- **Missing**: What documentation is missing
- **Action**: Specific documentation to create
- **Template**: Suggested format or tool
- **Owner**: Who should create it
- **Effort**: Time estimate
- **Benefits**: Why it's important

## Key Questions to Answer
1. Are architectural decisions documented?
2. Are diagrams current and accurate?
3. Is the API well-documented?
4. Are operational procedures documented?
5. Can new team members onboard easily?
6. Is documentation maintained regularly?
7. Is documentation accessible to stakeholders?
8. Are there documentation standards?

## Documentation Best Practices
- ✅ **Documentation as Code**: Store in version control
- ✅ **Living Documentation**: Keep it up-to-date
- ✅ **Automated Generation**: Generate from code where possible
- ✅ **Consistent Format**: Use templates and standards
- ✅ **Searchable**: Make it easy to find
- ✅ **Versioned**: Track changes over time
- ✅ **Reviewed**: Include in code reviews
- ✅ **Accessible**: Available to all stakeholders

## Documentation Tools
- **Diagrams**: PlantUML, Mermaid, Draw.io, Lucidchart
- **API Docs**: Swagger/OpenAPI, Postman, GraphQL Playground
- **ADRs**: adr-tools, log4brains
- **Wikis**: Confluence, Notion, GitHub Wiki
- **Static Sites**: MkDocs, Docusaurus, GitBook
- **Diagrams as Code**: Structurizr, Diagrams.net

## Common Documentation Anti-Patterns
- ❌ **Outdated Documentation**: Not maintained
- ❌ **Over-Documentation**: Too much detail
- ❌ **Under-Documentation**: Too little information
- ❌ **Scattered Documentation**: No central location
- ❌ **Duplicate Documentation**: Same info in multiple places
- ❌ **Code Comments as Documentation**: Should be supplementary
- ❌ **No Documentation Standards**: Inconsistent format
- ❌ **Documentation Debt**: Accumulating gaps