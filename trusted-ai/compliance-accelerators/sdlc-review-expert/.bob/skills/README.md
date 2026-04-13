# Architecture Review Skills

This directory contains reusable skill definitions for conducting architecture reviews. Each skill provides a structured methodology, checklist, and output format for a specific review area.

## Available Skills

### 1. Business Alignment (`business-alignment-skill.md`)
**Purpose**: Evaluate how well the architecture supports organizational goals and quality attributes.

**Key Areas**:
- Strategic technology planning
- Quality attribute requirements
- Stakeholder analysis
- Cost-benefit analysis
- Risk assessment

**When to Use**: Strategic reviews, quality attribute validation, stakeholder requirement analysis

---

### 2. Security & Threat Modeling (`security-threat-modeling-skill.md`)
**Purpose**: Identify security gaps, potential attack vectors, and provide security recommendations.

**Key Areas**:
- OWASP Top 10 vulnerabilities
- STRIDE threat modeling
- Authentication/authorization
- Data protection and encryption
- Compliance (GDPR, HIPAA, PCI-DSS)

**When to Use**: Security reviews, compliance assessments, threat modeling sessions

---

### 3. Scalability & Performance (`scalability-performance-skill.md`)
**Purpose**: Evaluate system capacity, identify bottlenecks, and provide performance optimization recommendations.

**Key Areas**:
- Horizontal/vertical scaling
- Load balancing strategies
- Caching mechanisms
- Database optimization
- Performance benchmarking

**When to Use**: Performance analysis, capacity planning, scalability assessments

---

### 4. Architecture Patterns (`architecture-patterns-skill.md`)
**Purpose**: Evaluate pattern usage, identify anti-patterns, and recommend appropriate architectural patterns.

**Key Areas**:
- Microservices vs. Monolith
- CQRS, Event Sourcing, DDD
- SOLID principles
- Design patterns
- API design (REST, GraphQL, gRPC)

**When to Use**: Pattern reviews, design principle validation, architectural decision evaluation

---

### 5. Maintainability & Technical Debt (`maintainability-technical-debt-skill.md`)
**Purpose**: Identify maintainability issues, quantify technical debt, and provide refactoring recommendations.

**Key Areas**:
- Code complexity analysis
- Coupling and cohesion
- Code duplication
- Test coverage
- Technical debt quantification

**When to Use**: Technical debt assessments, code quality reviews, refactoring planning

---

### 6. Documentation Review (`documentation-review-skill.md`)
**Purpose**: Evaluate documentation completeness, clarity, and currency.

**Key Areas**:
- Architecture Decision Records (ADRs)
- C4 Model diagrams
- UML diagrams
- API documentation
- Runbooks and operational guides

**When to Use**: Documentation quality reviews, ADR validation, diagram completeness checks

---

### 7. 12-Factor Compliance (`twelve-factor-compliance-skill.md`)
**Purpose**: Evaluate compliance with 12-factor app methodology and provide cloud-native recommendations.

**Key Areas**:
- Codebase, Dependencies, Config
- Backing Services, Build/Release/Run
- Processes, Port Binding, Concurrency
- Disposability, Dev/Prod Parity
- Logs, Admin Processes

**When to Use**: Cloud-native readiness assessments, 12-factor compliance checks, deployment reviews

---

## How to Use Skills

### In Architecture Review Mode

When using the 🏛️ Architecture Review mode, Bob will automatically:

1. **Read the relevant skill file(s)** based on your request
2. **Apply the skill's methodology** to your codebase
3. **Follow the skill's checklist** and review process
4. **Provide structured output** using the skill's format

### Example Requests

**Complete Review (All Skills)**:
```
"Conduct a comprehensive architecture review using all 7 skills"
```

**Focused Review (Single Skill)**:
```
"Review security using the security-threat-modeling skill"
"Check 12-factor compliance"
"Analyze scalability and performance"
```

**Multi-Skill Review**:
```
"Review security, scalability, and 12-factor compliance"
"Focus on maintainability and documentation"
```

**Iterative Review**:
```
"Start with security review, then we'll do performance"
```

## Skill Structure

Each skill file contains:

### 1. Purpose
Clear statement of what the skill evaluates

### 2. Expertise Areas
List of specific knowledge domains covered

### 3. Review Process
Step-by-step methodology with:
- What to analyze
- Questions to ask
- Checklists to follow
- Metrics to consider

### 4. Output Format
Structured format including:
- ✅ **Achieved**: What's working well
- ⚠️ **Concerns**: Areas needing attention
- ❌ **Not Achieved**: Critical gaps
- 💡 **Recommendations**: Actionable improvements

### 5. Key Questions
Critical questions the skill answers

### 6. Best Practices
Guidelines and common pitfalls

## Customizing Skills

Skills can be customized for your organization:

1. **Add Organization-Specific Sections**
   - Internal compliance requirements
   - Company-specific patterns
   - Custom quality attributes

2. **Modify Checklists**
   - Add/remove checklist items
   - Adjust priorities
   - Include tool-specific checks

3. **Extend Methodologies**
   - Add additional review steps
   - Include custom metrics
   - Reference internal standards

4. **Update Output Formats**
   - Add custom sections
   - Modify scoring criteria
   - Include organization templates

## Skill Reusability

Skills are designed to be reusable across:

- **Different Projects**: Apply same methodology to any codebase
- **Different Modes**: Reference skills from other custom modes
- **Different Teams**: Share consistent review practices
- **Different Contexts**: Adapt to various review scenarios

## Creating New Skills

To create a new skill:

1. **Copy an existing skill** as a template
2. **Define the purpose** and expertise areas
3. **Create the review process** with checklists
4. **Define the output format** with examples
5. **Add key questions** and best practices
6. **Test the skill** on a real project
7. **Update this README** with the new skill

## Skill Maintenance

Keep skills up-to-date:

- **Regular Reviews**: Review skills quarterly
- **Industry Updates**: Incorporate new best practices
- **Team Feedback**: Gather feedback from users
- **Tool Updates**: Update for new tools and technologies
- **Version Control**: Track changes in Git

## Benefits of Skill-Based Reviews

✅ **Consistency**: Same methodology across all reviews
✅ **Reusability**: Use skills across projects and teams
✅ **Modularity**: Focus on specific areas as needed
✅ **Scalability**: Easy to add new skills
✅ **Knowledge Sharing**: Codified expertise
✅ **Training**: Onboard new architects faster
✅ **Quality**: Comprehensive, structured reviews

---

**Last Updated**: 2026-03-31  
**Version**: 1.0  
**Skills Count**: 7