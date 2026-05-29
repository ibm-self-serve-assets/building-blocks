# Failure Mode Diagnosis Table

Use this table to identify which failure category applies to your task, then load the corresponding reference files.

| Failure Category | Symptoms | When to Diagnose | Primary References |
|------------------|----------|------------------|-------------------|
| **Identity churn** | Resource addresses shift after refactor, `count` index churn, missing `moved` blocks, destroy/recreate on rename | Refactoring resources, migrating count to for_each, renaming modules | [Code Patterns: count vs for_each](../references/code-patterns.md#count-vs-for_each-deep-dive), [Code Patterns: moved blocks](../references/code-patterns.md#moved-blocks-terraform-11) |
| **Secret exposure** | Secrets in variable defaults, state files, logs, CI artifacts, plaintext credentials | Handling passwords, API keys, certificates, any sensitive data | [Security & Compliance](../references/security-compliance.md), [Code Patterns: write-only](../references/code-patterns.md#write-only-arguments-terraform-111) |
| **Blast radius** | Oversized stacks (>500 resources), shared prod/non-prod state, unsafe applies affecting multiple environments | Organizing state files, splitting monolithic configurations | [State Management](../references/state-management.md), [Module Patterns](../references/module-patterns.md) |
| **CI drift** | Local plan ≠ CI plan, apply without reviewed artifact, unpinned versions, inconsistent results | Setting up CI/CD, debugging pipeline failures, version mismatches | [CI/CD Workflows](../references/ci-cd-workflows.md), [Code Patterns: versions](../references/code-patterns.md#version-management) |
| **Compliance gaps** | Missing policy stage, no approval model, no evidence retention, audit failures | Implementing governance, meeting compliance requirements | [Security & Compliance](../references/security-compliance.md), [CI/CD Workflows](../references/ci-cd-workflows.md) |
| **Testing blind spots** | Plan-only validation of computed values, set-type indexing errors, mock/real confusion | Writing tests, debugging test failures, validating complex logic | [Testing Frameworks](../references/testing-frameworks.md) |
| **State corruption / recovery** | Stuck lock, backend migration failures, drift reconciliation, lost state | State file issues, backend changes, disaster recovery | [State Management](../references/state-management.md) |
| **Provider upgrade risk** | Breaking-change provider bump, unpinned modules, deprecated resource types | Upgrading providers, updating dependencies | [Code Patterns: versions](../references/code-patterns.md#version-management), [Module Patterns](../references/module-patterns.md) |
| **Provider lifecycle** | Removing a provider with resources still in state, orphaned resources, `removed` block usage | Decommissioning resources, provider cleanup | [State Management: Provider Removal](../references/state-management.md#provider-removal) |
| **Bootstrap / orchestration misuse** | `null_resource` + `local-exec` for bootstrap, `remote-exec` for setup scripts, provisioner stdout leaking secrets | Using provisioners, bootstrap scripts, configuration management | [Code Patterns: Provisioners](../references/code-patterns.md#provisioners-as-last-resort) |
| **Navigation / safe-rename** | Cannot locate symbol defs/refs semantically, blind text replace, grep-only refactor missing refs | Refactoring variable names, renaming resources, code navigation | [Code Intelligence](../references/code-intelligence-lsp.md) |

## How to Use This Table

1. **Identify symptoms** - Match your current issue to the symptoms column
2. **Confirm category** - Read the "When to Diagnose" column to verify
3. **Load references** - Access only the listed reference files for that category
4. **Apply workflow** - Follow the diagnosis → solution → validation pattern

## Multiple Categories

If your task spans multiple categories:
- Load all relevant reference files
- Address categories in order of risk (secrets > blast radius > others)
- Document which categories were addressed in your response contract

## Unknown Category

If symptoms don't match any category:
- Start with [Quick Reference](../references/quick-reference.md) for general guidance
- Use [Code Patterns](../references/code-patterns.md) for code structure issues
- Consult [Module Patterns](../references/module-patterns.md) for architecture questions