# Turbonomic Resource Dashboard - Skills Documentation

## Overview

This directory contains comprehensive skills and guidelines for developing, maintaining, and deploying the Turbonomic Resource Dashboard. The documentation is organized into five comprehensive guides covering all aspects of the application.

---

## 📚 Available Guides

### 1. [Frontend Development Guide](./frontend-guide.md)
**Comprehensive frontend development covering React, Carbon Design System, UI/UX, styling, and content**

**Topics Covered:**
- **React Development** - React 18, hooks, state management, performance optimization
- **Carbon Design System** - IBM Carbon v11, components, design tokens, grid system
- **UI/UX Standards** - Design principles, layout standards, accessibility (WCAG 2.1)
- **Styling Patterns** - CSS architecture, color palette, typography, reusable patterns
- **Content Guidelines** - Writing standards, voice & tone, terminology

**When to Use:** Building or modifying frontend components, implementing UI designs, ensuring design consistency, writing user-facing content

**Size:** 1,337 lines | **Consolidates:** 6 previous skills

---

### 2. [Backend Development Guide](./backend-guide.md)
**Comprehensive backend development covering Node.js, Express, API design, and Turbonomic integration**

**Topics Covered:**
- **Server Architecture** - Express setup, middleware, application structure
- **API Design** - RESTful patterns, routing, validation, response formatting
- **Turbonomic Integration** - Proxy architecture, API client, authentication
- **Error Handling** - Centralized handlers, custom errors, async patterns
- **Security** - Input sanitization, rate limiting, secure practices
- **Performance** - Caching, compression, connection pooling, monitoring

**When to Use:** Developing backend APIs, integrating external services, implementing middleware, optimizing server performance

**Size:** 1,087 lines | **Consolidates:** 2 previous skills

---

### 3. [DevOps & Deployment Guide](./devops-guide.md)
**Comprehensive DevOps covering Docker, Kubernetes/OpenShift, Ansible automation, and CI/CD**

**Topics Covered:**
- **Docker Containerization** - Multi-stage builds, Dockerfiles, Nginx configuration
- **Kubernetes/OpenShift** - Deployments, services, ConfigMaps, secrets, routes
- **Ansible Automation** - Playbooks, roles, variable management, deployment workflow
- **CI/CD Pipeline** - GitHub Actions, automated deployments, environment configuration
- **Production** - Health checks, monitoring, security, troubleshooting

**When to Use:** Deploying applications, creating container images, automating infrastructure, setting up CI/CD pipelines

**Size:** 1,087 lines | **Consolidates:** 3 previous skills

---

### 4. [Testing Standards](./testing-standards.md)
**Comprehensive testing strategies covering unit, integration, and end-to-end testing**

**Topics Covered:**
- **Testing Philosophy** - Testing pyramid, principles, best practices
- **Unit Testing** - Jest, React Testing Library, component tests
- **Integration Testing** - API testing, MSW for mocking, service integration
- **End-to-End Testing** - Cypress, user workflows, visual testing
- **CI/CD Integration** - Automated testing, coverage requirements, quality gates

**When to Use:** Writing tests, setting up testing infrastructure, ensuring code quality through automated testing

**Size:** 724 lines | **Standalone guide**
### 5. [Troubleshooting Guide](./troubleshooting-guide.md)
**Common issues and solutions for Carbon Design System v11 and application setup**

**Topics Covered:**
- **Carbon CSS Import Errors** - Fixing path and package issues
- **Component Import Issues** - Stack, PasswordInput, and other v11 changes
- **Package Dependencies** - Correct Carbon v11 setup
- **Styling Problems** - CSS loading and CDN configuration
- **Quick Fix Checklist** - Step-by-step debugging guide

**When to Use:** Encountering build errors, styling issues, or component import problems

**Size:** 289 lines | **New guide**

---

---

## 🚀 Quick Start

### For New Developers
1. Start with [Frontend Guide](./frontend-guide.md) - Part 1 (React Development)
2. Review [Backend Guide](./backend-guide.md) - Part 1 (Server Architecture)
3. Read [Testing Standards](./testing-standards.md) for quality assurance
4. Check [DevOps Guide](./devops-guide.md) when ready to deploy

### For Frontend Work
1. [Frontend Guide](./frontend-guide.md) - Complete reference
   - Part 1: React Development
   - Part 2: Carbon Design System
   - Part 3: UI/UX Standards
   - Part 4: Styling Patterns
   - Part 5: Content Guidelines

### For Backend Work
1. [Backend Guide](./backend-guide.md) - Complete reference
   - Part 1: Server Architecture & Setup
   - Part 2: API Design & Routing
   - Part 3: Turbonomic Integration
   - Part 4: Error Handling & Security
   - Part 5: Performance & Monitoring

### For DevOps/Deployment
1. [DevOps Guide](./devops-guide.md) - Complete reference
   - Part 1: Docker Containerization
   - Part 2: Kubernetes/OpenShift
   - Part 3: Ansible Automation
   - Part 4: CI/CD & Production

---

## 📊 Documentation Structure

```
.bob/skills/
├── README.md                    # This file - Overview and navigation
├── frontend-guide.md            # Complete frontend development guide
├── backend-guide.md             # Complete backend development guide
├── devops-guide.md              # Complete DevOps and deployment guide
├── testing-standards.md         # Complete testing standards guide
└── troubleshooting-guide.md     # Common issues and solutions
```

### Guide Relationships

```
┌─────────────────────────────────────────────────────────┐
│              Frontend Development Guide                  │
│  React • Carbon • UI/UX • Styling • Content             │
└────────────────┬────────────────────────────────────────┘
                 │
                 ├──> User Interface
                 │
┌────────────────▼────────────────────────────────────────┐
│              Backend Development Guide                   │
│  Node.js • Express • API • Turbonomic • Security        │
└────────────────┬────────────────────────────────────────┘
                 │
                 ├──> Application Logic
                 │
┌────────────────▼────────────────────────────────────────┐
│              DevOps & Deployment Guide                   │
│  Docker • Kubernetes • Ansible • CI/CD                  │
└────────────────┬────────────────────────────────────────┘
                 │
                 ├──> Infrastructure
                 │
┌────────────────▼────────────────────────────────────────┐
│              Testing Standards                           │
│  Unit • Integration • E2E • Quality Assurance           │
└─────────────────────────────────────────────────────────┘
```

---

## 🎯 Finding What You Need

### By Technology

| Technology | Guide | Section |
|------------|-------|---------|
| React 18 | Frontend Guide | Part 1 |
| Carbon Design System | Frontend Guide | Part 2 |
| CSS/Styling | Frontend Guide | Part 4 |
| Node.js/Express | Backend Guide | Part 1 |
| API Design | Backend Guide | Part 2 |
| Turbonomic API | Backend Guide | Part 3 |
| Docker | DevOps Guide | Part 1 |
| Kubernetes | DevOps Guide | Part 2 |
| Ansible | DevOps Guide | Part 3 |
| Jest/Testing | Testing Standards | All |

### By Task

| Task | Primary Guide | Supporting Guides |
|------|---------------|-------------------|
| Create new component | Frontend Guide (Part 1) | Frontend Guide (Part 2-3) |
| Style component | Frontend Guide (Part 4) | Frontend Guide (Part 2) |
| Write UI text | Frontend Guide (Part 5) | - |
| Create API endpoint | Backend Guide (Part 2) | Backend Guide (Part 1) |
| Integrate Turbonomic | Backend Guide (Part 3) | Backend Guide (Part 4) |
| Secure backend | Backend Guide (Part 4) | - |
| Build Docker image | DevOps Guide (Part 1) | - |
| Deploy to K8s | DevOps Guide (Part 2) | DevOps Guide (Part 3) |
| Automate deployment | DevOps Guide (Part 3) | DevOps Guide (Part 4) |
| Write tests | Testing Standards | All Guides |

---

## 📖 Guide Features

Each comprehensive guide includes:

✅ **Table of Contents** - Easy navigation to specific topics  
✅ **Code Examples** - Real-world, tested code samples  
✅ **Best Practices** - DO ✅ and DON'T ❌ lists  
✅ **Architecture Diagrams** - Visual representations  
✅ **Step-by-Step Instructions** - Clear, actionable guidance  
✅ **Troubleshooting** - Common issues and solutions  
✅ **External Resources** - Links to official documentation  

---

## 🔄 Version History

### v2.0.0 (2026-05-22) - Consolidated Documentation
- **Consolidated 12 separate skills into 4 comprehensive guides**
- Reduced file count from 13 to 5 files (including README)
- Maintained all content with improved organization
- Added comprehensive table of contents to each guide
- Enhanced cross-referencing between guides
- Improved searchability and navigation

**Guides Created:**
- Frontend Development Guide (1,337 lines)
- Backend Development Guide (1,087 lines)
- DevOps & Deployment Guide (1,087 lines)
- Testing Standards (724 lines - kept as standalone)

### v1.1.0 (2026-05-22) - Technology-Specific Skills
- Added Ansible Automation
- Added Kubernetes/OpenShift
- Added React Frontend
- Added Node.js Backend

### v1.0.0 (2024-01-15) - Initial Documentation
- Frontend Development
- Carbon Design System
- UI/UX Standards
- Styling Patterns
- Content Guidelines
- API Integration
- Deployment Guidelines
- Testing Standards

---

## 💡 Tips for Using This Documentation

### Search Efficiently
- Use your editor's search (Cmd/Ctrl+F) within guides
- Search for specific technologies, patterns, or concepts
- Check the table of contents in each guide first

### Navigate Quickly
- Use the guide relationships diagram to understand dependencies
- Start with the overview section of each guide
- Jump to specific parts using the table of contents

### Stay Updated
- Check the version history for recent changes
- Review best practices sections regularly
- Refer to external resources for latest updates

### Contribute
When updating documentation:
1. Maintain consistent structure and format
2. Include code examples for new patterns
3. Update cross-references between guides
4. Add to best practices sections
5. Update version history

---

## 📞 Support

For questions or clarifications:
1. Review the specific guide thoroughly
2. Check related guides for additional context
3. Consult external resources linked in each guide
4. Review the actual codebase for implementation examples

---

## 📈 Documentation Statistics

| Metric | Value |
|--------|-------|
| Total Guides | 4 comprehensive + 1 README |
| Total Lines | ~4,235 lines |
| Topics Covered | 60+ major topics |
| Code Examples | 200+ examples |
| Best Practices | 100+ guidelines |
| Reduction | From 13 files to 5 files (62% reduction) |

---

**Comprehensive Skills Documentation for Turbonomic Resource Dashboard**  
**Last Updated:** 2026-05-22 | **Version:** 2.0.0 | **Maintainer:** Operations Dashboard Team