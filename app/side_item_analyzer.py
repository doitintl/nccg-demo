import json
import base64
from bedrock_utils import get_bedrock_client

class SideItemAnalyzerAgent:
    """Analyzes the image to identify side items and accompaniments"""
    
    def __init__(self, bedrock_client=None):
        self.bedrock_client = bedrock_client or get_bedrock_client()
    
    def analyze_sides(self, dish_name, image_bytes, chef_analysis):
        """Identify side items and accompaniments in the dish"""
        # Encode image as base64
        base64_string = base64.b64encode(image_bytes).decode('utf-8')
        
        # Define system prompt
        system_list = [{
            "text": "You are the Side Item Analyzer, a culinary expert specializing in identifying accompaniments and side dishes. "
                    "Your task is to carefully examine food images and distinguish between the main dish and its accompanying sides. "
                    "Provide detailed analysis of garnishes, sauces, and complementary items that enhance the main dish."
        }]
        
        # Convert chef analysis to a string representation
        chef_analysis_str = json.dumps(chef_analysis, indent=2)
        
        # Define user message with image and text
        prompt_text = f"""
        Analyze this image of "{dish_name}" and identify all side items and accompaniments.
        
        Chef's Analysis:
        {chef_analysis_str}
        
        Please identify:
        1. Which items are likely part of the main dish
        2. Which items appear to be side dishes or accompaniments
        3. Any sauces, garnishes, or condiments
        4. How the sides complement the main dish
        
        Format your response as a JSON object with the following structure:
        {{
            "main_dish_components": ["item1", "item2", ...],
            "side_items": [
                {{
                    "name": "side item name",
                    "description": "brief description",
                    "confidence": 0.XX
                }},
                ...
            ],
            "sauces_and_garnishes": ["item1", "item2", ...],
            "presentation_notes": "how sides are arranged relative to main dish"
        }}
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
            return parsed_result
        except Exception as e:
            print(f"Error parsing Side Item Analyzer response: {str(e)}")
            # Return a fallback structure
            return {
                "main_dish_components": [],
                "side_items": [],
                "sauces_and_garnishes": [],
                "presentation_notes": "Unable to determine"
            }