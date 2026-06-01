# Technical Debt Prioritization

## Prioritization Matrix

Use this matrix to prioritize technical debt items based on impact and effort:

| Impact | Quick Win (<1 day) | Medium (1-5 days) | Large (1-2 weeks) | Epic (>2 weeks) |
|--------|-------------------|-------------------|-------------------|-----------------|
| **Critical** | DO NOW | DO NOW | Plan immediately | Plan for quarter |
| **High** | DO NOW | Schedule next sprint | Plan for quarter | Evaluate ROI |
| **Medium** | Do when convenient | Schedule when capacity | Evaluate ROI | Backlog |
| **Low** | Optional | Backlog | Backlog | Ignore/Delete |

## Debt Inventory Template

```markdown
## Technical Debt Item: [Name]

**Category:** Code / Architecture / Test / Documentation / Infrastructure
**Severity:** Critical / High / Medium / Low
**Age:** [When introduced]
**Owner:** [Team/Person responsible]

### Description
[What is the debt and why does it exist?]

### Impact
- Development velocity: [How it slows down new features]
- Risk: [What could go wrong]
- Maintenance cost: [Ongoing burden]

### Remediation
- Effort: [Story points / days]
- Approach: [How to fix]
- Dependencies: [What must happen first]

### Interest Payment
[What we pay by not fixing it - bugs, slowdowns, workarounds]
```

## Example Inventory

| Area | Issue | Severity | Effort | Risk | Interest Payment |
|------|-------|----------|--------|------|------------------|
| Code Quality | God class (UserManager 2500 LOC) | High | 5 days | Medium | Slows all user features |
| Dependencies | Django 1.11 (EOL) | Critical | 2 weeks | High | Security vulnerabilities |
| Testing | 23% coverage | High | 3 weeks | High | Bugs in production |
| Architecture | Monolithic coupling | Medium | 8 weeks | Medium | Hard to scale |
| Documentation | Missing API docs | Low | 1 week | Low | Onboarding delays |
| Performance | N+1 queries | Medium | 3 days | Low | Slow page loads |
| Security | Hardcoded credentials | Critical | 1 day | Critical | Data breach risk |

## Severity Definitions

### Critical
- Security vulnerabilities
- Data loss risks
- System outages
- Compliance violations
- EOL dependencies with no support

### High
- Significant performance issues
- Major bugs affecting users
- Blocking new features
- High maintenance burden

### Medium
- Code quality issues
- Minor performance problems
- Technical limitations
- Moderate maintenance burden

### Low
- Style inconsistencies
- Minor optimizations
- Nice-to-have improvements
- Documentation gaps

## Prioritization Guidelines

1. **Always prioritize Critical items** - These pose immediate risk
2. **Quick wins first** - Build momentum with fast improvements
3. **Consider dependencies** - Some debt blocks other work
4. **Balance short and long-term** - Don't ignore large items
5. **Track interest payments** - What does NOT fixing cost?
6. **Reassess regularly** - Priorities change over time