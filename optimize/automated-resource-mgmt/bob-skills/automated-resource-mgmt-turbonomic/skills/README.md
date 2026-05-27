# Skills Documentation

This directory contains reusable skills for the Turbonomic Resource Dashboard project. Each skill is a specialized workflow that Bob can activate to help with specific development tasks.

## Available Skills

### 1. Frontend Development
**Folder:** `frontend-development/`  
**Activation:** Bob automatically activates when working on React components, UI design, or frontend code.

**Use for:**
- Building React components
- Implementing Carbon Design System
- Styling and layout
- Frontend performance optimization
- Writing user-facing content

**Files:**
- `SKILL.md` - Main skill instructions
- `detailed-reference.md` - Comprehensive examples and patterns
- `troubleshooting.md` - Common issues and solutions

---

### 2. Backend Development
**Folder:** `backend-development/`  
**Activation:** Bob automatically activates when working on APIs, server code, or backend services.

**Use for:**
- Creating API endpoints
- Integrating with Turbonomic API
- Implementing authentication and security
- Backend performance optimization
- Error handling

**Files:**
- `SKILL.md` - Main skill instructions
- `detailed-reference.md` - Complete implementation examples

---

### 3. DevOps & Deployment
**Folder:** `devops-deployment/`  
**Activation:** Bob automatically activates when working on Docker, Kubernetes, or deployment tasks.

**Use for:**
- Building Docker images
- Creating Kubernetes/OpenShift manifests
- Writing Ansible playbooks
- Setting up CI/CD pipelines
- Production deployment

**Files:**
- `SKILL.md` - Main skill instructions
- `detailed-reference.md` - Complete deployment configurations

---

### 4. Testing
**Folder:** `testing/`  
**Activation:** Bob automatically activates when writing tests or setting up testing infrastructure.

**Use for:**
- Writing unit tests
- Creating integration tests
- Setting up E2E tests with Cypress
- Configuring test coverage
- Test-driven development

**Files:**
- `SKILL.md` - Main skill instructions

---

## How Skills Work

### Automatic Activation
Bob automatically determines when to activate a skill based on:
- Your request content
- The skill's description
- The files you're working with

### Skill Structure
Each skill follows Bob's best practices:

```
skill-name/
├── SKILL.md              # Main skill file with YAML front matter
├── detailed-reference.md # Comprehensive examples (optional)
└── troubleshooting.md    # Common issues (optional)
```

### SKILL.md Format
```markdown
---
name: skill-name
description: Clear description of when to use this skill
---

# Skill Instructions

When to use this skill...

## Quick Reference
...

## Best Practices
...
```

## Using Skills

### In Your Workflow
1. Start working on a task
2. Bob automatically activates relevant skills
3. Bob follows the skill's instructions
4. Refer to supporting files for detailed examples

### Manual Reference
You can also reference skills manually:
- Check `SKILL.md` for quick guidance
- Consult `detailed-reference.md` for comprehensive examples
- Review `troubleshooting.md` for common issues

## Skill Locations

Skills can be defined at two levels:

| Location | Scope | Use Case |
|----------|-------|----------|
| `.bob/skills/` | Project-specific | Workflows unique to this project |
| `~/.bob/skills/` | Global | Personal or organization-wide workflows |

**Priority:** Project-level skills take precedence over global skills with the same name.

## Best Practices

### Creating Skills
- **Clear descriptions** - Help Bob understand when to activate
- **Focused instructions** - Keep SKILL.md concise
- **Supporting files** - Move detailed content to separate files
- **Actionable steps** - Structure as clear, step-by-step instructions

### Using Skills
- **Trust automation** - Let Bob activate skills automatically
- **Reference documentation** - Use supporting files for details
- **Keep updated** - Update skills as patterns evolve

## Project Structure

```
.bob/skills/
├── README.md                           # This file
├── frontend-development/
│   ├── SKILL.md                       # Frontend skill
│   ├── detailed-reference.md          # React & Carbon examples
│   └── troubleshooting.md             # Common issues
├── backend-development/
│   ├── SKILL.md                       # Backend skill
│   └── detailed-reference.md          # API & service examples
├── devops-deployment/
│   ├── SKILL.md                       # DevOps skill
│   └── detailed-reference.md          # Deployment configs
└── testing/
    └── SKILL.md                       # Testing skill
```

## Technology Coverage

| Technology | Skill | Section |
|------------|-------|---------|
| React 18 | Frontend Development | Core |
| Carbon Design System | Frontend Development | Core |
| Node.js/Express | Backend Development | Core |
| Turbonomic API | Backend Development | Integration |
| Docker | DevOps & Deployment | Containerization |
| Kubernetes/OpenShift | DevOps & Deployment | Orchestration |
| Ansible | DevOps & Deployment | Automation |
| Jest | Testing | Unit Testing |
| Cypress | Testing | E2E Testing |

## Quick Start

### For New Developers
1. Review `frontend-development/SKILL.md` for UI work
2. Review `backend-development/SKILL.md` for API work
3. Review `testing/SKILL.md` for quality assurance
4. Review `devops-deployment/SKILL.md` when ready to deploy

### For Specific Tasks
- **Creating a component** → Frontend Development skill
- **Adding an API endpoint** → Backend Development skill
- **Writing tests** → Testing skill
- **Deploying to production** → DevOps & Deployment skill

## Updating Skills

When updating skills:
1. Maintain consistent structure and format
2. Include code examples for new patterns
3. Update cross-references between skills
4. Add to best practices sections
5. Test that Bob can follow the instructions

## Resources

- [Bob Documentation](https://bob.ibm.com/docs)
- [Skills Best Practices](https://bob.ibm.com/docs/ide/features/skills)
- Project-specific documentation in each skill folder

---

**Last Updated:** 2026-05-26  
**Version:** 3.0.0 - Restructured to follow Bob best practices  
**Maintainer:** Operations Dashboard Team