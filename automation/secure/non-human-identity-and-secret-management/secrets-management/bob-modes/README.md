# Secrets Management — Bob Custom Modes

This directory contains custom Bob modes for the Secrets Management building block.

---

## 📦 Available Modes

### Vault Secret Migrator

A custom Bob mode that equips Bob with the knowledge and workflow to:

- Scan a codebase for hardcoded secrets (API keys, passwords, tokens, cloud credentials, private keys).
- Migrate detected secrets to HashiCorp Vault via the Vault MCP server.
- Replace hardcoded values in source code with Vault SDK references.
- Generate a `SECURITY_REPORT.md` and `VAULT_MIGRATION_GUIDE.md` on completion.

| Property | Value |
|----------|-------|
| Mode zip | `base-modes/vault-secret-migrator.zip` |
| Requires | HashiCorp Vault + Vault MCP server configured in Bob |

---

## 🚀 Installation

See the step-by-step installation guide in [`base-modes/README.md`](base-modes/README.md) for instructions on importing this mode into a new or existing Bob project.

---

## 🔧 Requirements

- Bob UI with custom modes support
- HashiCorp Vault 1.12+
- Vault MCP server configured and connected to Bob

---

## 🔗 Related

- [Bob Skills for Secrets Management](../bob-skills/README.md) — skills that complement these modes
- [Secrets Management Overview](../README.md) — building block overview and architecture
