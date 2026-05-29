# Bob Skills Directory

This directory contains modular, domain-specific skills that Bob can automatically activate based on user requests. Each skill follows the official Bob skills format with YAML front matter and structured instructions.

## Directory Structure

```
.bob/skills/
├── README.md                           # This file
├── SKILLS_SUMMARY.md                   # Comprehensive overview
├── ansible-automation/                 # Ansible and infrastructure automation
│   ├── SKILL.md                        # Core skill instructions
│   ├── vault-config-reference.md       # Configuration templates
│   └── vault-deployment-checklist.md   # Deployment checklist
├── frontend-development/               # React and frontend development
│   ├── SKILL.md                        # Core skill instructions
│   ├── app-capabilities.md             # App features and recent fixes
│   ├── carbon-design-guide.md          # Carbon component reference
│   ├── components/                     # Reusable React components
│   │   └── ProductionShellTemplate.jsx # Enterprise shell template
│   └── styles/                         # Shared CSS/SCSS assets
│       └── SharedStyles.scss           # Complete style library
├── backend-development/                # Python Flask and backend APIs
│   ├── SKILL.md                        # Core skill instructions
│   └── api-patterns.md                 # API patterns and examples
├── deployment-operations/              # Deployment and DevOps
│   ├── SKILL.md                        # Core skill instructions
│   └── scripts/                        # Startup and deployment scripts
│       ├── start-frontend.sh           # Frontend startup
│       ├── start-backend.sh            # Backend startup
│       └── start-all.sh                # Combined startup
└── troubleshooting/                    # Debugging and problem resolution
    ├── SKILL.md                        # Core skill instructions
    └── common-issues.md                # 30+ issues with solutions
```

## Skill Format

Each skill follows the official Bob skills format:

```markdown
---
name: skill-name
description: Clear description that helps Bob decide when to activate this skill
---

<Steps>
<Step>
First actionable step
</Step>
<Step>
Second actionable step
</Step>
</Steps>

Additional instructions and reference materials...
```

## Skill Activation

Bob automatically activates skills based on:
- **Description matching**: Bob analyzes the skill description to determine relevance
- **User request context**: Keywords and intent in user messages
- **Project context**: Current files and directory structure
- **Task requirements**: Type of work being requested

## Available Skills

### 1. **ansible-automation**
Deploy and manage HashiCorp Vault using Ansible automation with proper configuration, permissions, and security setup.

**Activates when:** User mentions ansible, playbook, deploy vault, vault installation, infrastructure automation

### 2. **frontend-development**
Build enterprise-grade React applications with IBM Carbon Design System, including reusable components and responsive design patterns.

**Activates when:** User mentions react, frontend, component, UI, carbon design, dashboard, menu, navigation

**Supporting files:**
- `app-capabilities.md` - Application features and recent implementations
- `carbon-design-guide.md` - Carbon component quick reference
- `components/ProductionShellTemplate.jsx` - Enterprise shell template
- `styles/SharedStyles.scss` - Complete style library

### 3. **backend-development**
Build Flask-based REST APIs with HashiCorp Vault integration, secret scanning, and Git repository analysis.

**Activates when:** User mentions flask, backend, API, endpoint, python, REST, server

### 4. **deployment-operations**
Deploy, run, and maintain applications with startup scripts, environment configuration, health monitoring, and operational procedures.

**Activates when:** User mentions deploy, start, run, launch, startup, environment

**Supporting files:**
- `scripts/start-frontend.sh` - Frontend startup script
- `scripts/start-backend.sh` - Backend startup script
- `scripts/start-all.sh` - Combined startup with health checks

### 5. **troubleshooting**
Debug and resolve common issues in applications, Vault, Docker, OpenShift, Nexus, and GPU operators with step-by-step solutions.

**Activates when:** User mentions error, not working, failed, issue, problem, troubleshoot, debug

**Coverage:** 30+ common issues with detailed solutions

## Usage Examples

### For Ansible Tasks
When user mentions "deploy vault" or "ansible playbook", Bob activates `ansible-automation/skills.md`

### For React Development
When user mentions "create component" or "frontend", Bob activates `frontend-development/skills.md`

### For API Development
When user mentions "create endpoint" or "Flask API", Bob activates `backend-development/skills.md`

### For Troubleshooting
When user mentions "error" or "not working", Bob activates `troubleshooting/skills.md`

## Best Practices

### Skill Structure
- **Keep SKILL.md focused**: Core workflow and actionable steps only
- **Use supporting files**: Move detailed content to companion files
- **Clear descriptions**: Help Bob determine when to activate the skill
- **Actionable steps**: Use `<Steps>` format for systematic workflows
- **Single responsibility**: One skill per specific task or domain

### Supporting Files
- **Reference materials**: Detailed guides, checklists, templates
- **Code examples**: Reusable components and patterns
- **Configuration**: Templates and examples
- **Documentation**: Comprehensive explanations and troubleshooting

### Maintenance
- Keep skills modular and focused
- Update templates as patterns evolve
- Document lessons learned and recent fixes
- Add new troubleshooting scenarios as encountered
- Maintain consistency across skills
- Version control all changes

## Contributing

When adding new skills:
1. Create appropriate subdirectory
2. Add skills.md with clear instructions
3. Include templates and examples
4. Update this README
5. Test skill activation

---

**Last Updated:** 2026-05-28
**Project:** Vault32 Secret Scanner & Migration Platform

## Recent Updates

### 2026-05-28
- **Skills Restructure**: Applied best practices - moved detailed content to supporting files
- **Frontend Development**: Created `app-capabilities.md` for features and recent fixes
- **Frontend Development**: Documented menu auto-close implementation with code examples
- **ProductionShell Component**: Implemented auto-close functionality for side navigation menu
- **README**: Updated structure to reflect best practices and supporting files