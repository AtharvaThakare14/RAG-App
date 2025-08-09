# ================================================
# Storage Module for RAG System (S3 + DynamoDB)
# ================================================
# Provisions secure document storage and metadata store with best practices

# ==============================
# Locals
# ==============================

locals {
  bucket_name = "${var.project_name}-${var.stage}-documents"

  common_tags = {
    Project     = var.project_name
    Environment = var.stage
    ManagedBy   = "Terraform"
  }
}

# ==============================
# Document Storage - S3 bucket
# ==============================

resource "aws_s3_bucket" "documents" {
  bucket = local.bucket_name
  
  tags = {
    Name = local.bucket_name
    Environment = var.stage
  }
  
  # Prevent destruction of existing buckets
  lifecycle {
    prevent_destroy = true
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "documents" {
  bucket = aws_s3_bucket.documents.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_cors_configuration" "documents" {
  bucket = aws_s3_bucket.documents.id

  cors_rule {
    allowed_headers = ["*"]
    allowed_methods = ["GET", "POST", "PUT"]
    allowed_origins = ["*"]
    max_age_seconds = 3000
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "documents" {
  bucket = aws_s3_bucket.documents.id
  
  rule {
    id = "archive-old-documents"
    status = "Enabled"
    
    filter {
      prefix = ""  # applies lifecycle rule to entire bucket
    }

    
    transition {
      days = 90
      storage_class = "STANDARD_IA"
    }
    
    transition {
      days = 365
      storage_class = "GLACIER"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "documents" {
  bucket                  = aws_s3_bucket.documents.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# ==============================
# DynamoDB for metadata storage
# ==============================

locals {
  table_name = "${var.project_name}-${var.stage}-metadata"
}

# DynamoDB for metadata storage
resource "aws_dynamodb_table" "metadata" {
  name         = local.table_name
  billing_mode = "PAY_PER_REQUEST"  # Serverless - pay only for what you use
  hash_key     = "id"
  
  # Only define attributes used in key schemas
  attribute {
    name = "id"
    type = "S"
  }
  
  attribute {
    name = "user_id"
    type = "S"
  }
  
  attribute {
    name = "document_id"
    type = "S"
  }
  
  global_secondary_index {
    name               = "UserIndex"
    hash_key           = "user_id"
    projection_type    = "ALL"
  }
  
  global_secondary_index {
    name               = "DocumentIndex"
    hash_key           = "document_id"
    projection_type    = "ALL"
  }
  
  point_in_time_recovery {
    enabled = true
  }
  
  server_side_encryption {
    enabled = false
  }
  
  tags = {
    Name = local.table_name
    Environment = var.stage
  }
  
  # Prevent destruction of existing tables
  lifecycle {
    prevent_destroy = true
  }
}