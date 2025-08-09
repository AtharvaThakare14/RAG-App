# ================================================
# Monitoring Module for RAG System (Logs & Alerts)
# ================================================
# Creates CloudWatch Log Groups, SNS Alerting, and Lambda Error Alarms

# ========================
# Locals
# ========================

locals {
  common_tags = {
    Project     = var.project_name
    Environment = var.stage
    ManagedBy   = "Terraform"
  }
}

# ==========================================================
# CloudWatch Log Groups for Lambda functions
# ==========================================================

resource "aws_cloudwatch_log_group" "document_processor" {
  name              = "/aws/lambda/${var.document_processor_name}"
  retention_in_days = 30
  
  tags = {
    Name = "${var.project_name}-${var.stage}-document-processor-logs"
  }
}

resource "aws_cloudwatch_log_group" "query_processor" {
  name              = "/aws/lambda/${var.query_processor_name}"
  retention_in_days = 30
  
  tags = {
    Name = "${var.project_name}-${var.stage}-query-processor-logs"
  }
}

resource "aws_cloudwatch_log_group" "upload_handler" {
  name              = "/aws/lambda/${var.upload_handler_name}"
  retention_in_days = 30
  
  tags = {
    Name = "${var.project_name}-${var.stage}-upload-handler-logs"
  }
}

# ==========================================================
# CloudWatch Log Group for auth_handler Lambda
# ==========================================================

resource "aws_cloudwatch_log_group" "auth_handler" {
  name              = "/aws/lambda/${var.auth_handler_name}"
  retention_in_days = 30
  
  tags = {
    Name = "${var.project_name}-${var.stage}-auth-handler-logs"
  }
}

# ==============================
# SNS Topic for Alerts
# ==============================

resource "aws_sns_topic" "alerts" {
  name = "${var.project_name}-${var.stage}-alerts"
  
  tags = {
    Name = "${var.project_name}-${var.stage}-alerts"
  }
}

resource "aws_sns_topic_subscription" "email" {
  topic_arn = aws_sns_topic.alerts.arn
  protocol  = "email"
  endpoint  = var.alert_email
}

# ==============================
# CloudWatch Alarms
# ==============================

resource "aws_cloudwatch_metric_alarm" "document_processor_errors" {
  alarm_name          = "${var.project_name}-${var.stage}-document-processor-errors"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name         = "Errors"
  namespace           = "AWS/Lambda"
  period              = 60
  statistic           = "Sum"
  threshold           = 3
  alarm_description   = "This alarm monitors for errors in the document processor Lambda"
  alarm_actions       = [aws_sns_topic.alerts.arn]
  
  dimensions = {
    FunctionName = var.document_processor_name
  }
  
  tags = {
    Name = "${var.project_name}-${var.stage}-document-processor-errors-alarm"
  }
}

resource "aws_cloudwatch_metric_alarm" "query_processor_errors" {
  alarm_name          = "${var.project_name}-${var.stage}-query-processor-errors"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name         = "Errors"
  namespace           = "AWS/Lambda"
  period              = 60
  statistic           = "Sum"
  threshold           = 3
  alarm_description   = "This alarm monitors for errors in the query processor Lambda"
  alarm_actions       = [aws_sns_topic.alerts.arn]
  
  dimensions = {
    FunctionName = var.query_processor_name
  }
  
  tags = {
    Name = "${var.project_name}-${var.stage}-query-processor-errors-alarm"
  }
}