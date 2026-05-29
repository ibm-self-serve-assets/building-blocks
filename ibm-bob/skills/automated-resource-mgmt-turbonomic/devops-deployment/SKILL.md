---
name: devops-deployment
description: Docker containerization, Kubernetes/OpenShift deployment, Ansible automation, and CI/CD pipeline configuration for production-ready applications
---

# DevOps & Deployment Skill

Use this skill when deploying applications, creating container images, automating infrastructure, setting up CI/CD pipelines, or managing Kubernetes/OpenShift resources.

## When to Use This Skill

- Building Docker images
- Creating Kubernetes/OpenShift manifests
- Writing Ansible playbooks
- Setting up CI/CD pipelines
- Configuring production environments
- Implementing health checks and monitoring
- Troubleshooting deployment issues

## Core Technologies

- Docker for containerization
- Kubernetes/OpenShift for orchestration
- Ansible for automation
- GitHub Actions for CI/CD
- Nginx for frontend serving

## Key Principles

1. **Infrastructure as Code** - Define infrastructure in version-controlled files
2. **Immutable Infrastructure** - Build once, deploy everywhere
3. **Security by Default** - Run as non-root, scan images, use secrets
4. **Observability** - Implement health checks, logging, and monitoring
5. **Automation** - Automate builds, tests, and deployments

## Quick Reference

### Multi-Stage Dockerfile (Frontend)
```dockerfile
# Build stage
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Production stage
FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### Kubernetes Deployment
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: frontend
  namespace: turbonomic-dashboard
spec:
  replicas: 2
  selector:
    matchLabels:
      app: frontend
  template:
    metadata:
      labels:
        app: frontend
    spec:
      containers:
      - name: frontend
        image: registry.example.com/frontend:latest
        ports:
        - containerPort: 80
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "256Mi"
            cpu: "200m"
        livenessProbe:
          httpGet:
            path: /
            port: 80
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /
            port: 80
          initialDelaySeconds: 5
          periodSeconds: 5
```

### Ansible Playbook
```yaml
---
- name: Deploy Turbonomic Dashboard
  hosts: openshift
  vars:
    project_name: turbonomic-dashboard
    registry: registry.example.com
  
  tasks:
    - name: Login to OpenShift
      command: oc login {{ openshift_url }} --token={{ openshift_token }}
      no_log: true
    
    - name: Create project
      command: oc new-project {{ project_name }}
      ignore_errors: yes
    
    - name: Apply manifests
      command: oc apply -f {{ item }}
      loop:
        - kubernetes/namespace.yaml
        - kubernetes/configmap.yaml
        - kubernetes/services.yaml
        - kubernetes/frontend-deployment.yaml
        - kubernetes/backend-deployment.yaml
```

## Common Patterns

### Docker Build and Push
```bash
# Build images
docker build -t registry.example.com/frontend:latest ./frontend
docker build -t registry.example.com/backend:latest ./backend

# Push to registry
docker push registry.example.com/frontend:latest
docker push registry.example.com/backend:latest
```

### Kubernetes ConfigMap
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
  namespace: turbonomic-dashboard
data:
  API_URL: "http://backend-service:4000"
  LOG_LEVEL: "info"
  NODE_ENV: "production"
```

### Kubernetes Secret
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: app-secrets
  namespace: turbonomic-dashboard
type: Opaque
stringData:
  turbo-username: "admin"
  turbo-password: "changeme"
```

### OpenShift Route
```yaml
apiVersion: route.openshift.io/v1
kind: Route
metadata:
  name: frontend
  namespace: turbonomic-dashboard
spec:
  to:
    kind: Service
    name: frontend-service
  port:
    targetPort: 80
  tls:
    termination: edge
    insecureEdgeTerminationPolicy: Redirect
```

## File Organization
```
project/
├── frontend/
│   └── Dockerfile
├── backend/
│   └── Dockerfile
├── kubernetes/
│   ├── namespace.yaml
│   ├── configmap.yaml
│   ├── services.yaml
│   ├── frontend-deployment.yaml
│   └── backend-deployment.yaml
├── ansible/
│   ├── deploy.yml
│   ├── inventory.ini
│   └── roles/
└── .github/
    └── workflows/
        └── deploy.yml
```

## CI/CD Pipeline (GitHub Actions)
```yaml
name: Build and Deploy

on:
  push:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Build Frontend
        run: |
          cd frontend
          docker build -t ${{ secrets.REGISTRY }}/frontend:${{ github.sha }} .
          docker push ${{ secrets.REGISTRY }}/frontend:${{ github.sha }}
      
      - name: Build Backend
        run: |
          cd backend
          docker build -t ${{ secrets.REGISTRY }}/backend:${{ github.sha }} .
          docker push ${{ secrets.REGISTRY }}/backend:${{ github.sha }}
  
  deploy:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Deploy to OpenShift
        run: |
          ansible-playbook ansible/deploy.yml \
            -e "image_tag=${{ github.sha }}" \
            -e "openshift_token=${{ secrets.OPENSHIFT_TOKEN }}"
```

## Health Checks

### Liveness Probe
Checks if the container is running. Kubernetes restarts the container if this fails.
```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 4000
  initialDelaySeconds: 30
  periodSeconds: 10
  timeoutSeconds: 5
  failureThreshold: 3
```

### Readiness Probe
Checks if the container is ready to serve traffic. Kubernetes removes it from service if this fails.
```yaml
readinessProbe:
  httpGet:
    path: /ready
    port: 4000
  initialDelaySeconds: 5
  periodSeconds: 5
  timeoutSeconds: 3
  failureThreshold: 3
```

## Security Best Practices

### Container Security
```dockerfile
# Run as non-root user
FROM node:18-alpine
RUN addgroup -g 1001 -S nodejs && adduser -S nodejs -u 1001
USER nodejs

# Scan for vulnerabilities
RUN npm audit fix

# Use specific versions
FROM node:18.17.0-alpine
```

### Kubernetes Security
```yaml
spec:
  securityContext:
    runAsNonRoot: true
    runAsUser: 1001
    fsGroup: 1001
  containers:
  - name: app
    securityContext:
      allowPrivilegeEscalation: false
      readOnlyRootFilesystem: true
      capabilities:
        drop:
        - ALL
```

## Monitoring Commands
```bash
# Check pod status
oc get pods -n turbonomic-dashboard

# View logs
oc logs -f deployment/frontend -n turbonomic-dashboard

# Describe pod
oc describe pod <pod-name> -n turbonomic-dashboard

# Execute command in pod
oc exec -it <pod-name> -n turbonomic-dashboard -- /bin/sh

# Port forward for debugging
oc port-forward svc/backend-service 4000:4000 -n turbonomic-dashboard
```

## Troubleshooting

### Image Pull Errors
```bash
# Create image pull secret
oc create secret docker-registry registry-secret \
  --docker-server=registry.example.com \
  --docker-username=user \
  --docker-password=pass \
  -n turbonomic-dashboard

# Add to deployment
spec:
  imagePullSecrets:
  - name: registry-secret
```

### Pod Crashes
```bash
# Check events
oc get events -n turbonomic-dashboard --sort-by='.lastTimestamp'

# Check logs from previous container
oc logs <pod-name> --previous -n turbonomic-dashboard

# Describe pod for details
oc describe pod <pod-name> -n turbonomic-dashboard
```

## Supporting Documentation

Refer to the following files in this skill folder for detailed guidance:
- `docker-guide.md` - Docker best practices and patterns
- `kubernetes-guide.md` - Kubernetes/OpenShift configuration
- `ansible-guide.md` - Ansible automation patterns
- `cicd-guide.md` - CI/CD pipeline setup
- `monitoring.md` - Monitoring and observability

## Best Practices

### DO ✅
- Use multi-stage Docker builds
- Run containers as non-root users
- Implement health checks (liveness and readiness)
- Use resource limits and requests
- Store secrets in Kubernetes Secrets
- Use specific image tags (not `latest`)
- Implement proper logging
- Automate deployments with CI/CD

### DON'T ❌
- Run containers as root
- Hardcode secrets in manifests
- Use `latest` tag in production
- Skip health checks
- Ignore resource limits
- Deploy without testing
- Store credentials in Git
- Skip security scanning

## Resources

- [Docker Documentation](https://docs.docker.com/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [OpenShift Documentation](https://docs.openshift.com/)
- [Ansible Documentation](https://docs.ansible.com/)
- [GitHub Actions](https://docs.github.com/en/actions)