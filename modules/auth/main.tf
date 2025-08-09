# /modules/auth/main.tf
resource "aws_cognito_user_pool" "main" {
  name = "${var.project_name}-${var.stage}-user-pool"
  
  # Password policy
  password_policy {
    minimum_length    = 8
    require_lowercase = true
    require_numbers   = true
    require_symbols   = true
    require_uppercase = true
  }
  
  # Auto-verification of email
  verification_message_template {
    default_email_option = "CONFIRM_WITH_CODE"
  }

  email_configuration {
    email_sending_account = "COGNITO_DEFAULT"
  }

  # Enable username attributes
  username_attributes = ["email"]

  auto_verified_attributes = ["email"]
  
  # Schema attributes
  schema {
    name                = "email"
    attribute_data_type = "String"
    mutable             = true
    required            = true
  }
  
  # MFA configuration
  mfa_configuration = "OFF"
  
  lifecycle {
    ignore_changes = [schema]
  }
}

resource "aws_cognito_user_pool_domain" "main" {
  domain       = "${var.project_name}-${var.stage}-auth"
  user_pool_id = aws_cognito_user_pool.main.id
}

# App client for frontend application
resource "aws_cognito_user_pool_client" "streamlit_client" {
  name                   = "${var.project_name}-${var.stage}-streamlit-client"
  user_pool_id           = aws_cognito_user_pool.main.id
  generate_secret        = false
  refresh_token_validity = 30
  access_token_validity  = 1
  id_token_validity      = 1
  
  # Explicitly set allowed OAuth flows and scopes
  allowed_oauth_flows                  = ["implicit"]
  allowed_oauth_flows_user_pool_client = true
  allowed_oauth_scopes                 = ["email", "openid", "profile"]
  
  # Add explicit auth flows to enable USER_PASSWORD_AUTH
  explicit_auth_flows = ["ALLOW_USER_PASSWORD_AUTH", "ALLOW_REFRESH_TOKEN_AUTH", "ALLOW_USER_SRP_AUTH"]

  callback_urls = ["http://localhost:8501/"]
  logout_urls   = ["http://localhost:8501/"]
  
  token_validity_units {
    access_token  = "hours"
    id_token      = "hours"
    refresh_token = "days"
  }
}