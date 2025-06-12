output "api_gateway_url" {
  description = "URL of the API Gateway endpoint"
  value       = "${aws_apigatewayv2_api.api.api_endpoint}/menu-description"
}

output "lambda_function_name" {
  description = "Name of the Lambda function"
  value       = aws_lambda_function.orchestrator.function_name
}

output "s3_bucket_name" {
  description = "Name of the S3 bucket for image storage"
  value       = aws_s3_bucket.images.bucket
}