# Ansible Skills

This directory contains specialized skills for Ansible automation workflows. Each skill provides step-by-step instructions for specific Ansible tasks.

## Available Skills

### playbook
**Use when:** Creating playbooks, roles, or inventory files. Automating infrastructure with Ansible. Encountering YAML syntax errors, module failures, or variable precedence issues.

**Provides:** 6-step workflow for developing Ansible playbooks with proper structure, FQCN usage, variable management, handlers, and verification.

### convert
**Use when:** Converting shell scripts to Ansible playbooks. Migrating bash automation, manual procedures, or Dockerfiles to idempotent Ansible tasks.

**Provides:** 8-step process for transforming imperative shell commands into declarative Ansible modules with proper idempotency.

### debug
**Use when:** Playbooks fail with UNREACHABLE, permission denied, MODULE FAILURE, or undefined variable errors. SSH connections fail or sudo password is missing.

**Provides:** 8-step systematic diagnosis for troubleshooting connection, authentication, module, and syntax errors.

### interactive
**Use when:** Guiding someone through Ansible setup step-by-step. Starting a new Ansible project from scratch. Teaching Ansible through hands-on development.

**Provides:** 6-step guided development process for incremental automation with continuous validation.

## Skill Structure

Each skill directory contains:
- `SKILL.md` - Main skill instructions with YAML front matter and `<Steps>` workflow
- Supporting files (optional) - Reference materials, templates, checklists, or scripts

## Usage

Skills are automatically activated by Bob in Advanced mode when your request matches the skill's description. You can also explicitly request a skill by name.

## Best Practices

- Skills follow IBM Bob conventions with clear, actionable steps
- Each skill has a single responsibility and focused purpose
- Supporting reference material is retained within each SKILL.md for context
- All skills use lowercase directory names with hyphens (kebab-case)