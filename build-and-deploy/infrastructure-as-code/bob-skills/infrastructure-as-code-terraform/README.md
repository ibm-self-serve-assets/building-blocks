# Terraform/OpenTofu IaC Skill

A comprehensive skill for Infrastructure as Code development with Terraform and OpenTofu, following IBM Bob Skills best practices.

## Quick Start

This skill activates automatically when you:
- Write or review Terraform/OpenTofu configurations
- Debug state issues or resource drift
- Set up testing frameworks or CI/CD pipelines
- Implement security best practices
- Migrate between backends or versions

## Structure

```
.bob/skills/
├── SKILL.md                    # Main skill file (core workflow)
├── README.md                   # This file
├── workflow/                   # Core workflow guidance
│   ├── diagnosis-table.md      # Failure mode identification
│   └── response-contract.md    # Required response format
├── checklists/                 # Quick validation checklists
│   ├── pre-commit.md          # Pre-commit validation
│   ├── module-release.md      # Module publishing checklist
│   └── security-review.md     # Security review checklist
└── references/                 # Deep-dive technical references
    ├── quick-reference.md      # Command cheat sheets
    ├── code-patterns.md        # Code structure and patterns
    ├── module-patterns.md      # Module development
    ├── testing-frameworks.md   # Testing strategies
    ├── ci-cd-workflows.md      # CI/CD integration
    ├── security-compliance.md  # Security best practices
    ├── state-management.md     # State file management
    └── code-intelligence-lsp.md # terraform-ls integration
```

## How It Works

### 1. Diagnose First
The skill uses a **diagnose-first approach**. When you request help, it:
1. Captures your execution context (runtime, version, providers, backend)
2. Identifies the failure mode using the diagnosis table
3. Loads only relevant reference materials
4. Proposes a solution with risk controls
5. Provides validation commands and rollback procedures

### 2. Progressive Disclosure
- **SKILL.md** contains the core workflow (kept concise)
- **workflow/** contains essential process guidance
- **checklists/** provide quick validation steps
- **references/** contain deep technical details (loaded on demand)

### 3. Response Contract
Every response includes:
- Assumptions & version floor
- Risk category addressed
- Chosen remediation & tradeoffs
- Validation plan
- Rollback notes

## Key Capabilities

### Failure Mode Diagnosis
Identifies and fixes 8 common failure patterns:
- Identity churn (resource address shifts)
- Secret exposure (credentials in state/logs)
- Blast radius (oversized stacks)
- CI drift (local vs CI mismatches)
- Compliance gaps (missing policies)
- State corruption (locks, migrations)
- Provider upgrade risks
- Testing blind spots

### Module Development
- 3-tier hierarchy: Resource → Infrastructure → Composition
- Standard file structure and naming conventions
- Variable/output contracts with validation
- Cross-cloud resource mapping (AWS/Azure/GCP)

### Testing Frameworks
- Static analysis (fmt, validate, tflint, trivy, checkov)
- Native tests (Terraform 1.6+)
- Terratest (Go-based integration)
- Mock providers (1.7+, cost-free)

### CI/CD Integration
- GitHub Actions and GitLab CI templates
- Atlantis automation
- Cost optimization strategies
- Drift prevention

### Security & Compliance
- Security scanning integration
- Secrets management patterns
- State file hardening
- Policy-as-code (OPA, Sentinel)

### State Management
- Remote backend selection and configuration
- Locking mechanisms
- State organization patterns
- Migration workflows
- Disaster recovery

## Version Support

- **Terraform**: 1.0+
- **OpenTofu**: 1.6+
- Version-specific features documented with minimum version requirements

## Quick Reference

### Common Commands
```bash
# Validation
terraform fmt -recursive -check
terraform validate
tflint

# Security scanning
trivy config .
checkov -d .

# Testing
terraform test  # 1.6+

# State operations
terraform state list
terraform state show <resource>
```

### When to Use Each File

| Need | Use This File |
|------|---------------|
| Identify failure mode | `workflow/diagnosis-table.md` |
| Understand response format | `workflow/response-contract.md` |
| Pre-commit validation | `checklists/pre-commit.md` |
| Module release | `checklists/module-release.md` |
| Security review | `checklists/security-review.md` |
| Command reference | `references/quick-reference.md` |
| Code structure | `references/code-patterns.md` |
| Module architecture | `references/module-patterns.md` |
| Testing strategy | `references/testing-frameworks.md` |
| CI/CD setup | `references/ci-cd-workflows.md` |
| Security hardening | `references/security-compliance.md` |
| State management | `references/state-management.md` |
| Code navigation | `references/code-intelligence-lsp.md` |

## Examples

### Example 1: Writing a New Module
1. Skill identifies this as module development
2. Loads `references/module-patterns.md`
3. Provides structure following best practices
4. References `checklists/module-release.md` for completion

### Example 2: Debugging State Lock
1. Skill diagnoses as "state corruption"
2. Loads `references/state-management.md`
3. Provides unlock procedure with safety checks
4. Documents rollback in response contract

### Example 3: Security Review
1. Skill identifies as "secret exposure" or "compliance gaps"
2. Loads `references/security-compliance.md`
3. Uses `checklists/security-review.md` for systematic review
4. Provides remediation with validation commands

## Best Practices

### For Users
- Let the skill diagnose before requesting specific solutions
- Provide context (runtime, version, environment) when possible
- Review the response contract before applying changes
- Use checklists for systematic validation

### For Skill Maintenance
- Keep SKILL.md focused on workflow (< 100 lines)
- Move detailed content to appropriate reference files
- Update checklists based on common issues
- Maintain version-specific guidance

## Contributing

When updating this skill:
1. Keep SKILL.md concise (core workflow only)
2. Add detailed content to appropriate reference files
3. Create checklists for repeatable processes
4. Update this README with structural changes
5. Test with real-world scenarios

## License

Apache-2.0

## Version

2.0.0 - Restructured following IBM Bob Skills best practices

## Author

Building Blocks