---
name: playbook
description: Use when creating playbooks, roles, or inventory files. Use when automating infrastructure with Ansible. Use when encountering YAML syntax errors, module failures, or variable precedence issues.
---

# Ansible Playbook Development

Ansible playbooks declare desired system state rather than imperative commands. The core principle is idempotency: running a playbook multiple times produces the same result without unintended changes.

<Steps>
<Step>
Analyze the automation requirements and determine the appropriate Ansible structure (playbook, role, or inventory).
</Step>

<Step>
Set up the project structure following Ansible best practices:
- Create `ansible.cfg` for configuration
- Define inventory with host groups
- Organize roles in `roles/` directory
- Place playbooks in `playbooks/` directory
</Step>

<Step>
Write tasks using fully qualified collection names (FQCN) like `ansible.builtin.copy` instead of short names.
</Step>

<Step>
Extract hardcoded values to variables in `defaults/main.yml` for easy override.
</Step>

<Step>
Add handlers for service restarts triggered by configuration changes.
</Step>

<Step>
Verify the playbook:
- Run `ansible-playbook --syntax-check playbook.yml`
- Test with `ansible-playbook --check --diff playbook.yml`
- Execute and verify idempotency (second run shows no changes)
</Step>
</Steps>

## Quick Reference

### Project Structure

```
project/
├── ansible.cfg          # Configuration
├── inventory            # Host definitions
├── group_vars/          # Group variables
├── host_vars/           # Host-specific vars
├── roles/               # Reusable roles
└── playbooks/           # Playbook files
```

### Essential ansible.cfg

```ini
[defaults]
inventory = ./inventory
roles_path = ./roles
host_key_checking = False
stdout_callback = yaml

[privilege_escalation]
become = True
become_method = sudo
```

### Module Patterns

| Operation | Module | Key Parameters |
|-----------|--------|----------------|
| Create directory | `ansible.builtin.file` | `state: directory`, `mode`, `owner` |
| Copy file | `ansible.builtin.copy` | `src`, `dest`, `mode` |
| Template | `ansible.builtin.template` | `src`, `dest`, variables in `.j2` |
| Install package | `ansible.builtin.package` | `name`, `state: present` |
| Manage service | `ansible.builtin.service` | `name`, `state`, `enabled` |
| Run command | `ansible.builtin.command` | `cmd`, register result, set `changed_when` |

### Variable Precedence (lowest to highest)

1. Role defaults (`defaults/main.yml`)
2. Inventory group_vars
3. Inventory host_vars
4. Playbook vars
5. Role vars (`vars/main.yml`)
6. Task vars
7. Extra vars (`-e`)

### Handlers

```yaml
tasks:
  - name: Update config
    ansible.builtin.template:
      src: app.conf.j2
      dest: /etc/app.conf
    notify: Restart app

handlers:
  - name: Restart app
    ansible.builtin.service:
      name: app
      state: restarted
```

### Error Handling

```yaml
- block:
    - name: Risky operation
      ansible.builtin.command: /opt/app/upgrade.sh
  rescue:
    - name: Handle failure
      ansible.builtin.debug:
        msg: "Upgrade failed, rolling back"
  always:
    - name: Cleanup
      ansible.builtin.file:
        path: /tmp/upgrade.lock
        state: absent
```

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Using short module names | Always use FQCN: `ansible.builtin.copy` not `copy` |
| Hardcoded values | Extract to variables in `defaults/main.yml` |
| Missing `changed_when` on commands | Add `changed_when: "'created' in result.stdout"` |
| Forgetting handler flush | Use `meta: flush_handlers` when needed before dependent tasks |
| YAML indentation errors | Use 2 spaces, never tabs |
| Colon in unquoted string | Quote values containing `: ` |

## Verification Commands

```bash
ansible-playbook --syntax-check playbook.yml  # Check YAML
ansible-playbook --check playbook.yml         # Dry run
ansible-playbook --check --diff playbook.yml  # Show file changes
ansible-inventory --list                       # Verify inventory
ansible-inventory --host hostname             # Check host vars
```
