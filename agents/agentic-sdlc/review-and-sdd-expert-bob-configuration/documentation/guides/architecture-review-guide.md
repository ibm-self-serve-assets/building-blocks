# Architecture Review Mode - Quick Reference Guide

## Overview
The Architecture Review mode (🏛️) is designed to conduct comprehensive architecture reviews covering all critical aspects of software systems.

## When to Use
- Pre-production architecture validation
- Technical debt assessment
- Security and compliance reviews
- Scalability and performance analysis
- Documentation completeness checks
- 12-factor app methodology compliance
- Preparing materials for architecture review boards

## Review Aspects Covered

### 1. Business Alignment
Ensures the architecture supports organizational goals and quality requirements.
- Strategic alignment with business objectives
- Quality attribute requirements (performance, security, availability, etc.)
- Stakeholder concerns and priorities
- Cost-benefit analysis

### 2. Security & Threat Modeling
Identifies security gaps and potential attack vectors early in the design phase.
- Authentication and authorization mechanisms
- Data protection and encryption
- Network security and segmentation
- Compliance requirements (GDPR, HIPAA, PCI-DSS, etc.)
- OWASP Top 10 vulnerabilities
- Threat modeling (STRIDE, PASTA, etc.)

### 3. Scalability & Performance
Evaluates if the system handles increased demand and meets response time goals.
- Horizontal and vertical scaling strategies
- Load balancing and distribution
- Caching strategies (CDN, application, database)
- Database optimization and indexing
- Asynchronous processing
- Performance benchmarks and SLAs

### 4. Architecture Patterns & Best Practices
Checks for appropriate use of patterns and industry standards.
- Microservices vs. Monolith
- CQRS (Command Query Responsibility Segregation)
- Event Sourcing
- Domain-Driven Design (DDD)
- SOLID principles
- Design patterns (Factory, Strategy, Observer, etc.)
- API design (REST, GraphQL, gRPC)

### 5. Maintainability & Technical Debt
Identifies issues that make future changes expensive.
- Code coupling and cohesion
- Dependency management
- Code complexity metrics
- Test coverage and quality
- Refactoring opportunities
- Technical debt tracking

### 6. Documentation Review
Ensures key decisions and diagrams are clear and documented.
- Architecture Decision Records (ADRs)
- C4 Model diagrams (Context, Container, Component, Code)
- Sequence and flow diagrams
- API documentation
- Deployment architecture
- Runbooks and operational guides

### 7. 12-Factor App Compliance
Verifies adherence to the twelve-factor methodology.
1. **Codebase:** One codebase tracked in revision control
2. **Dependencies:** Explicitly declare and isolate dependencies
3. **Config:** Store config in the environment
4. **Backing Services:** Treat backing services as attached resources
5. **Build, Release, Run:** Strictly separate build and run stages
6. **Processes:** Execute as stateless processes
7. **Port Binding:** Export services via port binding
8. **Concurrency:** Scale out via the process model
9. **Disposability:** Fast startup and graceful shutdown
10. **Dev/Prod Parity:** Keep environments similar
11. **Logs:** Treat logs as event streams
12. **Admin Processes:** Run admin tasks as one-off processes

## How to Use the Mode

### Step 1: Activate the Mode
Switch to the Architecture Review mode in Bob.

### Step 2: Provide Context
Give Bob access to:
- Source code repositories
- Architecture documentation
- Configuration files
- Deployment scripts
- API specifications
- Test results and metrics

### Step 3: Request the Review
Example prompts:
- "Conduct a comprehensive architecture review of this system"
- "Review the security architecture and identify potential threats"
- "Assess our 12-factor app compliance"
- "Evaluate the scalability of our microservices architecture"

### Step 4: Review the Output
Bob will generate a structured document covering all review aspects with:
- ✅ Achieved: What's working well
- ⚠️ Concerns: Areas needing attention
- ❌ Not Achieved: Critical gaps
- 💡 Recommendations: Actionable improvements

### Step 5: Prepare for Review Board
Use the generated document as the foundation for architecture review board discussions.

## Output Format

The review document includes:
1. **Executive Summary** - High-level overview and key findings
2. **Detailed Analysis** - Section for each review aspect
3. **Risk Assessment** - Prioritized findings (Critical, High, Medium, Low)
4. **Recommendations** - Specific, actionable improvements with effort estimates
5. **Action Items** - Prioritized list with owners and timelines
6. **Discussion Points** - Key questions for the review board
7. **Appendices** - Supporting diagrams, code examples, and references

## Best Practices

### For Reviewers
- Provide complete context (code, docs, configs)
- Be specific about areas of concern
- Share any existing metrics or test results
- Mention any known issues or constraints

### For Review Recipients
- Approach feedback constructively
- Prioritize critical and high-priority items
- Create action items with clear owners
- Schedule follow-up reviews for major changes

## Example Use Cases

### Use Case 1: Pre-Production Review
**Scenario:** New microservices application ready for production
**Focus:** Security, scalability, 12-factor compliance
**Outcome:** Identified 3 critical security issues, 5 scalability improvements, and 2 12-factor violations

### Use Case 2: Technical Debt Assessment
**Scenario:** Legacy monolith considering modernization
**Focus:** Maintainability, architecture patterns, technical debt
**Outcome:** Documented $500K in technical debt, proposed phased migration strategy

### Use Case 3: Compliance Review
**Scenario:** Healthcare application requiring HIPAA compliance
**Focus:** Security, documentation, compliance requirements
**Outcome:** Identified 12 compliance gaps, created remediation roadmap

### Use Case 4: Performance Optimization
**Scenario:** E-commerce platform experiencing slow response times
**Focus:** Scalability, performance, architecture patterns
**Outcome:** Identified database bottlenecks, proposed caching strategy, estimated 60% performance improvement

## Tips for Effective Reviews

1. **Be Thorough:** Review all aspects, not just code
2. **Be Objective:** Focus on facts and evidence
3. **Be Constructive:** Provide actionable recommendations
4. **Be Contextual:** Consider project maturity and constraints
5. **Be Prioritized:** Focus on high-impact issues first
6. **Be Documented:** Keep records of decisions and rationales
7. **Be Collaborative:** Involve stakeholders in discussions

## Common Pitfalls to Avoid

- ❌ Reviewing code without understanding business context
- ❌ Focusing only on technical aspects, ignoring business alignment
- ❌ Providing vague recommendations without specific actions
- ❌ Ignoring operational and maintenance concerns
- ❌ Not prioritizing findings by risk and impact
- ❌ Conducting reviews too late in the development cycle
- ❌ Not following up on action items

## Resources

### Templates
- `prompts/architecture-review-template.md` - Complete review document template

### Standards and Frameworks
- [12-Factor App](https://12factor.net/)
- [C4 Model](https://c4model.com/)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Architecture Decision Records](https://adr.github.io/)
- [STRIDE Threat Modeling](https://learn.microsoft.com/en-us/azure/security/develop/threat-modeling-tool-threats)

### Books
- "Software Architecture in Practice" by Bass, Clements, Kazman
- "Building Microservices" by Sam Newman
- "Domain-Driven Design" by Eric Evans
- "Clean Architecture" by Robert C. Martin

## Support

For questions or issues with the Architecture Review mode:
1. Check the template and guide documentation
2. Review example outputs
3. Consult with senior architects
4. Iterate on the review based on feedback

---

**Last Updated:** 2026-03-31  
**Version:** 1.0