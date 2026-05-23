# Data Streaming Bob Skills

This directory contains Bob skills for Automated Resource Management using IBM Turbonomic.

## Available Skill

The `automated-resource-mgmt-turbonomic.zip` file contains the following skill:

### data-streaming-confluent
A comprehensive skill for working with Confluent Kafka, providing capabilities for:
1. 🎨 Enterprise UI with IBM Carbon Design System v11
Build accessible, production-ready interfaces with IBM's design system - includes 200+ components, WCAG 2.1 AA compliance, responsive grids, and data visualization charts.

2. 🔐 Secure Node.js/Express Backend APIs
Create enterprise-grade REST APIs with built-in security (Helmet, rate limiting, input validation), proxy patterns, centralized error handling, and health checks.

3. ☸️ Kubernetes/OpenShift Production Deployment
Deploy containerized apps with multi-stage Docker builds, non-root containers, resource limits, health probes, ConfigMaps, and horizontal scaling.

4. 🤖 Ansible Deployment Automation
Automate infrastructure with role-based playbooks, variable management, Kubernetes provisioning, and automated deployment verification.

5. 🧪 Comprehensive Testing (80%+ Coverage)
Implement full testing pyramid: Jest unit tests, React Testing Library, Supertest API tests, Cypress E2E, with CI/CD integration and TDD practices.


## Installation and Setup

### Step 1: Download the Skill
Download the `automated-resource-mgmt-turbonomic.zip` file from this directory.

### Step 2: Extract the Skill to Bob Workspace
Extract the contents of `automated-resource-mgmt-turbonomic.zip` to your Bob workspace skills directory:

```bash
# Navigate to your Bob workspace skills directory
cd /path/to/your/bob/workspace/.bob/skills

# Extract the skill
unzip /path/to/automated-resource-mgmt-turbonomic.zip
```

After extraction, you should see a `automated-resource-mgmt-turbonomic` folder in your `.bob/skills` directory.

### Step 3: Verify Installation
Check that the skill is properly installed:

```bash
ls -la .bob/skills/automated-resource-mgmt-turbonomic
```

You should see the skill files and configuration.

### Step 4: Activate the Skill
To use the skill:
1. Open Bob and select any mode you want to work in
2. Enable the **Skills** button in that mode
3. The `automated-resource-mgmt-turbonomic` skill will be available for use within that mode


## Troubleshooting

If the skill doesn't appear after installation:
1. Verify the extraction path is correct (`.bob/skills/`)
2. Check file permissions
3. Restart Bob to refresh the skills list
4. Ensure you've enabled the Skills button in your current mode
5. Review Bob logs for any error messages

## Support

For issues or questions about this skill, please refer to the main documentation or contact your administrator.