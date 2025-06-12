import os
from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

# Environment detection
def is_aws_environment():
    """Detect if running in AWS"""
    return os.environ.get("AWS_EXECUTION_ENV") is not None or os.environ.get("AWS_LAMBDA_FUNCTION_NAME") is not None

# Configuration
ENVIRONMENT = os.environ.get("ENVIRONMENT", "local")
AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")
BEDROCK_MODEL_ID = os.environ.get("BEDROCK_MODEL_ID", "us.amazon.nova-pro-v1:0")
S3_BUCKET = os.environ.get("S3_BUCKET", "menu-maestro-images")
USE_S3 = os.environ.get("USE_S3", "False").lower() == "true" or is_aws_environment()

# Paths
UPLOAD_FOLDER = os.environ.get("UPLOAD_FOLDER", "uploads")