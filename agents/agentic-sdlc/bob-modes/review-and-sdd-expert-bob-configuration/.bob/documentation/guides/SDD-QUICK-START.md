# Spec-Driven Development (SDD) - Quick Start Guide

## 🚀 Get Started in 5 Minutes

This quick start guide helps you begin using Spec-Driven Development (SDD) mode immediately.

---

## Step 1: Choose Your Scenario

Select the scenario that best matches your current need:

### 📋 Scenario A: Starting a New Project
**You need to**: Define requirements and specifications for a new project

**Quick Actions**:
1. Activate SDD mode in Bob
2. Start with stakeholder identification
3. Use the [Requirements Management Skill](../../skills/requirements-management-skill.md#1-stakeholder-analysis)
4. Follow the [Requirements Phase Prompts](sdd-interactive-guide.md#requirements-phase-prompts)

**Template to Use**: [Requirements Document Template](../../skills/requirements-management-skill.md#output-format)

---

### ✍️ Scenario B: Crafting a Prompt for AI Development
**You need to**: Create an effective prompt for a specific development task

**Quick Actions**:
1. Open the [Interactive Guide](sdd-interactive-guide.md)
2. Follow the [5-Step Framework](sdd-interactive-guide.md#the-5-step-prompt-crafting-framework)
3. Use the [SDLC-Specific Guidelines](sdd-interactive-guide.md#step-3-apply-sdlc-specific-guidelines-) for your phase
4. Validate with the [Quality Checklist](sdd-interactive-guide.md#step-4-validate-your-prompt-)

**Templates to Use**: 
- [Feature Implementation](sdd-interactive-guide.md#template-1-feature-implementation)
- [Bug Fix](sdd-interactive-guide.md#template-2-bug-fix)
- [Architecture Decision](sdd-interactive-guide.md#template-3-architecture-decision)

---

### 🔍 Scenario C: Reviewing Existing Requirements
**You need to**: Review and improve existing requirements documentation

**Quick Actions**:
1. Use the [Requirements Validation](../../skills/requirements-management-skill.md#8-requirements-validation) checklist
2. Check for [Completeness, Consistency, and Testability](../../skills/requirements-management-skill.md#5-requirements-analysis)
3. Apply [Prioritization Frameworks](../../skills/requirements-management-skill.md#6-requirements-prioritization)
4. Update using [Change Management Process](../../skills/requirements-management-skill.md#9-requirements-change-management)

**Checklist to Use**: [Validation Checklist](../../skills/requirements-management-skill.md#validation-checklist)

---

### 🏗️ Scenario D: Creating Technical Specifications
**You need to**: Document technical specifications for implementation

**Quick Actions**:
1. Review [Design Phase Prompts](sdd-interactive-guide.md#design-phase-prompts)
2. Use the [Specification Creation](spec-driven-development.md#phase-2-specification-creation) guide
3. Include both functional and non-functional requirements
4. Validate with Architecture Review mode

**Template to Use**: [Technical Specifications](spec-driven-development.md#3-technical-specifications)

---

## Step 2: Use the Right Template

### For Requirements Documentation

```markdown
# Requirement: [Name]

## Description
[Clear description of what is needed]

## Priority
Must Have / Should Have / Could Have / Won't Have

## User Story
As a [user role]
I want [goal]
So that [benefit]

## Acceptance Criteria
- [ ] Given [context], when [action], then [outcome]
- [ ] Given [context], when [action], then [outcome]

## Dependencies
[List any dependencies]

## Assumptions
[List any assumptions]
```

### For Prompt Crafting

```markdown
# Task: [Title]

## Context
[Background and current state]

## Objective
[What you want to achieve]

## Requirements
- [Requirement 1]
- [Requirement 2]

## Constraints
- [Constraint 1]
- [Constraint 2]

## Expected Output
[Format and content expected]

## Success Criteria
- [ ] [Criterion 1]
- [ ] [Criterion 2]
```

---

## Step 3: Common Quick Wins

### Quick Win 1: Transform a Vague Request

**Before** ❌:
```
Create a login page
```

**After** ✅:
```markdown
# Task: User Authentication Login Page

## Context
Building a SaaS application that requires secure user authentication.
Current system has no authentication mechanism.

## Objective
Create a responsive login page with email/password authentication
that integrates with our existing Node.js backend API.

## Requirements
- Email and password input fields with validation
- "Remember me" checkbox
- "Forgot password" link
- Error messages for invalid credentials
- Loading state during authentication
- Redirect to dashboard on success
- WCAG 2.1 Level AA accessibility

## Constraints
- Must use React 18+ and TypeScript
- Must integrate with /api/auth/login endpoint
- Must work on mobile and desktop
- Response time < 200ms

## Expected Output
- React component with TypeScript
- Unit tests with >80% coverage
- Storybook stories for all states
- Accessibility audit passing

## Success Criteria
- [ ] All form validations work correctly
- [ ] Error handling for all scenarios
- [ ] Accessibility standards met
- [ ] Tests pass with >80% coverage
- [ ] Works on Chrome, Firefox, Safari
```

### Quick Win 2: Add Missing Context

**Before** ❌:
```
Fix the performance issue
```

**After** ✅:
```markdown
# Bug Fix: Slow Product Search Performance

## Problem
Product search taking 10-15 seconds, causing user frustration
and cart abandonment. Started after adding full-text search.

## Current State
- Products table: 500,000 rows
- Using PostgreSQL full-text search
- No indexes on search columns
- Database CPU at 90% during peak

## Expected Behavior
Search should complete in < 500ms for 95% of queries

## Root Cause Analysis Needed
- Analyze slow query logs
- Check index usage
- Identify N+1 queries
- Evaluate caching strategy

## Constraints
- Cannot change database (PostgreSQL)
- Zero downtime for optimization
- Must maintain search quality

## Success Criteria
- [ ] Search response < 500ms (95th percentile)
- [ ] Database CPU < 50%
- [ ] No degradation in search quality
- [ ] All tests pass
```

### Quick Win 3: Add Acceptance Criteria

**Before** ❌:
```
Users should be able to reset their password
```

**After** ✅:
```markdown
# Feature: Password Reset

## User Story
As a user who forgot my password
I want to reset it via email
So that I can regain access to my account

## Acceptance Criteria
- [ ] Given I'm on the login page
      When I click "Forgot Password"
      Then I see a password reset form

- [ ] Given I enter a valid email
      When I submit the form
      Then I receive a reset email within 5 minutes

- [ ] Given I click the reset link in email
      When the link is valid (< 1 hour old)
      Then I see a new password form

- [ ] Given I enter a new password
      When it meets security requirements
      Then my password is updated and I can log in

- [ ] Given the reset link is expired
      When I try to use it
      Then I see an error and can request a new link

## Security Requirements
- Reset links expire after 1 hour
- Links are single-use only
- Password must meet complexity requirements
- Rate limit: 3 requests per hour per email
```

---

## Step 4: Validate Your Work

### Quick Validation Checklist

Before submitting your requirements or prompt, check:

#### Clarity ✅
- [ ] Can someone unfamiliar understand it?
- [ ] Are all terms clearly defined?
- [ ] Is the objective specific and measurable?

#### Completeness ✅
- [ ] Is all necessary information included?
- [ ] Are edge cases considered?
- [ ] Are success criteria defined?

#### Quality ✅
- [ ] No ambiguous terms (fast, good, etc.)?
- [ ] Consistent terminology throughout?
- [ ] Proper formatting for readability?

---

## Step 5: Next Steps

After completing your quick start:

### For Deeper Learning
- Read the [Complete SDD Guide](../SDD-README.md)
- Study the [Interactive Guide](sdd-interactive-guide.md)
- Review [Real-World Examples](sdd-interactive-guide.md#real-world-examples)

### For Specific Skills
- [Requirements Management](../../skills/requirements-management-skill.md)
- [Architecture Review](../../skills/README.md)
- [All Available Skills](../../skills/README.md)

### For Integration
- Learn about [SDLC Integration](../SDD-README.md#sdlc-integration)
- Explore [Workflow Examples](../SDD-README.md#how-to-use-sdd-mode)
- Review [Best Practices](../SDD-README.md#best-practices)

---

## Common Mistakes to Avoid

### ❌ Mistake 1: Being Too Vague
**Problem**: "Make it fast"
**Solution**: "Response time < 200ms for 95% of requests under 1000 concurrent users"

### ❌ Mistake 2: Missing Context
**Problem**: "Create a login page"
**Solution**: Include tech stack, security requirements, integration points, and constraints

### ❌ Mistake 3: No Success Criteria
**Problem**: "Implement user authentication"
**Solution**: Define specific, testable criteria for completion

### ❌ Mistake 4: Ignoring Non-Functional Requirements
**Problem**: Only documenting features
**Solution**: Include performance, security, scalability, and usability requirements

### ❌ Mistake 5: No Prioritization
**Problem**: Everything is "critical"
**Solution**: Use MoSCoW or similar framework to prioritize

---

## Quick Reference: When to Use What

| Situation | Use This | Link |
|-----------|----------|------|
| Starting new project | Requirements Management Skill | [Link](../../skills/requirements-management-skill.md) |
| Crafting a prompt | Interactive Guide | [Link](sdd-interactive-guide.md) |
| Reviewing requirements | Validation Checklist | [Link](../../skills/requirements-management-skill.md#8-requirements-validation) |
| Creating specifications | SDD Mode Guide | [Link](spec-driven-development.md) |
| Prioritizing requirements | Prioritization Frameworks | [Link](../../skills/requirements-management-skill.md#6-requirements-prioritization) |
| Managing changes | Change Management | [Link](../../skills/requirements-management-skill.md#9-requirements-change-management) |
| SDLC-specific guidance | SDLC Integration | [Link](../SDD-README.md#sdlc-integration) |

---

## Getting Help

### Documentation
- **Overview**: [../SDD-README.md](../SDD-README.md)
- **Main Mode**: [spec-driven-development.md](spec-driven-development.md)
- **Interactive Guide**: [sdd-interactive-guide.md](sdd-interactive-guide.md)
- **Skills**: [../../skills/README.md](../../skills/README.md)

### External Resources
- [IBM Requirements Management](https://www.ibm.com/think/topics/what-is-requirements-management)
- [Spec-Driven Development with Bob](https://alain-airom.medium.com/spec-driven-development-with-ibm-bob-sdlc-01594799e38d)
- [Why IBM Bob for SDLC](https://heidloff.net/article/why-ibm-bob-software-development-lifecycle-partner/)

---

## Success Tips

💡 **Tip 1**: Start small - Don't try to document everything at once
💡 **Tip 2**: Iterate - Requirements evolve, and that's okay
💡 **Tip 3**: Collaborate - Get feedback from stakeholders early
💡 **Tip 4**: Be specific - Vague requirements lead to vague implementations
💡 **Tip 5**: Keep learning - Review your prompts and improve

---

**Ready to start?** Choose your scenario above and begin! 🚀

---

**Last Updated**: 2026-05-26  
**Version**: 1.0