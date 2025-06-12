import os
import json
import base64
import boto3
import sys

# Add shared code layer to path
sys.path.append('/opt/python')

# Import from shared code
from app.agents.visionary_chef import VisionaryChefAgent
from app.agents.authenticator import AuthenticatorAgent
from app.agents.dietary_detective import DietaryDetectiveAgent
from app.agents.side_item_analyzer import SideItemAnalyzerAgent
from app.agents.culinary_wordsmith import CulinaryWordsmithAgent
from app.utils.storage import StorageService

def lambda_handler(event, context):
    """Lambda handler for Bedrock Agent action groups"""
    try:
        # Extract action group and API path
        action_group = event.get('actionGroup', '')
        api_path = event.get('apiPath', '')
        parameters = event.get('parameters', {})
        
        # Storage service
        storage = StorageService()
        
        # Handle different action groups
        if action_group == 'ImageAnalysis':
            return handle_image_analysis(parameters, storage)
        elif action_group == 'DishValidation':
            return handle_dish_validation(parameters, storage)
        elif action_group == 'DietaryAnalysis':
            return handle_dietary_analysis(parameters, storage)
        elif action_group == 'SideItemAnalysis':
            return handle_side_item_analysis(parameters, storage)
        elif action_group == 'DescriptionGeneration':
            return handle_description_generation(parameters, storage)
        else:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': f'Unknown action group: {action_group}'})
            }
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }

def handle_image_analysis(parameters, storage):
    """Handle image analysis action"""
    # Get parameters
    image_key = parameters.get('imageKey', '')
    dish_name = parameters.get('dishName', '')
    
    # Get image from S3
    image_bytes = storage.get_image(image_key)
    
    # Analyze image
    agent = VisionaryChefAgent()
    result = agent.analyze_image(dish_name, image_bytes)
    
    return {
        'statusCode': 200,
        'body': json.dumps(result)
    }

def handle_dish_validation(parameters, storage):
    """Handle dish validation action"""
    # Get parameters
    dish_name = parameters.get('dishName', '')
    chef_analysis = parameters.get('chefAnalysis', {})
    
    # Validate dish name
    agent = AuthenticatorAgent()
    result = agent.validate_name(dish_name, chef_analysis)
    
    return {
        'statusCode': 200,
        'body': json.dumps(result)
    }

def handle_dietary_analysis(parameters, storage):
    """Handle dietary analysis action"""
    # Get parameters
    chef_analysis = parameters.get('chefAnalysis', {})
    
    # Analyze dietary aspects
    agent = DietaryDetectiveAgent()
    result = agent.analyze_dietary(chef_analysis)
    
    return {
        'statusCode': 200,
        'body': json.dumps(result)
    }

def handle_side_item_analysis(parameters, storage):
    """Handle side item analysis action"""
    # Get parameters
    dish_name = parameters.get('dishName', '')
    chef_analysis = parameters.get('chefAnalysis', {})
    image_key = parameters.get('imageKey', '')
    
    # Get image from S3
    image_bytes = storage.get_image(image_key)
    
    # Analyze side items
    agent = SideItemAnalyzerAgent()
    result = agent.analyze_sides(dish_name, image_bytes, chef_analysis)
    
    return {
        'statusCode': 200,
        'body': json.dumps(result)
    }

def handle_description_generation(parameters, storage):
    """Handle description generation action"""
    # Get parameters
    dish_name = parameters.get('dishName', '')
    chef_analysis = parameters.get('chefAnalysis', {})
    dietary_analysis = parameters.get('dietaryAnalysis', {})
    sides_analysis = parameters.get('sidesAnalysis', {})
    feedback = parameters.get('feedback', '')
    
    # Generate description
    agent = CulinaryWordsmithAgent()
    result = agent.generate_description(
        dish_name,
        chef_analysis,
        dietary_analysis,
        sides_analysis,
        feedback
    )
    
    return {
        'statusCode': 200,
        'body': json.dumps({'description': result})
    }