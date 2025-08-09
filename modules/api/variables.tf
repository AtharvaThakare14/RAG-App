#API Module
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

variable "document_processor_arn" {
  description = "ARN of the document processor Lambda function"
  type        = string
}

variable "query_processor_arn" {
  description = "ARN of the query processor Lambda function"
  type        = string
}

variable "upload_handler_arn" {
  description = "ARN of the upload handler Lambda function"
  type        = string
}

variable "query_processor_name" {
  description = "Name of the query processor Lambda function"
  type        = string
}

variable "upload_handler_name" {
  description = "Name of the upload handler Lambda function"
  type        = string
}

variable "auth_handler_arn" {
  description = "ARN of the auth handler Lambda function"
  type        = string
}

variable "auth_handler_name" {
  description = "Name of the auth handler Lambda function"
  type        = string
}

variable "cognito_user_pool_id" {
  description = "ID of the Cognito User Pool"
  type        = string
}

variable "cognito_app_client_id" {
  description = "ID of the Cognito App Client"
  type        = string
}

variable "cognito_user_pool_arn" {
  description = "ARN of the Cognito User Pool"
  type        = string
}

variable "cognito_domain" {
  type = string
}