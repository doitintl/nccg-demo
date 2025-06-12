import boto3
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_bedrock_access():
    """Check if we have access to Amazon Bedrock and the required models"""
    try:
        # Initialize Bedrock client
        bedrock = boto3.client(
            service_name='bedrock',
            region_name=os.getenv('AWS_REGION', 'us-east-1')
        )
        
        # List available foundation models
        response = bedrock.list_foundation_models()
        
        # Check if our model is available
        model_id = os.getenv('BEDROCK_MODEL_ID', 'anthropic.claude-3-sonnet-20240229-v1:0')
        model_available = any(model['modelId'] == model_id for model in response['modelSummaries'])
        
        if model_available:
            print(f"✅ Model {model_id} is available")
        else:
            print(f"❌ Model {model_id} is not available. Available models:")
            for model in response['modelSummaries']:
                print(f"- {model['modelId']}")
        
        return model_available
    
    except Exception as e:
        print(f"❌ Error checking Bedrock access: {str(e)}")
        print("Please check your AWS credentials and permissions.")
        return False

def setup_aws_resources():
    """Set up any required AWS resources for the application"""
    # This function can be expanded to create S3 buckets, IAM roles, etc.
    # For now, we'll just check Bedrock access
    return check_bedrock_access()

if __name__ == "__main__":
    print("Setting up AWS resources for Nova Culinary Content Generator...")
    setup_aws_resources()