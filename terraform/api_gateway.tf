# API Gateway REST API
resource "aws_api_gateway_rest_api" "list_service" {
  name        = "${var.project_name}-api"
  description = "REST API for List Service"

  endpoint_configuration {
    types = ["REGIONAL"]
  }
}

# API Gateway Resource: /lists
resource "aws_api_gateway_resource" "lists" {
  rest_api_id = aws_api_gateway_rest_api.list_service.id
  parent_id   = aws_api_gateway_rest_api.list_service.root_resource_id
  path_part   = "lists"
}

# API Gateway Resource: /lists/{list_id}
resource "aws_api_gateway_resource" "list_item" {
  rest_api_id = aws_api_gateway_rest_api.list_service.id
  parent_id   = aws_api_gateway_resource.lists.id
  path_part   = "{list_id}"
}

# API Gateway Resource: /lists/{list_id}/head
resource "aws_api_gateway_resource" "head" {
  rest_api_id = aws_api_gateway_rest_api.list_service.id
  parent_id   = aws_api_gateway_resource.list_item.id
  path_part   = "head"
}

# API Gateway Resource: /lists/{list_id}/tail
resource "aws_api_gateway_resource" "tail" {
  rest_api_id = aws_api_gateway_rest_api.list_service.id
  parent_id   = aws_api_gateway_resource.list_item.id
  path_part   = "tail"
}

# ===== Methods for /lists =====

# GET /lists (Get all lists)
resource "aws_api_gateway_method" "get_all_lists" {
  rest_api_id   = aws_api_gateway_rest_api.list_service.id
  resource_id   = aws_api_gateway_resource.lists.id
  http_method   = "GET"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "get_all_lists" {
  rest_api_id             = aws_api_gateway_rest_api.list_service.id
  resource_id             = aws_api_gateway_resource.lists.id
  http_method             = aws_api_gateway_method.get_all_lists.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.list_service.invoke_arn
}

# POST /lists (Create new list)
resource "aws_api_gateway_method" "post_list" {
  rest_api_id   = aws_api_gateway_rest_api.list_service.id
  resource_id   = aws_api_gateway_resource.lists.id
  http_method   = "POST"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "post_list" {
  rest_api_id             = aws_api_gateway_rest_api.list_service.id
  resource_id             = aws_api_gateway_resource.lists.id
  http_method             = aws_api_gateway_method.post_list.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.list_service.invoke_arn
}

# ===== Methods for /lists/{list_id} =====

# GET /lists/{list_id}
resource "aws_api_gateway_method" "get_list" {
  rest_api_id   = aws_api_gateway_rest_api.list_service.id
  resource_id   = aws_api_gateway_resource.list_item.id
  http_method   = "GET"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "get_list" {
  rest_api_id             = aws_api_gateway_rest_api.list_service.id
  resource_id             = aws_api_gateway_resource.list_item.id
  http_method             = aws_api_gateway_method.get_list.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.list_service.invoke_arn
}

# PUT /lists/{list_id}
resource "aws_api_gateway_method" "put_list" {
  rest_api_id   = aws_api_gateway_rest_api.list_service.id
  resource_id   = aws_api_gateway_resource.list_item.id
  http_method   = "PUT"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "put_list" {
  rest_api_id             = aws_api_gateway_rest_api.list_service.id
  resource_id             = aws_api_gateway_resource.list_item.id
  http_method             = aws_api_gateway_method.put_list.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.list_service.invoke_arn
}

# DELETE /lists/{list_id}
resource "aws_api_gateway_method" "delete_list" {
  rest_api_id   = aws_api_gateway_rest_api.list_service.id
  resource_id   = aws_api_gateway_resource.list_item.id
  http_method   = "DELETE"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "delete_list" {
  rest_api_id             = aws_api_gateway_rest_api.list_service.id
  resource_id             = aws_api_gateway_resource.list_item.id
  http_method             = aws_api_gateway_method.delete_list.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.list_service.invoke_arn
}

# ===== Methods for /lists/{list_id}/head =====

# GET /lists/{list_id}/head
resource "aws_api_gateway_method" "get_head" {
  rest_api_id   = aws_api_gateway_rest_api.list_service.id
  resource_id   = aws_api_gateway_resource.head.id
  http_method   = "GET"
  authorization = "NONE"

  request_parameters = {
    "method.request.querystring.n" = false
  }
}

resource "aws_api_gateway_integration" "get_head" {
  rest_api_id             = aws_api_gateway_rest_api.list_service.id
  resource_id             = aws_api_gateway_resource.head.id
  http_method             = aws_api_gateway_method.get_head.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.list_service.invoke_arn
}

# ===== Methods for /lists/{list_id}/tail =====

# GET /lists/{list_id}/tail
resource "aws_api_gateway_method" "get_tail" {
  rest_api_id   = aws_api_gateway_rest_api.list_service.id
  resource_id   = aws_api_gateway_resource.tail.id
  http_method   = "GET"
  authorization = "NONE"

  request_parameters = {
    "method.request.querystring.n" = false
  }
}

resource "aws_api_gateway_integration" "get_tail" {
  rest_api_id             = aws_api_gateway_rest_api.list_service.id
  resource_id             = aws_api_gateway_resource.tail.id
  http_method             = aws_api_gateway_method.get_tail.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.list_service.invoke_arn
}

# API Gateway Deployment
resource "aws_api_gateway_deployment" "list_service" {
  rest_api_id = aws_api_gateway_rest_api.list_service.id

  triggers = {
    redeployment = sha1(jsonencode([
      aws_api_gateway_resource.lists.id,
      aws_api_gateway_resource.list_item.id,
      aws_api_gateway_resource.head.id,
      aws_api_gateway_resource.tail.id,
      aws_api_gateway_method.get_all_lists.id,
      aws_api_gateway_method.post_list.id,
      aws_api_gateway_method.get_list.id,
      aws_api_gateway_method.put_list.id,
      aws_api_gateway_method.delete_list.id,
      aws_api_gateway_method.get_head.id,
      aws_api_gateway_method.get_tail.id,
      aws_api_gateway_integration.get_all_lists.id,
      aws_api_gateway_integration.post_list.id,
      aws_api_gateway_integration.get_list.id,
      aws_api_gateway_integration.put_list.id,
      aws_api_gateway_integration.delete_list.id,
      aws_api_gateway_integration.get_head.id,
      aws_api_gateway_integration.get_tail.id,
      aws_api_gateway_gateway_response.missing_authentication_token.id,
      aws_api_gateway_gateway_response.resource_not_found.id,
    ]))
  }

  lifecycle {
    create_before_destroy = true
  }

  depends_on = [
    aws_api_gateway_integration.get_all_lists,
    aws_api_gateway_integration.post_list,
    aws_api_gateway_integration.get_list,
    aws_api_gateway_integration.put_list,
    aws_api_gateway_integration.delete_list,
    aws_api_gateway_integration.get_head,
    aws_api_gateway_integration.get_tail,
    aws_api_gateway_gateway_response.missing_authentication_token,
    aws_api_gateway_gateway_response.resource_not_found,
  ]
}

# API Gateway Stage
resource "aws_api_gateway_stage" "list_service" {
  deployment_id = aws_api_gateway_deployment.list_service.id
  rest_api_id   = aws_api_gateway_rest_api.list_service.id
  stage_name    = "api"

  tags = {
    Name = "${var.project_name}-api-stage"
  }
}

# API Gateway Method Settings for throttling
resource "aws_api_gateway_method_settings" "list_service" {
  rest_api_id = aws_api_gateway_rest_api.list_service.id
  stage_name  = aws_api_gateway_stage.list_service.stage_name
  method_path = "*/*"

  settings {
    metrics_enabled = true

    throttling_burst_limit = var.api_throttle_burst_limit
    throttling_rate_limit  = var.api_throttle_rate_limit
  }
}

# Custom Gateway Response for Missing Authentication Token (treat as 404 Not Found)
resource "aws_api_gateway_gateway_response" "missing_authentication_token" {
  rest_api_id   = aws_api_gateway_rest_api.list_service.id
  response_type = "MISSING_AUTHENTICATION_TOKEN"
  status_code   = "404"

  response_templates = {
    "application/json" = jsonencode({
      error   = "NotFound"
      message = "Resource not found"
    })
  }

  response_parameters = {
    "gatewayresponse.header.Content-Type" = "'application/json'"
  }
}

# Custom Gateway Response for Resource Not Found
resource "aws_api_gateway_gateway_response" "resource_not_found" {
  rest_api_id   = aws_api_gateway_rest_api.list_service.id
  response_type = "RESOURCE_NOT_FOUND"
  status_code   = "404"

  response_templates = {
    "application/json" = jsonencode({
      error   = "NotFound"
      message = "Resource not found"
    })
  }

  response_parameters = {
    "gatewayresponse.header.Content-Type" = "'application/json'"
  }
}

