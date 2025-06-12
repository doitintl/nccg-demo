import json
from app.bedrock_utils import get_bedrock_client

class AuthenticatorAgent:
    """Validates that the dish description aligns with the main visual evidence"""
    
    def __init__(self, bedrock_client=None):
        self.bedrock_client = bedrock_client or get_bedrock_client()
    
    def validate_name(self, dish_name, chef_analysis):
        """Validate the dish description against the identified components"""
        # Define system prompt
        system_list = [{
            "text": "You are the Authenticator, a quality control expert for food menus. "
                    "Your task is to validate that the main dish type in the user's description is visible in the image. "
                    "Trust user-provided details that cannot be visually verified (like fillings, cooking methods, or ingredients). "
                    "Only flag major mismatches where the fundamental dish type is completely wrong."
        }]
        
        # Convert chef analysis to a string representation
        chef_analysis_str = json.dumps(chef_analysis, indent=2)
        
        # Define user message
        prompt_text = f"""
        Validate whether the main dish type in "{dish_name}" is visible in the identified components:
        
        {chef_analysis_str}
        
        IMPORTANT GUIDELINES:
        1. Focus ONLY on the main dish type (e.g., if it's a burger, pizza, salad, pupusa, etc.)
        2. ALWAYS trust user-provided details that cannot be easily verified from the image (like fillings, seasonings, cooking methods)
        3. For example, if user says "Chicken Pupusas" and you see pupusas but can't verify the filling, CONFIRM the match
        4. Only flag a "Mismatch" if the fundamental dish type is completely wrong (e.g., user says "Pizza" but image clearly shows "Soup")
        5. If the description is too generic, suggest a more descriptive name based on the primary ingredients
        6. When in doubt, CONFIRM the match and trust the user's description
        
        Format your response as a JSON object with the following structure:
        {{
            "validation_status": "Confirmed" or "Mismatch",
            "reason": "Explanation if there's a mismatch or empty string if confirmed",
            "suggested_name": "Original or improved dish name"
        }}
        """
        
        message_list = [{
            "role": "user",
            "content": [
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
            print(f"Error parsing Authenticator response: {str(e)}")
            # Return a fallback structure
            return {
                "validation_status": "Unknown",
                "reason": f"Error processing: {str(e)}",
                "suggested_name": dish_name
            }