import os
import json
import base64
import boto3
import sys

# Add shared code layer to path
sys.path.append('/opt/python')

# Import from shared code
from app.agents.orchestrator import OrchestratorAgent
from app.utils.storage import StorageService

def lambda_handler(event, context):
    """Lambda handler for the Orchestrator function"""
    try:
        # Parse the request body
        body = json.loads(event['body']) if isinstance(event.get('body'), str) else event.get('body', {})
        
        # Get parameters
        dish_name = body.get('dish_name', '')
        spice_level = body.get('spice_level', 'Medium')
        
        # Get image from request
        image_base64 = body.get('image', '')
        if not image_base64:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Image is required'})
            }
        
        # Decode image
        image_bytes = base64.b64decode(image_base64)
        
        # Process the dish
        orchestrator = OrchestratorAgent()
        result = orchestrator.process_dish(dish_name, image_bytes, spice_level)
        
        # Return the result
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(result)
        }
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }