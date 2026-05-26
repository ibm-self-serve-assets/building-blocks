# Architecture Review System - Diagram

## System Overview

```mermaid
graph TB
    subgraph "Bob Code Assistant"
        User[👤 User/Architect]
    end
    
    subgraph "Architecture Review Mode"
        Mode[🏛️ Architecture Review Mode<br/>Orchestrator]
    end
    
    subgraph "Reusable Review Skills"
        S1[🎯 Business Alignment<br/>Strategic Planning & QA]
        S2[🔒 Security & Threat Modeling<br/>OWASP, STRIDE, Compliance]
        S3[📈 Scalability & Performance<br/>Capacity & Optimization]
        S4[🎨 Architecture Patterns<br/>Design Principles & Patterns]
        S5[🔧 Maintainability & Tech Debt<br/>Code Quality & Refactoring]
        S6[📚 Documentation Review<br/>ADRs, Diagrams, APIs]
        S7[☁️ 12-Factor Compliance<br/>Cloud-Native Readiness]
    end
    
    subgraph "Review Output"
        Output[📊 Structured Review Report<br/>✅ Achieved<br/>⚠️ Concerns<br/>❌ Not Achieved<br/>💡 Recommendations]
    end
    
    User -->|Request Review| Mode
    Mode -->|Uses| S1
    Mode -->|Uses| S2
    Mode -->|Uses| S3
    Mode -->|Uses| S4
    Mode -->|Uses| S5
    Mode -->|Uses| S6
    Mode -->|Uses| S7
    
    S1 --> Output
    S2 --> Output
    S3 --> Output
    S4 --> Output
    S5 --> Output
    S6 --> Output
    S7 --> Output
    
    Output -->|Presents| User
    
    style Mode fill:#e1f5ff,stroke:#0288d1,stroke-width:3px
    style S1 fill:#fff3e0,stroke:#f57c00,stroke-width:2px
    style S2 fill:#fce4ec,stroke:#c2185b,stroke-width:2px
    style S3 fill:#e8f5e9,stroke:#388e3c,stroke-width:2px
    style S4 fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    style S5 fill:#fff9c4,stroke:#f9a825,stroke-width:2px
    style S6 fill:#e0f2f1,stroke:#00897b,stroke-width:2px
    style S7 fill:#e3f2fd,stroke:#1976d2,stroke-width:2px
    style Output fill:#f1f8e9,stroke:#558b2f,stroke-width:3px
```

## Detailed Skill Breakdown

```mermaid
graph LR
    subgraph "🎯 Business Alignment"
        BA1[Strategic Planning]
        BA2[Quality Attributes]
        BA3[Stakeholder Analysis]
        BA4[Cost-Benefit Analysis]
        BA5[Risk Assessment]
    end
    
    subgraph "🔒 Security & Threat Modeling"
        S1[OWASP Top 10]
        S2[STRIDE Modeling]
        S3[Auth/Authorization]
        S4[Data Protection]
        S5[Compliance<br/>GDPR, HIPAA, PCI-DSS]
    end
    
    subgraph "📈 Scalability & Performance"
        SP1[Horizontal/Vertical Scaling]
        SP2[Load Balancing]
        SP3[Caching Strategies]
        SP4[Database Optimization]
        SP5[Performance Benchmarking]
    end
    
    subgraph "🎨 Architecture Patterns"
        AP1[Microservices vs Monolith]
        AP2[CQRS & Event Sourcing]
        AP3[SOLID Principles]
        AP4[Design Patterns]
        AP5[API Design<br/>REST, GraphQL, gRPC]
    end
    
    subgraph "🔧 Maintainability & Tech Debt"
        MT1[Code Complexity]
        MT2[Coupling & Cohesion]
        MT3[Code Duplication]
        MT4[Test Coverage]
        MT5[Debt Quantification]
    end
    
    subgraph "📚 Documentation Review"
        DR1[ADRs]
        DR2[C4 Model Diagrams]
        DR3[UML Diagrams]
        DR4[API Documentation]
        DR5[Runbooks]
    end
    
    subgraph "☁️ 12-Factor Compliance"
        TF1[Codebase & Dependencies]
        TF2[Config & Backing Services]
        TF3[Build/Release/Run]
        TF4[Processes & Concurrency]
        TF5[Logs & Admin Processes]
    end
    
    style BA1 fill:#fff3e0
    style BA2 fill:#fff3e0
    style BA3 fill:#fff3e0
    style BA4 fill:#fff3e0
    style BA5 fill:#fff3e0
    
    style S1 fill:#fce4ec
    style S2 fill:#fce4ec
    style S3 fill:#fce4ec
    style S4 fill:#fce4ec
    style S5 fill:#fce4ec
    
    style SP1 fill:#e8f5e9
    style SP2 fill:#e8f5e9
    style SP3 fill:#e8f5e9
    style SP4 fill:#e8f5e9
    style SP5 fill:#e8f5e9
    
    style AP1 fill:#f3e5f5
    style AP2 fill:#f3e5f5
    style AP3 fill:#f3e5f5
    style AP4 fill:#f3e5f5
    style AP5 fill:#f3e5f5
    
    style MT1 fill:#fff9c4
    style MT2 fill:#fff9c4
    style MT3 fill:#fff9c4
    style MT4 fill:#fff9c4
    style MT5 fill:#fff9c4
    
    style DR1 fill:#e0f2f1
    style DR2 fill:#e0f2f1
    style DR3 fill:#e0f2f1
    style DR4 fill:#e0f2f1
    style DR5 fill:#e0f2f1
    
    style TF1 fill:#e3f2fd
    style TF2 fill:#e3f2fd
    style TF3 fill:#e3f2fd
    style TF4 fill:#e3f2fd
    style TF5 fill:#e3f2fd
```

## Review Workflow

```mermaid
sequenceDiagram
    participant User as 👤 Architect
    participant Mode as 🏛️ Review Mode
    participant Skills as 📚 Skills Library
    participant Code as 💻 Codebase
    participant Report as 📊 Report
    
    User->>Mode: Request Review<br/>(Complete or Focused)
    Mode->>Skills: Read Relevant Skill(s)
    Skills-->>Mode: Skill Methodology & Checklist
    
    loop For Each Skill
        Mode->>Code: Analyze Codebase
        Code-->>Mode: Code Structure & Patterns
        Mode->>Mode: Apply Skill Checklist
        Mode->>Report: Generate Findings
    end
    
    Mode->>Report: Compile Results
    Report->>Report: Structure Output<br/>✅ ⚠️ ❌ 💡
    Report-->>User: Present Review Report
    
    User->>User: Review Findings
    User->>User: Create Action Items
    
    opt Follow-up Review
        User->>Mode: Request Focused Review
    end
```

## Usage Patterns

```mermaid
graph TD
    Start[Start Review]
    
    Start --> Choice{Review Type?}
    
    Choice -->|Complete| All[Use All 7 Skills]
    Choice -->|Focused| Select[Select Specific Skills]
    Choice -->|Pre-Production| PreProd[Security + Scalability<br/>+ 12-Factor]
    Choice -->|Tech Debt| TechDebt[Maintainability<br/>+ Documentation]
    
    All --> Execute[Execute Review]
    Select --> Execute
    PreProd --> Execute
    TechDebt --> Execute
    
    Execute --> Analyze[Analyze Codebase]
    Analyze --> Findings[Generate Findings]
    Findings --> Report[Structured Report]
    
    Report --> Review[Team Review]
    Review --> Actions[Create Action Items]
    
    Actions --> Decision{Need Follow-up?}
    Decision -->|Yes| Start
    Decision -->|No| End[Complete]
    
    style Start fill:#4caf50,stroke:#2e7d32,color:#fff
    style Execute fill:#2196f3,stroke:#1565c0,color:#fff
    style Report fill:#ff9800,stroke:#e65100,color:#fff
    style End fill:#4caf50,stroke:#2e7d32,color:#fff
```

## File Structure

```
📁 Project Root
│
├── 📁 .bob/
│   └── 📄 custom_modes.yaml          # Architecture Review Mode Definition
│
├── 📁 skills/                         # Reusable Review Skills
│   ├── 📄 README.md
│   ├── 🎯 business-alignment-skill.md
│   ├── 🔒 security-threat-modeling-skill.md
│   ├── 📈 scalability-performance-skill.md
│   ├── 🎨 architecture-patterns-skill.md
│   ├── 🔧 maintainability-technical-debt-skill.md
│   ├── 📚 documentation-review-skill.md
│   └── ☁️ twelve-factor-compliance-skill.md
│
└── 📁 documentation/
    ├── 📄 README-ARCHITECTURE-REVIEW.md
    ├── 📄 SDD-README.md
    └── 📁 guides/
        ├── 📄 architecture-review-template.md
        └── 📄 architecture-review-guide.md
```

## Key Benefits

```mermaid
mindmap
  root((Architecture<br/>Review System))
    Flexibility
      Use all skills
      Focus on specific areas
      Combine multiple skills
      Iterative reviews
    Reusability
      Same methodology
      Cross-project use
      Team sharing
      Mode integration
    Consistency
      Structured process
      Standard checklists
      Uniform output
      Quality assurance
    Maintainability
      Independent updates
      Version control
      Easy customization
      Skill evolution
    Extensibility
      Add new skills
      Modify existing
      Organization-specific
      Tool integration
```

## Review Output Structure

```mermaid
graph TD
    Review[Review Report]
    
    Review --> Achieved[✅ Achieved<br/>What's Working Well]
    Review --> Concerns[⚠️ Concerns<br/>Areas Needing Attention]
    Review --> NotAchieved[❌ Not Achieved<br/>Critical Gaps]
    Review --> Recommendations[💡 Recommendations]
    
    Recommendations --> Priority[Priority Level<br/>Critical/High/Medium/Low]
    Recommendations --> Impact[Impact & Benefits]
    Recommendations --> Implementation[Implementation Approach]
    Recommendations --> Effort[Effort Estimate]
    
    style Review fill:#1976d2,stroke:#0d47a1,color:#fff,stroke-width:3px
    style Achieved fill:#4caf50,stroke:#2e7d32,color:#fff
    style Concerns fill:#ff9800,stroke:#e65100,color:#fff
    style NotAchieved fill:#f44336,stroke:#c62828,color:#fff
    style Recommendations fill:#9c27b0,stroke:#6a1b9a,color:#fff
```

---

**Diagram Version**: 1.0  
**Created**: 2026-04-01  
**Format**: Mermaid (Markdown)  
**Compatible With**: GitHub, GitLab, VS Code, Obsidian, and other Mermaid-supporting platforms