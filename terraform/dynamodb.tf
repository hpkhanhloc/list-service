# DynamoDB table for storing lists
resource "aws_dynamodb_table" "lists" {
  name         = "${var.project_name}-lists"
  billing_mode = "PAY_PER_REQUEST" # On-demand pricing for cost optimization
  hash_key     = "list_id"

  attribute {
    name = "list_id"
    type = "S"
  }

  # Enable point-in-time recovery for data protection
  point_in_time_recovery {
    enabled = true
  }

  # Enable encryption at rest
  server_side_encryption {
    enabled = true
  }

  # TTL attribute (optional, can be used for automatic cleanup)
  ttl {
    enabled        = true
    attribute_name = "ttl"
  }

  tags = {
    Name = "${var.project_name}-lists"
  }
}

# CloudWatch alarm for DynamoDB throttles
resource "aws_cloudwatch_metric_alarm" "dynamodb_throttles" {
  alarm_name          = "${var.project_name}-dynamodb-throttles"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name         = "ThrottledRequests"
  namespace           = "AWS/DynamoDB"
  period              = 300
  statistic           = "Sum"
  threshold           = 10
  alarm_description   = "This metric monitors DynamoDB throttling events"
  treat_missing_data  = "notBreaching"

  dimensions = {
    TableName = aws_dynamodb_table.lists.name
  }
}

