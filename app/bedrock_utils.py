import os
import boto3
import config

def get_bedrock_client():
    """Get a Bedrock client based on the current environment"""
    region = config.AWS_REGION
    
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