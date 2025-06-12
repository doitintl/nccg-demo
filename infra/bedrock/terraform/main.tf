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

# IAM role for Bedrock Agent
resource "aws_iam_role" "bedrock_agent_role" {
  name = "menu-maestro-bedrock-agent-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "bedrock.amazonaws.com"
        }
      }
    ]
  })
}

# IAM policy for Bedrock Agent
resource "aws_iam_policy" "bedrock_agent_policy" {
  name        = "menu-maestro-bedrock-agent-policy"
  description = "Policy for Menu Maestro Bedrock Agent"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
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
resource "aws_iam_role_policy_attachment" "bedrock_agent_policy_attachment" {
  role       = aws_iam_role.bedrock_agent_role.name
  policy_arn = aws_iam_policy.bedrock_agent_policy.arn
}

# Lambda function for action groups
resource "aws_lambda_function" "action_group_handler" {
  function_name = "menu-maestro-action-group-handler"
  
  filename      = "../action_groups/function.zip"
  handler       = "handler.lambda_handler"
  runtime       = "python3.9"
  
  role          = aws_iam_role.bedrock_agent_role.arn
  
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

# Note: Bedrock Agent resources would be created here, but Terraform doesn't 
# currently have native support for Bedrock Agents. You would need to use 
# the AWS CLI or custom Terraform providers to create these resources.