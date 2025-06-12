import json
from ..utils.bedrock import get_bedrock_client

class CulinaryWordsmithAgent:
    """Generates engaging menu descriptions"""
    
    def __init__(self, bedrock_client=None):
        self.bedrock_client = bedrock_client or get_bedrock_client()
    
    def generate_description(self, dish_name, chef_analysis, dietary_analysis, sides_analysis=None, feedback=None):
        """Generate an engaging menu description"""
        # Define system prompt
        system_list = [{
            "text": "You are the Culinary Wordsmith, a creative writer specializing in appetizing food descriptions. "
                    "Your task is to transform ingredient lists and cooking notes into enticing marketing copy. "
                    "Create descriptions that are engaging, descriptive, and make the reader's mouth water."
        }]
        
        # Convert analyses to string representations
        chef_analysis_str = json.dumps(chef_analysis, indent=2)
        dietary_analysis_str = json.dumps(dietary_analysis, indent=2)
        
        # Get spice level from chef analysis
        spice_level = chef_analysis.get("spice_level", "Medium")
        
        # Include sides analysis if provided
        sides_text = ""
        if sides_analysis:
            sides_analysis_str = json.dumps(sides_analysis, indent=2)
            sides_text = f"""
            Side Items Analysis:
            {sides_analysis_str}
            
            Be sure to mention notable side items and how they complement the main dish.
            """
        
        # Include feedback if provided
        feedback_text = ""
        if feedback:
            feedback_text = f"""
            Previous description feedback:
            {feedback}
            
            Please incorporate this feedback when creating the new description.
            """
        
        # Define user message
        prompt_text = f"""
        Create an engaging, appetizing menu description for "{dish_name}" based on the following information:
        
        Chef's Analysis:
        {chef_analysis_str}
        
        Dietary Analysis:
        {dietary_analysis_str}
        
        Spice Level: {spice_level}
        
        {sides_text}
        
        {feedback_text}
        
        Your description should:
        1. Be approximately 50-75 words
        2. Highlight key ingredients and cooking methods
        3. Use sensory language (taste, texture, aroma)
        4. Be enticing and appetizing
        5. Subtly incorporate relevant dietary information when appropriate
        6. Accurately reflect the specified spice level
        7. Mention notable side items if present
        
        Provide only the final description text, with no additional commentary.
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
        
        # Clean up the result - remove any markdown formatting or extra quotes
        result_text = result_text.replace('```', '').strip()
        
        return result_text