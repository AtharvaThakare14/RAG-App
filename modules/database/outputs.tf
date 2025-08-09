output "db_instance_id" {
  description = "ID of the RDS instance"
  value       = local.create_db && length(aws_db_instance.postgres) > 0 ? aws_db_instance.postgres[0].id : "${local.name}-postgres"
}

output "db_instance_address" {
  description = "The address of the RDS instance"
  value       = local.create_db && length(aws_db_instance.postgres) > 0 ? aws_db_instance.postgres[0].address : local.db_endpoint_fallback
}

output "db_instance_endpoint" {
  description = "The connection endpoint of the RDS instance"
  value       = local.create_db && length(aws_db_instance.postgres) > 0 ? aws_db_instance.postgres[0].endpoint : "${local.db_endpoint_fallback}:${local.db_port_fallback}"
}

output "db_instance_port" {
  description = "The port of the RDS instance"
  value       = local.create_db && length(aws_db_instance.postgres) > 0 ? aws_db_instance.postgres[0].port : local.db_port_fallback
}

output "db_credentials_secret_arn" {
  description = "ARN of the Secrets Manager secret containing the database credentials"
  value       = aws_secretsmanager_secret.db_credentials.arn
}