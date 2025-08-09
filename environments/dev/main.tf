# ============================================================
# Root Module for RAG Application Deployment in Dev env (main.tf)
# ============================================================
# Provisions project-wide infrastructure by composing all modules

# =====================================
# S3 Bucket to Store Lambda ZIP Artifacts
# =====================================

resource "aws_s3_bucket" "lambda_code" {
  bucket = "${var.project_name}-${var.stage}-lambda-code"
  
  tags = {
    Name = "${var.project_name}-${var.stage}-lambda-code"
    Environment = var.stage
  }
  
  # Prevent destruction of existing buckets
  lifecycle {
    prevent_destroy = true
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "lambda_code" {
  bucket = aws_s3_bucket.lambda_code.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "lambda_code" {
  bucket                  = aws_s3_bucket.lambda_code.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_versioning" "lambda_code" {
  bucket = aws_s3_bucket.lambda_code.id
  
  versioning_configuration {
    status = "Enabled"
  }
}

# ====================
# VPC Networking Module
# ====================

module "vpc" {
  source = "../../modules/vpc"
  
  project_name = var.project_name
  stage        = var.stage
  aws_region   = var.aws_region
  vpc_cidr     = var.vpc_cidr
  az_count     = var.az_count
  
  # Cost optimization - use single NAT gateway for non-prod environments
  single_nat_gateway = var.stage != "prod"
  
  # Enable flow logs only in production for better monitoring
  enable_flow_logs = var.stage == "prod"
  
  # Create bastion security group in dev environment
  create_bastion_sg = var.stage == "dev"
  bastion_allowed_cidr = var.bastion_allowed_cidr
}

# =======================
# Storage (S3 + DynamoDB)
# =======================

module "storage" {
  source = "../../modules/storage"
  
  project_name = var.project_name
  stage        = var.stage
  
  # Add these optional variables if you want to customize S3 lifecycle rules
  enable_lifecycle_rules     = var.enable_lifecycle_rules
  standard_ia_transition_days = var.standard_ia_transition_days
  glacier_transition_days    = var.glacier_transition_days
}

# =====================
# Database (PostgreSQL)
# =====================

module "database" {
  source = "../../modules/database"
  
  project_name       = var.project_name
  stage              = var.stage
  db_subnet_group_name = module.vpc.db_subnet_group_name
  db_security_group_id = module.vpc.database_security_group_id
  db_instance_class  = var.db_instance_class
  db_allocated_storage = var.db_allocated_storage
  db_name           = var.db_name
  db_username       = var.db_username
  
  # Add this new variable to control password resets
  reset_db_password = var.reset_db_password
  
  # This should already be in your config, but make sure it's properly set
  import_db = var.import_db
  
  depends_on = [module.vpc]
}

# Add auth module before api and compute modules
module "auth" {
  source = "../../modules/auth"
  
  project_name = var.project_name
  stage        = var.stage
}

# ====================
# API Gateway Module
# ====================

module "api" {
  source = "../../modules/api"
  
  project_name            = var.project_name
  stage                   = var.stage
  aws_region              = var.aws_region
  document_processor_arn  = module.compute.document_processor_arn
  query_processor_arn     = module.compute.query_processor_arn
  upload_handler_arn      = module.compute.upload_handler_arn
  query_processor_name    = module.compute.query_processor_name
  upload_handler_name     = module.compute.upload_handler_name
  
  auth_handler_arn  = module.compute.auth_handler_arn 
  auth_handler_name = module.compute.auth_handler_name
  
  # Auth references from auth module
  cognito_user_pool_id  = module.auth.cognito_user_pool_id
  cognito_app_client_id = module.auth.cognito_app_client_id
  cognito_user_pool_arn = module.auth.cognito_user_pool_arn
  cognito_domain         = module.auth.cognito_domain

  
  # Make sure compute and auth modules are created first
  depends_on = [module.compute, module.auth]
}

# =======================
# Compute (Lambda System)
# =======================

module "compute" {
  source = "../../modules/compute"
  
  project_name      = var.project_name
  stage             = var.stage
  lambda_memory_size = var.lambda_memory_size
  lambda_timeout    = var.lambda_timeout
  
  # Pass outputs from storage module
  documents_bucket  = module.storage.documents_bucket_name
  metadata_table    = module.storage.metadata_table_name
  lambda_code_bucket = aws_s3_bucket.lambda_code.bucket
  
  # Pass VPC configuration
  vpc_subnet_ids          = module.vpc.private_subnet_ids
  lambda_security_group_id = module.vpc.lambda_security_group_id
  db_secret_arn           = module.database.db_credentials_secret_arn
  
  # Add Cognito details from auth module
  cognito_user_pool_id    = module.auth.cognito_user_pool_id
  cognito_app_client_id   = module.auth.cognito_app_client_id
  cognito_user_pool_arn   = module.auth.cognito_user_pool_arn
  
  depends_on = [module.storage, module.vpc, module.database, module.auth]
}


# ===================
# Monitoring & Alerts
# ===================

module "monitoring" {
  source = "../../modules/monitoring"
  
  project_name              = var.project_name
  stage                     = var.stage
  aws_region                = var.aws_region
  alert_email               = var.alert_email
  document_processor_name   = module.compute.document_processor_name
  query_processor_name      = module.compute.query_processor_name
  upload_handler_name       = module.compute.upload_handler_name
  auth_handler_name         = module.compute.auth_handler_name
  
  depends_on = [module.compute]
}

# ===================
# Outputs
# ===================

output "api_endpoint" {
  description = "URL of the API endpoint"
  value       = module.api.api_endpoint
}

output "document_bucket" {
  description = "Name of the document bucket"
  value       = module.storage.documents_bucket_name
}

output "dynamodb_table" {
  description = "Name of the DynamoDB metadata table"
  value       = module.storage.metadata_table_name
}

output "vpc_id" {
  description = "ID of the VPC"
  value       = module.vpc.vpc_id
}

output "db_endpoint" {
  description = "Endpoint of the PostgreSQL database"
  value       = module.database.db_instance_endpoint
}

output "cognito_user_pool_id" {
  description = "ID of the Cognito User Pool"
  value       = module.auth.cognito_user_pool_id
}

output "cognito_app_client_id" {
  description = "ID of the Cognito App Client"
  value       = module.auth.cognito_app_client_id
}

output "cognito_domain" {
  description = "Cognito domain for hosted UI"
  value       = module.auth.cognito_domain
}

output "auth_endpoint" {
  description = "URL of the auth endpoint"
  value       = "${module.api.api_endpoint}/auth"
}