import os
import json
import base64
import boto3
import sys
import traceback

# Add shared code layer to path
sys.path.append('/opt/python')

# Import from shared code
from app.orchestrator import OrchestratorAgent

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
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'error': 'Image is required'})
            }
        
        # Decode image
        image_bytes = base64.b64decode(image_base64)
        
        # Process the dish
        orchestrator = OrchestratorAgent()
        result = orchestrator.process_dish(dish_name, image_bytes, spice_level)
        
        # Check if there was an error
        if 'error' in result:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps(result)
            }
        
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
        # Get full traceback for debugging
        error_traceback = traceback.format_exc()
        print(f"Error: {str(e)}")
        print(f"Traceback: {error_traceback}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': str(e),
                'traceback': error_traceback
            })
        }