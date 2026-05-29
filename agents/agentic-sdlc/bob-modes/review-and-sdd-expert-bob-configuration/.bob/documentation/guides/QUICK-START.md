# Architecture Review - Quick Start Guide

## 🚀 Get Started in 3 Steps

### 1. Switch to the Right Review Mode
Select one of the review-oriented modes from Bob's mode selector:
- **🏛️ Architecture Review** for multi-skill reviews
- **🔒 Security & Threat Modeling** for focused security analysis
- **📈 Scalability & Performance** for focused performance analysis
- **🎨 Architecture Patterns** for focused pattern analysis
- **🔧 Maintainability & Technical Debt** for focused maintainability analysis
- **📚 Documentation Review** for focused documentation analysis
- **☁️ 12-Factor Compliance** for focused cloud-native analysis
- **🎯 Business Alignment** for focused business alignment analysis

### 2. Choose Your Review Type
Pick from the examples below based on your needs

### 3. Bob Does the Rest
Bob will read the relevant skills, apply the methodology, and provide structured findings

---

## 📋 Common Review Requests

### Complete Reviews

**Full Architecture Review**
```
"Conduct a comprehensive architecture review using all relevant skills"
```

**Pre-Production Checklist**
```
"Review security, scalability, and 12-factor compliance before production"
```

**Architecture Board Preparation**
```
"Prepare a complete architecture review for the review board"
```

---

### Focused Reviews

**Security Review**
```
"Review security using the security-threat-modeling skill"
"Perform STRIDE threat modeling"
"Check for OWASP Top 10 vulnerabilities"
```

**Performance Review**
```
"Analyze scalability and performance"
"Identify performance bottlenecks"
"Review caching and load balancing strategies"
```

**Technical Debt Assessment**
```
"Analyze technical debt and maintainability"
"Review code complexity and coupling"
"Quantify technical debt"
```

**12-Factor Compliance**
```
"Check 12-factor app compliance"
"Assess cloud-native readiness"
"Review configuration management"
```

**Documentation Review**
```
"Review documentation completeness"
"Check for ADRs and C4 diagrams"
"Assess API documentation quality"
```

**Pattern Review**
```
"Review architecture patterns and best practices"
"Check SOLID principle adherence"
"Identify anti-patterns"
```

**Business Alignment**
```
"Review business alignment and quality attributes"
"Assess stakeholder requirements"
"Evaluate cost-benefit"
```

---

### Multi-Skill Reviews

**Security + Performance**
```
"Review security and scalability"
```

**Maintainability + Documentation**
```
"Review code quality and documentation"
```

**Patterns + Technical Debt**
```
"Review architecture patterns and technical debt"
```

---

## 🎯 What You'll Get

For each review, Bob provides:

### ✅ Achieved
- What's working well
- Standards being met
- Good practices identified

### ⚠️ Concerns
- Areas needing attention
- Potential risks
- Improvement opportunities

### ❌ Not Achieved
- Critical gaps
- Missing requirements
- Compliance violations

### 💡 Recommendations
- Specific actions to take
- Priority levels (Critical/High/Medium/Low)
- Implementation guidance
- Effort estimates

---

## 📚 Available Skills

| # | Skill | Focus Area | File |
|---|-------|------------|------|
| 1 | 🎯 Business Alignment | Strategy & Quality Attributes | `business-alignment-skill.md` |
| 2 | 🔒 Security & Threat Modeling | Security & Compliance | `security-threat-modeling-skill.md` |
| 3 | 📈 Scalability & Performance | Capacity & Performance | `scalability-performance-skill.md` |
| 4 | 🎨 Architecture Patterns | Patterns & Best Practices | `architecture-patterns-skill.md` |
| 5 | 🔧 Maintainability & Tech Debt | Code Quality & Debt | `maintainability-technical-debt-skill.md` |
| 6 | 📚 Documentation | Docs & Diagrams | `documentation-review-skill.md` |
| 7 | ☁️ 12-Factor Compliance | Cloud-Native Readiness | `twelve-factor-compliance-skill.md` |
| 8 | 🧭 Requirements Management | Requirements & Specifications | `requirements-management-skill.md` |

---

## 💡 Pro Tips

### Tip 1: Be Specific
Instead of: "Review the system"
Try: "Review security and scalability for production readiness"

### Tip 2: Prioritize
Instead of: "Review everything"
Try: "Focus on security and 12-factor compliance first"

### Tip 3: Iterate
Instead of: "Do all reviews at once"
Try: "Start with security, then we'll do performance"

### Tip 4: Provide Context
```
"Review security for a healthcare application that needs HIPAA compliance"
"Analyze scalability for an e-commerce platform expecting 10x growth"
```

### Tip 5: Reference Skills Directly
```
"Use the security-threat-modeling skill to review authentication"
"Apply the twelve-factor-compliance skill to check our deployment"
```

---

## 🔄 Typical Workflow

```
1. Request Review
   "Review security and scalability"
   
2. Bob Reads Skills
   - security-threat-modeling-skill.md
   - scalability-performance-skill.md
   
3. Bob Analyzes Codebase
   - Checks authentication
   - Reviews scaling strategy
   - Identifies issues
   
4. Bob Provides Findings
   ✅ Achieved: OAuth2 implemented
   ⚠️ Concerns: No rate limiting
   ❌ Not Achieved: Missing auto-scaling
   💡 Recommendations: Add rate limiting, implement auto-scaling
   
5. Team Takes Action
   - Create tickets for recommendations
   - Prioritize by severity
   - Schedule implementation
   
6. Follow-up Review (Optional)
   "Re-review security after implementing rate limiting"
```

---

## 📖 Learn More

- **[Skills Documentation](../../skills/README.md)** - Detailed skill information
- **[Review Template](architecture-review-template.md)** - Output format
- **[Usage Guide](architecture-review-guide.md)** - Comprehensive guide
- **[Main README](../README-ARCHITECTURE-REVIEW.md)** - Full documentation

---

## 🎯 Quick Decision Tree

**Need to prepare for production?**
→ "Review security, scalability, and 12-factor compliance"

**Experiencing performance issues?**
→ "Analyze scalability and performance"

**Planning a refactoring sprint?**
→ "Analyze technical debt and maintainability"

**Preparing for architecture board?**
→ "Conduct comprehensive architecture review"

**Need compliance audit?**
→ "Review security and 12-factor compliance"

**Documentation outdated?**
→ "Review documentation completeness"

**Evaluating architecture decisions?**
→ "Review architecture patterns and best practices"

**Strategic planning?**
→ "Review business alignment and quality attributes"

---

**Version**: 3.0
**Last Updated**: 2026-05-29