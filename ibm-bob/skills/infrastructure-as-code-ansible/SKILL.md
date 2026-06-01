---
name: infrastructure-as-code-ansible
description: Use for any Ansible-related tasks including playbook development, shell script conversion, debugging failures, or interactive setup. This is the parent skill that provides access to specialized Ansible workflows.
---

# Ansible Skills

This skill provides access to specialized Ansible workflows for automation tasks. When activated, you can leverage four focused sub-skills for different Ansible scenarios.

## Available Workflows

### Playbook Development
Use the **playbook** skill when:
- Creating new playbooks, roles, or inventory files
- Automating infrastructure with Ansible
- Encountering YAML syntax errors, module failures, or variable precedence issues

### Shell Script Conversion
Use the **convert** skill when:
- Converting shell scripts to Ansible playbooks
- Migrating bash automation, manual procedures, or Dockerfiles
- Transforming imperative commands to declarative Ansible tasks

### Debugging & Troubleshooting
Use the **debug** skill when:
- Playbooks fail with UNREACHABLE, permission denied, or MODULE FAILURE errors
- SSH connections fail or sudo password is missing
- Encountering undefined variable or template rendering errors

### Interactive Setup & Teaching
Use the **interactive** skill when:
- Guiding someone through Ansible setup step-by-step
- Starting a new Ansible project from scratch
- Teaching Ansible through hands-on development with continuous validation

## Quick Start

<Steps>
<Step>
Identify your Ansible task category:
- **Development**: Creating or modifying playbooks → use `playbook` skill
- **Migration**: Converting scripts to Ansible → use `convert` skill
- **Troubleshooting**: Fixing errors or failures → use `debug` skill
- **Learning**: Setting up or teaching Ansible → use `interactive` skill
</Step>

<Step>
Bob will automatically activate the appropriate sub-skill based on your request, or you can explicitly request a specific skill by name.
</Step>

<Step>
Follow the step-by-step workflow provided by the activated skill to complete your task systematically.
</Step>
</Steps>

## Core Principles

All Ansible skills follow these principles:
- **Idempotency**: Operations can be run multiple times safely
- **Declarative**: Define desired state, not imperative commands
- **FQCN**: Use fully qualified collection names (e.g., `ansible.builtin.copy`)
- **Validation**: Test with `--check --diff` before execution
- **Incremental**: Build and test one component at a time

## Reference

For detailed module usage, command syntax, and troubleshooting patterns, refer to the supporting documentation within each skill directory.
