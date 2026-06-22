---
name: debug
description: Use when playbooks fail with UNREACHABLE, permission denied, MODULE FAILURE, or undefined variable errors. Use when SSH connections fail or sudo password is missing.
---

# Ansible Debugging

Ansible errors fall into four categories: connection, authentication, module, and syntax. Systematic diagnosis starts with identifying the category, then isolating the specific cause.

<Steps>
<Step>
Identify the error category from the failure message:
- **Connection**: UNREACHABLE, network timeout
- **Authentication**: Permission denied, missing sudo password
- **Module**: MODULE FAILURE, invalid parameters
- **Syntax**: YAML parse error, indentation issues
</Step>

<Step>
For **Connection Errors**:
- Test SSH directly: `ssh -v -i /path/to/key user@hostname`
- Check port connectivity: `nc -zv hostname 22`
- Verify inventory parsing: `ansible-inventory --host hostname`
- Common causes: wrong IP/hostname, firewall blocking port 22, SSH key permissions (must be 600)
</Step>

<Step>
For **Authentication Errors**:
- Test with explicit options: `ansible hostname -m ping -u user --private-key /path/to/key`
- For sudo password issues: use `ansible-playbook playbook.yml --ask-become-pass`
- Or configure NOPASSWD in `/etc/sudoers`
- Verify SSH key permissions are 600
</Step>

<Step>
For **Module Errors**:
- Check module documentation: `ansible-doc ansible.builtin.copy`
- Verify module parameters match your Ansible version: `ansible --version`
- Ensure required parameters are provided
- Check target system state matches module expectations
</Step>

<Step>
For **Variable Errors**:
- Use default filter for optional variables: `{{ my_var | default('fallback') }}`
- Debug variable values: Add `ansible.builtin.debug` task with `var: problematic_variable`
- Check variable precedence (role defaults < inventory < playbook < extra vars)
</Step>

<Step>
Use progressive verbosity for deeper diagnosis:
- `-v`: Task results
- `-vv`: Task input parameters
- `-vvv`: SSH connection details
- `-vvvv`: Full plugin internals

Start with `-v` and increase only if needed.
</Step>

<Step>
Isolate the problem:
- Run syntax check: `ansible-playbook --syntax-check playbook.yml`
- Dry run: `ansible-playbook --check playbook.yml`
- Step through tasks: `ansible-playbook --step playbook.yml`
- Start at specific task: `ansible-playbook --start-at-task "Task Name" playbook.yml`
- Limit to specific host: `ansible-playbook --limit hostname playbook.yml`
</Step>

<Step>
For performance issues:
- Enable task timing in `ansible.cfg`: `callback_whitelist = profile_tasks`
- Enable SSH pipelining: `pipelining = True` in `[ssh_connection]`
- Skip fact gathering if not needed: `gather_facts: no`
</Step>
</Steps>

## Quick Diagnosis

### Connection Errors

```bash
# Test SSH directly
ssh -v -i /path/to/key user@hostname

# Test port connectivity
nc -zv hostname 22

# Verify inventory parsing
ansible-inventory --host hostname
```

**Common causes:**
- Wrong IP/hostname in inventory
- Firewall blocking port 22
- SSH key permissions (must be 600)

### Authentication Errors

```bash
# Test with explicit options
ansible hostname -m ping -u user --private-key /path/to/key

# For sudo password issues, either:
ansible-playbook playbook.yml --ask-become-pass
# Or configure NOPASSWD in /etc/sudoers
```

### Module Errors

```bash
# Check module documentation
ansible-doc ansible.builtin.copy

# Verify module parameters match your Ansible version
ansible --version
```

### Variable Errors

```yaml
# Use default filter for optional variables
{{ my_var | default('fallback') }}

# Debug variable values
- ansible.builtin.debug:
    var: problematic_variable
```

## Verbosity Levels

| Flag | Shows |
|------|-------|
| `-v` | Task results |
| `-vv` | Task input parameters |
| `-vvv` | SSH connection details |
| `-vvvv` | Full plugin internals |

Start with `-v`, increase only if needed.

## Debugging Commands

```bash
# Syntax check only
ansible-playbook --syntax-check playbook.yml

# Dry run
ansible-playbook --check playbook.yml

# Step through tasks
ansible-playbook --step playbook.yml

# Start at specific task
ansible-playbook --start-at-task "Task Name" playbook.yml

# Limit to specific host
ansible-playbook --limit hostname playbook.yml
```

## Common Error Patterns

| Error | Cause | Fix |
|-------|-------|-----|
| `Permission denied (publickey)` | SSH key not accepted | Check key permissions, verify authorized_keys |
| `Missing sudo password` | become=true without password | Use `--ask-become-pass` or configure NOPASSWD |
| `No such file or directory` | Path doesn't exist | Create parent directories first |
| `Unable to lock` (apt/yum) | Package manager locked | Wait for other process, remove stale lock |
| `undefined variable` | Variable not defined | Check spelling, use `default()` filter |

## Performance Debugging

```ini
# ansible.cfg
[defaults]
callback_whitelist = profile_tasks  # Show task timing

[ssh_connection]
pipelining = True                   # Faster SSH
```

```yaml
# Skip fact gathering if not needed
- hosts: all
  gather_facts: no
```
