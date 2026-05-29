# Bob Custom Modes and Skills Overview

A modular, skill-based Bob configuration for architecture review, specification-driven development, and configuration gap detection.

## 📋 Overview

This `.bob` configuration provides:

- **9 Custom Modes**
  - 1 orchestrator review mode
  - 7 focused review modes
  - 1 specification-driven development mode
  - 1 configuration gap detection mode
- **8 Reusable Skills**
  - 7 architecture review skills
  - 1 requirements management skill

This modular approach provides:
- ✅ **Flexibility**: Use broad orchestration or focused modes
- ✅ **Reusability**: Skills can be used across projects and modes
- ✅ **Consistency**: Shared methodologies across workflows
- ✅ **Maintainability**: Update modes and skills independently
- ✅ **Extensibility**: Add new modes or skills incrementally

## 🎯 Configuration Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                        Custom Modes                          │
├──────────────────────────────────────────────────────────────┤
│ 🏛️ Architecture Review      - Orchestrates review skills     │
│ 🧭 Spec-Driven Development  - Drives requirements/spec work  │
│ 🔒 Security Review          - Focused security analysis      │
│ 📈 Scalability Review       - Focused performance analysis   │
│ 🎨 Patterns Review          - Focused pattern analysis       │
│ 🔧 Maintainability Review   - Focused code quality review    │
│ 📚 Documentation Review     - Focused documentation review   │
│ ☁️ 12-Factor Review         - Focused cloud-native review    │
│ 🎯 Business Alignment       - Focused business alignment     │
│ 🔍 Config Gap Detector      - Detects missing capabilities   │
└──────────────────────────────────────────────────────────────┘
                              │
                              │ Uses
                              ▼
┌──────────────────────────────────────────────────────────────┐
│                      Reusable Skills                         │
├──────────────────────────────────────────────────────────────┤
│ 1. Business Alignment                                        │
│ 2. Security & Threat Modeling                                │
│ 3. Scalability & Performance                                 │
│ 4. Architecture Patterns                                     │
│ 5. Maintainability & Technical Debt                          │
│ 6. Documentation Review                                      │
│ 7. 12-Factor Compliance                                      │
│ 8. Requirements Management                                   │
└──────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### 1. Activate the Appropriate Mode

Choose the mode that matches your task in Bob:

- **🏛️ Architecture Review** for multi-skill or broad architecture reviews
- **🧭 Spec-Driven Development** for requirements, specifications, and prompt engineering
- **Focused review modes** for a single review domain
- **🔍 Configuration Gap Detector** when current capabilities seem insufficient

### 2. Request the Task

**Architecture Review**
```text
"Conduct a comprehensive architecture review using all relevant skills"
"Review security, scalability, and 12-factor compliance before production"
```

**Spec-Driven Development**
```text
"Help me define requirements for a new project"
"Review this specification for completeness and testability"
"Turn these notes into structured functional and non-functional requirements"
```

**Configuration Gap Detection**
```text
"Check whether the current Bob configuration is sufficient for this task"
"Identify missing modes or skills for regulated medical software reviews"
```

### 3. Bob Will

1. Read the relevant mode instructions
2. Read the relevant skill file(s)
3. Apply the documented methodology
4. Produce structured, actionable output

## 🧩 Available Modes

### 1. 🏛️ Architecture Review (`arch-review`)
Orchestrates architecture reviews using reusable review skills.

**Use When**:
- You need a comprehensive review
- You want multiple review areas combined
- You need pre-production validation

### 2. 🧭 Spec-Driven Development (`sdd`)
Supports requirements management, specification creation, and prompt engineering across the SDLC.

**Use When**:
- You need to define or refine requirements
- You want to create or review specifications
- You need prompt engineering support for AI-assisted development

### 3. 🔒 Security & Threat Modeling (`security-review`)
Focused security architecture and threat analysis.

### 4. 📈 Scalability & Performance (`scalability-review`)
Focused scalability and performance analysis.

### 5. 🎨 Architecture Patterns (`patterns-review`)
Focused architecture pattern and design review.

### 6. 🔧 Maintainability & Technical Debt (`maintainability-review`)
Focused maintainability and technical debt analysis.

### 7. 📚 Documentation Review (`documentation-review`)
Focused architecture documentation and diagram review.

### 8. ☁️ 12-Factor Compliance (`twelve-factor-review`)
Focused cloud-native and 12-factor compliance review.

### 9. 🎯 Business Alignment (`business-alignment-review`)
Focused business goals and quality attribute review.

### 10. 🔍 Configuration Gap Detector (`config-gap-detector`)
Detects missing capabilities and proposes new modes or skills.

## 📚 Available Skills

### 1. 🎯 Business Alignment
**File**: `../skills/business-alignment-skill.md`

Evaluates how well the architecture supports organizational goals and quality attributes.

### 2. 🔒 Security & Threat Modeling
**File**: `../skills/security-threat-modeling-skill.md`

Identifies security gaps, potential attack vectors, and provides security recommendations.

### 3. 📈 Scalability & Performance
**File**: `../skills/scalability-performance-skill.md`

Evaluates system capacity, identifies bottlenecks, and provides performance optimization recommendations.

### 4. 🎨 Architecture Patterns
**File**: `../skills/architecture-patterns-skill.md`

Evaluates pattern usage, identifies anti-patterns, and recommends appropriate patterns.

### 5. 🔧 Maintainability & Technical Debt
**File**: `../skills/maintainability-technical-debt-skill.md`

Identifies maintainability issues, quantifies technical debt, and provides refactoring recommendations.

### 6. 📚 Documentation Review
**File**: `../skills/documentation-review-skill.md`

Evaluates documentation completeness, clarity, and currency.

### 7. ☁️ 12-Factor Compliance
**File**: `../skills/twelve-factor-compliance-skill.md`

Evaluates compliance with 12-factor app methodology and provides cloud-native recommendations.

### 8. 🧭 Requirements Management
**File**: `../skills/requirements-management-skill.md`

Supports elicitation, documentation, prioritization, validation, and traceability of requirements.

## 💡 Usage Examples

### Example 1: Complete Architecture Review
```text
User: "Conduct a comprehensive architecture review of this system"
```

### Example 2: Security-Focused Review
```text
User: "Review security using the security-threat-modeling skill"
```

### Example 3: Specification Review
```text
User: "Review this specification for completeness, consistency, and testability"
```

### Example 4: Requirements Definition
```text
User: "Help me define functional and non-functional requirements for a new feature"
```

### Example 5: Configuration Gap Detection
```text
User: "Do we need a dedicated compliance mode for medical devices?"
```

## 📊 Output Patterns

Depending on the mode and skill, Bob typically provides:

### ✅ Achieved
What is already strong or complete

### ⚠️ Concerns
Areas needing attention or clarification

### ❌ Not Achieved
Critical gaps or missing elements

### 💡 Recommendations
Specific next actions, priorities, and improvements

## 🎓 Benefits of the Modular Approach

### For Architects and Engineers
- ✅ **Consistent methodology** across reviews and specification work
- ✅ **Reusable expertise** codified in skills
- ✅ **Flexible scope** from focused analysis to orchestration
- ✅ **Easy extension** with new modes and skills

### For Teams
- ✅ **Knowledge sharing** through documented modes and skills
- ✅ **Faster onboarding** with clear workflows
- ✅ **Quality assurance** with structured checklists
- ✅ **Continuous improvement** through modular updates

## 🔧 Customization

### 1. Modify Existing Skills
Edit files in `../skills/` to:
- Add organization-specific requirements
- Include custom compliance checks
- Reference internal standards
- Extend review or requirements workflows

### 2. Create New Skills
Copy an existing skill and customize it for your domain.

### 3. Add New Modes
Update `.bob/custom_modes.yaml` when a new role, workflow, or behavior style is needed.

## 📖 Documentation

- **[Skills README](../skills/README.md)** - Detailed skill documentation
- **[Architecture Review Quick Start](guides/QUICK-START.md)** - Review-oriented quick start
- **[Architecture Review Guide](guides/architecture-review-guide.md)** - Detailed review guidance
- **[SDD Guide](SDD-README.md)** - Spec-driven development documentation

## 🆘 Support

For questions or issues:
1. Review the [Skills README](../skills/README.md)
2. Check the relevant guide in `guides/`
3. Review `.bob/custom_modes.yaml`
4. Use Configuration Gap Detector when capabilities appear incomplete

## 🔄 Version History

- **v3.0** (2026-05-29) - Multi-mode configuration aligned with current `.bob` setup
  - Added Spec-Driven Development mode
  - Documented focused review modes
  - Documented Configuration Gap Detector
  - Updated skill inventory to 8 skills

- **v2.0** (2026-03-31) - Skill-based modular architecture review approach
- **v1.0** (2026-03-31) - Initial architecture review release

---

**Created**: 2026-03-31
**Last Updated**: 2026-05-29
**Version**: 3.0
**Modes**: 10
**Skills**: 8

For the latest updates, check `.bob/custom_modes.yaml` and the documentation directory regularly.