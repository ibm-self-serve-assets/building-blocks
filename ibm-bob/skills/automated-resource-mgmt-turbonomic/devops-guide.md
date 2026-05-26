# DevOps & Deployment Guide

## Overview

This comprehensive guide covers all aspects of DevOps practices for the Turbonomic Resource Dashboard, including Docker containerization, Kubernetes/OpenShift deployment, Ansible automation, CI/CD pipelines, and production best practices.

**Technology Stack:**
- Docker/Podman for containerization
- Kubernetes/OpenShift for orchestration
- Ansible for automation
- Nginx for web serving
- Node.js for backend runtime

---

## Table of Contents

### Part 1: Docker Containerization
1. [Container Architecture](#1-container-architecture)
2. [Frontend Dockerfile](#2-frontend-dockerfile)
3. [Backend Dockerfile](#3-backend-dockerfile)
4. [Nginx Configuration](#4-nginx-configuration)
5. [Multi-Stage Builds](#5-multi-stage-builds)

### Part 2: Kubernetes/OpenShift
6. [Kubernetes Fundamentals](#6-kubernetes-fundamentals)
7. [Deployment Manifests](#7-deployment-manifests)
8. [Service Configuration](#8-service-configuration)
9. [ConfigMaps & Secrets](#9-configmaps--secrets)
10. [Routes & Ingress](#10-routes--ingress)

### Part 3: Ansible Automation
11. [Ansible Architecture](#11-ansible-architecture)
12. [Playbook Structure](#12-playbook-structure)
13. [Role-Based Automation](#13-role-based-automation)
14. [Variable Management](#14-variable-management)
15. [Deployment Workflow](#15-deployment-workflow)

### Part 4: CI/CD & Production
16. [CI/CD Pipeline](#16-cicd-pipeline)
17. [Environment Configuration](#17-environment-configuration)
18. [Health Checks & Monitoring](#18-health-checks--monitoring)
19. [Security Best Practices](#19-security-best-practices)
20. [Troubleshooting](#20-troubleshooting)

---

# Part 1: Docker Containerization

## 1. Container Architecture

### Deployment Architecture

```
┌─────────────────────────────────────────┐
│         OpenShift/Kubernetes            │
├─────────────────────────────────────────┤
│  ┌─────────────┐    ┌─────────────┐   │
│  │  Frontend   │    │   Backend   │   │
│  │   (Nginx)   │◄───┤  (Node.js)  │   │
│  │   :80       │    │    :4000    │   │
│  └─────────────┘    └─────────────┘   │
│         │                   │          │
│  ┌─────────────┐    ┌─────────────┐   │
│  │   Route     │    │   Route     │   │
│  │  (External) │    │  (External) │   │
│  └─────────────┘    └─────────────┘   │
└─────────────────────────────────────────┘
```

### Container Benefits

1. **Consistency** - Same environment everywhere
2. **Isolation** - Dependencies contained
3. **Portability** - Run anywhere
4. **Scalability** - Easy horizontal scaling
5. **Efficiency** - Lightweight and fast

## 2. Frontend Dockerfile

### Multi-Stage Build

```dockerfile
# Stage 1: Build
FROM node:18-alpine AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy source code
COPY . .

# Build application
RUN npm run build

# Stage 2: Production
FROM nginx:alpine

# Copy custom nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf
COPY default.conf /etc/nginx/conf.d/default.conf

# Copy built application
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy runtime configuration
COPY docker-entrypoint.sh /docker-entrypoint.sh
COPY public/config.js /usr/share/nginx/html/config.js

RUN chmod +x /docker-entrypoint.sh

# Expose port
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget --quiet --tries=1 --spider http://localhost/ || exit 1

# Start nginx
ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["nginx", "-g", "daemon off;"]
```

### Build Command

```bash
# Build frontend image
docker build -t turbonomic-dashboard-frontend:latest ./frontend

# Build with specific tag
docker build -t registry.example.com/turbonomic-dashboard-frontend:1.0.0 ./frontend

# Build with build args
docker build --build-arg NODE_ENV=production -t frontend:latest ./frontend
```

## 3. Backend Dockerfile

### Production Dockerfile

```dockerfile
FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy source code
COPY src ./src

# Create non-root user
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nodejs -u 1001

# Change ownership
RUN chown -R nodejs:nodejs /app

# Switch to non-root user
USER nodejs

# Expose port
EXPOSE 4000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD node -e "require('http').get('http://localhost:4000/health', (r) => {process.exit(r.statusCode === 200 ? 0 : 1)})"

# Start application
CMD ["node", "src/server.js"]
```

### Build Command

```bash
# Build backend image
docker build -t turbonomic-dashboard-backend:latest ./backend

# Build and push
docker build -t registry.example.com/turbonomic-dashboard-backend:1.0.0 ./backend
docker push registry.example.com/turbonomic-dashboard-backend:1.0.0
```

## 4. Nginx Configuration

### nginx.conf

```nginx
user nginx;
worker_processes auto;
error_log /var/log/nginx/error.log warn;
pid /var/run/nginx.pid;

events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';

    access_log /var/log/nginx/access.log main;

    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    client_max_body_size 20M;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types text/plain text/css text/xml text/javascript 
               application/json application/javascript application/xml+rss 
               application/rss+xml font/truetype font/opentype 
               application/vnd.ms-fontobject image/svg+xml;

    include /etc/nginx/conf.d/*.conf;
}
```

### default.conf

```nginx
server {
    listen 80;
    server_name _;
    root /usr/share/nginx/html;
    index index.html;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;

    # Cache static assets
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Don't cache HTML
    location ~* \.html$ {
        expires -1;
        add_header Cache-Control "no-store, no-cache, must-revalidate";
    }

    # SPA routing
    location / {
        try_files $uri $uri/ /index.html;
    }

    # Health check
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
}
```

## 5. Multi-Stage Builds

### Benefits

1. **Smaller Images** - Only production dependencies
2. **Security** - No build tools in production
3. **Faster Deployments** - Smaller image size
4. **Clean Separation** - Build vs runtime

### Example Pattern

```dockerfile
# Build stage
FROM node:18 AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Production stage
FROM node:18-alpine
WORKDIR /app
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
CMD ["node", "dist/server.js"]
```

---

# Part 2: Kubernetes/OpenShift

## 6. Kubernetes Fundamentals

### Core Concepts

**Pod** - Smallest deployable unit
**Deployment** - Manages pod replicas
**Service** - Network access to pods
**ConfigMap** - Configuration data
**Secret** - Sensitive data
**Route/Ingress** - External access

### Resource Hierarchy

```
Namespace
├── Deployments
│   └── Pods
├── Services
├── Routes
├── ConfigMaps
└── Secrets
```

## 7. Deployment Manifests

### Frontend Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: turbonomic-dashboard-frontend
  namespace: turbonomic-dashboard
  labels:
    app: turbonomic-dashboard
    component: frontend
spec:
  replicas: 2
  selector:
    matchLabels:
      app: turbonomic-dashboard
      component: frontend
  template:
    metadata:
      labels:
        app: turbonomic-dashboard
        component: frontend
    spec:
      containers:
      - name: frontend
        image: registry.example.com/turbonomic-dashboard-frontend:1.0.0
        ports:
        - containerPort: 80
          protocol: TCP
        env:
        - name: BACKEND_URL
          valueFrom:
            configMapKeyRef:
              name: turbonomic-dashboard-config
              key: backend-url
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "256Mi"
            cpu: "200m"
        livenessProbe:
          httpGet:
            path: /health
            port: 80
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 80
          initialDelaySeconds: 5
          periodSeconds: 5
      imagePullSecrets:
      - name: registry-secret
```

### Backend Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: turbonomic-dashboard-backend
  namespace: turbonomic-dashboard
  labels:
    app: turbonomic-dashboard
    component: backend
spec:
  replicas: 2
  selector:
    matchLabels:
      app: turbonomic-dashboard
      component: backend
  template:
    metadata:
      labels:
        app: turbonomic-dashboard
        component: backend
    spec:
      containers:
      - name: backend
        image: registry.example.com/turbonomic-dashboard-backend:1.0.0
        ports:
        - containerPort: 4000
          protocol: TCP
        env:
        - name: PORT
          value: "4000"
        - name: NODE_ENV
          value: "production"
        resources:
          requests:
            memory: "256Mi"
            cpu: "200m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health/live
            port: 4000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health/ready
            port: 4000
          initialDelaySeconds: 10
          periodSeconds: 5
      imagePullSecrets:
      - name: registry-secret
```

## 8. Service Configuration

### Frontend Service

```yaml
apiVersion: v1
kind: Service
metadata:
  name: turbonomic-dashboard-frontend
  namespace: turbonomic-dashboard
  labels:
    app: turbonomic-dashboard
    component: frontend
spec:
  type: ClusterIP
  ports:
  - port: 80
    targetPort: 80
    protocol: TCP
    name: http
  selector:
    app: turbonomic-dashboard
    component: frontend
```

### Backend Service

```yaml
apiVersion: v1
kind: Service
metadata:
  name: turbonomic-dashboard-backend
  namespace: turbonomic-dashboard
  labels:
    app: turbonomic-dashboard
    component: backend
spec:
  type: ClusterIP
  ports:
  - port: 4000
    targetPort: 4000
    protocol: TCP
    name: http
  selector:
    app: turbonomic-dashboard
    component: backend
```

## 9. ConfigMaps & Secrets

### ConfigMap

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: turbonomic-dashboard-config
  namespace: turbonomic-dashboard
data:
  backend-url: "http://turbonomic-dashboard-backend:4000"
  log-level: "info"
  environment: "production"
```

### Secret

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: turbonomic-dashboard-secrets
  namespace: turbonomic-dashboard
type: Opaque
stringData:
  turbonomic-username: "admin"
  turbonomic-password: "password"
```

### Registry Secret

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: registry-secret
  namespace: turbonomic-dashboard
type: kubernetes.io/dockerconfigjson
data:
  .dockerconfigjson: <base64-encoded-docker-config>
```

## 10. Routes & Ingress

### OpenShift Route (Frontend)

```yaml
apiVersion: route.openshift.io/v1
kind: Route
metadata:
  name: turbonomic-dashboard-frontend
  namespace: turbonomic-dashboard
spec:
  to:
    kind: Service
    name: turbonomic-dashboard-frontend
  port:
    targetPort: http
  tls:
    termination: edge
    insecureEdgeTerminationPolicy: Redirect
```

### OpenShift Route (Backend)

```yaml
apiVersion: route.openshift.io/v1
kind: Route
metadata:
  name: turbonomic-dashboard-backend
  namespace: turbonomic-dashboard
spec:
  to:
    kind: Service
    name: turbonomic-dashboard-backend
  port:
    targetPort: http
  tls:
    termination: edge
```

---

# Part 3: Ansible Automation

## 11. Ansible Architecture

### Project Structure

```
ansible/
├── site.yaml                    # Main playbook
├── requirements.txt             # Python dependencies
├── vars/
│   └── main.yaml               # Configuration variables
└── roles/
    ├── oc_login/               # OpenShift authentication
    ├── podman_login/           # Container registry login
    ├── prepare_namespace/      # Namespace creation
    ├── create_secrets/         # Secret management
    ├── build_frontend/         # Frontend image build
    ├── build_backend/          # Backend image build
    ├── deploy_manifests/       # Kubernetes deployment
    └── verify_deployment/      # Deployment verification
```

### Deployment Flow

```
┌─────────────────┐
│   oc_login      │ ──> Authenticate to OpenShift
└────────┬────────┘
         │
┌────────▼────────┐
│prepare_namespace│ ──> Create/verify namespace
└────────┬────────┘
         │
┌────────▼────────┐
│ podman_login    │ ──> Login to registry
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
┌───▼──┐  ┌──▼───┐
│build │  │build │ ──> Build images
│front│  │back  │
└───┬──┘  └──┬───┘
    │         │
    └────┬────┘
         │
┌────────▼────────┐
│ create_secrets  │ ──> Create secrets
└────────┬────────┘
         │
┌────────▼────────┐
│deploy_manifests │ ──> Deploy to cluster
└────────┬────────┘
         │
┌────────▼────────┐
│verify_deployment│ ──> Verify success
└─────────────────┘
```

## 12. Playbook Structure

### Main Playbook (site.yaml)

```yaml
---
- name: Deploy Turbonomic Dashboard to OpenShift
  hosts: localhost
  gather_facts: yes
  
  vars_files:
    - vars/main.yaml
  
  tasks:
    - name: Display deployment information
      debug:
        msg: |
          ========================================
          Turbonomic Dashboard Deployment
          ========================================
          Registry: {{ container_registry }}
          Version: {{ app_version }}
          Namespace: {{ openshift_namespace }}
          ========================================

    - name: Validate required variables
      assert:
        that:
          - container_registry is defined
          - container_registry_username is defined
          - container_registry_password is defined
          - openshift_server is defined
          - openshift_token is defined
          - openshift_namespace is defined
        fail_msg: "Required variables missing"

  roles:
    - role: oc_login
    - role: prepare_namespace
    - role: podman_login
    - role: build_frontend
    - role: build_backend
    - role: create_secrets
    - role: deploy_manifests
    - role: verify_deployment
```

### Variables File (vars/main.yaml)

```yaml
---
# Container Registry
container_registry: "registry.example.com"
container_registry_username: "{{ lookup('env', 'REGISTRY_USERNAME') }}"
container_registry_password: "{{ lookup('env', 'REGISTRY_PASSWORD') }}"

# OpenShift Configuration
openshift_server: "{{ lookup('env', 'OPENSHIFT_SERVER') }}"
openshift_token: "{{ lookup('env', 'OPENSHIFT_TOKEN') }}"
openshift_namespace: "turbonomic-dashboard"

# Application Configuration
app_name: "turbonomic-dashboard"
app_version: "1.0.0"
frontend_image: "{{ container_registry }}/{{ app_name }}-frontend"
backend_image: "{{ container_registry }}/{{ app_name }}-backend"

# Resource Limits
frontend_replicas: 2
backend_replicas: 2
frontend_memory_request: "128Mi"
frontend_memory_limit: "256Mi"
backend_memory_request: "256Mi"
backend_memory_limit: "512Mi"
```

## 13. Role-Based Automation

### OpenShift Login Role

```yaml
# roles/oc_login/tasks/main.yaml
---
- name: Login to OpenShift cluster
  command: >
    oc login {{ openshift_server }}
    --token={{ openshift_token }}
    --insecure-skip-tls-verify=true
  register: oc_login_result
  changed_when: false

- name: Verify login
  command: oc whoami
  register: whoami_result
  changed_when: false

- name: Display current user
  debug:
    msg: "Logged in as: {{ whoami_result.stdout }}"
```

### Build Frontend Role

```yaml
# roles/build_frontend/tasks/main.yaml
---
- name: Build frontend container image
  command: >
    podman build
    -t {{ frontend_image }}:{{ app_version }}
    -t {{ frontend_image }}:latest
    ./frontend
  args:
    chdir: "{{ playbook_dir }}/.."

- name: Push frontend image to registry
  command: >
    podman push {{ frontend_image }}:{{ app_version }}

- name: Push latest tag
  command: >
    podman push {{ frontend_image }}:latest
```

### Deploy Manifests Role

```yaml
# roles/deploy_manifests/tasks/main.yaml
---
- name: Apply ConfigMap
  kubernetes.core.k8s:
    state: present
    definition: "{{ lookup('file', 'k8s/configmap.yaml') }}"
    namespace: "{{ openshift_namespace }}"

- name: Apply frontend deployment
  kubernetes.core.k8s:
    state: present
    definition: "{{ lookup('template', 'k8s/frontend-deployment.yaml.j2') }}"
    namespace: "{{ openshift_namespace }}"

- name: Apply backend deployment
  kubernetes.core.k8s:
    state: present
    definition: "{{ lookup('template', 'k8s/backend-deployment.yaml.j2') }}"
    namespace: "{{ openshift_namespace }}"

- name: Wait for deployments to be ready
  kubernetes.core.k8s_info:
    kind: Deployment
    namespace: "{{ openshift_namespace }}"
    name: "{{ item }}"
    wait: yes
    wait_condition:
      type: Available
      status: "True"
    wait_timeout: 300
  loop:
    - turbonomic-dashboard-frontend
    - turbonomic-dashboard-backend
```

## 14. Variable Management

### Environment Variables

```bash
# .env file
export REGISTRY_USERNAME="myuser"
export REGISTRY_PASSWORD="mypassword"
export OPENSHIFT_SERVER="https://api.cluster.example.com:6443"
export OPENSHIFT_TOKEN="sha256~xxxxx"
```

### Ansible Vault

```bash
# Create encrypted file
ansible-vault create vars/secrets.yaml

# Edit encrypted file
ansible-vault edit vars/secrets.yaml

# Run playbook with vault
ansible-playbook site.yaml --ask-vault-pass
```

## 15. Deployment Workflow

### Complete Deployment

```bash
# 1. Set environment variables
source .env

# 2. Run Ansible playbook
ansible-playbook ansible/site.yaml

# 3. Verify deployment
oc get pods -n turbonomic-dashboard
oc get routes -n turbonomic-dashboard
```

### Rollback

```bash
# Rollback to previous version
oc rollout undo deployment/turbonomic-dashboard-frontend -n turbonomic-dashboard
oc rollout undo deployment/turbonomic-dashboard-backend -n turbonomic-dashboard

# Check rollout status
oc rollout status deployment/turbonomic-dashboard-frontend -n turbonomic-dashboard
```

---

# Part 4: CI/CD & Production

## 16. CI/CD Pipeline

### GitHub Actions Example

```yaml
name: Build and Deploy

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    
    - name: Build frontend
      run: |
        cd frontend
        npm ci
        npm run build
    
    - name: Build backend
      run: |
        cd backend
        npm ci
        npm test
    
    - name: Build Docker images
      run: |
        docker build -t frontend:${{ github.sha }} ./frontend
        docker build -t backend:${{ github.sha }} ./backend
    
    - name: Push to registry
      run: |
        echo ${{ secrets.REGISTRY_PASSWORD }} | docker login -u ${{ secrets.REGISTRY_USERNAME }} --password-stdin
        docker push frontend:${{ github.sha }}
        docker push backend:${{ github.sha }}
  
  deploy:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
    - uses: actions/checkout@v2
    
    - name: Deploy to OpenShift
      run: |
        ansible-playbook ansible/site.yaml \
          -e "app_version=${{ github.sha }}"
      env:
        OPENSHIFT_SERVER: ${{ secrets.OPENSHIFT_SERVER }}
        OPENSHIFT_TOKEN: ${{ secrets.OPENSHIFT_TOKEN }}
```

## 17. Environment Configuration

### Development

```yaml
environment: development
replicas: 1
resources:
  requests:
    memory: "128Mi"
    cpu: "100m"
  limits:
    memory: "256Mi"
    cpu: "200m"
```

### Production

```yaml
environment: production
replicas: 3
resources:
  requests:
    memory: "256Mi"
    cpu: "200m"
  limits:
    memory: "512Mi"
    cpu: "500m"
autoscaling:
  enabled: true
  minReplicas: 3
  maxReplicas: 10
  targetCPUUtilizationPercentage: 70
```

## 18. Health Checks & Monitoring

### Liveness Probe

```yaml
livenessProbe:
  httpGet:
    path: /health/live
    port: 4000
  initialDelaySeconds: 30
  periodSeconds: 10
  timeoutSeconds: 5
  failureThreshold: 3
```

### Readiness Probe

```yaml
readinessProbe:
  httpGet:
    path: /health/ready
    port: 4000
  initialDelaySeconds: 10
  periodSeconds: 5
  timeoutSeconds: 3
  failureThreshold: 3
```

### Monitoring Commands

```bash
# Check pod status
oc get pods -n turbonomic-dashboard

# View logs
oc logs -f deployment/turbonomic-dashboard-frontend -n turbonomic-dashboard

# Describe pod
oc describe pod <pod-name> -n turbonomic-dashboard

# Check events
oc get events -n turbonomic-dashboard --sort-by='.lastTimestamp'
```

## 19. Security Best Practices

### Container Security

1. **Non-root user** - Run as non-root
2. **Read-only filesystem** - Where possible
3. **No privileged containers**
4. **Resource limits** - Always set
5. **Security scanning** - Scan images

### Network Security

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: turbonomic-dashboard-policy
spec:
  podSelector:
    matchLabels:
      app: turbonomic-dashboard
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: turbonomic-dashboard
    ports:
    - protocol: TCP
      port: 80
    - protocol: TCP
      port: 4000
```

## 20. Troubleshooting

### Common Issues

**Pod not starting:**
```bash
oc describe pod <pod-name>
oc logs <pod-name>
```

**Image pull errors:**
```bash
oc get secret registry-secret -o yaml
oc create secret docker-registry registry-secret \
  --docker-server=registry.example.com \
  --docker-username=user \
  --docker-password=pass
```

**Service not accessible:**
```bash
oc get svc
oc get routes
oc port-forward svc/turbonomic-dashboard-frontend 8080:80
```

---

## Best Practices Summary

### DO ✅

- Use multi-stage Docker builds
- Set resource limits and requests
- Implement health checks
- Use non-root users in containers
- Version your images
- Use ConfigMaps for configuration
- Use Secrets for sensitive data
- Implement proper logging
- Monitor resource usage
- Test deployments in staging
- Use Ansible for automation
- Document deployment process

### DON'T ❌

- Run containers as root
- Hardcode credentials
- Skip health checks
- Use latest tag in production
- Ignore resource limits
- Store secrets in code
- Skip security scanning
- Deploy without testing
- Ignore monitoring
- Manual deployments
- Skip documentation

---

## Resources

### Official Documentation
- [Docker Documentation](https://docs.docker.com/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [OpenShift Documentation](https://docs.openshift.com/)
- [Ansible Documentation](https://docs.ansible.com/)

### Tools
- [Podman](https://podman.io/)
- [kubectl](https://kubernetes.io/docs/reference/kubectl/)
- [oc CLI](https://docs.openshift.com/container-platform/latest/cli_reference/openshift_cli/getting-started-cli.html)

### Best Practices
- [12-Factor App](https://12factor.net/)
- [Container Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [Kubernetes Best Practices](https://kubernetes.io/docs/concepts/configuration/overview/)

---

**Last Updated:** 2026-05-22  
**Version:** 2.0.0  
**Maintainer:** Operations Dashboard Team