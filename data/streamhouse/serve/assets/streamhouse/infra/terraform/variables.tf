variable "deployment_name" {
  description = "Isolated demo name; must be unique per Terraform state."
  type        = string
  default     = "factory-pulse-demo"
  validation {
    condition     = can(regex("^[a-z][a-z0-9-]{2,38}$", var.deployment_name))
    error_message = "Use 3-39 lowercase letters, numbers, or hyphens; start with a letter."
  }
}

variable "region" {
  type        = string
  default     = "us-east-2"
  description = "Confluent Cloud AWS region; select one that supports ALL desired add-ons."
}

variable "enable_flink" {
  type        = bool
  default     = true
  description = "Create Flink compute pool and deploy three continuous CTAS statements."
}

variable "enable_tableflow" {
  type        = bool
  default     = true
  description = "Enable Confluent-managed Iceberg Tableflow on IoT telemetry."
}

variable "enable_rtce" {
  type        = bool
  default     = true
  description = "Enable RTCE on asset state and generate a global MCP API key."
}

variable "flink_max_cfu" {
  type        = number
  default     = 5
  validation {
    condition     = contains([5, 10, 20, 30, 40, 50], var.flink_max_cfu)
    error_message = "Confluent supports max CFUs 5, 10, 20, 30, 40, or 50."
  }
}

variable "confluent_cloud_api_key" {
  description = "Confluent Cloud API key used to authenticate the Terraform provider."
  type        = string
  sensitive   = true
}

variable "confluent_cloud_api_secret" {
  description = "Confluent Cloud API secret paired with confluent_cloud_api_key."
  type        = string
  sensitive   = true
}
