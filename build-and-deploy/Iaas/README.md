# 🏗️ Infrastructure as a Service (IaaS) Building Blocks

---

## 📑 Table of Contents

- [Overview](#overview)
- [What's Included](#whats-included)
- [Key Components](#key-components)
- [Getting Started](#getting-started)
- [Use Cases](#use-cases)
- [Architecture](#architecture)
- [Best Practices](#best-practices)
- [Related Resources](#related-resources)

---

## 🔗 Navigation

**Build & Deploy Building Blocks:**
- [← Back to Build & Deploy](../README.md)
- [iPaaS →](../ipaas/README.md)
- [Code Modernisation →](../code-modernisation/README.md)

**IaaS Assets:**
- [Ansible Deployment Guide →](assets/deploy-bob-anisble/README.md)
- [Retail Application →](assets/retailapp/README.md)

**Other Categories:**
- [Optimize](../../optimize/finops/README.md)
- [Secure](../../secure/quantum-safe/README.md)

---

## Overview

This building block provides **Infrastructure as Code (IaC)** solutions for deploying applications on **IBM Cloud** and **Red Hat OpenShift**. It includes production-ready Ansible automation, a full-stack retail demo application, and comprehensive deployment guides designed to be simple, reusable, and cost-safe.

### What You Get

✅ **Production-Ready Ansible Automation** - Multi-environment deployment for OpenShift  
✅ **Full-Stack Retail Application** - Complete demo app with frontend, backend, and database  
✅ **Terraform Best Practices** - IaC patterns for IBM Cloud  
✅ **Load Testing Framework** - JMeter-based spike testing  
✅ **Multi-Environment Support** - Development, Test, and Production configurations  
✅ **Comprehensive Documentation** - Quick starts, troubleshooting, and best practices

---

## What's Included

### 1. Ansible-Based Retail Application Deployment

Production-ready Ansible automation for deploying the Retail application on OpenShift clusters. Replaces script-based approaches with a robust, maintainable, and reusable solution.

**Location:** [`assets/deploy-bob-anisble/`](assets/deploy-bob-anisble/README.md)

**Features:**

#### 🚀 Deployment Automation
- **System Dependencies:** Automated installation of Podman, Java 11, OpenShift CLI, JMeter
- **Application Source:** GitHub repository cloning and validation
- **Container Images:** Build and push to Docker Hub (backend, frontend, PostgreSQL)
- **OpenShift Setup:** Cluster authentication, namespace creation, image pull secrets
- **Kubernetes Manifests:** Dynamic updates with environment-specific configurations
- **Application Deployment:** PostgreSQL, Backend, Frontend with services and routes
- **Database Seeding:** Automated seed data loading
- **Frontend Rebuild:** Dynamic backend route configuration

#### 🌍 Multi-Environment Support
| Feature | Development | Test | Production |
|---------|-------------|------|------------|
| Namespace | retail-dev | retail-test | retail-prod |
| Replicas | 1 | 2 | 3 |
| CPU Request | 50m | 100m | 200m |
| Memory Request | 64Mi | 128Mi | 256Mi |
| CPU Limit | 250m | 500m | 1000m |
| Memory Limit | 256Mi | 512Mi | 1Gi |
| Image Tag | 1.0.0-dev | 1.0.0-test | 1.0.0 |

#### 📦 Project Structure
```
deploy-bob-anisble/
├── ansible.cfg                      # Ansible configuration
├── README.md                        # Comprehensive documentation
├── QUICKSTART.md                    # Quick start guide
├── PROJECT_SUMMARY.md              # Project summary
├── Makefile                        # Convenience commands
├── inventories/                    # Multi-environment inventories
│   ├── development/hosts
│   ├── test/hosts
│   └── production/hosts
├── group_vars/                     # Environment-specific variables
│   ├── development.yml
│   ├── test.yml
│   └── production.yml
├── playbooks/                      # Ansible playbooks
│   ├── deploy.yml                  # Main deployment
│   ├── deploy-development.yml
│   ├── deploy-test.yml
│   └── deploy-production.yml
└── roles/                          # 8 Ansible roles
    ├── system_dependencies/        # Install dependencies
    ├── app_source/                 # Clone source code
    ├── container_images/           # Build and push images
    ├── openshift_setup/            # OpenShift authentication
    ├── k8s_manifests/              # Update manifests
    ├── app_deployment/             # Deploy application
    ├── database_seed/              # Load seed data
    └── frontend_rebuild/           # Rebuild frontend
```

**Quick Start:**
```bash
cd assets/deploy-bob-anisble

# Set environment variables
export OC_TOKEN="your-openshift-token"
export DOCKER_USERNAME="your-dockerhub-username"
export DOCKER_PASSWORD="your-dockerhub-password"

# Update configuration
nano group_vars/development.yml

# Deploy
ansible-playbook playbooks/deploy-development.yml
```

[📖 Full Documentation](assets/deploy-bob-anisble/README.md) | [⚡ Quick Start](assets/deploy-bob-anisble/QUICKSTART.md) | [📊 Project Summary](assets/deploy-bob-anisble/PROJECT_SUMMARY.md)

---

### 2. Retail Demo Application

A full-stack retail demo application built for deployment on IBM Cloud Red Hat OpenShift.

**Location:** [`assets/retailapp/`](assets/retailapp/README.md)

**Features:**

#### 🛒 Application Capabilities
- **Product Catalog:** Browsing with filters and sorting
- **User Authentication:** JWT-based with bcryptjs password hashing
- **Shopping Cart:** User-specific carts with multi-user support
- **Checkout Flow:** Inventory locking and stock decrement
- **Order History:** Per-user order tracking
- **Health Checks:** Readiness/liveness probes for backend and frontend

#### 🛠️ Technology Stack
- **Backend:** Node.js, Express, PostgreSQL (pg), bcryptjs, jsonwebtoken
- **Frontend:** React + Vite, Axios
- **Database:** PostgreSQL with full seed data
- **Container Runtime:** Podman
- **Registry:** Docker Hub

#### 📦 Project Structure
```
retailapp/
├── README.md                       # Application overview
├── deploy-steps.md                 # Manual deployment guide
├── deploy.sh                       # Automated deployment script
├── backend/                        # Node.js backend
│   ├── Dockerfile
│   ├── package.json
│   └── src/
│       ├── server.js
│       ├── db.js
│       └── features_1_2_3_4_14.js
├── frontend/                       # React frontend
│   ├── Dockerfile
│   ├── nginx.conf
│   ├── package.json
│   └── src/
│       ├── App.jsx
│       ├── api.js
│       ├── components/
│       └── pages/
├── postgresql/                     # Database
│   ├── Dockerfile
│   └── full_dump.sql              # Seed data
├── k8s/                           # Kubernetes manifests
│   ├── namespace.yaml
│   ├── postgres-*.yaml
│   ├── backend-*.yaml
│   ├── frontend-*.yaml
│   └── *-hpa.yaml                 # Horizontal Pod Autoscalers
└── jmeter/                        # Load testing
    ├── README.md
    ├── retail_spike.jmx
    ├── run_spike.sh
    └── users.csv
```

**Deployment Options:**
1. **Ansible (Recommended):** Use the [Ansible deployment guide](assets/deploy-bob-anisble/README.md)
2. **Manual Script:** Follow [deployment steps](assets/retailapp/deploy-steps.md)

[📖 Application Documentation](assets/retailapp/README.md) | [📋 Deployment Steps](assets/retailapp/deploy-steps.md)

---

### 3. JMeter Load Testing Framework

Spike test framework for the Retail application using Apache JMeter.

**Location:** [`assets/retailapp/jmeter/`](assets/retailapp/jmeter/README.md)

**Features:**

#### ⚡ Three-Phase Load Test
1. **Warm-up:** 20 users, 10s ramp-up, 1 loop
2. **Spike Load:** 300 users, 90s ramp-up, 80 loops (~5 minutes)
3. **Cool-down:** 40 users, 20s ramp-up, 1 loop

#### 🎯 APIs Tested
- Authentication: `/api/auth/login`, `/api/user/profile`
- Product & Catalog: `/api/catalog/products`, `/api/catalog/product/{id}`
- Cart Operations: `/api/cart/*`
- Checkout & Orders: `/api/checkout`, `/api/orders/*`
- Health Check: `/health`

**Quick Start:**
```bash
cd assets/retailapp/jmeter
./run_spike.sh <backend-route>
```

[📖 JMeter Documentation](assets/retailapp/jmeter/README.md)

---

## Key Components

### Ansible Automation Highlights

**8 Production-Ready Roles:**

1. **system_dependencies** (159 lines)
   - Installs Podman, Java 11, OpenShift CLI, JMeter
   - Version-specific installations
   - Idempotent operations

2. **app_source** (103 lines)
   - Clones application repository
   - Validates repository structure
   - Verifies Dockerfiles and seed data

3. **container_images** (103 lines)
   - Docker Hub authentication
   - Builds PostgreSQL, backend, frontend images
   - Pushes images with environment-specific tags

4. **openshift_setup** (125 lines)
   - OpenShift cluster login
   - Namespace creation/verification
   - Docker Hub secret management

5. **k8s_manifests** (157 lines)
   - Namespace replacement in manifests
   - Image reference updates
   - Resource limits configuration
   - Environment variable updates

6. **app_deployment** (218 lines)
   - PostgreSQL deployment with PVC
   - Backend/Frontend deployment with HPA
   - Service and Route creation
   - Readiness verification

7. **database_seed** (137 lines)
   - Seed file verification
   - Data copy to PostgreSQL pod
   - Database loading
   - Backend restart

8. **frontend_rebuild** (139 lines)
   - Backend URL configuration
   - Frontend image rebuild
   - Image push and deployment update

### Retail Application Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    User Browser                          │
│               https://frontend-route                     │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│              Frontend (React + Vite)                     │
│  - Product browsing                                      │
│  - Shopping cart                                         │
│  - User authentication                                   │
│  - Order management                                      │
└────────────────────────┬────────────────────────────────┘
                         │ HTTPS/REST API
                         ▼
┌─────────────────────────────────────────────────────────┐
│              Backend (Node.js + Express)                 │
│  - JWT authentication                                    │
│  - Business logic                                        │
│  - API endpoints                                         │
│  - Database queries                                      │
└────────────────────────┬────────────────────────────────┘
                         │ PostgreSQL Protocol
                         ▼
┌─────────────────────────────────────────────────────────┐
│              PostgreSQL Database                         │
│  - User data                                             │
│  - Product catalog                                       │
│  - Orders and carts                                      │
│  - Inventory management                                  │
└─────────────────────────────────────────────────────────┘
```

---

## Getting Started

### Prerequisites

**System Requirements:**
- RHEL/CentOS/Fedora-based system (for Ansible automation)
- Root or sudo access
- Internet connectivity

**Required Credentials:**
1. **OpenShift Cluster Access:**
   - Cluster URL
   - Authentication token with appropriate permissions

2. **Docker Hub Account:**
   - Username
   - Password or access token

### Quick Setup - Ansible Deployment

1. **Navigate to Ansible directory:**
   ```bash
   cd build-and-deploy/Iaas/assets/deploy-bob-anisble
   ```

2. **Set environment variables:**
   ```bash
   export OC_TOKEN="sha256~your-token-here"
   export DOCKER_USERNAME="your-dockerhub-username"
   export DOCKER_PASSWORD="your-dockerhub-password"
   ```

3. **Update configuration:**
   ```bash
   nano group_vars/development.yml
   ```
   
   Update:
   ```yaml
   openshift_server: "https://api.your-cluster.example.com:6443"
   namespace: retail-dev
   ```

4. **Run deployment:**
   ```bash
   ansible-playbook playbooks/deploy-development.yml
   ```

5. **Access application:**
   ```bash
   # Get frontend URL
   oc get route retail-frontend -n retail-dev
   
   # Open in browser
   https://retail-frontend-retail-dev.apps.your-cluster.example.com
   ```

**Deployment Time:** Approximately 10-15 minutes for first-time deployment

---

## Use Cases

### 1. Development Environment Setup

**Scenario:** Set up a complete development environment for the retail application

**Workflow:**
1. Deploy using Ansible to development namespace
2. Configure with minimal resources (1 replica, 50m CPU)
3. Use for feature development and testing
4. Iterate quickly with automated deployments

**Benefits:**
- Consistent development environment
- Quick setup and teardown
- Cost-effective resource usage

### 2. Multi-Environment CI/CD Pipeline

**Scenario:** Implement a complete CI/CD pipeline with dev, test, and production environments

**Workflow:**
1. **Development:**
   - Deploy to `retail-dev` namespace
   - Run unit and integration tests
   - Validate new features

2. **Test:**
   - Promote to `retail-test` namespace
   - Run JMeter load tests
   - Perform UAT

3. **Production:**
   - Deploy to `retail-prod` namespace
   - Use production-grade resources (3 replicas, higher limits)
   - Monitor with Instana

**Benefits:**
- Automated promotion between environments
- Consistent deployment process
- Risk mitigation through staged rollout

### 3. Performance Testing and Optimization

**Scenario:** Test application performance under load and optimize

**Workflow:**
1. Deploy application to test environment
2. Run JMeter spike tests:
   ```bash
   cd assets/retailapp/jmeter
   ./run_spike.sh <backend-route>
   ```
3. Monitor application performance
4. Analyze results and optimize:
   - Adjust HPA settings
   - Tune resource limits
   - Optimize database queries
5. Re-test and validate improvements

**Benefits:**
- Identify performance bottlenecks
- Validate scalability
- Optimize resource utilization

### 4. Disaster Recovery Testing

**Scenario:** Test disaster recovery procedures

**Workflow:**
1. Deploy application to production
2. Simulate failures:
   - Delete pods
   - Scale down replicas
   - Introduce network issues
3. Verify automatic recovery:
   - HPA scaling
   - Pod restart
   - Service continuity
4. Document recovery procedures

**Benefits:**
- Validate resilience
- Test recovery automation
- Build confidence in production deployment

---

## Architecture

### Deployment Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  Developer Workstation                   │
│                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │   Ansible    │  │   Terraform  │  │   Scripts    │ │
│  │  Playbooks   │  │   Configs    │  │              │ │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘ │
└─────────┼──────────────────┼──────────────────┼─────────┘
          │                  │                  │
          └──────────────────┴──────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────┐
│              IBM Cloud / Red Hat OpenShift               │
│                                                          │
│  ┌────────────────────────────────────────────────────┐ │
│  │              Namespace: retail-dev/test/prod       │ │
│  │                                                    │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌─────────┐ │ │
│  │  │  PostgreSQL  │  │   Backend    │  │Frontend │ │ │
│  │  │  - PVC       │  │  - Deployment│  │- Deploy │ │ │
│  │  │  - Service   │  │  - Service   │  │- Service│ │ │
│  │  │              │  │  - Route     │  │- Route  │ │ │
│  │  │              │  │  - HPA       │  │- HPA    │ │ │
│  │  └──────────────┘  └──────────────┘  └─────────┘ │ │
│  │                                                    │ │
│  └────────────────────────────────────────────────────┘ │
│                                                          │
│  ┌────────────────────────────────────────────────────┐ │
│  │              Container Registry                     │ │
│  │  - Docker Hub (public images)                      │ │
│  │  - Image pull secrets                              │ │
│  └────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

---

## Best Practices

### 1. Infrastructure as Code

**Terraform Best Practices:**
- Keep code simple and readable
- Use clear naming conventions
- Add comments explaining each block
- Structure into reusable modules
- Use variables with sensible defaults
- Output important information (IPs, URLs)
- Tag resources for cost tracking

**Example Structure:**
```
terraform-ibm-demo/
├── main.tf               # Root module
├── variables.tf          # Input variables
├── outputs.tf            # Outputs
├── providers.tf          # Provider config
└── modules/
    ├── network/          # VPC, subnets, SGs
    ├── compute/          # VSI resources
    └── storage/          # Object Storage
```

### 2. Ansible Automation

**Deployment Best Practices:**
- Use idempotent operations
- Implement comprehensive error handling
- Log all operations
- Use tags for selective execution
- Maintain separate inventories per environment
- Version control all configurations
- Test in development before production

**Using Tags:**
```bash
# Only install dependencies
ansible-playbook playbooks/deploy-development.yml --tags dependencies

# Only build and push images
ansible-playbook playbooks/deploy-development.yml --tags images

# Skip database seeding
ansible-playbook playbooks/deploy-development.yml --skip-tags seed
```

### 3. Multi-Environment Management

**Configuration Strategy:**
- Use environment-specific variable files
- Maintain separate namespaces per environment
- Scale resources appropriately per environment
- Use different image tags (dev, test, prod)
- Implement environment-specific secrets

**Environment Progression:**
1. Development → Test → Production
2. Validate at each stage
3. Automate promotion process
4. Maintain rollback capability

### 4. Security

**Best Practices:**
- Never commit credentials to Git
- Use environment variables for secrets
- Rotate API keys regularly
- Implement RBAC in OpenShift
- Use image pull secrets
- Enable pod security policies
- Regular security scanning

### 5. Monitoring and Observability

**Integration:**
- Deploy monitoring agents for application observability
- Configure health checks (readiness/liveness)
- Set up logging aggregation
- Implement distributed tracing
- Monitor resource utilization
- Set up alerting

### 6. Cost Optimization

**Strategies:**
- Use appropriate resource limits
- Implement HPA for auto-scaling
- Use spot instances where applicable
- Tag resources for cost tracking
- Regular cleanup of unused resources
- Monitor with [FinOps tools](../../optimize/finops/README.md)

---

## 📚 Related Resources

### IaaS Assets & Guides
- [Ansible Deployment for Retail App](assets/deploy-bob-anisble/README.md) - Production-ready automation
  - [Quick Start Guide](assets/deploy-bob-anisble/QUICKSTART.md)
  - [Project Summary](assets/deploy-bob-anisble/PROJECT_SUMMARY.md)
- [Retail Application](assets/retailapp/README.md) - Full-stack demo application
  - [Deployment Steps](assets/retailapp/deploy-steps.md)
  - [JMeter Load Testing](assets/retailapp/jmeter/README.md)

### Build & Deploy Building Blocks
- [Integration Platform as a Service (iPaaS)](../ipaas/README.md) - Integration workflows
- [Code Modernisation](../code-modernisation/README.md) - Middleware modernization

### Optimize Building Blocks
- [Automated Resilience](../../optimize/automated-resilience-and-compliance/README.md) - IBM Concert insights
  - [Dashboard](../../optimize/automated-resilience-and-compliance/assets/automate-resilience/README.md)
- [FinOps](../../optimize/finops/README.md) - Cost optimization with IBM Turbonomic
- [Automated Resource Management](../../optimize/automated-resource-mgmt/README.md) - IBM Turbonomic

### Secure Building Blocks
- [Non-Human Identity](../../secure/non-human-identity/README.md) - IBM Security Verify
- [Quantum-Safe](../../secure/quantum-safe/README.md) - IBM Guardium Crypto Manager

---

## Support & Troubleshooting

### Common Issues

**Authentication Failures:**
- Verify `OC_TOKEN` is valid and not expired
- Check OpenShift cluster accessibility
- Ensure proper permissions

**Image Push Failures:**
- Verify Docker Hub credentials
- Check repository exists and has push permissions
- Try manual login: `podman login docker.io`

**Pod Not Starting:**
- Check pod logs: `oc logs <pod-name> -n <namespace>`
- Verify image pull secret: `oc get secret dockerhub-secret -n <namespace>`
- Check resource quotas: `oc describe quota -n <namespace>`

**Database Connection Issues:**
- Verify PostgreSQL pod is running
- Check service: `oc get svc retail-postgres -n <namespace>`
- Review backend logs for connection errors

### Getting Help

- **Ansible Issues:** Check [Ansible README](assets/deploy-bob-anisble/README.md) troubleshooting section
- **Application Issues:** Review [Retail App README](assets/retailapp/README.md)
- **Load Testing:** See [JMeter README](assets/retailapp/jmeter/README.md)
- **Logs:** Check `oc logs` for pod-specific issues

---

**[⬆ Back to Top](#️-infrastructure-as-a-service-iaas-building-blocks)**
