---
name: terraform-infrastructure-as-code
description: Use when writing, reviewing, or debugging Terraform/OpenTofu modules, tests, CI/CD pipelines, or state operations. Diagnoses failure modes (identity churn, secrets, blast radius, CI drift, state corruption) with version-aware guidance.
license: Apache-2.0
metadata:
  author: Building Blocks
  version: 2.0.0
---

# Terraform/OpenTofu IaC Skill

Diagnose-first guidance for Infrastructure as Code. This skill helps you write, review, and debug Terraform/OpenTofu configurations by identifying failure modes before generating solutions.

## When to Use This Skill

Activate this skill when you need to:
- Write or review Terraform/OpenTofu configurations
- Debug state issues or resource drift
- Set up testing frameworks or CI/CD pipelines
- Implement security best practices
- Migrate between backends or versions
- Refactor modules or resource addressing

## Core Workflow

<Steps>
<Step>
**Capture Context** - Identify runtime (terraform/tofu), version, providers, backend, execution path (local/CI/Cloud), and environment criticality.
</Step>

<Step>
**Diagnose Failure Mode** - Use the failure mode table in `workflow/diagnosis-table.md` to identify which category applies: identity churn, secret exposure, blast radius, CI drift, compliance gaps, testing blind spots, state corruption, or provider risks.
</Step>

<Step>
**Load Reference Materials** - Access only the relevant reference files based on the diagnosed failure mode. Don't preload unnecessary depth.
</Step>

<Step>
**Propose Solution** - Generate fix with risk controls, explaining why this addresses the failure mode, what could still go wrong, and what guardrails are needed (tests/approvals/rollback).
</Step>

<Step>
**Generate Artifacts** - Create HCL code, migration blocks (`moved`, `import`), CI configuration, or policy rules as needed.
</Step>

<Step>
**Validate** - Run validation commands tailored to the risk tier before finalizing.
</Step>

<Step>
**Document Response** - Provide the complete response contract (see `workflow/response-contract.md`).
</Step>
</Steps>

## Response Contract

Every response must include:

1. **Assumptions & version floor** - Runtime, exact version, providers, backend, execution path, environment criticality
2. **Risk category addressed** - Which failure mode(s) being solved
3. **Chosen remediation & tradeoffs** - What was chosen, what was traded off, why
4. **Validation plan** - Exact commands (`fmt -check`, `validate`, `plan -out`, policy check)
5. **Rollback notes** - For destructive changes: how to undo, what evidence to keep

**Critical Rule:** Never recommend direct production apply without a reviewed plan artifact and approval.

## Key Principles

- **Diagnose before generate** - Identify root cause first
- **Version-aware** - Check feature availability for target version
- **Progressive disclosure** - Load depth only when needed
- **Risk-first** - Always consider blast radius and rollback
- **Validation-gated** - Test before apply

## Supporting Resources

All detailed guidance lives in supporting files:

- `workflow/` - Core workflow steps and contracts
- `references/` - Deep-dive technical references
- `checklists/` - Quick validation checklists
- `templates/` - Reusable code templates

Refer to `references/quick-reference.md` for command cheat sheets and decision flowcharts.

## Version Support

- Terraform 1.0+ and OpenTofu 1.6+
- Version-specific features documented in `references/version-features.md`
- Cross-version migration guidance available

---

**License:** Apache-2.0 | **Author:** Building Blocks | **Version:** 2.0.0
