# Infrastructure as Code (IaC) Skills

Infrastructure as Code building blocks enable automated infrastructure provisioning, multi-cloud blueprints, and declarative resource orchestration using Terraform and OpenTofu.

## 📦 Available Assets & Skills

### `infrastructure-as-code-terraform.zip`

A comprehensive skill and automation package for Terraform and OpenTofu development, providing capabilities for:

- **Failure Mode Diagnosis**: Systematic identification of common IaC issues such as state drift, locking, and blast-radius concerns.
- **Module Development**: Modular 3-tier architecture (Resource → Infrastructure → Composition) with variable/output validation.
- **Testing & Verification**: Static analysis (tflint, checkov, trivy), native Terraform testing, and integration testing frameworks.
- **CI/CD & State Automation**: Automated pipeline workflows (GitHub Actions, GitLab CI, Atlantis) and state backend management.

## 🚀 Installation and Setup

### Step 1: Extract the Skill to Bob Workspace
Extract the `infrastructure-as-code-terraform.zip` archive into your Bob workspace skills directory:

```bash
# Navigate to your Bob workspace skills directory
cd /path/to/your/bob/workspace/.bob/skills

# Extract the package
unzip /path/to/automation/operate/infrastructure-as-code/bob-skills/infrastructure-as-code-terraform.zip
```

### Step 2: Verify Installation
Check that the skill files are present:

```bash
ls -la .bob/skills/
```

### Step 3: Activate in Bob
1. Open Bob and select your preferred mode.
2. Ensure the **Skills** option is enabled.
3. The Infrastructure as Code capabilities will be active and ready to assist.
