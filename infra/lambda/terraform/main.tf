provider "aws" {
  region = var.aws_region
}

# S3 bucket for image storage
resource "aws_s3_bucket" "images" {
  bucket = var.s3_bucket_name
  
  tags = {
    Name        = "Menu Maestro Images"
    Environment = var.environment
  }
}

# Lambda execution role
resource "aws_iam_role" "lambda_role" {
  name = "menu-maestro-lambda-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

# Lambda policy for S3, DynamoDB, and Bedrock
resource "aws_iam_policy" "lambda_policy" {
  name        = "menu-maestro-lambda-policy"
  description = "Policy for Menu Maestro Lambda functions"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Effect   = "Allow"
        Resource = "arn:aws:logs:*:*:*"
      },
      {
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:ListBucket"
        ]
        Effect   = "Allow"
        Resource = [
          "${aws_s3_bucket.images.arn}",
          "${aws_s3_bucket.images.arn}/*"
        ]
      },
      {
        Action = [
          "bedrock:InvokeModel"
        ]
        Effect   = "Allow"
        Resource = "*"
      }
    ]
  })
}

# Attach policy to role
resource "aws_iam_role_policy_attachment" "lambda_policy_attachment" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = aws_iam_policy.lambda_policy.arn
}

# Lambda layer for shared code
resource "aws_lambda_layer_version" "shared_code" {
  layer_name = "menu-maestro-shared-code"
  
  filename = "../../../app.zip"
  
  compatible_runtimes = ["python3.9"]
}

# Orchestrator Lambda function
resource "aws_lambda_function" "orchestrator" {
  function_name = "menu-maestro-orchestrator"
  
  filename      = "../functions/orchestrator/function.zip"
  handler       = "lambda_function.lambda_handler"
  runtime       = "python3.9"
  
  role          = aws_iam_role.lambda_role.arn
  
  layers        = [aws_lambda_layer_version.shared_code.arn]
  
  timeout       = 30
  memory_size   = 1024
  
  environment {
    variables = {
      ENVIRONMENT = var.environment
      AWS_REGION  = var.aws_region
      S3_BUCKET   = aws_s3_bucket.images.bucket
      USE_S3      = "true"
    }
  }
}

# API Gateway
resource "aws_apigatewayv2_api" "api" {
  name          = "menu-maestro-api"
  protocol_type = "HTTP"
}

resource "aws_apigatewayv2_stage" "default" {
  api_id      = aws_apigatewayv2_api.api.id
  name        = "$default"
  auto_deploy = true
}

resource "aws_apigatewayv2_integration" "orchestrator" {
  api_id           = aws_apigatewayv2_api.api.id
  integration_type = "AWS_PROXY"
  
  integration_uri    = aws_lambda_function.orchestrator.invoke_arn
  integration_method = "POST"
}

resource "aws_apigatewayv2_route" "orchestrator" {
  api_id    = aws_apigatewayv2_api.api.id
  route_key = "POST /menu-description"
  
  target = "integrations/${aws_apigatewayv2_integration.orchestrator.id}"
}

resource "aws_lambda_permission" "api_gateway" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.orchestrator.function_name
  principal     = "apigateway.amazonaws.com"
  
  source_arn = "${aws_apigatewayv2_api.api.execution_arn}/*/*"
}