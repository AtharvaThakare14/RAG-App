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
}

variable "alert_email" {
  description = "Email address for CloudWatch alerts"
  type        = string
}

variable "document_processor_name" {
  description = "Name of the document processor Lambda function"
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

variable "auth_handler_name" {
  description = "Name of the auth handler Lambda function"
  type        = string
}