# 🛒 Retail Demo Application

---

## 🔗 Navigation

**Parent:**
- [← Back to IaaS Building Blocks](../../README.md)
- [Ansible Deployment Guide →](../deploy-bob-anisble/README.md)

**Documentation:**
- [Deployment Steps →](deploy-steps.md)
- [JMeter Load Testing →](jmeter/README.md)

**Other Building Blocks:**
- [Application Observability](../../../../../observe/application-observability/README.md)
- [Automated Resilience](../../../../../optimize/automated-resilience-and-compliance/assets/automate-resilience/README.md)

---

## 📋 Overview

This is a full-stack retail demo application built for deployment on IBM Cloud Red Hat OpenShift.

## ✨ Features
- Product catalog browsing with filters and sorting
- User authentication (JWT-based) with bcryptjs password hashing
- User-specific carts (multi-user support)
- Checkout flow with inventory locking and stock decrement in the database
- Orders history (per user)
- PostgreSQL database
- NGINX-based production frontend container
- Health checks (readiness/liveness) for backend and frontend
- OpenShift-ready Kubernetes manifests

## 🛠️ Technology Stack
- Backend: Node.js, Express, PostgreSQL (pg), bcryptjs, jsonwebtoken
- Frontend: React + Vite, Axios
- DB: PostgreSQL
- Container runtime: podman
- Registry: docker.io/sunilmanika

See [`deploy-steps.md`](deploy-steps.md) for deployment steps on OpenShift.

---

## 📚 Related Resources

### Deployment Guides
- [Deployment Steps](deploy-steps.md) - Manual deployment guide
- [Ansible Deployment](../deploy-bob-anisble/README.md) - Automated deployment with Ansible
  - [Quick Start](../deploy-bob-anisble/QUICKSTART.md)
  - [Project Summary](../deploy-bob-anisble/PROJECT_SUMMARY.md)

### Testing
- [JMeter Load Testing](jmeter/README.md) - Performance testing guide

### Building Blocks
- [IaaS Overview](../../README.md)
- [Application Observability](../../../../../observe/application-observability/README.md) - Monitor with Instana
- [Automated Resilience](../../../../../optimize/automated-resilience-and-compliance/assets/automate-resilience/README.md)

---

**[⬆ Back to Top](#-retail-demo-application)**
