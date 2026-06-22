# Module Release Checklist

Use this checklist before publishing or handing off a reusable Terraform/OpenTofu module.

## Prerequisites

- [ ] Runtime choice decided (Terraform vs OpenTofu)
- [ ] Target version floor determined (e.g., ≥1.6.0)
- [ ] Module scope defined (public vs private)
- [ ] Module type identified (resource/infrastructure/composition)

## Core Files

- [ ] `main.tf` - Primary resources implemented
- [ ] `variables.tf` - All inputs with descriptions and types
- [ ] `outputs.tf` - All outputs with descriptions
- [ ] `versions.tf` - Provider and Terraform version constraints
- [ ] `README.md` - Complete usage documentation
- [ ] `.gitignore` - Excludes `.terraform/`, `*.tfstate*`, `*.tfvars`, override files

## Documentation

- [ ] README includes module purpose and use cases
- [ ] Usage examples provided (copy-paste ready)
- [ ] All variables documented with:
  - Description
  - Type
  - Default value (if applicable)
  - Example values
- [ ] All outputs documented with:
  - Description
  - Type
  - Example usage
- [ ] Requirements table (Terraform/OpenTofu version, provider versions)
- [ ] Links use absolute paths (for Terraform Registry compatibility)

## Code Quality

- [ ] All variables have explicit `type` constraints
- [ ] All variables have `description`
- [ ] Sensitive variables marked with `sensitive = true`
- [ ] Complex constraints use `validation` blocks
- [ ] No hardcoded environment-specific values
- [ ] No hardcoded region or account IDs
- [ ] Follows naming conventions (descriptive, context-specific)
- [ ] Block ordering follows standard (see pre-commit checklist)

## Examples

- [ ] `examples/` directory exists
- [ ] `examples/minimal/` - Simplest possible usage
- [ ] `examples/complete/` - Full-featured example
- [ ] Examples are runnable (can `terraform init && plan`)
- [ ] Examples demonstrate key features
- [ ] Examples include README with instructions

## Testing

- [ ] Tests written and passing
  - Native `terraform test` (1.6+), OR
  - Terratest (Go-based)
- [ ] All `validation` blocks exercised in tests
- [ ] Both happy path and error cases tested
- [ ] Tests run in CI/CD pipeline
- [ ] Mock providers used for unit tests (1.7+)
- [ ] Integration tests use real cloud (on main branch only)

## Security

- [ ] No secrets in defaults or examples
- [ ] Security scanning passed (`trivy`, `checkov`)
- [ ] Sensitive outputs marked appropriately
- [ ] Follows least-privilege principles
- [ ] Encryption enabled where applicable

## Version Management

- [ ] Provider versions pinned with `~>` (e.g., `~> 5.0`)
- [ ] `.terraform.lock.hcl` committed
- [ ] Module version tagged in git (e.g., `v1.0.0`)
- [ ] CHANGELOG.md updated with changes
- [ ] Breaking changes clearly documented

## CI/CD Integration

- [ ] Pre-commit hooks configured
  - `terraform_fmt`
  - `terraform_validate`
  - `terraform_tflint`
  - `terraform_docs`
- [ ] Pre-commit config pinned to specific `rev`
- [ ] GitHub Actions / GitLab CI configured
- [ ] Automated tests run on PR
- [ ] Security scans run on every commit

## Public Modules Only

- [ ] LICENSE file present (MIT or Apache-2.0)
- [ ] Module name follows convention: `terraform-<PROVIDER>-<NAME>`
- [ ] Published to Terraform Registry or private registry
- [ ] Registry metadata configured
- [ ] Semantic versioning followed

## Multi-Provider Modules

- [ ] `configuration_aliases` declared in `required_providers`
- [ ] Provider passing documented in README
- [ ] Examples show how to pass aliased providers
- [ ] Each resource specifies `provider = aws.alias` explicitly

## Final Validation

```bash
# Run complete validation suite
terraform fmt -recursive -check
terraform validate
tflint
trivy config .
checkov -d .

# Test examples
cd examples/minimal && terraform init && terraform plan
cd ../complete && terraform init && terraform plan

# Run tests
terraform test  # or: cd tests && go test -v
```

## Release Process

1. [ ] Update version in metadata
2. [ ] Update CHANGELOG.md
3. [ ] Commit all changes
4. [ ] Tag release: `git tag v1.0.0`
5. [ ] Push tags: `git push --tags`
6. [ ] Publish to registry (if public)
7. [ ] Announce to team/community

## Post-Release

- [ ] Monitor for issues in first 48 hours
- [ ] Respond to user feedback
- [ ] Update documentation based on questions
- [ ] Plan next version improvements