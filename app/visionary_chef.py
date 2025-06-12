import json
import base64
from bedrock_utils import get_bedrock_client

class VisionaryChefAgent:
    """Analyzes the food image to identify ingredients and cooking style"""
    
    def __init__(self, bedrock_client=None):
        self.bedrock_client = bedrock_client or get_bedrock_client()
    
    def _verify_food_image(self, image_bytes):
        """Verify that the image contains food"""
        # Encode image as base64
        base64_string = base64.b64encode(image_bytes).decode('utf-8')
        
        # Define system prompt
        system_list = [{"text": "You are a food image verification expert. Your only task is to determine if an image contains food or not."}]
        
        # Define user message with image
        prompt_text = """
        Does this image contain food? Answer with ONLY 'yes' or 'no'.
        If the image shows any edible food items, even if they're part of a larger scene, answer 'yes'.
        If the image contains NO food whatsoever (e.g., landscapes, people, objects, etc.), answer 'no'.
        """
        
        message_list = [{
            "role": "user",
            "content": [
                {
                    "image": {
                        "format": "jpeg",
                        "source": {"bytes": base64_string}
                    }
                },
                {
                    "text": prompt_text
                }
            ]
        }]
        
        # Configure inference parameters
        inf_params = {
            "maxTokens": 10,
            "temperature": 0.0,
            "topP": 1.0,
            "topK": 1
        }
        
        # Create the request payload
        request_body = {
            "schemaVersion": "messages-v1",
            "messages": message_list,
            "system": system_list,
            "inferenceConfig": inf_params
        }
        
        try:
            # Call the Bedrock API
            response = self.bedrock_client.invoke_model(
                modelId="us.amazon.nova-pro-v1:0",
                body=json.dumps(request_body)
            )
            
            # Parse the response
            response_body = json.loads(response['body'].read())
            result_text = response_body["output"]["message"]["content"][0]["text"].strip().lower()
            
            # Check if the response indicates food
            return "yes" in result_text
        except Exception as e:
            print(f"Error verifying food image: {str(e)}")
            # Default to True in case of error to avoid blocking legitimate requests
            return True
    
    def analyze_image(self, dish_name, image_bytes):
        """Analyze the image and identify components"""
        # First verify the image contains food
        is_food = self._verify_food_image(image_bytes)
        
        # Encode image as base64
        base64_string = base64.b64encode(image_bytes).decode('utf-8')
        
        # Define system prompt
        system_list = [{
            "text": "You are the Visionary Chef, an expert culinary professional with decades of experience. "
                    "Your task is to analyze food images with exceptional detail and precision. "
                    "Provide structured, accurate information about the dish components, cooking methods, and presentation."
        }]
        
        # Define user message with image and text
        prompt_text = f"""
        Analyze this image of a dish called "{dish_name}" in extreme detail.
        
        Identify:
        1. Primary Components: The main protein, carbohydrate, and key vegetables
        2. Secondary Ingredients & Garnishes: Herbs, sauces, seeds, spices, and other toppings
        3. Cooking Method: Visual cues that suggest the cooking style (e.g., grilled, fried, steamed)
        4. Presentation Style: How the dish is plated
        
        Format your response as a JSON object with the following structure:
        {{
            "items": [
                {{"item": "ingredient name", "confidence": 0.XX}},
                ...
            ],
            "cooking_style": "method",
            "presentation": "description"
        }}
        
        Assign a confidence score between 0 and 1 to each identified item based on your certainty.
        """
        
        message_list = [{
            "role": "user",
            "content": [
                {
                    "image": {
                        "format": "jpeg",
                        "source": {"bytes": base64_string}
                    }
                },
                {
                    "text": prompt_text
                }
            ]
        }]
        
        # Configure inference parameters
        inf_params = {
            "maxTokens": 500,
            "temperature": 0.7,
            "topP": 0.9,
            "topK": 20
        }
        
        # Create the request payload
        request_body = {
            "schemaVersion": "messages-v1",
            "messages": message_list,
            "system": system_list,
            "inferenceConfig": inf_params
        }
        
        # Call the Bedrock API
        response = self.bedrock_client.invoke_model(
            modelId="us.amazon.nova-pro-v1:0",
            body=json.dumps(request_body)
        )
        
        # Parse the response
        response_body = json.loads(response['body'].read())
        result_text = response_body["output"]["message"]["content"][0]["text"]
        
        # Extract JSON from the response
        try:
            # Find JSON content between triple backticks if present
            if "```json" in result_text:
                json_str = result_text.split("```json")[1].split("```")[0].strip()
            elif "```" in result_text:
                json_str = result_text.split("```")[1].strip()
            else:
                # Try to find JSON-like content
                start_idx = result_text.find('{')
                end_idx = result_text.rfind('}') + 1
                if start_idx >= 0 and end_idx > start_idx:
                    json_str = result_text[start_idx:end_idx]
                else:
                    raise ValueError("Could not extract JSON from response")
            
            parsed_result = json.loads(json_str)
            # Add the food verification result
            parsed_result["is_food"] = is_food
            return parsed_result
        except Exception as e:
            print(f"Error parsing Visionary Chef response: {str(e)}")
            # Return a fallback structure
            return {
                "is_food": is_food,
                "items": [],
                "cooking_style": "unknown",
                "presentation": "unknown"
            }