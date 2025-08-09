# =========================
# Root variables.tf
# =========================

# -------------------------
# Project Configuration
# -------------------------
variable "aws_region" {
  description = "AWS region for all resources"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Name of the project"
  type        = string
}

variable "stage" {
  description = "Deployment stage (dev, staging, prod)"
  type        = string
  default     = "staging"
}

# -------------------------
# Lambda Configuration
# -------------------------
variable "lambda_memory_size" {
  description = "Memory size for Lambda functions in MB"
  type        = number
  default     = 4096
}

variable "lambda_timeout" {
  description = "Timeout for Lambda functions in seconds"
  type        = number
  default     = 120
}

# -------------------------
# VPC Configuration
# -------------------------
variable "vpc_cidr" {
  description = "CIDR block for the VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "az_count" {
  description = "Number of Availability Zones to use"
  type        = number
  default     = 2
}

variable "single_nat_gateway" {
  description = "NAT Gateway to use"
  type        = bool
  default     = true
}

variable "enable_flow_logs" {
  description = "Enable flow log"
  type        = bool
  default     = false
}

variable "bastion_allowed_cidr" {
  description = "CIDR blocks allowed to connect to bastion hosts"
  type        = list(string)
  default     = ["0.0.0.0/0"]  # Should be restricted to your company IP range in production
}

variable "create_bastion_sg" {
  description = "Create a security group for bastion hosts"
  type        = bool
  default     = true
}

# -------------------------
# Database Configuration
# -------------------------
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

variable "import_db" {
  description = "Whether to import existing database instead of creating a new one"
  type        = bool
  default     = false
}

variable "reset_db_password" {
  description = "Flag to reset the database password"
  type        = bool
  default     = false
}

# -------------------------
# Storage Configuration
# -------------------------
variable "enable_lifecycle_rules" {
  description = "Enable S3 lifecycle rules for cost optimization"
  type        = bool
  default     = true
}

variable "standard_ia_transition_days" {
  description = "Days before transitioning to STANDARD_IA storage class"
  type        = number
  default     = 90
}

variable "glacier_transition_days" {
  description = "Days before transitioning to GLACIER storage class"
  type        = number
  default     = 365
}

# -------------------------
# Monitoring Configuration
# -------------------------
variable "alert_email" {
  description = "Email address for CloudWatch alerts"
  type        = string
  default     = ""  # Set this in your tfvars file
}

# -------------------------
# Dashboard References
# -------------------------
variable "metadata_table_name" {
  description = "Name of the DynamoDB table for metadata (used in prod dashboards)"
  type        = string
  default     = ""
}

variable "documents_bucket_name" {
  description = "Name of the S3 bucket for documents (used in prod dashboards)"
  type        = string
  default     = ""
}

# -------------------------
# GitHub Repo
# -------------------------
variable "github_repo" {
  description = "GitHub Repo Name"
  type        = string
  default     = "genieincodebottle/rag-app-on-aws"
}

variable "github_branch" {
  description = "GitHub Branch"
  type        = string
  default     = "main"
}