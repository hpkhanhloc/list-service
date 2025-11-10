# CloudWatch Dashboard for monitoring
resource "aws_cloudwatch_dashboard" "list_service" {
  dashboard_name = "${var.project_name}-dashboard"

  dashboard_body = jsonencode({
    widgets = [
      {
        type = "metric"
        properties = {
          metrics = [
            ["AWS/Lambda", "Invocations", { stat = "Sum", label = "Lambda Invocations" }],
            [".", "Errors", { stat = "Sum", label = "Lambda Errors" }],
            [".", "Throttles", { stat = "Sum", label = "Lambda Throttles" }],
            [".", "Duration", { stat = "Average", label = "Lambda Duration (Avg)" }],
          ]
          view    = "timeSeries"
          stacked = false
          region  = var.aws_region
          title   = "Lambda Metrics"
          period  = 300
        }
      },
      {
        type = "metric"
        properties = {
          metrics = [
            ["AWS/ApiGateway", "Count", { stat = "Sum", label = "API Requests" }],
            [".", "4XXError", { stat = "Sum", label = "4XX Errors" }],
            [".", "5XXError", { stat = "Sum", label = "5XX Errors" }],
            [".", "Latency", { stat = "Average", label = "API Latency (Avg)" }],
          ]
          view    = "timeSeries"
          stacked = false
          region  = var.aws_region
          title   = "API Gateway Metrics"
          period  = 300
        }
      },
      {
        type = "metric"
        properties = {
          metrics = [
            ["AWS/DynamoDB", "ConsumedReadCapacityUnits", { stat = "Sum", label = "Read Capacity" }],
            [".", "ConsumedWriteCapacityUnits", { stat = "Sum", label = "Write Capacity" }],
            [".", "UserErrors", { stat = "Sum", label = "User Errors" }],
            [".", "SystemErrors", { stat = "Sum", label = "System Errors" }],
          ]
          view    = "timeSeries"
          stacked = false
          region  = var.aws_region
          title   = "DynamoDB Metrics"
          period  = 300
        }
      },
      {
        type = "log"
        properties = {
          query   = <<-EOT
            SOURCE '/aws/lambda/${var.project_name}'
            | fields @timestamp, @message
            | filter @message like /ERROR/
            | sort @timestamp desc
            | limit 20
          EOT
          region  = var.aws_region
          stacked = false
          title   = "Recent Lambda Errors"
          view    = "table"
        }
      }
    ]
  })
}

# Custom metric filter for successful operations
resource "aws_cloudwatch_log_metric_filter" "successful_operations" {
  name           = "${var.project_name}-successful-operations"
  log_group_name = aws_cloudwatch_log_group.lambda_logs.name
  pattern        = "[timestamp, request_id, level=INFO, msg=\"Operation completed\", ...]"

  metric_transformation {
    name      = "SuccessfulOperations"
    namespace = var.project_name
    value     = "1"
  }
}

# Custom metric filter for head operations
resource "aws_cloudwatch_log_metric_filter" "head_operations" {
  name           = "${var.project_name}-head-operations"
  log_group_name = aws_cloudwatch_log_group.lambda_logs.name
  pattern        = "[timestamp, request_id, level, msg=\"Operation completed\", operation=head, ...]"

  metric_transformation {
    name      = "HeadOperations"
    namespace = var.project_name
    value     = "1"
  }
}

# Custom metric filter for tail operations
resource "aws_cloudwatch_log_metric_filter" "tail_operations" {
  name           = "${var.project_name}-tail-operations"
  log_group_name = aws_cloudwatch_log_group.lambda_logs.name
  pattern        = "[timestamp, request_id, level, msg=\"Operation completed\", operation=tail, ...]"

  metric_transformation {
    name      = "TailOperations"
    namespace = var.project_name
    value     = "1"
  }
}

