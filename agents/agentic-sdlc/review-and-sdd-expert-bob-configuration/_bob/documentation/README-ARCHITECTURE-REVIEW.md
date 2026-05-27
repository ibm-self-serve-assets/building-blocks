# Architecture Review Mode with Reusable Skills

A modular, skill-based architecture review system for Bob Code Assistant.

The initial example usage was showcased in the YouTube video before being integrated into our core library of building blocks.

<div align="left">
      <a href="https://www.youtube.com/watch?v=vx-8XHzsvG4">
         <img src="https://img.youtube.com/vi/vx-8XHzsvG4/0.jpg" style="width:100%;">
      </a>
</div>


## 📋 Overview

This repository provides a **skill-based architecture review mode** that uses reusable, specialized review skills. Instead of multiple separate modes, you have:

- **1 Architecture Review Mode** (🏛️) - Orchestrates reviews using skills
- **7 Specialized Skills** - Reusable review methodologies for different areas

This modular approach provides:
- ✅ **Flexibility**: Use all skills or focus on specific areas
- ✅ **Reusability**: Skills can be used across projects and modes
- ✅ **Consistency**: Same methodology every time
- ✅ **Maintainability**: Update skills independently
- ✅ **Extensibility**: Easy to add new skills

## 🎯 Architecture

```
┌─────────────────────────────────────┐
│  🏛️ Architecture Review Mode        │
│  (Orchestrator)                     │
└──────────────┬──────────────────────┘
               │
               │ Uses
               ▼
┌─────────────────────────────────────┐
│  📚 Review Skills (Reusable)        │
├─────────────────────────────────────┤
│  1. Business Alignment              │
│  2. Security & Threat Modeling      │
│  3. Scalability & Performance       │
│  4. Architecture Patterns           │
│  5. Maintainability & Tech Debt     │
│  6. Documentation Review            │
│  7. 12-Factor Compliance            │
└─────────────────────────────────────┘
```

## 📁 File Structure

```
.bob/
  └── custom_modes.yaml              # Architecture Review mode definition

prompts/
  ├── skills/                        # Reusable review skills
  │   ├── README.md                  # Skills documentation
  │   ├── business-alignment-skill.md
  │   ├── security-threat-modeling-skill.md
  │   ├── scalability-performance-skill.md
  │   ├── architecture-patterns-skill.md
  │   ├── maintainability-technical-debt-skill.md
  │   ├── documentation-review-skill.md
  │   └── twelve-factor-compliance-skill.md
  │
  ├── architecture-review-template.md    # Review document template
  └── architecture-review-guide.md       # Comprehensive usage guide
```

## 🚀 Quick Start

### 1. Activate the Mode
Switch to **🏛️ Architecture Review** mode in Bob

### 2. Request a Review

**Complete Review (All 7 Skills)**:
```
"Conduct a comprehensive architecture review using all skills"
```

**Focused Review (Specific Skills)**:
```
"Review security using the security-threat-modeling skill"
"Check 12-factor compliance"
"Analyze scalability and performance"
```

**Multi-Skill Review**:
```
"Review security, scalability, and 12-factor compliance"
```

### 3. Bob Will:
1. Read the relevant skill file(s) from `skills/`
2. Apply the skill's methodology to your codebase
3. Follow the skill's checklist and review process
4. Provide structured output with findings and recommendations

## 📚 Available Skills

### 1. 🎯 Business Alignment
**File**: `skills/business-alignment-skill.md`

Evaluates how well the architecture supports organizational goals and quality attributes.

**Key Areas**:
- Strategic technology planning
- Quality attribute requirements (performance, security, availability)
- Stakeholder analysis and management
- Cost-benefit analysis and ROI
- Risk assessment and mitigation

**Use When**: Strategic reviews, quality attribute validation, stakeholder analysis

---

### 2. 🔒 Security & Threat Modeling
**File**: `skills/security-threat-modeling-skill.md`

Identifies security gaps, potential attack vectors, and provides security recommendations.

**Key Areas**:
- OWASP Top 10 vulnerabilities
- STRIDE threat modeling
- Authentication and authorization
- Data protection and encryption
- Compliance (GDPR, HIPAA, PCI-DSS, SOC2)

**Use When**: Security reviews, compliance assessments, threat modeling

---

### 3. 📈 Scalability & Performance
**File**: `skills/scalability-performance-skill.md`

Evaluates system capacity, identifies bottlenecks, and provides performance optimization recommendations.

**Key Areas**:
- Horizontal and vertical scaling strategies
- Load balancing and distribution
- Caching strategies (CDN, application, database)
- Database optimization and indexing
- Performance benchmarking and SLAs

**Use When**: Performance analysis, capacity planning, scalability assessments

---

### 4. 🎨 Architecture Patterns
**File**: `skills/architecture-patterns-skill.md`

Evaluates pattern usage, identifies anti-patterns, and recommends appropriate patterns.

**Key Areas**:
- Microservices vs. Monolith architecture
- CQRS, Event Sourcing, DDD
- SOLID principles
- Design patterns (GoF, Enterprise)
- API design (REST, GraphQL, gRPC)

**Use When**: Pattern reviews, design principle validation, architectural decisions

---

### 5. 🔧 Maintainability & Technical Debt
**File**: `skills/maintainability-technical-debt-skill.md`

Identifies maintainability issues, quantifies technical debt, and provides refactoring recommendations.

**Key Areas**:
- Code complexity analysis (cyclomatic, cognitive)
- Coupling and cohesion analysis
- Code duplication detection
- Test coverage and quality
- Technical debt quantification

**Use When**: Technical debt assessments, code quality reviews, refactoring planning

---

### 6. 📚 Documentation Review
**File**: `skills/documentation-review-skill.md`

Evaluates documentation completeness, clarity, and currency.

**Key Areas**:
- Architecture Decision Records (ADRs)
- C4 Model diagrams (Context, Container, Component, Code)
- UML diagrams (sequence, class, deployment)
- API documentation (OpenAPI, AsyncAPI)
- Runbooks and operational guides

**Use When**: Documentation quality reviews, ADR validation, diagram completeness

---

### 7. ☁️ 12-Factor Compliance
**File**: `skills/twelve-factor-compliance-skill.md`

Evaluates compliance with 12-factor app methodology and provides cloud-native recommendations.

**Key Areas**:
- Codebase, Dependencies, Config
- Backing Services, Build/Release/Run
- Processes, Port Binding, Concurrency
- Disposability, Dev/Prod Parity
- Logs, Admin Processes

**Use When**: Cloud-native readiness, 12-factor compliance, deployment reviews

---

## 💡 Usage Examples

### Example 1: Complete Architecture Review
```
User: "Conduct a comprehensive architecture review of this system"

Bob will:
1. Read all 7 skill files
2. Apply each skill's methodology
3. Provide findings for each area
4. Create executive summary
5. Prioritize recommendations
```

### Example 2: Security-Focused Review
```
User: "Review security using the security-threat-modeling skill"

Bob will:
1. Read security-threat-modeling-skill.md
2. Perform STRIDE threat modeling
3. Check OWASP Top 10
4. Assess authentication/authorization
5. Provide security recommendations
```

### Example 3: Pre-Production Checklist
```
User: "Review security, scalability, and 12-factor compliance before production"

Bob will:
1. Read the 3 relevant skill files
2. Apply each skill's checklist
3. Identify production readiness gaps
4. Prioritize critical issues
```

### Example 4: Technical Debt Assessment
```
User: "Analyze technical debt and maintainability"

Bob will:
1. Read maintainability-technical-debt-skill.md
2. Analyze code complexity
3. Identify coupling issues
4. Quantify technical debt
5. Provide refactoring roadmap
```

## 📊 Review Output Format

Each skill provides structured output:

### ✅ Achieved
What's working well and meets standards

### ⚠️ Concerns
Areas needing attention or improvement

### ❌ Not Achieved
Critical gaps that must be addressed

### 💡 Recommendations
Specific, actionable improvements with:
- Priority (Critical/High/Medium/Low)
- Impact and benefits
- Implementation approach
- Effort estimate

## 🎓 Benefits of Skill-Based Approach

### For Architects
- ✅ **Consistent methodology** across all reviews
- ✅ **Reusable expertise** codified in skills
- ✅ **Flexible scope** - use what you need
- ✅ **Easy to extend** with new skills

### For Teams
- ✅ **Knowledge sharing** through documented skills
- ✅ **Faster onboarding** with clear processes
- ✅ **Quality assurance** with checklists
- ✅ **Continuous improvement** by updating skills

### For Organizations
- ✅ **Standardized reviews** across projects
- ✅ **Scalable process** as teams grow
- ✅ **Audit trail** of review decisions
- ✅ **Best practices** captured and shared

## 🔧 Customizing Skills

Skills can be customized for your organization:

### 1. Modify Existing Skills
Edit skill files in `skills/` to:
- Add organization-specific requirements
- Include custom compliance checks
- Reference internal standards
- Add company-specific patterns

### 2. Create New Skills
Copy an existing skill and customize:
```bash
cp skills/security-threat-modeling-skill.md \
   skills/custom-compliance-skill.md
```

### 3. Update the Mode
No changes needed! The mode automatically uses any skill files in `skills/`

## 📖 Documentation

- **[Skills README](../skills/README.md)** - Detailed skill documentation
- **[Review Template](guides/architecture-review-template.md)** - Output template
- **[Usage Guide](guides/architecture-review-guide.md)** - Comprehensive guide

## 🎯 Use Cases

### Pre-Production Review
```
"Review security, scalability, and 12-factor compliance before production deployment"
```

### Technical Debt Sprint
```
"Analyze maintainability and technical debt to plan refactoring sprint"
```

### Architecture Board Preparation
```
"Conduct comprehensive review for architecture board presentation"
```

### Compliance Audit
```
"Review security and 12-factor compliance for SOC2 audit"
```

### Performance Investigation
```
"Analyze scalability and performance to identify bottlenecks"
```

### Documentation Sprint
```
"Review documentation completeness and create improvement plan"
```

## 🔄 Workflow

```
1. Request Review
   ↓
2. Bob Reads Relevant Skills
   ↓
3. Bob Applies Skill Methodology
   ↓
4. Bob Analyzes Codebase
   ↓
5. Bob Provides Structured Findings
   ↓
6. Team Reviews Recommendations
   ↓
7. Team Creates Action Items
   ↓
8. Follow-up Review (if needed)
```

## 📈 Success Metrics

Track the effectiveness of your reviews:
- Number of critical issues identified
- Issues resolved before production
- Reduction in production incidents
- Improvement in code quality metrics
- Team satisfaction with review process
- Time saved in review board meetings

## 🆘 Support

For questions or issues:
1. Review the [Skills README](../skills/README.md)
2. Check the [Usage Guide](guides/architecture-review-guide.md)
3. Review the [Template](guides/architecture-review-template.md)
4. Consult with senior architects

## 🔄 Version History

- **v2.0** (2026-03-31) - Skill-based modular approach
  - 7 reusable review skills
  - Single orchestrator mode
  - Flexible, focused reviews
  - Enhanced reusability

- **v1.0** (2026-03-31) - Initial release
  - Single comprehensive mode
  - 7 review areas
  - Structured output

---

**Created**: 2026-03-31  
**Last Updated**: 2026-03-31  
**Version**: 2.0  
**Skills**: 7

For the latest updates, check the repository regularly.