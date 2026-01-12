---
title: Deploy and Manage a Retail Application on IBM Cloud Red Hat OpenShift Using Terraform and Ansible
subtitle: Provision infrastructure with Terraform and deploy applications using Ansible
authors:
  - name: Sunil Gajula
    role: Senior Solution Architect
  - name: Yasser Sheriff
    role: Senior Solution Architect
skill_level: Intermediate
technologies:
  - IBM Cloud
  - Red Hat OpenShift
  - Terraform
  - Ansible
  - Kubernetes
  - PostgreSQL
---

## Overview

Enterprise cloud-native platforms benefit from a **clear separation of responsibilities** between infrastructure provisioning and application deployment.  
This tutorial demonstrates an end-to-end approach using:

- **Terraform** to provision a Red Hat OpenShift cluster on **IBM Cloud VPC Gen2**
- **Ansible** to deploy and manage a Retail application on the provisioned cluster

By following this tutorial, you will learn how to adopt a scalable, repeatable, and IBM-recommended deployment model suitable for production environments.

---

## Understanding Terraform and Ansible

### What Is Terraform?

Terraform is an **Infrastructure as Code (IaC)** tool used to provision and manage cloud infrastructure using declarative configuration files.

Terraform is commonly used to provision:
- Virtual Private Clouds (VPC)
- Networking and security components
- Managed Kubernetes and OpenShift clusters
- Cloud storage and identity resources

Terraform maintains a **state file**, allowing it to track and reconcile infrastructure changes safely.

#### Why Use Terraform?

Terraform is best suited for:
- Day 0 and Day 1 infrastructure provisioning
- Creating consistent environments across regions and accounts
- Enforcing infrastructure standards at scale

---

### What Is Ansible?

Ansible is a **configuration management and automation tool** designed for:
- Application deployment
- Configuration management
- Day 2 operations
- Operational workflows

In Kubernetes and OpenShift environments, Ansible interacts directly with the Kubernetes API using native modules.

#### Why Use Ansible?

Ansible is ideal for:
- Application deployment and lifecycle management
- Post-provisioning automation
- CI/CD pipelines and operational consistency
- Avoiding infrastructure state complexity for application changes

---

## Recommended IBM Tooling Strategy

IBM recommends a **layered automation approach**:

| Layer | Tool | Responsibility |
|------|------|----------------|
| Infrastructure | Terraform | Provision IBM Cloud VPC and OpenShift |
| Platform & Applications | Ansible | Deploy and manage applications |
| Operations | Ansible | Day 2 automation |

---

## Phase 1: Provision Red Hat OpenShift on IBM Cloud Using Terraform

IBM provides officially supported Terraform modules for provisioning Red Hat OpenShift clusters on **IBM Cloud VPC Gen2**.

### Terraform Module Reference

Use the following repository to provision the OpenShift cluster:

https://github.com/terraform-ibm-modules/terraform-ibm-base-ocp-vpc

This module automates:
- IBM Cloud VPC Gen2 creation
- Networking and security configuration
- Red Hat OpenShift cluster provisioning
- Worker node pool configuration

Once the cluster is provisioned, proceed to Phase 2.

---

## Phase 2: Deploy the Retail Application Using Ansible

After the OpenShift cluster is available, application deployment is handled **entirely using Ansible**.

---

## Architecture

The solution deploys the following components into a **user-defined namespace**:

### PostgreSQL
Deployed as a **StatefulSet** with persistent identity.  
Credentials are stored securely in a **Kubernetes Secret**.

### Retail Backend Service
A stateless deployment that consumes PostgreSQL credentials via environment variables.

### Retail Frontend Service
A stateless deployment exposing the user interface.

### Ansible Control Plane
Uses the **kubernetes.core** collection to interact directly with the Kubernetes API.

All components are deployed using **idempotent Ansible roles**, enabling repeatable deployments.

---

## Prerequisites

- Red Hat OpenShift cluster (4.12 or later)
- `oc` CLI configured and authenticated
- Ansible 2.14 or later
- Python 3.9 or later
- Docker Hub account (or compatible registry)

---

## Install Required Ansible Dependencies

Install the Kubernetes Ansible collection:

```bash
ansible-galaxy collection install kubernetes.core
```

Install Python dependencies:

```bash
pip install kubernetes openshift pyyaml
```

Verify cluster access:

```bash
oc whoami
```

---

## Solution Structure

```text
ansible-retailapp
├── inventory
│   ├── group_vars
│   │   └── all.yml
│   └── localhost.ini
├── playbooks
│   └── deploy-retailapp.yml
└── roles
    ├── database
    │   └── tasks
    │       └── main.yml
    ├── frontend_rebuild
    │   └── tasks
    │       └── main.yml
    ├── images
    │   └── tasks
    │       └── main.yml
    ├── jmeter
    │   └── tasks
    │       └── main.yml
    ├── oc_cli
    │   └── tasks
    │       └── main.yml
    ├── openshift
    │   └── tasks
    │       └── main.yml
    ├── prereqs
    │   └── tasks
    │       └── main.yml
    └── source
        └── tasks
            └── main.yml
```

---

## Define Application Configuration

### inventory/group_vars/all.yml

```yaml
oc_token: ""
oc_server: ""

docker_username: ""
docker_password: ""

namespace: retail-automation
postgres_label: "app=retail-postgres"

backend_image: "docker.io/{{ docker_username }}/retail-backend:1.0.0"
frontend_image: "docker.io/{{ docker_username }}/retail-frontend:1.0.0"
postgresql_image: "docker.io/{{ docker_username }}/retail-postgresql:1.0.0"

openshift_version: "4.18.28"
jmeter_version: "5.6.3"

github_zip_url: "https://github.com/SunilManika/retailapp/archive/refs/heads/main.zip"
workspace: "/root/retailapp"
```

---

## Deploy the Application

```bash

ansible-playbook -i inventory/localhost.ini playbooks/deploy-retailapp.yml

```

---

## Verify the Deployment

```bash
oc get pods -n retail-automation
oc get svc -n retail-automation
```

Verify PostgreSQL:

```bash
oc rsh <postgres-pod-name>
psql -U retail -d retaildb
```

Accessing Retail App:

To access the Retail application, run the below command to get the route
```bash
oc get route | grep retail-frontend | awk {'print $2'}
```

---

## Clean Up

```bash
oc delete namespace retail-automation
```

---

## Summary

In this tutorial, you learned how to:

- Provision Red Hat OpenShift on IBM Cloud VPC Gen2 using Terraform
- Deploy a cloud-native Retail application using Ansible
- Separate infrastructure provisioning from application deployment
- Follow IBM Developer and OpenShift best practices
