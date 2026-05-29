---
name: interactive
description: Use when guiding someone through Ansible setup step-by-step. Use when starting a new Ansible project from scratch. Use when teaching Ansible through hands-on development.
---

# Interactive Ansible Development

Interactive development builds automation incrementally with continuous validation. Each component is tested before adding the next. This catches errors early when they're easy to diagnose.

<Steps>
<Step>
**Environment Analysis** - Gather information before writing any code:
- How many servers? (affects inventory organization)
- IP addresses/hostnames? (required for inventory)
- SSH user and key location? (connection configuration)
- Password or key authentication? (determines SSH setup)
- Sudo with or without password? (privilege escalation config)
- Server roles (web, db, app)? (inventory grouping)
- Operating systems? (module selection: apt vs yum)

Verify Ansible is installed: `ansible --version`
</Step>

<Step>
**Project Setup** - Create minimal structure:

```bash
mkdir ansible-project && cd ansible-project
```

Create `ansible.cfg`:
```ini
[defaults]
inventory = ./inventory
host_key_checking = False
stdout_callback = yaml

[privilege_escalation]
become = True
become_method = sudo
```

Create `inventory`:
```ini
[webservers]
web1 ansible_host=192.168.1.10 ansible_user=admin ansible_ssh_private_key_file=~/.ssh/id_rsa

[dbservers]
db1 ansible_host=192.168.1.20 ansible_user=admin ansible_ssh_private_key_file=~/.ssh/id_rsa
```
</Step>

<Step>
**Connectivity Test** - Always test before writing playbooks:

```bash
ansible all -m ping
```

Interpret results:
- **SUCCESS**: Proceed to playbooks
- **UNREACHABLE**: Check `ssh -v user@host`
- **Permission denied**: Verify key path, permissions (600)
- **Sudo password required**: Add `--ask-become-pass` or configure NOPASSWD
</Step>

<Step>
**Incremental Playbook Development** - Start simple, add one task at a time:

Create `playbook.yml` starting with facts:
```yaml
---
- hosts: all
  tasks:
    - name: Show OS info
      ansible.builtin.debug:
        msg: "{{ ansible_distribution }} {{ ansible_distribution_version }}"
```

Run: `ansible-playbook playbook.yml`

Then add tasks one by one, testing after each addition.
</Step>

<Step>
**Validation Cycle** - After each change:
1. Syntax check: `ansible-playbook --syntax-check playbook.yml`
2. Dry run: `ansible-playbook --check --diff playbook.yml`
3. Execute: `ansible-playbook playbook.yml`
4. Verify idempotency: Run again and confirm `changed=0`
</Step>

<Step>
**Communication Pattern** when guiding users:
- Explain what will happen before running commands
- After completion, summarize what was accomplished
- When multiple approaches exist, present options with tradeoffs
- Acknowledge progress at milestones
- Stop and debug if any step fails before proceeding
</Step>
</Steps>

**Red Flags - Stop and Debug:**
- Adding multiple untested tasks at once
- Skipping `--check` before real runs
- Ignoring "changed" status on second run
- Not testing SSH before writing playbooks

### Phase 2: Project Setup

Create minimal structure:

```bash
mkdir ansible-project && cd ansible-project
```

**ansible.cfg:**
```ini
[defaults]
inventory = ./inventory
host_key_checking = False
stdout_callback = yaml

[privilege_escalation]
become = True
become_method = sudo
```

**inventory:**
```ini
[webservers]
web1 ansible_host=192.168.1.10 ansible_user=admin ansible_ssh_private_key_file=~/.ssh/id_rsa

[dbservers]
db1 ansible_host=192.168.1.20 ansible_user=admin ansible_ssh_private_key_file=~/.ssh/id_rsa
```

### Phase 3: Connectivity Test

**Always test before writing playbooks:**

```bash
ansible all -m ping
```

| Result | Action |
|--------|--------|
| SUCCESS | Proceed to playbooks |
| UNREACHABLE | Check `ssh -v user@host` |
| Permission denied | Verify key path, permissions (600) |
| Sudo password required | Add `--ask-become-pass` or configure NOPASSWD |

### Phase 4: Incremental Playbook Development

Start simple, add one task at a time:

```yaml
# playbook.yml - start with facts
---
- hosts: all
  tasks:
    - name: Show OS info
      ansible.builtin.debug:
        msg: "{{ ansible_distribution }} {{ ansible_distribution_version }}"
```

Run: `ansible-playbook playbook.yml`

Then add tasks one by one, testing after each:

```yaml
    - name: Ensure nginx installed
      ansible.builtin.package:
        name: nginx
        state: present
```

Run again. Fix any errors before adding more.

### Phase 5: Validation Cycle

After each change:

1. `ansible-playbook --syntax-check playbook.yml`
2. `ansible-playbook --check --diff playbook.yml`
3. `ansible-playbook playbook.yml`
4. Run again—verify `changed=0` (idempotency)

## Red Flags - Stop and Debug

- Adding multiple untested tasks at once
- Skipping `--check` before real runs
- Ignoring "changed" on second run
- Not testing SSH before writing playbooks

## Communication Pattern

When guiding users:
- Explain what will happen before running commands
- After completion, summarize what was done
- When multiple approaches exist, present options with tradeoffs
- Acknowledge progress at milestones
