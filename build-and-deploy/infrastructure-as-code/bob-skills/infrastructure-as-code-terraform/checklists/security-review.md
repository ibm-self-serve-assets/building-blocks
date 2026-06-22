# Security Review Checklist

Use this checklist when reviewing Terraform/OpenTofu configurations for security issues.

## Secrets Management

- [ ] No secrets in variable defaults
- [ ] No secrets in `terraform.tfvars` files
- [ ] No hardcoded credentials in code
- [ ] Secrets sourced from external secret managers:
  - AWS Secrets Manager
  - Azure Key Vault
  - GCP Secret Manager
  - HashiCorp Vault
- [ ] `write_only` arguments used for secrets (Terraform 1.11+)
- [ ] Sensitive variables marked with `sensitive = true`
- [ ] Verify secrets not in state file: `terraform show | grep -i password`

## Encryption

- [ ] Encryption at rest enabled for:
  - S3 buckets (`server_side_encryption_configuration`)
  - EBS volumes (`encrypted = true`)
  - RDS databases (`storage_encrypted = true`)
  - DynamoDB tables (`server_side_encryption`)
- [ ] TLS/HTTPS enforced for data in transit
- [ ] KMS keys used (not default encryption)
- [ ] Key rotation enabled where supported

## Network Security

- [ ] No `0.0.0.0/0` in ingress rules (unless explicitly required and documented)
- [ ] Security groups follow least-privilege
- [ ] Separate security groups for different tiers (web, app, data)
- [ ] Use `aws_vpc_security_group_ingress_rule` not inline blocks (AWS provider v5+)
- [ ] Network ACLs configured appropriately
- [ ] VPC flow logs enabled
- [ ] No default VPC usage in production

## IAM & Access Control

- [ ] IAM policies follow least-privilege principle
- [ ] No wildcard (`*`) permissions unless absolutely necessary
- [ ] Service-specific IAM roles (not shared roles)
- [ ] MFA required for sensitive operations
- [ ] IAM password policy enforced
- [ ] Access keys rotated regularly
- [ ] No IAM user access keys (prefer roles)

## State File Security

- [ ] Remote state backend configured (not local)
- [ ] State file encryption enabled
- [ ] State file access restricted (IAM policies)
- [ ] State file versioning enabled
- [ ] State locking enabled
- [ ] Backup strategy in place

## Logging & Monitoring

- [ ] CloudTrail / Azure Activity Log / GCP Cloud Audit Logs enabled
- [ ] Log aggregation configured
- [ ] Sensitive data not logged
- [ ] Provisioner output doesn't leak secrets
- [ ] CI/CD logs don't expose credentials

## Compliance

- [ ] Resources tagged appropriately
- [ ] Compliance policies enforced (OPA, Sentinel)
- [ ] Audit trail maintained
- [ ] Data residency requirements met
- [ ] Retention policies configured

## Scanning Tools

Run these security scanners:

```bash
# Trivy (includes tfsec rules)
trivy config .

# Checkov
checkov -d .

# Custom policies (if using OPA)
terraform plan -out=tfplan
terraform show -json tfplan > tfplan.json
conftest test tfplan.json --policy policy/
```

## Common Vulnerabilities

### AWS-Specific
- [ ] S3 buckets not publicly accessible (unless intended)
- [ ] S3 bucket versioning enabled
- [ ] S3 bucket logging enabled
- [ ] RDS instances not publicly accessible
- [ ] RDS backup retention configured
- [ ] Lambda functions use latest runtime
- [ ] Lambda environment variables encrypted

### Azure-Specific
- [ ] Storage accounts use HTTPS only
- [ ] Storage accounts not publicly accessible
- [ ] Key Vault soft delete enabled
- [ ] Network security groups properly configured
- [ ] Managed identities used (not service principals)

### GCP-Specific
- [ ] Storage buckets not publicly accessible
- [ ] Storage bucket versioning enabled
- [ ] Cloud SQL instances not publicly accessible
- [ ] Cloud SQL backups enabled
- [ ] Service accounts follow least-privilege

## CI/CD Security

- [ ] Secrets stored in CI/CD secret management (not in code)
- [ ] CI/CD runners use minimal permissions
- [ ] Plan artifacts reviewed before apply
- [ ] Apply requires manual approval for production
- [ ] Terraform state backend credentials secured
- [ ] Lock file (`.terraform.lock.hcl`) committed

## Documentation

- [ ] Security decisions documented
- [ ] Exceptions documented with justification
- [ ] Threat model reviewed
- [ ] Security contacts identified

## Quick Security Scan

```bash
# Run all security checks
trivy config . && \
checkov -d . && \
terraform validate

# Check for common issues
grep -r "0.0.0.0/0" . --include="*.tf"
grep -r "password.*=" . --include="*.tf"
grep -r "secret.*=" . --include="*.tf"
grep -r "key.*=" . --include="*.tf"
```

## Severity Levels

When reporting findings, use these severity levels:

- **Critical**: Immediate security risk (exposed secrets, public databases)
- **High**: Significant security gap (missing encryption, overly permissive access)
- **Medium**: Security best practice violation (missing logging, weak policies)
- **Low**: Minor improvement (missing tags, documentation gaps)

## References

- [Security & Compliance Reference](../references/security-compliance.md)
- [State Management Security](../references/state-management.md)
- [CI/CD Security](../references/ci-cd-workflows.md)