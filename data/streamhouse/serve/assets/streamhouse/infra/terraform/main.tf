data "confluent_organization" "current" {}

locals {
  source_topics  = toset(["factory-iot-telemetry", "factory-asset-state", "factory-maintenance-events"])
  derived_topics = toset(["factory-risk-signals", "factory-shift-kpis", "factory-quality-alerts", "factory-governed-telemetry"])
  source_schema_files = {
    for filename in fileset("${path.module}/schemas", "*.json") :
    trimsuffix(filename, ".json") => filename
  }
  flink_jobs = {
    risk    = "02-risk-ctas.sql"
    quality = "03-quality-ctas.sql"
    kpis    = "04-shift-kpis-ctas.sql"
    governance = "05-governed-topic-ctas.sql"
  }
}

resource "confluent_environment" "demo" {
  display_name = var.deployment_name
  stream_governance {
    package = "ESSENTIALS"
  }
}

resource "confluent_kafka_cluster" "demo" {
  display_name = "${var.deployment_name}-kafka"
  availability = "SINGLE_ZONE"
  cloud        = "AWS"
  region       = var.region
  standard {}
  environment {
    id = confluent_environment.demo.id
  }
}

data "confluent_schema_registry_cluster" "demo" {
  environment {
    id = confluent_environment.demo.id
  }
  depends_on = [confluent_kafka_cluster.demo]
}

# The automation principal is deliberately elevated for repeatable demos.
# Use a dedicated Confluent Cloud sandbox organization, never production.
resource "confluent_service_account" "manager" {
  display_name = "${var.deployment_name}-admin"
  description  = "Factory Pulse sandbox automation for Flink, schemas, Tableflow and RTCE"
}
resource "confluent_role_binding" "manager_org_admin" {
  principal   = "User:${confluent_service_account.manager.id}"
  role_name   = "OrganizationAdmin"
  crn_pattern = data.confluent_organization.current.resource_name
}

resource "confluent_service_account" "app" {
  display_name = "${var.deployment_name}-app"
  description  = "Factory Pulse simulator Kafka producer and derived-topic consumer"
}

# Propagation wait avoids 403 on immediately-created resource scoped keys.
# 60s is required in practice; 25s is insufficient for cross-region propagation.
resource "time_sleep" "rbac" {
  create_duration = "60s"
  depends_on      = [confluent_role_binding.manager_org_admin]
}

resource "confluent_api_key" "admin_kafka" {
  display_name = "${var.deployment_name}-kafka-admin"
  owner {
    id          = confluent_service_account.manager.id
    api_version = confluent_service_account.manager.api_version
    kind        = confluent_service_account.manager.kind
  }
  managed_resource {
    id          = confluent_kafka_cluster.demo.id
    api_version = confluent_kafka_cluster.demo.api_version
    kind        = confluent_kafka_cluster.demo.kind
    environment { id = confluent_environment.demo.id }
  }
  depends_on = [time_sleep.rbac]
}

resource "confluent_api_key" "app_kafka" {
  display_name = "${var.deployment_name}-app-kafka"
  owner {
    id          = confluent_service_account.app.id
    api_version = confluent_service_account.app.api_version
    kind        = confluent_service_account.app.kind
  }
  managed_resource {
    id          = confluent_kafka_cluster.demo.id
    api_version = confluent_kafka_cluster.demo.api_version
    kind        = confluent_kafka_cluster.demo.kind
    environment { id = confluent_environment.demo.id }
  }
}

resource "confluent_kafka_topic" "source" {
  for_each = local.source_topics
  kafka_cluster { id = confluent_kafka_cluster.demo.id }
  topic_name    = each.key
  partitions_count = 3
  rest_endpoint = confluent_kafka_cluster.demo.rest_endpoint
  credentials {
    key    = confluent_api_key.admin_kafka.id
    secret = confluent_api_key.admin_kafka.secret
  }
  # IMPORTANT: asset-state is intentionally NOT compacted: RTCE append mode
  # accepts JSON Schema keys. Upsert mode requires raw bytes keys.
  config = {
    "retention.ms" = "604800000"
  }
}

resource "confluent_kafka_acl" "app_source_write" {
  for_each      = local.source_topics
  kafka_cluster { id = confluent_kafka_cluster.demo.id }
  resource_type = "TOPIC"
  resource_name = confluent_kafka_topic.source[each.key].topic_name
  pattern_type  = "LITERAL"
  principal     = "User:${confluent_service_account.app.id}"
  host          = "*"
  operation     = "WRITE"
  permission    = "ALLOW"
  rest_endpoint = confluent_kafka_cluster.demo.rest_endpoint
  credentials {
    key    = confluent_api_key.admin_kafka.id
    secret = confluent_api_key.admin_kafka.secret
  }
}

resource "confluent_kafka_acl" "app_source_describe" {
  for_each      = local.source_topics
  kafka_cluster { id = confluent_kafka_cluster.demo.id }
  resource_type = "TOPIC"
  resource_name = confluent_kafka_topic.source[each.key].topic_name
  pattern_type  = "LITERAL"
  principal     = "User:${confluent_service_account.app.id}"
  host          = "*"
  operation     = "DESCRIBE"
  permission    = "ALLOW"
  rest_endpoint = confluent_kafka_cluster.demo.rest_endpoint
  credentials {
    key    = confluent_api_key.admin_kafka.id
    secret = confluent_api_key.admin_kafka.secret
  }
}

resource "confluent_kafka_acl" "app_derived_read" {
  for_each      = var.enable_flink ? local.derived_topics : toset([])
  kafka_cluster { id = confluent_kafka_cluster.demo.id }
  resource_type = "TOPIC"
  resource_name = each.key
  pattern_type  = "LITERAL"
  principal     = "User:${confluent_service_account.app.id}"
  host          = "*"
  operation     = "READ"
  permission    = "ALLOW"
  rest_endpoint = confluent_kafka_cluster.demo.rest_endpoint
  credentials {
    key    = confluent_api_key.admin_kafka.id
    secret = confluent_api_key.admin_kafka.secret
  }
}

resource "confluent_kafka_acl" "app_consumer_group" {
  count         = var.enable_flink ? 1 : 0
  kafka_cluster { id = confluent_kafka_cluster.demo.id }
  resource_type = "GROUP"
  resource_name = "factory-pulse-output-"
  pattern_type  = "PREFIXED"
  principal     = "User:${confluent_service_account.app.id}"
  host          = "*"
  operation     = "READ"
  permission    = "ALLOW"
  rest_endpoint = confluent_kafka_cluster.demo.rest_endpoint
  credentials {
    key    = confluent_api_key.admin_kafka.id
    secret = confluent_api_key.admin_kafka.secret
  }
}

resource "confluent_api_key" "schema_registry" {
  display_name = "${var.deployment_name}-schema-registry"
  owner {
    id          = confluent_service_account.manager.id
    api_version = confluent_service_account.manager.api_version
    kind        = confluent_service_account.manager.kind
  }
  managed_resource {
    id          = data.confluent_schema_registry_cluster.demo.id
    api_version = data.confluent_schema_registry_cluster.demo.api_version
    kind        = data.confluent_schema_registry_cluster.demo.kind
    environment { id = confluent_environment.demo.id }
  }
  depends_on = [time_sleep.rbac]
}

# Register the EXACT JSON schemas used by the Node.js simulator so Flink,
# Tableflow and RTCE can infer the topic structure before app startup.
resource "confluent_schema" "source_subject" {
  for_each = local.source_schema_files
  schema_registry_cluster { id = data.confluent_schema_registry_cluster.demo.id }
  rest_endpoint = data.confluent_schema_registry_cluster.demo.rest_endpoint
  subject_name  = each.key
  format        = "JSON"
  schema        = file("${path.module}/schemas/${each.value}")
  credentials {
    key    = confluent_api_key.schema_registry.id
    secret = confluent_api_key.schema_registry.secret
  }
  depends_on = [confluent_kafka_topic.source]
}

# The business actions (maintenance dispatch) are intentionally NOT Topic
# Actions. Confluent UI Topic Actions can be demonstrated independently.

# A fresh region-specific Flink key and compute pool for continuous transforms.
resource "confluent_flink_compute_pool" "demo" {
  count        = var.enable_flink ? 1 : 0
  display_name = "${var.deployment_name}-flink"
  cloud        = "AWS"
  region       = var.region
  max_cfu      = var.flink_max_cfu
  environment { id = confluent_environment.demo.id }
}

data "confluent_flink_region" "demo" {
  count  = var.enable_flink ? 1 : 0
  cloud  = "AWS"
  region = var.region
}

resource "confluent_api_key" "flink" {
  count        = var.enable_flink ? 1 : 0
  display_name = "${var.deployment_name}-flink"
  owner {
    id          = confluent_service_account.manager.id
    api_version = confluent_service_account.manager.api_version
    kind        = confluent_service_account.manager.kind
  }
  managed_resource {
    id          = data.confluent_flink_region.demo[0].id
    api_version = data.confluent_flink_region.demo[0].api_version
    kind        = data.confluent_flink_region.demo[0].kind
    environment { id = confluent_environment.demo.id }
  }
  depends_on = [time_sleep.rbac]
}

resource "time_sleep" "flink_catalog" {
  count           = var.enable_flink ? 1 : 0
  create_duration = "45s"
  depends_on      = [confluent_schema.source_subject]
}

resource "confluent_flink_statement" "pipeline" {
  for_each = var.enable_flink ? local.flink_jobs : {}
  organization { id = data.confluent_organization.current.id }
  environment  { id = confluent_environment.demo.id }
  compute_pool { id = confluent_flink_compute_pool.demo[0].id }
  principal    { id = confluent_service_account.manager.id }
  statement    = trimspace(file("${path.module}/sql/${each.value}"))
  properties = {
    "sql.current-catalog"  = confluent_environment.demo.display_name
    "sql.current-database" = confluent_kafka_cluster.demo.display_name
  }
  rest_endpoint = data.confluent_flink_region.demo[0].rest_endpoint
  credentials {
    key    = confluent_api_key.flink[0].id
    secret = confluent_api_key.flink[0].secret
  }
  depends_on = [time_sleep.flink_catalog]
}

resource "confluent_api_key" "tableflow" {
  count        = var.enable_tableflow ? 1 : 0
  display_name = "${var.deployment_name}-tableflow"
  owner {
    id          = confluent_service_account.manager.id
    api_version = confluent_service_account.manager.api_version
    kind        = confluent_service_account.manager.kind
  }
  managed_resource {
    id          = "tableflow"
    api_version = "tableflow/v1"
    kind        = "Tableflow"
  }
  depends_on = [time_sleep.rbac]
}

resource "confluent_tableflow_topic" "telemetry" {
  count = var.enable_tableflow ? 1 : 0
  environment { id = confluent_environment.demo.id }
  kafka_cluster { id = confluent_kafka_cluster.demo.id }
  display_name  = confluent_kafka_topic.source["factory-iot-telemetry"].topic_name
  table_formats = ["ICEBERG"]
  managed_storage {}
  credentials {
    key    = confluent_api_key.tableflow[0].id
    secret = confluent_api_key.tableflow[0].secret
  }
  depends_on = [confluent_schema.source_subject]
}

resource "confluent_rtce_topic" "asset_state" {
  count       = var.enable_rtce ? 1 : 0
  cloud       = "AWS"
  region      = var.region
  topic_name  = confluent_kafka_topic.source["factory-asset-state"].topic_name
  description = "Current robot health, vibration, temperature, site and line context for synthetic US factories. Append events; assetId and siteId identify an asset."
  environment { id = confluent_environment.demo.id }
  kafka_cluster { id = confluent_kafka_cluster.demo.id }
  depends_on = [confluent_schema.source_subject]
}

# Global-scoped API key required for Confluent RTCE MCP Basic authentication.
# The demo automation principal has broad rights; restrict before production.
resource "confluent_api_key" "mcp_global" {
  count        = var.enable_rtce ? 1 : 0
  display_name = "${var.deployment_name}-rtce-mcp"
  description  = "Global key for Factory Pulse RTCE MCP tool explorer"
  owner {
    id          = confluent_service_account.manager.id
    api_version = confluent_service_account.manager.api_version
    kind        = confluent_service_account.manager.kind
  }
  # Omitting managed_resource creates a Global API Key (not resource-scoped).
  depends_on = [time_sleep.rbac]
}
