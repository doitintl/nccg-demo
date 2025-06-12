import os
import boto3

def get_bedrock_client():
    """Get a Bedrock client based on the current environment"""
    region = os.environ.get("AWS_REGION", "us-east-1")
    
    # Check if running in AWS environment
    if os.environ.get("AWS_EXECUTION_ENV") or os.environ.get("AWS_LAMBDA_FUNCTION_NAME"):
        # Running in AWS, use instance role
        return boto3.client("bedrock-runtime", region_name=region)
    else:
        # Running locally, use configured credentials
        return boto3.client(
            "bedrock-runtime",
            region_name=region,
            aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY")
        )