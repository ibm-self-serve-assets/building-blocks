# Review & SDD Expert Bob Configuration

A comprehensive Bob configuration for **Architecture Reviews** and **Spec-Driven Development (SDD)**, providing specialized modes and reusable skills for software development lifecycle excellence.

The initial example usage was showcased in the YouTube video before being integrated into our core library of building blocks.

<div align="left">
      <a href="https://www.youtube.com/watch?v=vx-8XHzsvG4">
         <img src="https://img.youtube.com/vi/vx-8XHzsvG4/0.jpg" style="width:100%;">
      </a>
</div>
---

## 📋 Overview

This configuration transforms IBM Bob into a powerful architecture review and requirements management partner with:

- 🏛️ **Architecture Review Mode** - Comprehensive reviews using 8 specialized skills
- 📝 **Spec-Driven Development Mode** - Requirements management and prompt crafting
- 🔍 **Configuration Gap Detector** - Adaptive configuration improvement
- 📚 **8 Reusable Skills** - Modular expertise for different review areas

**Key Benefits**:
- ✅ Consistent, repeatable review methodology
- ✅ Modular skills that can be used independently
- ✅ Comprehensive coverage of architecture concerns
- ✅ Easy to customize for your organization
- ✅ Integrates seamlessly with your SDLC

---

## Specialized Review Modes

Each specialized mode focuses on a specific aspect of architecture review.

![](./images/architecture-review.png)

---

---

## Configuration Gap Detector Mode

The **🔍 Configuration Gap Detector** identifies when current configuration is insufficient and proposes new capabilities based on research from authoritative sources.

![](./images/configuration-gap-detector.png)

---

## Detailed Skills

![](./images/skills-review.png)

---

## SDD Skills

![](./images/spec-driven-development-overview.png)

## 🚀 Quick Start (5 Minutes)

### Prerequisites

- ✅ **IBM Bob installed** - [Download here](https://bob.ibm.com/docs/ide/getting-started/install)
- ✅ **IBMid account** - Required for authentication
- ✅ **System requirements**:
  - Operating Systems: macOS, Linux, or Windows
  - Memory: Minimum 4 GB RAM (8 GB recommended)

### Get Modes and Configurations for IBM Bob

This configuration is available in the [IBM Technology Building Blocks repository](https://github.com/thomassuedbroecker/building-blocks).

**Selective Download Options:**

GitHub does not provide a native "Download directory" button in the standard web UI. Recommended approaches:

1. **Single files** (modes, skills, rules):
   - Navigate to the file in GitHub
   - Click "Raw" button
   - Save the file using your browser's "Save As" function

2. **Multiple related files** (one skill or rule set):
   - Download the repository as a ZIP file
   - Extract only the required folder from the ZIP

3. **Browser-based folder download** (optional):
   - Change the repository URL in your browser from:
     ```
     https://github.com/thomassuedbroecker/building-blocks
     ```
     to:
     ```
     https://github.dev/thomassuedbroecker/building-blocks
     ```
   - This opens the repository in the GitHub web editor
   - Right-click on folders to download them directly

### Installation

1. **Copy configuration to your project**

   Copy these folders to your project root:

   ```bash
   your-project/
   ├── .bob/
   │   └── custom_modes.yaml          # From: modes/custom_modes.yaml
   └── skills/                         # From: skills/
       ├── README.md
       ├── architecture-patterns-skill.md
       ├── business-alignment-skill.md
       ├── documentation-review-skill.md
       ├── maintainability-technical-debt-skill.md
       ├── requirements-management-skill.md
       ├── scalability-performance-skill.md
       ├── security-threat-modeling-skill.md
       └── twelve-factor-compliance-skill.md
   ```

   **Alternative**: Use the pre-configured `_bob` folder:
   - Copy the entire `_bob` folder from this repository
   - Rename it to `.bob` in your project root
   - All paths are already configured correctly

2. **Verify installation**

   - Open your project in Bob
   - Check mode selector (bottom-left) for new modes:
     - 🏛️ Architecture Review
     - 🔍 Configuration Gap Detector

3. **Try your first review**

   ```
   Switch to: 🏛️ Architecture Review mode
   Request: "Review security using the security-threat-modeling skill"
   ```

---

## 📁 Repository Structure

```
review-and-sdd-expert-bob-configuration/
├── README.md                          # This file - main documentation
├── modes/
│   └── custom_modes.yaml              # Mode definitions for Bob
├── skills/
│   ├── README.md                      # Skills documentation
│   ├── architecture-patterns-skill.md
│   ├── business-alignment-skill.md
│   ├── documentation-review-skill.md
│   ├── maintainability-technical-debt-skill.md
│   ├── requirements-management-skill.md
│   ├── scalability-performance-skill.md
│   ├── security-threat-modeling-skill.md
│   └── twelve-factor-compliance-skill.md
└── documentation/                     # Additional guides and references
    ├── README-ARCHITECTURE-REVIEW.md
    ├── SDD-README.md
    └── guides/
        ├── QUICK-START.md
        ├── SDD-QUICK-START.md
        ├── architecture-review-guide.md
        ├── architecture-review-template.md
        ├── sdd-interactive-guide.md
        └── spec-driven-development.md
```

---

## 🎯 Available Modes

### 1. 🏛️ Architecture Review Mode

**Purpose**: Conduct comprehensive architecture reviews using specialized skills

**When to use**:
- Pre-production validation
- Technical debt assessment
- Architecture board preparation
- Compliance checks
- Security audits
- Performance analysis

**Example requests**:
```
"Conduct a comprehensive architecture review using all skills"
"Review security using the security-threat-modeling skill"
"Check 12-factor compliance"
"Analyze scalability and performance"
```

### 2. 🔍 Configuration Gap Detector Mode

**Purpose**: Detect configuration gaps and propose new modes or skills

**When to use**:
- Task seems outside scope of existing modes
- New domain requirements emerge (IoT, blockchain, ML)
- Workflow gaps suspected
- Before starting complex, unfamiliar tasks

**Features**:
- Analyzes task requirements against current configuration
- Identifies missing domain knowledge
- Researches best practices using browser capabilities
- Proposes minimal, targeted additions

---

## 📚 Available Skills

### 1. 🎯 Business Alignment
**File**: [`skills/business-alignment-skill.md`](skills/business-alignment-skill.md)

Evaluates how well architecture supports organizational goals and quality attributes.

**Key Areas**: Strategic planning, quality attributes, stakeholder analysis, cost-benefit analysis

### 2. 🔒 Security & Threat Modeling
**File**: [`skills/security-threat-modeling-skill.md`](skills/security-threat-modeling-skill.md)

Identifies security gaps, attack vectors, and provides security recommendations.

**Key Areas**: OWASP Top 10, STRIDE, authentication/authorization, compliance (GDPR, HIPAA, PCI-DSS)

### 3. 📈 Scalability & Performance
**File**: [`skills/scalability-performance-skill.md`](skills/scalability-performance-skill.md)

Evaluates system capacity, identifies bottlenecks, provides optimization recommendations.

**Key Areas**: Scaling strategies, load balancing, caching, database optimization, SLAs

### 4. 🎨 Architecture Patterns
**File**: [`skills/architecture-patterns-skill.md`](skills/architecture-patterns-skill.md)

Evaluates pattern usage, identifies anti-patterns, recommends appropriate patterns.

**Key Areas**: Microservices, CQRS, Event Sourcing, DDD, SOLID principles, API design

### 5. 🔧 Maintainability & Technical Debt
**File**: [`skills/maintainability-technical-debt-skill.md`](skills/maintainability-technical-debt-skill.md)

Identifies maintainability issues, quantifies technical debt, provides refactoring recommendations.

**Key Areas**: Code complexity, coupling/cohesion, duplication, test coverage, debt quantification

### 6. 📚 Documentation Review
**File**: [`skills/documentation-review-skill.md`](skills/documentation-review-skill.md)

Evaluates documentation completeness, clarity, and currency.

**Key Areas**: ADRs, C4 diagrams, UML, API documentation, runbooks

### 7. ☁️ 12-Factor Compliance
**File**: [`skills/twelve-factor-compliance-skill.md`](skills/twelve-factor-compliance-skill.md)

Evaluates compliance with 12-factor app methodology for cloud-native readiness.

**Key Areas**: All 12 factors from codebase to admin processes

### 8. 📋 Requirements Management
**File**: [`skills/requirements-management-skill.md`](skills/requirements-management-skill.md)

Elicits, documents, analyzes, and validates software requirements.

**Key Areas**: Requirements elicitation, documentation, analysis, prioritization, traceability

---

## 💡 Usage Examples

### Example 1: Pre-Production Review

```
User: "Review security, scalability, and 12-factor compliance before production"

Bob will:
1. Read 3 relevant skill files
2. Apply each skill's methodology
3. Analyze codebase against checklists
4. Provide prioritized findings
5. Recommend critical fixes

Output:
✅ Achieved: OAuth2 implemented, auto-scaling configured
⚠️ Concerns: No rate limiting, logs not centralized
❌ Not Achieved: Missing circuit breakers
💡 Recommendations: [Prioritized action items]
```

### Example 2: Technical Debt Assessment

```
User: "Analyze technical debt and maintainability"

Bob will:
1. Read maintainability-technical-debt-skill.md
2. Analyze code complexity and coupling
3. Detect code duplication
4. Assess test coverage
5. Quantify technical debt
6. Provide refactoring roadmap

Output: Prioritized technical debt backlog with effort estimates
```

### Example 3: Security Audit

```
User: "Perform STRIDE threat modeling and check OWASP Top 10"

Bob will:
1. Read security-threat-modeling-skill.md
2. Identify security gaps and attack vectors
3. Check for OWASP Top 10 vulnerabilities
4. Assess authentication/authorization
5. Provide risk ratings and remediation steps

Output: Security assessment report with prioritized fixes
```

---

## 🎓 Best Practices

### Mode Selection Strategy

1. **Start with Plan mode** for new projects
   - Create detailed implementation plan
   - Break down into clear steps
   - Get user approval

2. **Switch to Code/Advanced mode** for implementation
   - Execute approved plan
   - Make code changes
   - Run tests

3. **Use Architecture Review mode** for validation
   - Review completed work
   - Identify issues early
   - Ensure quality standards

4. **Use Ask mode** for explanations
   - Understand concepts
   - Get recommendations
   - Learn technologies

### Effective Review Requests

#### ✅ Good Examples

**Specific and focused**:
```
"Review security for a healthcare application that needs HIPAA compliance"
```

**With context**:
```
"Analyze scalability for an e-commerce platform expecting 10x growth"
```

**Prioritized**:
```
"Focus on security and 12-factor compliance first, then performance"
```

#### ❌ Avoid These

- "Review the system" (too vague)
- "Check everything" (no context)
- "Do all reviews at once and fix all issues" (unrealistic scope)

---

## 🔧 Customization

### Adding Organization-Specific Requirements

1. **Modify existing skills**

   Edit skill files in `skills/` to add:
   - Internal compliance requirements
   - Company-specific patterns
   - Custom quality attributes
   - Organization standards

2. **Create new skills**

   ```bash
   # Copy an existing skill as template
   cp skills/security-threat-modeling-skill.md \
      skills/custom-compliance-skill.md
   ```

   Then customize:
   - Purpose and expertise areas
   - Review process and checklists
   - Output format
   - Key questions and best practices

3. **Update mode configuration**

   The Architecture Review mode automatically uses any skill files in `skills/`, so no mode changes needed!

### Skill Structure Template

```markdown
# [Skill Name]

## Purpose
[What this skill evaluates]

## Expertise Areas
- [Area 1]
- [Area 2]

## Review Process
### 1. [Step Name]
- [Checklist item]
- [Question to ask]

## Output Format
### ✅ Achieved
[What's working well]

### ⚠️ Concerns
[Areas needing attention]

### ❌ Not Achieved
[Critical gaps]

### 💡 Recommendations
[Actionable improvements]
```

---

## 📖 Documentation

### Quick References

| Document | Purpose |
|----------|---------|
| **README.md** | Main documentation (this file) |
| **[skills/README.md](skills/README.md)** | Skills documentation |
| **[documentation/README-ARCHITECTURE-REVIEW.md](documentation/README-ARCHITECTURE-REVIEW.md)** | Architecture review details |
| **[documentation/guides/QUICK-START.md](documentation/guides/QUICK-START.md)** | Quick start guide |
| **[documentation/SDD-README.md](documentation/SDD-README.md)** | Spec-driven development |
