# Infrastructure as a service (Terraform) Building Block Demo for IBM Cloud

This repository provides a sample **Infrastructure as Code (IaC)** demo using Terraform on IBM Cloud.  
It is designed to be **simple, reusable, and cost-safe**, while showcasing best practices for demos and learning.

---

## Key Aspects

### 1. Clarity & Simplicity
- Keep the code **simple and readable** — avoid overcomplicated resources.  
- Use **clear naming conventions** for resources, variables, and outputs.  
- Add **comments** explaining each block for demo consumers.  

---

### 2. Reusability & Modularity
- Structure code into **modules** (e.g., network, compute, storage).  
- Showcase best practices: how **modules make code reusable** across environments.  
- Keep the **root module small** and delegate logic to sub-modules.  

---

### 3. Parameterization
- Use `variables.tf` with **defaults for flexibility**.  
- Provide sensible defaults so users can run the demo quickly.  

Example:

```
variable "region" {
  description = "IBM Cloud region to deploy resources in"
  default     = "us-south"
}
```

---

### 4. Outputs & Observability

Use outputs.tf to show important information after deployment (e.g., IPs, URLs, bucket names).

Makes the demo more engaging when participants immediately see something usable.

---

### 5. Documentation

Include a README.md with:
-- Overview of what the demo builds.
-- Prerequisites (Terraform version, provider credentials).

Step-by-step usage instructions:

```
terraform init
terraform plan
terraform apply
terraform destroy
```

-- Expected outcomes (add screenshots/diagrams).

---

### 6. Safety & Cost Control

Avoid deploying large/expensive resources — stick to free/low-cost tiers.

Ensure everything can be easily destroyed (terraform destroy).

Add resource tags/labels like:

```
tags = {
  Environment = "Demo"
}
```
---

### 7. Provider & Authentication

Clearly document provider setup:
```
provider "ibm" {
  ibmcloud_api_key = var.ibmcloud_api_key
  region           = var.region
}

```
Use variables for credentials or rely on environment variables:

```
export IC_API_KEY=<your-ibmcloud-api-key>
```

---
Example Project Structure

```
terraform-ibm-demo/
│── main.tf               # Root module calling submodules
│── variables.tf          # Input variables with defaults
│── outputs.tf            # Outputs (IP, URLs, bucket name, etc.)
│── providers.tf          # IBM Cloud provider config
│── README.md             # Documentation
│
├── modules/
│   ├── network/
│   │   ├── main.tf       # Defines VPC, subnets, SGs
│   │   ├── variables.tf
│   │   └── outputs.tf
│   │
│   ├── compute/
│   │   ├── main.tf       # Defines VSI (VM) resources
│   │   ├── variables.tf
│   │   └── outputs.tf
│   │
│   └── storage/
│       ├── main.tf       # Defines Object Storage bucket
│       ├── variables.tf
│       └── outputs.tf
```

---

### 7. Cleanup

To remove resources and avoid costs:

```
terraform destroy -auto-approve
```
