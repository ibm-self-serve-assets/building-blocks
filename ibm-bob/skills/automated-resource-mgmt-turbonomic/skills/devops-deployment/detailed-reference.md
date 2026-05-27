# DevOps & Deployment - Detailed Reference

This file contains comprehensive reference material for DevOps and deployment. Refer to SKILL.md for quick guidance and use this file for detailed examples and patterns.

## Complete Dockerfile Examples

### Frontend Production Dockerfile
```dockerfile
# Build stage
FROM node:18-alpine AS builder

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production && \
    npm cache clean --force

# Copy source code
COPY . .

# Build application
RUN npm run build

# Production stage
FROM nginx:alpine

# Install curl for health checks
RUN apk add --no-cache curl

# Copy built assets from builder
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf
COPY default.conf /etc/nginx/conf.d/default.conf

# Create non-root user
RUN addgroup -g 1001 -S nginx && \
    adduser -S nginx -u 1001 && \
    chown -R nginx:nginx /usr/share/nginx/html && \
    chown -R nginx:nginx /var/cache/nginx && \
    chown -R nginx:nginx /var/log/nginx && \
    touch /var/run/nginx.pid && \
    chown -R nginx:nginx /var/run/nginx.pid

# Switch to non-root user
USER nginx

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8080/ || exit 1

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
```

### Backend Production Dockerfile
```dockerfile
FROM node:18-alpine

# Create app directory
WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm ci --only=production && \
    npm cache clean --force

# Copy application code
COPY . .

# Create non-root user
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nodejs -u 1001 && \
    chown -R nodejs:nodejs /app

# Switch to non-root user
USER nodejs

# Expose port
EXPOSE 4000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
  CMD node -e "require('http').get('http://localhost:4000/health', (r) => {process.exit(r.statusCode === 200 ? 0 : 1)})"

# Start application
CMD ["node", "src/server.js"]
```

## Complete Kubernetes Manifests

### Namespace
```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: turbonomic-dashboard
  labels:
    name: turbonomic-dashboard
    environment: production
```

### ConfigMap
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
  namespace: turbonomic-dashboard
data:
  # Frontend configuration
  VITE_API_URL: "http://backend-service:4000"
  
  # Backend configuration
  NODE_ENV: "production"
  PORT: "4000"
  LOG_LEVEL: "info"
  CORS_ORIGIN: "*"
  
  # Cache configuration
  CACHE_TTL: "300"
```

### Secrets
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
  api-key: "your-api-key-here"
```

### Frontend Deployment
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: frontend
  namespace: turbonomic-dashboard
  labels:
    app: frontend
    version: v1
spec:
  replicas: 2
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  selector:
    matchLabels:
      app: frontend
  template:
    metadata:
      labels:
        app: frontend
        version: v1
    spec:
      securityContext:
        runAsNonRoot: true
        runAsUser: 1001
        fsGroup: 1001
      containers:
      - name: frontend
        image: registry.example.com/frontend:latest
        imagePullPolicy: Always
        ports:
        - containerPort: 8080
          name: http
          protocol: TCP
        env:
        - name: VITE_API_URL
          valueFrom:
            configMapKeyRef:
              name: app-config
              key: VITE_API_URL
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
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3
        readinessProbe:
          httpGet:
            path: /
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 5
          timeoutSeconds: 3
          failureThreshold: 3
        securityContext:
          allowPrivilegeEscalation: false
          readOnlyRootFilesystem: true
          capabilities:
            drop:
            - ALL
        volumeMounts:
        - name: cache
          mountPath: /var/cache/nginx
        - name: run
          mountPath: /var/run
      volumes:
      - name: cache
        emptyDir: {}
      - name: run
        emptyDir: {}
      imagePullSecrets:
      - name: registry-secret
```

### Backend Deployment
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend
  namespace: turbonomic-dashboard
  labels:
    app: backend
    version: v1
spec:
  replicas: 2
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  selector:
    matchLabels:
      app: backend
  template:
    metadata:
      labels:
        app: backend
        version: v1
    spec:
      securityContext:
        runAsNonRoot: true
        runAsUser: 1001
        fsGroup: 1001
      containers:
      - name: backend
        image: registry.example.com/backend:latest
        imagePullPolicy: Always
        ports:
        - containerPort: 4000
          name: http
          protocol: TCP
        env:
        - name: NODE_ENV
          valueFrom:
            configMapKeyRef:
              name: app-config
              key: NODE_ENV
        - name: PORT
          valueFrom:
            configMapKeyRef:
              name: app-config
              key: PORT
        - name: TURBO_USERNAME
          valueFrom:
            secretKeyRef:
              name: app-secrets
              key: turbo-username
        - name: TURBO_PASSWORD
          valueFrom:
            secretKeyRef:
              name: app-secrets
              key: turbo-password
        resources:
          requests:
            memory: "256Mi"
            cpu: "200m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 4000
          initialDelaySeconds: 30
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3
        readinessProbe:
          httpGet:
            path: /ready
            port: 4000
          initialDelaySeconds: 10
          periodSeconds: 5
          timeoutSeconds: 3
          failureThreshold: 3
        securityContext:
          allowPrivilegeEscalation: false
          readOnlyRootFilesystem: false
          capabilities:
            drop:
            - ALL
      imagePullSecrets:
      - name: registry-secret
```

### Services
```yaml
---
apiVersion: v1
kind: Service
metadata:
  name: frontend-service
  namespace: turbonomic-dashboard
  labels:
    app: frontend
spec:
  type: ClusterIP
  ports:
  - port: 80
    targetPort: 8080
    protocol: TCP
    name: http
  selector:
    app: frontend

---
apiVersion: v1
kind: Service
metadata:
  name: backend-service
  namespace: turbonomic-dashboard
  labels:
    app: backend
spec:
  type: ClusterIP
  ports:
  - port: 4000
    targetPort: 4000
    protocol: TCP
    name: http
  selector:
    app: backend
```

### OpenShift Routes
```yaml
---
apiVersion: route.openshift.io/v1
kind: Route
metadata:
  name: frontend
  namespace: turbonomic-dashboard
  labels:
    app: frontend
spec:
  to:
    kind: Service
    name: frontend-service
    weight: 100
  port:
    targetPort: http
  tls:
    termination: edge
    insecureEdgeTerminationPolicy: Redirect
  wildcardPolicy: None

---
apiVersion: route.openshift.io/v1
kind: Route
metadata:
  name: backend
  namespace: turbonomic-dashboard
  labels:
    app: backend
spec:
  to:
    kind: Service
    name: backend-service
    weight: 100
  port:
    targetPort: http
  tls:
    termination: edge
    insecureEdgeTerminationPolicy: Redirect
  wildcardPolicy: None
```

## Complete Ansible Playbook

### Main Playbook
```yaml
---
- name: Deploy Turbonomic Dashboard to OpenShift
  hosts: localhost
  gather_facts: no
  
  vars:
    project_name: turbonomic-dashboard
    registry: registry.example.com
    image_tag: latest
    openshift_url: https://api.openshift.example.com:6443
    
  tasks:
    - name: Login to OpenShift
      command: >
        oc login {{ openshift_url }}
        --token={{ openshift_token }}
        --insecure-skip-tls-verify=true
      no_log: true
      
    - name: Create or switch to project
      command: oc project {{ project_name }}
      register: project_result
      failed_when: false
      
    - name: Create project if it doesn't exist
      command: oc new-project {{ project_name }}
      when: project_result.rc != 0
      
    - name: Create registry secret
      command: >
        oc create secret docker-registry registry-secret
        --docker-server={{ registry }}
        --docker-username={{ registry_username }}
        --docker-password={{ registry_password }}
        --namespace={{ project_name }}
      ignore_errors: yes
      no_log: true
      
    - name: Apply namespace
      command: oc apply -f kubernetes/namespace.yaml
      
    - name: Apply ConfigMap
      command: oc apply -f kubernetes/configmap.yaml
      
    - name: Create secrets
      command: >
        oc create secret generic app-secrets
        --from-literal=turbo-username={{ turbo_username }}
        --from-literal=turbo-password={{ turbo_password }}
        --namespace={{ project_name }}
      ignore_errors: yes
      no_log: true
      
    - name: Apply services
      command: oc apply -f kubernetes/services.yaml
      
    - name: Apply frontend deployment
      command: oc apply -f kubernetes/frontend-deployment.yaml
      
    - name: Apply backend deployment
      command: oc apply -f kubernetes/backend-deployment.yaml
      
    - name: Apply routes
      command: oc apply -f kubernetes/route.yaml
      
    - name: Wait for frontend deployment
      command: >
        oc rollout status deployment/frontend
        --namespace={{ project_name }}
        --timeout=5m
      
    - name: Wait for backend deployment
      command: >
        oc rollout status deployment/backend
        --namespace={{ project_name }}
        --timeout=5m
      
    - name: Get route URLs
      command: oc get routes --namespace={{ project_name }} -o json
      register: routes_output
      
    - name: Display deployment information
      debug:
        msg: "Deployment completed successfully. Routes: {{ routes_output.stdout | from_json }}"
```

## CI/CD Pipeline

### Complete GitHub Actions Workflow
```yaml
name: Build and Deploy

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

env:
  REGISTRY: registry.example.com
  NAMESPACE: turbonomic-dashboard

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        component: [frontend, backend]
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'npm'
          cache-dependency-path: ${{ matrix.component }}/package-lock.json
      
      - name: Install dependencies
        working-directory: ./${{ matrix.component }}
        run: npm ci
      
      - name: Run tests
        working-directory: ./${{ matrix.component }}
        run: npm test -- --coverage
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./${{ matrix.component }}/coverage/lcov.info
          flags: ${{ matrix.component }}

  build:
    needs: test
    runs-on: ubuntu-latest
    if: github.event_name == 'push'
    strategy:
      matrix:
        component: [frontend, backend]
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v2
      
      - name: Login to Registry
        uses: docker/login-action@v2
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ secrets.REGISTRY_USERNAME }}
          password: ${{ secrets.REGISTRY_PASSWORD }}
      
      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v4
        with:
          images: ${{ env.REGISTRY }}/${{ matrix.component }}
          tags: |
            type=ref,event=branch
            type=sha,prefix={{branch}}-
            type=raw,value=latest,enable={{is_default_branch}}
      
      - name: Build and push
        uses: docker/build-push-action@v4
        with:
          context: ./${{ matrix.component }}
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=registry,ref=${{ env.REGISTRY }}/${{ matrix.component }}:buildcache
          cache-to: type=registry,ref=${{ env.REGISTRY }}/${{ matrix.component }}:buildcache,mode=max

  deploy:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v3
      
      - name: Install OpenShift CLI
        run: |
          curl -LO https://mirror.openshift.com/pub/openshift-v4/clients/ocp/latest/openshift-client-linux.tar.gz
          tar -xzf openshift-client-linux.tar.gz
          sudo mv oc /usr/local/bin/
          oc version
      
      - name: Install Ansible
        run: |
          sudo apt-get update
          sudo apt-get install -y ansible
      
      - name: Deploy to OpenShift
        env:
          OPENSHIFT_TOKEN: ${{ secrets.OPENSHIFT_TOKEN }}
          OPENSHIFT_URL: ${{ secrets.OPENSHIFT_URL }}
          TURBO_USERNAME: ${{ secrets.TURBO_USERNAME }}
          TURBO_PASSWORD: ${{ secrets.TURBO_PASSWORD }}
        run: |
          ansible-playbook ansible/deploy.yml \
            -e "openshift_token=$OPENSHIFT_TOKEN" \
            -e "openshift_url=$OPENSHIFT_URL" \
            -e "image_tag=${{ github.sha }}" \
            -e "turbo_username=$TURBO_USERNAME" \
            -e "turbo_password=$TURBO_PASSWORD" \
            -e "registry_username=${{ secrets.REGISTRY_USERNAME }}" \
            -e "registry_password=${{ secrets.REGISTRY_PASSWORD }}"
      
      - name: Verify deployment
        run: |
          oc login ${{ secrets.OPENSHIFT_URL }} --token=${{ secrets.OPENSHIFT_TOKEN }}
          oc project ${{ env.NAMESPACE }}
          oc get pods
          oc get routes
```

For the complete original guide with all sections, see the archived `devops-guide.md` file.