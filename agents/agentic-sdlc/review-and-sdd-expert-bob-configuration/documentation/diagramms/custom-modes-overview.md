# Custom Modes Overview Diagram

This document explains the [`custom-modes-overview.drawio`](custom-modes-overview.drawio:1) diagram that visualizes all modes defined in [`.bob/custom_modes.yaml`](../.bob/custom_modes.yaml:1).

## Diagram Purpose

The diagram provides a comprehensive visual representation of:
- The main Architecture Review mode (orchestrator)
- All 7 specialized review modes
- The 7 review skill files they utilize
- The relationships between modes and skills

## Target Audience

**Primary Users:** Developers and programmers who maintain the [`.bob/custom_modes.yaml`](../.bob/custom_modes.yaml:1) file

**Use Cases:**
- Understanding the complete mode architecture
- Verifying all modes are properly defined
- Identifying relationships between modes and skills
- Onboarding new team members to the review system
- Planning mode enhancements or additions

## Diagram Structure

### Main Orchestrator Mode

**Architecture Review (arch-review)**
- Central orchestrator that can use all 7 specialized skills
- Conducts comprehensive reviews across all areas
- Supports focused reviews using specific skills
- Enables iterative reviews, one skill at a time

### Specialized Review Modes

The diagram shows 7 specialized modes, each focusing on a specific aspect:

1. **Security and Threat Modeling (security-review)**
   - OWASP Top 10, STRIDE threat modeling
   - Authentication, authorization, data protection
   - Compliance requirements (GDPR, HIPAA, PCI-DSS, SOC2)

2. **Scalability and Performance (scalability-review)**
   - Horizontal/vertical scaling strategies
   - Load balancing, caching, optimization
   - Performance benchmarking and capacity planning

3. **Architecture Patterns (patterns-review)**
   - Microservices, CQRS, Event Sourcing, DDD
   - SOLID principles and design patterns
   - API design (REST, GraphQL, gRPC)

4. **Maintainability and Technical Debt (maintainability-review)**
   - Code complexity and coupling analysis
   - Test coverage and refactoring strategies
   - Technical debt quantification

5. **Documentation Review (documentation-review)**
   - Architecture Decision Records (ADRs)
   - C4 Model and UML diagrams
   - API documentation and runbooks

6. **12-Factor Compliance (twelve-factor-review)**
   - Cloud-native principles (all 12 factors)
   - Configuration, processes, logs
   - Dev/prod parity and disposability

7. **Business Alignment (business-alignment-review)**
   - Strategic technology planning
   - Quality attribute requirements
   - Stakeholder analysis and ROI evaluation

### Review Skills

All skills are located in [`skills/`](../../skills/README.md:1) directory:

1. [`business-alignment-skill.md`](../../skills/business-alignment-skill.md:1)
2. [`security-threat-modeling-skill.md`](../../skills/security-threat-modeling-skill.md:1)
3. [`scalability-performance-skill.md`](../../skills/scalability-performance-skill.md:1)
4. [`architecture-patterns-skill.md`](../../skills/architecture-patterns-skill.md:1)
5. [`maintainability-technical-debt-skill.md`](../../skills/maintainability-technical-debt-skill.md:1)
6. [`documentation-review-skill.md`](../../skills/documentation-review-skill.md:1)
7. [`twelve-factor-compliance-skill.md`](../../skills/twelve-factor-compliance-skill.md:1)

## Visual Elements

### Color Coding

- **Blue (#4A90E2)**: Main orchestrator mode
- **Purple (#7B68EE)**: Specialized review modes
- **Green (#50C878)**: Review skill files
- **Gray (#f5f5f5)**: Container backgrounds

### Connection Types

- **Solid arrows**: Direct orchestration relationship
- **Dashed arrows**: "uses" relationship between modes and skills

## Mode Capabilities

All modes share these capabilities:
- **Groups**: read, edit, command, mcp
- **Structured Output**: Achieved, Concerns, Not Achieved, Recommendations
- **Priority Levels**: Critical, High, Medium, Low
- **Evidence-Based**: Specific examples and code references

## Usage Patterns

### Complete Review
Use the **Architecture Review** mode to conduct comprehensive reviews across all 7 areas.

### Focused Review
Use specialized modes for deep analysis in specific areas:
- Security concerns → Security and Threat Modeling
- Performance issues → Scalability and Performance
- Design decisions → Architecture Patterns
- Code quality → Maintainability and Technical Debt
- Documentation gaps → Documentation Review
- Cloud readiness → 12-Factor Compliance
- Business alignment → Business Alignment

### Iterative Review
Start with Architecture Review and work through skills one at a time based on priority.

## Maintenance Notes

When updating [`.bob/custom_modes.yaml`](../.bob/custom_modes.yaml:1):
1. Ensure all modes are reflected in the diagram
2. Verify skill file references are correct
3. Update relationships if new modes or skills are added
4. Keep color coding consistent for visual clarity
5. Update this documentation to reflect changes

## Related Files

- Configuration: [`modes/custom_modes.yaml`](../../modes/custom_modes.yaml:1)
- Skills Directory: [`skills/`](../../skills/README.md:1)
- Architecture Review Guide: [`documentation/guides/architecture-review-guide.md`](../guides/architecture-review-guide.md:1)
- System Diagram: [`architecture-review-system.drawio`](architecture-review-system.drawio:1)