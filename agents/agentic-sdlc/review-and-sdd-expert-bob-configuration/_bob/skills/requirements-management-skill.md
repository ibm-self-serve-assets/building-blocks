# Requirements Management Skill

## Purpose
Elicit, document, analyze, and validate software requirements to ensure they are complete, consistent, testable, and aligned with business objectives.

## Expertise Areas
- Requirements elicitation techniques (interviews, workshops, observation)
- Requirements documentation standards (IEEE 830, IREB)
- Requirements analysis and modeling
- Requirements prioritization (MoSCoW, Kano, WSJF)
- Requirements traceability
- Stakeholder management
- User story writing and acceptance criteria
- Use case modeling
- Non-functional requirements specification
- Requirements validation and verification

## Review Process

### 1. Stakeholder Analysis
**Identify and analyze all stakeholders:**
- Who are the primary users of the system?
- Who are the secondary stakeholders (managers, administrators, etc.)?
- What are their goals, needs, and pain points?
- What are their technical skill levels?
- What are their priorities and constraints?
- Who has decision-making authority?
- Who will be impacted by the system?

**Stakeholder Matrix:**
| Stakeholder | Role | Interest | Influence | Priority |
|-------------|------|----------|-----------|----------|
| End Users | Primary | High | Medium | Critical |
| Product Owner | Decision Maker | High | High | Critical |
| Development Team | Implementer | Medium | High | High |
| Operations | Maintainer | Medium | Medium | High |

### 2. Requirements Elicitation
**Techniques to gather requirements:**

**Interviews:**
- Conduct one-on-one or group interviews
- Prepare structured questions
- Document responses and insights
- Follow up on unclear points

**Workshops:**
- Facilitate collaborative sessions
- Use brainstorming techniques
- Create shared understanding
- Resolve conflicts early

**Observation:**
- Watch users in their environment
- Identify unstated needs
- Understand workflows
- Discover pain points

**Document Analysis:**
- Review existing documentation
- Analyze current systems
- Study business processes
- Identify gaps and opportunities

**Prototyping:**
- Create mockups or prototypes
- Gather feedback iteratively
- Validate assumptions
- Refine requirements

### 3. Functional Requirements Documentation

**Format: User Stories**
```
As a [user role]
I want [goal/desire]
So that [benefit/value]

Acceptance Criteria:
- Given [context]
  When [action]
  Then [expected outcome]
```

**Format: Use Cases**
```
Use Case: [Name]
Actor: [Primary actor]
Preconditions: [What must be true before]
Main Flow:
  1. [Step 1]
  2. [Step 2]
  3. [Step 3]
Alternative Flows:
  - [Alternative scenario]
Postconditions: [What is true after]
```

**Checklist for Functional Requirements:**
- [ ] Clear and unambiguous description
- [ ] Testable and verifiable
- [ ] Traceable to business objective
- [ ] Prioritized (Must/Should/Could/Won't)
- [ ] Acceptance criteria defined
- [ ] Dependencies identified
- [ ] Assumptions documented
- [ ] Unique identifier assigned

### 4. Non-Functional Requirements (NFRs)

**Performance Requirements:**
- Response time targets (e.g., < 200ms for 95% of requests)
- Throughput requirements (e.g., 1000 transactions/second)
- Resource utilization limits (CPU, memory, disk)
- Concurrent user capacity
- Data volume handling

**Security Requirements:**
- Authentication mechanisms (OAuth, SAML, MFA)
- Authorization model (RBAC, ABAC)
- Data encryption (at rest, in transit)
- Audit logging requirements
- Compliance requirements (GDPR, HIPAA, PCI-DSS)
- Security testing requirements

**Scalability Requirements:**
- Horizontal scaling capability
- Vertical scaling limits
- Geographic distribution
- Load balancing strategy
- Auto-scaling triggers

**Usability Requirements:**
- Accessibility standards (WCAG 2.1 Level AA)
- User interface guidelines
- Learning curve expectations
- Error message clarity
- Help and documentation

**Reliability Requirements:**
- Uptime targets (e.g., 99.9% availability)
- Mean Time Between Failures (MTBF)
- Mean Time To Recovery (MTTR)
- Backup and recovery procedures
- Disaster recovery requirements

**Maintainability Requirements:**
- Code quality standards
- Documentation requirements
- Modularity and extensibility
- Technology stack constraints
- Upgrade and migration paths

**Checklist for NFRs:**
- [ ] Specific and measurable
- [ ] Realistic and achievable
- [ ] Testable with clear metrics
- [ ] Prioritized by importance
- [ ] Trade-offs identified
- [ ] Monitoring approach defined

### 5. Requirements Analysis

**Completeness Check:**
- Are all user scenarios covered?
- Are all system interfaces defined?
- Are all data requirements specified?
- Are all business rules documented?
- Are error conditions addressed?
- Are edge cases considered?

**Consistency Check:**
- Do requirements contradict each other?
- Are terms used consistently?
- Are priorities aligned?
- Do NFRs support functional requirements?

**Feasibility Analysis:**
- Technical feasibility: Can it be built with available technology?
- Economic feasibility: Is it cost-effective?
- Operational feasibility: Can it be operated and maintained?
- Schedule feasibility: Can it be delivered on time?

**Risk Analysis:**
- What requirements are high-risk?
- What are the technical risks?
- What are the business risks?
- What mitigation strategies exist?

### 6. Requirements Prioritization

**MoSCoW Method:**
- **Must Have**: Critical for project success
- **Should Have**: Important but not critical
- **Could Have**: Nice to have if time permits
- **Won't Have**: Out of scope for this release

**Kano Model:**
- **Basic Needs**: Expected features (dissatisfiers if missing)
- **Performance Needs**: More is better (satisfiers)
- **Excitement Needs**: Unexpected delighters

**WSJF (Weighted Shortest Job First):**
```
WSJF = (Business Value + Time Criticality + Risk Reduction) / Job Size
```

**Priority Matrix:**
| Requirement | Business Value | Technical Complexity | Priority | Release |
|-------------|----------------|---------------------|----------|---------|
| FR-001 | High | Low | Must Have | 1.0 |
| FR-002 | Medium | High | Should Have | 1.1 |
| FR-003 | Low | Low | Could Have | 2.0 |

### 7. Requirements Traceability

**Traceability Matrix:**
| Req ID | Business Goal | Design Element | Implementation | Test Case | Status |
|--------|---------------|----------------|----------------|-----------|--------|
| FR-001 | Goal-1 | Component-A | Module-X | TC-001 | ✅ |
| FR-002 | Goal-1 | Component-B | Module-Y | TC-002 | 🔄 |
| NFR-001 | Goal-2 | Architecture | Config | TC-003 | ⏳ |

**Traceability Links:**
- **Forward Traceability**: Requirements → Design → Implementation → Tests
- **Backward Traceability**: Tests → Implementation → Design → Requirements
- **Bidirectional Traceability**: Both forward and backward

### 8. Requirements Validation

**Validation Techniques:**

**Reviews and Inspections:**
- Peer review of requirements documents
- Stakeholder review sessions
- Technical feasibility reviews
- Compliance reviews

**Prototyping:**
- Create UI mockups
- Build proof-of-concepts
- Demonstrate workflows
- Gather feedback

**Test Case Derivation:**
- Can test cases be written?
- Are acceptance criteria testable?
- Can requirements be verified?

**Validation Checklist:**
- [ ] Stakeholders approve requirements
- [ ] Requirements are complete
- [ ] Requirements are consistent
- [ ] Requirements are testable
- [ ] Requirements are feasible
- [ ] Requirements are unambiguous
- [ ] Requirements are traceable
- [ ] Acceptance criteria are clear

### 9. Requirements Change Management

**Change Request Process:**
1. **Submit Change Request**
   - Describe proposed change
   - Justify the change
   - Assess impact

2. **Impact Analysis**
   - Technical impact
   - Schedule impact
   - Cost impact
   - Risk impact

3. **Review and Approval**
   - Change control board review
   - Stakeholder approval
   - Priority assessment

4. **Implementation**
   - Update requirements
   - Update traceability
   - Communicate changes
   - Update documentation

**Change Tracking:**
| Change ID | Requirement | Description | Impact | Status | Approved By |
|-----------|-------------|-------------|--------|--------|-------------|
| CR-001 | FR-005 | Add export feature | Medium | Approved | Product Owner |
| CR-002 | NFR-003 | Increase capacity | High | Pending | Architecture |

## Output Format

### Requirements Document Structure

```markdown
# Requirements Specification: [Project Name]

## Document Information
- **Version**: 1.0
- **Date**: YYYY-MM-DD
- **Author**: [Name]
- **Status**: Draft / Review / Approved

## 1. Introduction

### 1.1 Purpose
[Purpose of this document]

### 1.2 Scope
[What is included and excluded]

### 1.3 Definitions and Acronyms
| Term | Definition |
|------|------------|
| API | Application Programming Interface |

### 1.4 References
- [Related documents]

## 2. Overall Description

### 2.1 Product Perspective
[How this fits into the larger system]

### 2.2 Product Functions
[High-level capabilities]

### 2.3 User Characteristics
[Who will use the system]

### 2.4 Constraints
- Technical constraints
- Business constraints
- Regulatory constraints

### 2.5 Assumptions and Dependencies
- [Assumption 1]
- [Dependency 1]

## 3. Functional Requirements

### 3.1 [Feature Area 1]

#### FR-001: [Requirement Name]
- **Priority**: Must Have / Should Have / Could Have / Won't Have
- **Description**: [Clear description]
- **User Story**: As a [user], I want [goal] so that [benefit]
- **Acceptance Criteria**:
  - [ ] Given [context], when [action], then [outcome]
  - [ ] Given [context], when [action], then [outcome]
- **Dependencies**: [List of dependent requirements]
- **Assumptions**: [Any assumptions]
- **Notes**: [Additional information]

## 4. Non-Functional Requirements

### 4.1 Performance Requirements
#### NFR-001: Response Time
- **Description**: System response time for user interactions
- **Metric**: 95% of requests complete within 200ms
- **Priority**: Critical
- **Test Method**: Load testing with 1000 concurrent users

### 4.2 Security Requirements
#### NFR-002: Authentication
- **Description**: User authentication mechanism
- **Metric**: Support OAuth 2.0 and MFA
- **Priority**: Critical
- **Compliance**: GDPR, SOC2

### 4.3 Scalability Requirements
#### NFR-003: Concurrent Users
- **Description**: System capacity for concurrent users
- **Metric**: Support 10,000 concurrent users
- **Priority**: High
- **Test Method**: Load testing and capacity planning

### 4.4 Usability Requirements
#### NFR-004: Accessibility
- **Description**: Accessibility compliance
- **Metric**: WCAG 2.1 Level AA compliance
- **Priority**: High
- **Test Method**: Automated accessibility testing

### 4.5 Reliability Requirements
#### NFR-005: Availability
- **Description**: System uptime
- **Metric**: 99.9% uptime (8.76 hours downtime/year)
- **Priority**: Critical
- **Test Method**: Monitoring and incident tracking

## 5. System Features

### 5.1 [Feature Name]
- **Description**: [Feature description]
- **Priority**: [Must/Should/Could/Won't]
- **Functional Requirements**: FR-001, FR-002, FR-003
- **Non-Functional Requirements**: NFR-001, NFR-002

## 6. External Interface Requirements

### 6.1 User Interfaces
- [UI requirements]

### 6.2 Hardware Interfaces
- [Hardware requirements]

### 6.3 Software Interfaces
- [Integration requirements]

### 6.4 Communication Interfaces
- [Network protocols, APIs]

## 7. Quality Attributes

### 7.1 Maintainability
- Code quality standards
- Documentation requirements
- Modularity requirements

### 7.2 Portability
- Platform independence
- Browser compatibility
- Mobile support

### 7.3 Testability
- Test coverage requirements
- Automated testing requirements
- Test data requirements

## 8. Appendices

### Appendix A: Traceability Matrix
[Requirements traceability]

### Appendix B: Glossary
[Terms and definitions]

### Appendix C: Analysis Models
[Diagrams and models]
```

## Key Questions This Skill Answers

1. **What needs to be built?**
   - Functional capabilities
   - System features
   - User workflows

2. **Why does it need to be built?**
   - Business justification
   - User needs
   - Value proposition

3. **Who will use it?**
   - User personas
   - Stakeholder groups
   - Access levels

4. **How well must it perform?**
   - Performance targets
   - Quality attributes
   - Success metrics

5. **What are the constraints?**
   - Technical limitations
   - Business constraints
   - Regulatory requirements

6. **How will we know it's done?**
   - Acceptance criteria
   - Test cases
   - Definition of Done

## Best Practices

### DO:
✅ Involve stakeholders early and often
✅ Use clear, unambiguous language
✅ Make requirements testable and verifiable
✅ Prioritize ruthlessly
✅ Maintain traceability
✅ Document assumptions and constraints
✅ Use visual models to complement text
✅ Review and validate regularly
✅ Manage changes systematically
✅ Keep requirements at appropriate level of detail

### DON'T:
❌ Use vague terms like "fast", "user-friendly", "robust"
❌ Mix requirements with design decisions
❌ Assume stakeholders understand technical terms
❌ Document everything as "must have"
❌ Ignore non-functional requirements
❌ Skip validation with stakeholders
❌ Let requirements become stale
❌ Forget to trace requirements to implementation
❌ Overlook edge cases and error conditions
❌ Write requirements in isolation

## Common Pitfalls

### Pitfall 1: Vague Requirements
❌ **Bad**: "The system should be fast"
✅ **Good**: "The system shall respond to user search queries within 200ms for 95% of requests under normal load (1000 concurrent users)"

### Pitfall 2: Solution-Focused Requirements
❌ **Bad**: "The system shall use Redis for caching"
✅ **Good**: "The system shall cache frequently accessed data to achieve sub-200ms response times"

### Pitfall 3: Missing Acceptance Criteria
❌ **Bad**: "Users can log in"
✅ **Good**: 
```
Users can log in
Acceptance Criteria:
- Given valid credentials, when user submits login form, then user is authenticated and redirected to dashboard
- Given invalid credentials, when user submits login form, then error message is displayed
- Given locked account, when user attempts login, then account locked message is displayed
```

### Pitfall 4: Ignoring Non-Functional Requirements
❌ **Bad**: Only documenting functional features
✅ **Good**: Documenting performance, security, scalability, usability, and reliability requirements

### Pitfall 5: No Prioritization
❌ **Bad**: Everything is "critical" or "must have"
✅ **Good**: Clear prioritization using MoSCoW or similar method

## Integration with Other Skills

- **Architecture Patterns**: Validate that requirements align with architectural decisions
- **Security & Threat Modeling**: Ensure security requirements are comprehensive
- **Scalability & Performance**: Define performance and scalability requirements
- **Documentation Review**: Ensure requirements are well-documented
- **12-Factor Compliance**: Align requirements with cloud-native principles

## Tools and Techniques

### Requirements Management Tools
- JIRA / Azure DevOps
- IBM DOORS
- Confluence
- Notion
- Miro / Mural (for workshops)

### Modeling Techniques
- Use Case Diagrams (UML)
- User Story Mapping
- Event Storming
- Domain Modeling (DDD)
- Process Flow Diagrams

### Prioritization Frameworks
- MoSCoW (Must, Should, Could, Won't)
- Kano Model
- WSJF (Weighted Shortest Job First)
- Value vs. Effort Matrix

### Validation Techniques
- Requirements Reviews
- Prototyping
- Acceptance Test-Driven Development (ATDD)
- Behavior-Driven Development (BDD)

## Success Metrics

Track requirements management effectiveness:
- **Requirements Stability**: % of requirements that don't change after baseline
- **Requirements Coverage**: % of requirements with test cases
- **Defect Traceability**: % of defects traced to requirements issues
- **Stakeholder Satisfaction**: Feedback on requirements quality
- **Time to Clarity**: Average time to get clear, approved requirements
- **Rework Rate**: % of work redone due to unclear requirements

---

**Skill Version**: 1.0  
**Last Updated**: 2026-05-26  
**Maintained By**: Requirements Engineering Team