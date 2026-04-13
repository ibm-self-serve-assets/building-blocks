# 12-Factor App Compliance Review Skill

## Purpose
Evaluate compliance with 12-factor app methodology and provide cloud-native recommendations.

## Expertise Areas
- Cloud-native architecture principles
- Container orchestration (Kubernetes, Docker)
- Configuration management
- Stateless application design
- Microservices deployment
- DevOps and CI/CD practices
- Cloud platforms (AWS, Azure, GCP)
- Infrastructure as Code
- Observability and monitoring

## The 12 Factors

### I. Codebase
**Principle**: One codebase tracked in revision control, many deploys

**Review Checklist**
- [ ] Is there a single codebase in version control (Git)?
- [ ] Are there multiple deployments from the same codebase?
- [ ] Is the codebase shared across environments?
- [ ] Are environment-specific configs excluded from codebase?
- [ ] Is there proper branching strategy?

**Common Issues**
- ❌ Multiple codebases for different environments
- ❌ Environment-specific code branches
- ❌ Configuration in codebase
- ❌ No version control

**Best Practices**
- ✅ Single Git repository
- ✅ Feature branches for development
- ✅ Tags for releases
- ✅ Same codebase for all environments

### II. Dependencies
**Principle**: Explicitly declare and isolate dependencies

**Review Checklist**
- [ ] Are all dependencies explicitly declared?
- [ ] Is there a dependency manifest (package.json, requirements.txt, pom.xml)?
- [ ] Are dependency versions pinned?
- [ ] Is there dependency isolation (virtual environments, containers)?
- [ ] Are system dependencies documented?

**Common Issues**
- ❌ Implicit system dependencies
- ❌ Unpinned dependency versions
- ❌ Global dependency installation
- ❌ Missing dependency documentation

**Best Practices**
- ✅ Use package managers (npm, pip, maven)
- ✅ Lock files (package-lock.json, Pipfile.lock)
- ✅ Container images with dependencies
- ✅ Dependency vulnerability scanning

### III. Config
**Principle**: Store config in the environment

**Review Checklist**
- [ ] Is configuration stored in environment variables?
- [ ] Are secrets excluded from codebase?
- [ ] Is there different config for each environment?
- [ ] Is configuration validated at startup?
- [ ] Are there no hardcoded values?

**Common Issues**
- ❌ Configuration in code
- ❌ Secrets in version control
- ❌ Environment-specific config files in codebase
- ❌ Hardcoded URLs, credentials

**Best Practices**
- ✅ Environment variables for config
- ✅ Secret management (Vault, AWS Secrets Manager)
- ✅ Configuration validation
- ✅ Default values for non-sensitive config

### IV. Backing Services
**Principle**: Treat backing services as attached resources

**Review Checklist**
- [ ] Are backing services accessed via URLs/connection strings?
- [ ] Can backing services be swapped without code changes?
- [ ] Are backing services configured via environment?
- [ ] Is there no distinction between local and third-party services?
- [ ] Are connections properly managed?

**Common Issues**
- ❌ Hardcoded database connections
- ❌ Different code for different backing services
- ❌ Tight coupling to specific services
- ❌ No connection pooling

**Best Practices**
- ✅ Connection strings in environment variables
- ✅ Service abstraction layers
- ✅ Connection pooling
- ✅ Graceful degradation

### V. Build, Release, Run
**Principle**: Strictly separate build and run stages

**Review Checklist**
- [ ] Is there a clear build stage?
- [ ] Is there a release stage combining build + config?
- [ ] Is there a run stage executing the release?
- [ ] Are releases immutable and versioned?
- [ ] Can releases be rolled back?

**Common Issues**
- ❌ Building in production
- ❌ Modifying code at runtime
- ❌ No release versioning
- ❌ Manual deployment steps

**Best Practices**
- ✅ CI/CD pipeline
- ✅ Immutable artifacts (Docker images)
- ✅ Release tagging
- ✅ Automated deployments

### VI. Processes
**Principle**: Execute the app as one or more stateless processes

**Review Checklist**
- [ ] Are processes stateless?
- [ ] Is session state stored in backing services?
- [ ] Can processes be killed and restarted?
- [ ] Is there no local file system dependency?
- [ ] Are processes share-nothing?

**Common Issues**
- ❌ In-memory session storage
- ❌ Local file storage
- ❌ Sticky sessions required
- ❌ Process-specific state

**Best Practices**
- ✅ Stateless application design
- ✅ External session storage (Redis)
- ✅ Object storage for files (S3)
- ✅ Horizontal scalability

### VII. Port Binding
**Principle**: Export services via port binding

**Review Checklist**
- [ ] Does the app bind to a port?
- [ ] Is the port configurable?
- [ ] Is the app self-contained?
- [ ] Does the app not rely on a web server?
- [ ] Can the app be a backing service for another app?

**Common Issues**
- ❌ Dependency on external web server
- ❌ Hardcoded ports
- ❌ Not self-contained
- ❌ Cannot run standalone

**Best Practices**
- ✅ Embedded web server
- ✅ Port from environment variable
- ✅ Self-contained application
- ✅ HTTP/gRPC service exposure

### VIII. Concurrency
**Principle**: Scale out via the process model

**Review Checklist**
- [ ] Can the app scale horizontally?
- [ ] Are different workloads handled by different process types?
- [ ] Is there no daemon or background process?
- [ ] Can processes be added/removed dynamically?
- [ ] Is there proper process management?

**Common Issues**
- ❌ Only vertical scaling
- ❌ Single-threaded bottlenecks
- ❌ Background daemons
- ❌ No process type separation

**Best Practices**
- ✅ Horizontal scaling
- ✅ Process types (web, worker, scheduler)
- ✅ Container orchestration
- ✅ Auto-scaling policies

### IX. Disposability
**Principle**: Maximize robustness with fast startup and graceful shutdown

**Review Checklist**
- [ ] Does the app start quickly (<1 minute)?
- [ ] Does the app handle SIGTERM gracefully?
- [ ] Are in-flight requests completed on shutdown?
- [ ] Can the app be killed without data loss?
- [ ] Is the app resilient to sudden termination?

**Common Issues**
- ❌ Slow startup times
- ❌ No graceful shutdown
- ❌ Data loss on termination
- ❌ Long-running transactions

**Best Practices**
- ✅ Fast startup (<30 seconds)
- ✅ Graceful shutdown handlers
- ✅ Request draining
- ✅ Idempotent operations

### X. Dev/Prod Parity
**Principle**: Keep development, staging, and production as similar as possible

**Review Checklist**
- [ ] Are environments similar?
- [ ] Is the same backing service used across environments?
- [ ] Is deployment frequency high?
- [ ] Is the time gap between dev and prod small?
- [ ] Are the same tools used across environments?

**Common Issues**
- ❌ Different databases in dev vs. prod
- ❌ Long deployment cycles
- ❌ Different tools/versions
- ❌ Manual processes in production

**Best Practices**
- ✅ Containerization (Docker)
- ✅ Infrastructure as Code
- ✅ Continuous deployment
- ✅ Same backing services

### XI. Logs
**Principle**: Treat logs as event streams

**Review Checklist**
- [ ] Does the app write logs to stdout/stderr?
- [ ] Are logs not managed by the app?
- [ ] Is there structured logging?
- [ ] Are logs aggregated centrally?
- [ ] Is there no log rotation in the app?

**Common Issues**
- ❌ Writing to log files
- ❌ Log rotation in app
- ❌ Unstructured logs
- ❌ No centralized logging

**Best Practices**
- ✅ Stdout/stderr logging
- ✅ Structured logs (JSON)
- ✅ Log aggregation (ELK, Splunk)
- ✅ Correlation IDs

### XII. Admin Processes
**Principle**: Run admin/management tasks as one-off processes

**Review Checklist**
- [ ] Are admin tasks run as one-off processes?
- [ ] Do admin tasks use the same codebase?
- [ ] Do admin tasks use the same config?
- [ ] Are admin tasks idempotent?
- [ ] Is there no separate admin interface?

**Common Issues**
- ❌ Admin tasks in separate codebase
- ❌ Direct database access for admin tasks
- ❌ Manual admin procedures
- ❌ No audit trail for admin tasks

**Best Practices**
- ✅ CLI commands in codebase
- ✅ Database migrations as code
- ✅ Kubernetes Jobs for one-off tasks
- ✅ Audit logging for admin tasks

## Output Format

### Factor Compliance Table
| Factor | Status | Score | Notes |
|--------|--------|-------|-------|
| I. Codebase | ✅/⚠️/❌ | [0-10] | [specific findings] |
| II. Dependencies | ✅/⚠️/❌ | [0-10] | [specific findings] |
| III. Config | ✅/⚠️/❌ | [0-10] | [specific findings] |
| IV. Backing Services | ✅/⚠️/❌ | [0-10] | [specific findings] |
| V. Build, Release, Run | ✅/⚠️/❌ | [0-10] | [specific findings] |
| VI. Processes | ✅/⚠️/❌ | [0-10] | [specific findings] |
| VII. Port Binding | ✅/⚠️/❌ | [0-10] | [specific findings] |
| VIII. Concurrency | ✅/⚠️/❌ | [0-10] | [specific findings] |
| IX. Disposability | ✅/⚠️/❌ | [0-10] | [specific findings] |
| X. Dev/Prod Parity | ✅/⚠️/❌ | [0-10] | [specific findings] |
| XI. Logs | ✅/⚠️/❌ | [0-10] | [specific findings] |
| XII. Admin Processes | ✅/⚠️/❌ | [0-10] | [specific findings] |
| **Overall Score** | | **[0-120]** | **[percentage]%** |

### ✅ Compliant Factors
List factors that are fully compliant with explanations

### ⚠️ Partially Compliant Factors
List factors that need improvement with specific issues

### ❌ Non-Compliant Factors
List factors that are not compliant with critical gaps

### 💡 Recommendations
For each non-compliant or partially compliant factor:
- **Factor**: Factor name and number
- **Current State**: What's currently implemented
- **Gap**: What's missing or incorrect
- **Required Changes**: Specific actions to achieve compliance
- **Priority**: Critical/High/Medium/Low
- **Effort**: Implementation complexity
- **Benefits**: Cloud-native advantages gained

## Key Questions to Answer
1. Is the application cloud-native ready?
2. Can the application scale horizontally?
3. Is configuration properly externalized?
4. Are environments consistent?
5. Is the application stateless?
6. Can the application be deployed via CI/CD?
7. Is the application observable?
8. Can the application recover from failures?

## Cloud-Native Readiness Score
- **90-120 points (75-100%)**: Excellent - Cloud-native ready
- **72-89 points (60-74%)**: Good - Minor improvements needed
- **60-71 points (50-59%)**: Fair - Significant work required
- **<60 points (<50%)**: Poor - Major refactoring needed

## Migration Path
For applications not yet 12-factor compliant:
1. **Phase 1**: Externalize configuration (Factor III)
2. **Phase 2**: Implement proper logging (Factor XI)
3. **Phase 3**: Separate build/release/run (Factor V)
4. **Phase 4**: Make processes stateless (Factor VI)
5. **Phase 5**: Achieve dev/prod parity (Factor X)
6. **Phase 6**: Implement remaining factors