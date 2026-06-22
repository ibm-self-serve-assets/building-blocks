# Pre-Commit Checklist

Run these checks before every commit to catch issues early.

## Quick Validation (Required)

```bash
# Format check
terraform fmt -recursive -check

# Syntax validation
terraform validate
```

## Code Quality Checks

### Naming Conventions
- [ ] All identifiers use `_` not `-`
- [ ] No resource names repeat resource type (no `aws_vpc.main_vpc`)
- [ ] Single-instance resources named `this` or descriptive name
- [ ] Variables have plural names for lists/maps (`subnet_ids` not `subnet_id`)
- [ ] All variables have descriptions
- [ ] All outputs have descriptions
- [ ] Output names follow `{name}_{type}_{attribute}` pattern
- [ ] No double negatives in variable names

### Code Structure
- [ ] `count`/`for_each` at top of resource blocks (blank line after)
- [ ] `tags` as last real argument in resources
- [ ] `depends_on` after tags (if used)
- [ ] `lifecycle` at end of resource (if used)
- [ ] Variables ordered: description → type → default → sensitive → nullable → validation
- [ ] Only `#` comments used (no `//` or `/* */`)

### Modern Features
- [ ] Using `try()` not `element(concat())`
- [ ] Secrets use write-only arguments or external data sources (not in state)
- [ ] `nullable = false` set on non-null variables
- [ ] `optional()` used in object types where applicable (Terraform 1.3+)
- [ ] Variable validation blocks added where constraints needed
- [ ] Consider cross-variable validation for related variables (Terraform 1.9+)

### Architecture
- [ ] `terraform.tfvars` only at composition level (not in modules)
- [ ] Remote state configured (never local state)
- [ ] Resource modules don't hardcode values (use variables/data sources)
- [ ] `terraform_remote_state` used only at ownership boundaries
- [ ] File structure follows standard: main.tf, variables.tf, outputs.tf, versions.tf

## Security Checks (Recommended)

```bash
# Linting
tflint --init && tflint

# Security scanning
trivy config .
checkov -d .
```

### Security Review
- [ ] No secrets in variable defaults
- [ ] No hardcoded credentials
- [ ] Encryption enabled for data at rest
- [ ] TLS/HTTPS enforced for data in transit
- [ ] Security groups follow least-privilege
- [ ] IAM policies follow least-privilege
- [ ] No `0.0.0.0/0` in security group rules (unless explicitly required)

## Documentation (For Modules)

- [ ] README.md exists with usage examples
- [ ] All variables documented in README
- [ ] All outputs documented in README
- [ ] Version requirements specified
- [ ] Examples provided (minimal and complete)

## Version Management

- [ ] `.terraform.lock.hcl` committed
- [ ] Provider versions pinned (`~> 5.0`)
- [ ] Terraform version specified in `required_version`
- [ ] Module sources pinned with `version` (in consumer code)

## Quick Command Reference

```bash
# Run all quick checks
terraform fmt -recursive && \
terraform validate && \
tflint && \
trivy config . && \
checkov -d .

# Or use pre-commit hooks (recommended)
pre-commit run --all-files
```

## Pre-Commit Hooks Setup

Create `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/antonbabenko/pre-commit-terraform
    rev: v1.88.0
    hooks:
      - id: terraform_fmt
      - id: terraform_validate
      - id: terraform_tflint
      - id: terraform_trivy
```

Install and run:
```bash
pre-commit install
pre-commit run --all-files