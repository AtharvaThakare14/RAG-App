# Database Module variables.tf
variable "project_name" {
  description = "Name of the project"
  type        = string
}

variable "stage" {
  description = "Deployment stage (dev, staging, prod)"
  type        = string
}

variable "aws_region" {
  description = "AWS region for all resources"
  type        = string
  default     = "us-east-1"
}

variable "db_subnet_group_name" {
  description = "Name of the DB subnet group"
  type        = string
}

variable "db_security_group_id" {
  description = "ID of the security group for the database"
  type        = string
}

variable "db_instance_class" {
  description = "Instance class for the RDS instance"
  type        = string
  default     = "db.t3.micro"
}

variable "db_allocated_storage" {
  description = "Allocated storage for the RDS instance in GiB"
  type        = number
  default     = 20
}

variable "db_engine_version" {
  description = "Engine version for PostgreSQL"
  type        = string
  default     = "15"
}

variable "db_name" {
  description = "Name of the database"
  type        = string
  default     = "ragapp"
}

variable "db_username" {
  description = "Username for the database"
  type        = string
  default     = "ragadmin"
}

variable "skip_final_snapshot" {
  description = "Whether to skip the final snapshot when the database is deleted"
  type        = bool
  default     = true
}

variable "import_db" {
  description = "Whether to import existing database"
  type        = bool
  default     = false
}

variable "reset_db_password" {
  description = "Flag to reset the database password"
  type        = bool
  default     = false
}