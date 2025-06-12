import json
from bedrock_utils import get_bedrock_client

class DietaryDetectiveAgent:
    """Identifies allergens and dietary classifications"""
    
    def __init__(self, bedrock_client=None):
        self.bedrock_client = bedrock_client or get_bedrock_client()
    
    def analyze_dietary(self, chef_analysis):
        """Analyze the ingredients for allergens and dietary classifications"""
        # Extract dish name if available
        dish_name = chef_analysis.get("dish_name", "")
        # Define system prompt
        system_list = [{
            "text": "You are the Dietary Detective, an expert in food allergies, intolerances, and dietary restrictions. "
                    "Your task is to thoroughly identify ALL potential allergens and classify dishes based on dietary restrictions. "
                    "Be comprehensive and safety-focused, erring on the side of caution when identifying potential allergens."
        }]
        
        # Extract dish name if available
        dish_name = chef_analysis.get("dish_name", "")
        
        # Convert chef analysis to a string representation
        chef_analysis_str = json.dumps(chef_analysis, indent=2)
        
        # Define user message
        prompt_text = f"""
        Analyze the following ingredients list and dish name for ALL potential allergens and dietary classifications:
        
        Dish Name: {dish_name}
        
        {chef_analysis_str}
        
        IMPORTANT: Pay special attention to the dish name as it may contain ingredients not visible in the image. For example, if the dish name mentions "chicken", "beef", "pork", "fish", or any other meat, the dish CANNOT be vegetarian or vegan, even if these ingredients are not detected in the image.
        
        For each identified ingredient, check against this COMPREHENSIVE list of food allergens and sensitivities:
        
        1. Major allergens:
           - Dairy/Milk products (including lactose)
           - Eggs
           - Peanuts
           - Tree nuts (almonds, walnuts, cashews, etc.)
           - Fish
           - Shellfish (shrimp, crab, lobster, etc.)
           - Wheat/Gluten
           - Soy
        
        2. Additional common allergens:
           - Sesame
           - Mustard
           - Celery
           - Lupin
           - Sulfites
        
        3. Other potential allergens:
           - Legumes (beans, lentils, chickpeas, etc.)
           - Corn
           - Nightshades (tomatoes, peppers, eggplant, potatoes)
           - Specific fruits (berries, citrus, etc.)
           - Specific spices
           - Food additives and preservatives
           - Garlic/Onions
        
        Also determine dietary categories:
        - Vegetarian
        - Vegan
        - Gluten-free
        - Dairy-free
        - Keto-friendly
        - Paleo-friendly
        - Low-FODMAP
        - Halal
        - Kosher
        
        Format your response as a JSON object with the following structure:
        {{
            "allergens": ["Allergen1", "Allergen2", ...],
            "potential_allergens": ["PotentialAllergen1", "PotentialAllergen2", ...],
            "dietary_tags": ["Tag1", "Tag2", ...],
            "disclaimer": "Standard disclaimer about AI-generated allergen information"
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
            
            # Ensure the disclaimer is present
            if "disclaimer" not in parsed_result:
                parsed_result["disclaimer"] = "Allergen and dietary information is AI-generated based on visual analysis and may not account for hidden ingredients or cross-contamination. Please consult the restaurant for severe allergies."
                
            return parsed_result
        except Exception as e:
            print(f"Error parsing Dietary Detective response: {str(e)}")
            # Return a fallback structure
            return {
                "allergens": [],
                "potential_allergens": [],
                "dietary_tags": [],
                "disclaimer": "Allergen and dietary information is AI-generated based on visual analysis and may not account for hidden ingredients or cross-contamination. Please consult the restaurant for severe allergies."
            }