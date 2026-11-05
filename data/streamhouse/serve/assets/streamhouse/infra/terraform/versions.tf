terraform {
  required_version = ">= 1.5.0"
  required_providers {
    confluent = {
      source  = "confluentinc/confluent"
      version = "= 2.87.0"
    }
    time = {
      source  = "hashicorp/time"
      version = "~> 0.13"
    }
  }
}

# CONFLUENT_CLOUD_API_KEY and CONFLUENT_CLOUD_API_SECRET are read from
# the deployment process environment. Never store them in tfvars or Git.
provider "confluent" {}
