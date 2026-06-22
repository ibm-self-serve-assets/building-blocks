# Infrastructure as Code (IaC) Skills

This directory contains Bob skills for Infrastructure as a Service (IaaS) Building Blocks, enabling automated infrastructure provisioning, configuration management, and deployment workflows.

## 🎯 Overview

The Infrastructure as Code skills empower Bob to help you automate infrastructure provisioning and configuration management using industry-standard tools like Terraform/OpenTofu and Ansible. These skills enable declarative infrastructure definitions, automated deployments, and systematic troubleshooting of IaC workflows.

## 📦 Available Skills

### infrastructure-as-code-terraform

A comprehensive skill for Infrastructure as Code development with Terraform and OpenTofu, providing capabilities for:

#### 1. 🔍 **Diagnose-First Approach**
Systematic failure mode identification and resolution:
- Identity churn (resource address shifts)
- Secret exposure (credentials in state/logs)
- Blast radius (oversized stacks)
- CI drift (local vs CI mismatches)
- Compliance gaps (missing policies)
- State corruption (locks, migrations)
- Provider upgrade risks
- Testing blind spots

#### 2. 📝 **Module Development**
Best practices for Terraform/OpenTofu modules:
- 3-tier hierarchy: Resource → Infrastructure → Composition
- Standard file structure and naming conventions
- Variable/output contracts with validation
- Cross-cloud resource mapping (AWS/Azure/GCP)
- Version-aware feature guidance

#### 3. 🧪 **Testing Frameworks**
Comprehensive testing strategies:
- Static analysis (fmt, validate, tflint, trivy, checkov)
- Native tests (Terraform 1.6+)
- Terratest (Go-based integration)
- Mock providers (1.7+, cost-free)
- Pre-commit validation checklists

#### 4. 🔄 **CI/CD Integration**
Automated deployment pipelines:
- GitHub Actions and GitLab CI templates
- Atlantis automation
- Cost optimization strategies
- Drift prevention and detection
- Plan review workflows

#### 5. 🔒 **Security & Compliance**
Infrastructure security hardening:
- Security scanning integration
- Secrets management patterns
- State file hardening
- Policy-as-code (OPA, Sentinel)
- Compliance validation

#### 6. 💾 **State Management**
Robust state file operations:
- Remote backend selection and configuration
- Locking mechanisms
- State organization patterns
- Migration workflows
- Disaster recovery procedures

### infrastructure-as-code-ansible

A comprehensive skill for automation with Ansible, providing specialized workflows for:

#### 1. 📖 **Playbook Development**
Creating and maintaining Ansible automation:
- Playbook, role, and inventory creation
- Infrastructure automation patterns
- YAML syntax and module usage
- Variable precedence and templating
- Best practices and idempotency

#### 2. 🔄 **Shell Script Conversion**
Migrating imperative scripts to declarative Ansible:
- Bash script to playbook conversion
- Manual procedure automation
- Dockerfile to Ansible transformation
- Imperative to declarative patterns
- Migration validation

#### 3. 🐛 **Debugging & Troubleshooting**
Systematic error resolution:
- UNREACHABLE and MODULE FAILURE errors
- SSH connection issues
- Permission and sudo problems
- Undefined variable errors
- Template rendering issues

#### 4. 🎓 **Interactive Setup & Teaching**
Guided learning and project setup:
- Step-by-step Ansible installation
- New project scaffolding
- Hands-on development with validation
- Best practices teaching
- Continuous feedback loops

## 🚀 Installation and Setup

### Step 1: Download the Skills

Download the skill packages from the IBM Bob skills directory:
- `infrastructure-as-code-terraform` - Located at `ibm-bob/skills/infrastructure-as-code-terraform/`
- `infrastructure-as-code-ansible` - Located at `ibm-bob/skills/infrastructure-as-code-ansible/`

### Step 2: Extract Skills to Bob Workspace

Extract the contents to your Bob workspace skills directory:

```bash
# Navigate to your Bob workspace skills directory
cd /path/to/your/bob/workspace/.bob/skills

# Copy the Terraform skill
cp -r /path/to/ibm-bob/skills/infrastructure-as-code-terraform ./

# Copy the Ansible skill
cp -r /path/to/ibm-bob/skills/infrastructure-as-code-ansible ./
```

After extraction, you should see both skill folders in your `.bob/skills` directory.

### Step 3: Verify Installation

Check that the skills are properly installed:

```bash
ls -la .bob/skills/infrastructure-as-code-terraform
ls -la .bob/skills/infrastructure-as-code-ansible
```

You should see the skill files including SKILL.md, README.md, and supporting documentation.

### Step 4: Activate the Skills

To use the skills:
1. Open Bob and select Advanced mode (or any mode with skills support)
2. Enable the **Skills** button in that mode
3. The `infrastructure-as-code-terraform` and `infrastructure-as-code-ansible` skills will be available for use within that mode

## 💡 Usage Examples

Once activated, you can ask Bob to help with tasks like:

### Terraform/OpenTofu Tasks

#### Module Development
- *"Create a Terraform module for AWS VPC with public and private subnets"*
- *"Review this Terraform configuration for security issues"*
- *"Refactor this module to follow best practices"*
- *"Generate a composition module for multi-region deployment"*

#### State Management
- *"Help me migrate from local to S3 backend"*
- *"Debug this state lock issue"*
- *"Show me how to import existing resources"*
- *"Recover from state corruption"*

#### Testing & Validation
- *"Set up Terraform testing with native test framework"*
- *"Create Terratest integration tests"*
- *"Configure pre-commit hooks for validation"*
- *"Add security scanning to CI pipeline"*

#### CI/CD Integration
- *"Create GitHub Actions workflow for Terraform"*
- *"Set up Atlantis for PR automation"*
- *"Implement drift detection in CI"*
- *"Add cost estimation to pipeline"*

### Ansible Tasks

#### Playbook Development
- *"Create an Ansible playbook to configure web servers"*
- *"Write a role for PostgreSQL installation"*
- *"Help me structure my Ansible project"*
- *"Debug this variable precedence issue"*

#### Script Conversion
- *"Convert this bash deployment script to Ansible"*
- *"Transform this Dockerfile to an Ansible playbook"*
- *"Migrate manual server setup to Ansible automation"*
- *"Convert imperative commands to declarative tasks"*

#### Debugging
- *"Fix this 'UNREACHABLE' error in my playbook"*
- *"Resolve SSH connection failures"*
- *"Debug undefined variable in template"*
- *"Fix sudo password authentication"*

#### Interactive Setup
- *"Guide me through setting up Ansible from scratch"*
- *"Help me create my first Ansible project"*
- *"Teach me Ansible best practices step-by-step"*
- *"Walk me through inventory configuration"*

## 🎓 What Bob Can Help You Build

With these skills, Bob can assist you in creating:

### Terraform/OpenTofu Projects
1. **Cloud Infrastructure**: Multi-cloud infrastructure provisioning (AWS, Azure, GCP)
2. **Reusable Modules**: Well-structured, tested, and documented modules
3. **CI/CD Pipelines**: Automated testing and deployment workflows
4. **Security Policies**: Policy-as-code for compliance validation
5. **State Management**: Robust backend configurations and migration plans
6. **Testing Frameworks**: Comprehensive test suites for infrastructure code

### Ansible Projects
1. **Configuration Management**: Server configuration and application deployment
2. **Automation Playbooks**: Infrastructure automation and orchestration
3. **Role Libraries**: Reusable roles for common tasks
4. **Inventory Management**: Dynamic and static inventory configurations
5. **Migration Scripts**: Converting existing scripts to Ansible
6. **Troubleshooting Guides**: Systematic debugging procedures

## 📋 Prerequisites

To work with these skills effectively, you should have:

### For Terraform/OpenTofu
- Terraform 1.0+ or OpenTofu 1.6+ installed
- Cloud provider credentials (AWS, Azure, GCP, etc.)
- Basic understanding of infrastructure concepts
- Git for version control
- Bob AI assistant with skills support enabled

### For Ansible
- Ansible 2.9+ installed (2.15+ recommended)
- SSH access to target hosts
- Basic understanding of YAML syntax
- Python 3.6+ on control and managed nodes
- Bob AI assistant with skills support enabled

## 🔧 Key Technologies

These skills help you work with:

### Terraform/OpenTofu Stack
- **Terraform/OpenTofu**: Infrastructure as Code runtime
- **HCL**: HashiCorp Configuration Language
- **Terraform Cloud/Enterprise**: Collaboration platform
- **Atlantis**: Pull request automation
- **Terratest**: Go-based testing framework
- **TFLint**: Terraform linter
- **Trivy/Checkov**: Security scanners
- **OPA/Sentinel**: Policy-as-code engines

### Ansible Stack
- **Ansible Core**: Automation engine
- **Ansible Collections**: Reusable content packages
- **Jinja2**: Template engine
- **YAML**: Configuration language
- **Ansible Galaxy**: Role repository
- **Ansible Vault**: Secrets management
- **Molecule**: Testing framework
- **Ansible Lint**: Playbook linter

## 🔍 Skill Capabilities Summary

### Terraform/OpenTofu Skill

| Capability | Description |
|------------|-------------|
| **Failure Mode Diagnosis** | Systematic identification of 8 common IaC failure patterns |
| **Module Development** | 3-tier architecture with best practices and validation |
| **Testing Frameworks** | Static analysis, native tests, Terratest, mock providers |
| **CI/CD Integration** | GitHub Actions, GitLab CI, Atlantis automation |
| **Security & Compliance** | Scanning, secrets management, policy-as-code |
| **State Management** | Backend configuration, locking, migration, recovery |
| **Version Support** | Terraform 1.0+, OpenTofu 1.6+, version-aware guidance |
| **Progressive Disclosure** | Load detailed content only when needed |

### Ansible Skill

| Capability | Description |
|------------|-------------|
| **Playbook Development** | Create roles, playbooks, and inventory with best practices |
| **Script Conversion** | Transform bash scripts and Dockerfiles to Ansible |
| **Debugging** | Systematic troubleshooting of common Ansible errors |
| **Interactive Setup** | Step-by-step guidance for new projects and learning |
| **Idempotency** | Ensure operations can run multiple times safely |
| **FQCN Usage** | Fully qualified collection names for clarity |
| **Validation** | Test with --check --diff before execution |
| **Incremental Development** | Build and test one component at a time |

## 🐛 Troubleshooting

### Skills don't appear after installation
1. Verify the extraction path is correct (`.bob/skills/`)
2. Check file permissions on the extracted files
3. Restart Bob to refresh the skills list
4. Ensure you've enabled the Skills button in your current mode
5. Review Bob logs for any error messages

### Skill is active but Bob doesn't understand IaC requests
1. Be specific in your requests (mention "Terraform", "Ansible", or specific tools)
2. Reference specific features (e.g., "module development", "playbook conversion")
3. Provide context about what you're trying to accomplish
4. Ask Bob to explain the skill's capabilities if unsure

### Terraform-specific issues
- **Version compatibility**: Check minimum version requirements in responses
- **Provider errors**: Verify provider versions and credentials
- **State lock**: Follow state management guidance for unlock procedures
- **Module not found**: Check module source and version constraints

### Ansible-specific issues
- **Connection failures**: Verify SSH access and credentials
- **Module errors**: Check Ansible version and collection installation
- **Variable undefined**: Review variable precedence and scope
- **Syntax errors**: Validate YAML syntax and indentation

## 📚 Related Resources

### Terraform/OpenTofu
- [Terraform Documentation](https://www.terraform.io/docs)
- [OpenTofu Documentation](https://opentofu.org/docs)
- [Terraform Registry](https://registry.terraform.io/)
- [Terratest Documentation](https://terratest.gruntwork.io/)
- [Atlantis Documentation](https://www.runatlantis.io/)

### Ansible
- [Ansible Documentation](https://docs.ansible.com/)
- [Ansible Galaxy](https://galaxy.ansible.com/)
- [Ansible Collections](https://docs.ansible.com/ansible/latest/collections/index.html)
- [Molecule Documentation](https://molecule.readthedocs.io/)
- [Ansible Lint](https://ansible-lint.readthedocs.io/)

### Building Blocks
- [Parent Directory README](../README.md) - Complete building block documentation
- [IaC Best Practices](../assets/) - Reference implementations and examples

## 📊 Performance

Typical response times:

### Terraform/OpenTofu
- **Module Generation**: ~5-15 seconds (depends on complexity)
- **Code Review**: ~10-30 seconds (includes security scanning)
- **State Diagnosis**: ~3-10 seconds (failure mode identification)
- **CI/CD Template**: ~5-20 seconds (includes validation setup)
- **Migration Plan**: ~15-45 seconds (includes risk assessment)

### Ansible
- **Playbook Generation**: ~5-15 seconds (depends on complexity)
- **Script Conversion**: ~10-30 seconds (includes validation)
- **Debugging**: ~5-15 seconds (systematic diagnosis)
- **Interactive Setup**: ~20-60 seconds (step-by-step guidance)

## 💬 Support

For issues or questions about these skills:
1. Check the troubleshooting section above
2. Review the [parent directory README](../README.md) for detailed examples
3. Review each skill's README.md and supporting documentation
4. Ask Bob directly - the skills include comprehensive knowledge
5. Refer to official Terraform/Ansible documentation for tool-specific questions

## 📝 Version Information

### infrastructure-as-code-terraform
- **Skill Version**: 2.0.0
- **Compatible with**: Terraform 1.0+, OpenTofu 1.6+
- **Last Updated**: 2026-06-22
- **Status**: Production Ready ✅

### infrastructure-as-code-ansible
- **Skill Version**: 1.0.0
- **Compatible with**: Ansible 2.9+ (2.15+ recommended)
- **Last Updated**: 2026-06-22
- **Status**: Production Ready ✅

---

**Note**: These skills require appropriate tool installations (Terraform/OpenTofu and/or Ansible) and proper access credentials for target infrastructure. Ensure you have the necessary tools and permissions before starting.

Made with ❤️ for Infrastructure as Code practitioners