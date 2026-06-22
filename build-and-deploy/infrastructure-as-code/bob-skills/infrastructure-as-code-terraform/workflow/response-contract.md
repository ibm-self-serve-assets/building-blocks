# Response Contract

Every Terraform/OpenTofu response must include these five elements. This ensures consistency, traceability, and safety across all infrastructure changes.

## 1. Assumptions & Version Floor

State explicitly:
- **Runtime**: `terraform` or `tofu`
- **Version**: Exact version or minimum required (e.g., "1.9.0" or "≥1.6.0")
- **Providers**: Name and version constraints (e.g., "aws ~> 5.0")
- **State backend**: Type and location (e.g., "S3 bucket: prod-terraform-state")
- **Execution path**: Where this runs (local, GitHub Actions, GitLab CI, Terraform Cloud, Atlantis)
- **Environment criticality**: dev, staging, production, or shared infrastructure

**Example:**
```
Assumptions:
- Runtime: Terraform 1.9.0
- Providers: aws ~> 5.0, random ~> 3.0
- Backend: S3 (prod-terraform-state/networking/terraform.tfstate)
- Execution: GitHub Actions on main branch
- Environment: Production (high criticality)
```

If the user didn't provide these details, state your assumptions explicitly.

## 2. Risk Category Addressed

Identify which failure mode(s) this solution addresses:
- Identity churn
- Secret exposure
- Blast radius
- CI drift
- Compliance gaps
- State corruption
- Provider upgrade risk
- Testing blind spots

**Example:**
```
Risk Categories:
- Secret exposure: Moving database password from variable to AWS Secrets Manager
- Compliance gaps: Adding policy-as-code validation stage
```

## 3. Chosen Remediation & Tradeoffs

Explain:
- **What was chosen**: The specific solution approach
- **What was traded off**: Alternative approaches not taken
- **Why**: Reasoning for this choice

**Example:**
```
Remediation:
- Chosen: AWS Secrets Manager data source with write_only argument (Terraform 1.11+)
- Traded off: Environment variables (less secure), encrypted tfvars (still in state)
- Why: Keeps secrets out of state entirely, integrates with AWS IAM, supports rotation
```

## 4. Validation Plan

Provide exact commands tailored to the risk tier:

**Low risk (dev environment, non-destructive):**
```bash
terraform fmt -check
terraform validate
terraform plan
```

**Medium risk (staging, or prod with safeguards):**
```bash
terraform fmt -check
terraform validate
tflint
terraform plan -out=tfplan
terraform show -json tfplan | jq '.'
# Review plan, then:
terraform apply tfplan
```

**High risk (production, destructive changes):**
```bash
terraform fmt -check
terraform validate
tflint
trivy config .
checkov -d .
terraform plan -out=tfplan
# Save plan artifact
terraform show -json tfplan > tfplan.json
# Policy validation
conftest test tfplan.json --policy policy/
# Manual review + approval required
# Then:
terraform apply tfplan
```

## 5. Rollback Notes

For any destructive or state-mutating change, document:
- **How to undo**: Exact steps to reverse the change
- **What evidence to keep**: Logs, plan files, state backups
- **Recovery time**: Expected time to rollback

**Example:**
```
Rollback:
- How: Restore state from backup: `terraform state push backup-20260529.tfstate`
- Evidence: Keep tfplan artifact, apply logs, pre-change state backup
- Recovery: ~5 minutes (state restore + re-apply previous config)
- Prevention: State versioning enabled in S3, can restore from any version
```

## Critical Rule

**Never recommend direct production apply without:**
1. A reviewed plan artifact (`terraform plan -out=tfplan`)
2. Approval from appropriate stakeholder
3. Documented rollback procedure

## Template

Use this template for consistency:

```markdown
## Response

### Assumptions & Version Floor
- Runtime: [terraform/tofu version]
- Providers: [provider versions]
- Backend: [backend type and location]
- Execution: [where this runs]
- Environment: [criticality level]

### Risk Category Addressed
- [Category]: [specific issue being solved]

### Chosen Remediation & Tradeoffs
- Chosen: [solution approach]
- Traded off: [alternatives not taken]
- Why: [reasoning]

### Validation Plan
```bash
[exact commands for this risk tier]
```

### Rollback Notes
- How: [undo steps]
- Evidence: [what to keep]
- Recovery: [time estimate]