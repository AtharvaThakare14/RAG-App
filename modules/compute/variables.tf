#Compute Module
# =========================
# Lambda Module Variables
# =========================

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

# -------------------------
# Lambda Configuration
# -------------------------
variable "lambda_memory_size" {
  description = "Memory size for Lambda functions in MB"
  type        = number
  default     = 256
}

variable "lambda_timeout" {
  description = "Timeout for Lambda functions in seconds"
  type        = number
  default     = 30
}

# -------------------------
# Storage & Metadata
# -------------------------
variable "documents_bucket" {
  description = "Name of the S3 bucket for documents"
  type        = string
}

variable "metadata_table" {
  description = "Name of the DynamoDB table for metadata"
  type        = string
}

# -------------------------
# Networking Configuration
# -------------------------
variable "vpc_subnet_ids" {
  description = "List of subnet IDs for Lambda functions"
  type        = list(string)
  default     = []
}

variable "lambda_security_group_id" {
  description = "ID of the security group for Lambda functions"
  type        = string
  default     = ""
}

# -------------------------
# Secrets and Lambda Code
# -------------------------
variable "db_secret_arn" {
  description = "ARN of the Secrets Manager secret containing database credentials"
  type        = string
  default     = ""
}

variable "lambda_code_bucket" {
  description = "Name of the S3 bucket for Lambda code"
  type        = string
}

# -------------------------
# Gemini Configuration
# -------------------------
variable "gemini_embedding_model" {
  description = "Gemini Embedding model to use"
  type        = string
  default     = "text-embedding-004"
}

variable "gemini_api_key" {
  description = "Google's Gemini API Key"
  type        = string
  default     = "PLACE_HOLDER"
}

variable "max_retries" {
  description = "Max Retry"
  type        = number
  default     = 5
}

variable "retry_delay" {
  description = "Retry Delay"
  type        = number
  default     = 10
}

variable "cognito_user_pool_id" {
  description = "ID of the Cognito User Pool"
  type        = string
  default     = ""
}

variable "cognito_app_client_id" {
  description = "ID of the Cognito App Client"
  type        = string
  default     = ""
}

variable "cognito_user_pool_arn" {
  description = "ARN of the Cognito User Pool"
  type        = string
  default     = ""
}