output "documents_bucket_name" {
  description = "Name of the document bucket"
  value       = aws_s3_bucket.documents.bucket
}

output "documents_bucket_arn" {
  description = "ARN of the document bucket"
  value       = aws_s3_bucket.documents.arn
}

output "metadata_table_name" {
  description = "Name of the DynamoDB metadata table"
  value       = aws_dynamodb_table.metadata.name
}

output "metadata_table_arn" {
  description = "ARN of the DynamoDB metadata table"
  value       = aws_dynamodb_table.metadata.arn
}