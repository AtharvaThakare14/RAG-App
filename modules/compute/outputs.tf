#Compute Module
# =========================
# Lambda Function Outputs
# =========================

output "document_processor_arn" {
  description = "ARN of the document processor Lambda function"
  value       = aws_lambda_function.document_processor.arn
}

output "query_processor_arn" {
  description = "ARN of the query processor Lambda function"
  value       = aws_lambda_function.query_processor.arn
}

output "upload_handler_arn" {
  description = "ARN of the upload handler Lambda function"
  value       = aws_lambda_function.upload_handler.arn
}

output "document_processor_name" {
  description = "Name of the document processor Lambda function"
  value       = aws_lambda_function.document_processor.function_name
}

output "query_processor_name" {
  description = "Name of the query processor Lambda function"
  value       = aws_lambda_function.query_processor.function_name
}

output "upload_handler_name" {
  description = "Name of the upload handler Lambda function"
  value       = aws_lambda_function.upload_handler.function_name
}

output "lambda_role_arn" {
  description = "ARN of the IAM role for Lambda functions"
  value       = aws_iam_role.lambda_role.arn
}

output "auth_handler_arn" {
  description = "ARN of the auth handler Lambda function"
  value       = aws_lambda_function.auth_handler.arn
}

output "auth_handler_name" {
  description = "Name of the auth handler Lambda function"
  value       = aws_lambda_function.auth_handler.function_name
}