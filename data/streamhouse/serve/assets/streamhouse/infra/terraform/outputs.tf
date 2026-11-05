output "environment_id"      { value = confluent_environment.demo.id }
output "organization_id"     { value = data.confluent_organization.current.id }
output "cluster_id"          { value = confluent_kafka_cluster.demo.id }
output "cluster_name"        { value = confluent_kafka_cluster.demo.display_name }
output "environment_name"    { value = confluent_environment.demo.display_name }
output "region"              { value = var.region }
output "kafka_bootstrap"     { value = replace(confluent_kafka_cluster.demo.bootstrap_endpoint, "SASL_SSL://", "") }
output "schema_registry_url" { value = data.confluent_schema_registry_cluster.demo.rest_endpoint }
output "flink_compute_pool_id" { value = var.enable_flink ? confluent_flink_compute_pool.demo[0].id : null }
output "flink_statement_ids" { value = { for name, job in confluent_flink_statement.pipeline : name => job.id } }
output "tableflow_enabled"  { value = var.enable_tableflow }
output "rtce_enabled"       { value = var.enable_rtce }
output "mcp_endpoint" {
  value = var.enable_rtce ? "https://mcp.${var.region}.aws.confluent.cloud/mcp/v1/context-engine/organizations/${data.confluent_organization.current.id}/environments/${confluent_environment.demo.id}/kafka-clusters/${confluent_kafka_cluster.demo.id}" : null
}
output "kafka_app_key" {
  value = confluent_api_key.app_kafka.id
  sensitive = true
}
output "kafka_app_secret" {
  value = confluent_api_key.app_kafka.secret
  sensitive = true
}
output "schema_registry_key" {
  value = confluent_api_key.schema_registry.id
  sensitive = true
}
output "schema_registry_secret" {
  value = confluent_api_key.schema_registry.secret
  sensitive = true
}
output "mcp_global_key" {
  value = var.enable_rtce ? confluent_api_key.mcp_global[0].id : null
  sensitive = true
}
output "mcp_global_secret" {
  value = var.enable_rtce ? confluent_api_key.mcp_global[0].secret : null
  sensitive = true
}
output "tableflow_key" {
  value = var.enable_tableflow ? confluent_api_key.tableflow[0].id : null
  sensitive = true
}
output "tableflow_secret" {
  value = var.enable_tableflow ? confluent_api_key.tableflow[0].secret : null
  sensitive = true
}
