import os
import boto3
import json
import base64
import streamlit as st
from PIL import Image
import io
from dotenv import load_dotenv
import datetime
import uuid

# Load environment variables
load_dotenv()

# Set page configuration
st.set_page_config(
    page_title="Menu Maestro",
    page_icon="🍽️",
    layout="wide"
)

# Get configuration from environment variables
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
BEDROCK_MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "us.amazon.nova-pro-v1:0")

# Initialize Bedrock client
@st.cache_resource
def get_bedrock_client():
    return boto3.client(
        service_name='bedrock-runtime',
        region_name=AWS_REGION
    )

def invoke_nova_agent(prompt_text, image_bytes=None, system_instruction=None):
    """Generic function to invoke Nova model with different system instructions"""
    try:
        # Default system instruction if none provided
        if system_instruction is None:
            system_instruction = "You are a helpful AI assistant."
            
        # Define system prompt
        system_list = [{"text": system_instruction}]
        
        # Define user message with optional image
        content_list = []
        
        # Add image if provided
        if image_bytes is not None:
            base64_string = base64.b64encode(image_bytes).decode('utf-8')
            content_list.append({
                "image": {
                    "format": "jpeg",
                    "source": {"bytes": base64_string}
                }
            })
        
        # Add text prompt
        content_list.append({"text": prompt_text})
        
        message_list = [{"role": "user", "content": content_list}]
        
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
        bedrock_runtime = get_bedrock_client()
        response = bedrock_runtime.invoke_model(
            modelId=BEDROCK_MODEL_ID,
            body=json.dumps(request_body)
        )
        
        # Parse the response
        response_body = json.loads(response['body'].read())
        result = response_body["output"]["message"]["content"][0]["text"]
        
        return result
    
    except Exception as e:
        st.error(f"Error invoking Nova agent: {str(e)}")
        return f"Error: {str(e)}"

class SideItemAnalyzerAgent:
    """Analyzes the image to identify side items and accompaniments"""
    
    def analyze_sides(self, dish_name, image_bytes, chef_analysis):
        """Identify side items and accompaniments in the dish"""
        system_instruction = """
        You are the Side Item Analyzer, a culinary expert specializing in identifying accompaniments and side dishes.
        Your task is to carefully examine food images and distinguish between the main dish and its accompanying sides.
        Provide detailed analysis of garnishes, sauces, and complementary items that enhance the main dish.
        """
        
        # Convert chef analysis to a string representation
        chef_analysis_str = json.dumps(chef_analysis, indent=2)
        
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
        
        result = invoke_nova_agent(prompt_text, image_bytes, system_instruction)
        
        # Extract JSON from the response
        try:
            # Find JSON content between triple backticks if present
            if "```json" in result:
                json_str = result.split("```json")[1].split("```")[0].strip()
            elif "```" in result:
                json_str = result.split("```")[1].strip()
            else:
                # Try to find JSON-like content
                start_idx = result.find('{')
                end_idx = result.rfind('}') + 1
                if start_idx >= 0 and end_idx > start_idx:
                    json_str = result[start_idx:end_idx]
                else:
                    raise ValueError("Could not extract JSON from response")
            
            parsed_result = json.loads(json_str)
            return parsed_result
        except Exception as e:
            st.error(f"Error parsing Side Item Analyzer response: {str(e)}")
            # Return a fallback structure
            return {
                "main_dish_components": [],
                "side_items": [],
                "sauces_and_garnishes": [],
                "presentation_notes": "Unable to determine"
            }

class OrchestratorAgent:
    """Manages the workflow between specialized agents"""
    
    def __init__(self):
        self.visionary_chef = VisionaryChefAgent()
        self.authenticator = AuthenticatorAgent()
        self.dietary_detective = DietaryDetectiveAgent()
        self.side_item_analyzer = SideItemAnalyzerAgent()
        self.culinary_wordsmith = CulinaryWordsmithAgent()
    
    def process_dish(self, dish_name, image_bytes, spice_level="Medium"):
        """Process a dish through the entire agent pipeline"""
        
        # Step 1: Analyze the image with the Visionary Chef
        with st.spinner("🧑‍🍳 Visionary Chef is analyzing the image..."):
            chef_analysis = self.visionary_chef.analyze_image(dish_name, image_bytes)
            
            # Add spice level to chef analysis
            chef_analysis["spice_level"] = spice_level
        
        # Step 2: Validate the dish name with the Authenticator
        with st.spinner("🔍 Authenticator is validating the dish name..."):
            auth_result = self.authenticator.validate_name(dish_name, chef_analysis)
        
        # Step 3: Analyze dietary aspects with the Dietary Detective
        with st.spinner("🥗 Dietary Detective is identifying allergens and dietary tags..."):
            dietary_analysis = self.dietary_detective.analyze_dietary(chef_analysis)
            
        # Step 4: Analyze side items with the Side Item Analyzer
        with st.spinner("🍟 Side Item Analyzer is identifying accompaniments..."):
            sides_analysis = self.side_item_analyzer.analyze_sides(dish_name, image_bytes, chef_analysis)
        
        # Step 5: Generate the description with the Culinary Wordsmith
        with st.spinner("✍️ Culinary Wordsmith is crafting the perfect description..."):
            description = self.culinary_wordsmith.generate_description(
                auth_result["suggested_name"], 
                chef_analysis, 
                dietary_analysis,
                sides_analysis
            )
        
        # Compile the final result
        result = {
            "dish_id": f"item-{uuid.uuid4().hex[:8]}",
            "input_name": dish_name,
            "processed_timestamp": datetime.datetime.now().isoformat(),
            "refined_name": auth_result["suggested_name"],
            "generated_description": description,
            "validation": {
                "status": auth_result["validation_status"],
                "notes": auth_result.get("reason", "")
            },
            "dietary_analysis": {
                "allergens": dietary_analysis["allergens"],
                "potential_allergens": dietary_analysis.get("potential_allergens", []),
                "tags": dietary_analysis["dietary_tags"],
                "disclaimer": dietary_analysis["disclaimer"]
            },
            "sides_analysis": {
                "main_dish_components": sides_analysis.get("main_dish_components", []),
                "side_items": sides_analysis.get("side_items", []),
                "sauces_and_garnishes": sides_analysis.get("sauces_and_garnishes", []),
                "presentation_notes": sides_analysis.get("presentation_notes", "")
            },
            "identified_components": chef_analysis["items"]
        }
        
        return result

class VisionaryChefAgent:
    """Analyzes the food image to identify ingredients and cooking style"""
    
    def analyze_image(self, dish_name, image_bytes):
        """Analyze the image and identify components"""
        system_instruction = """
        You are the Visionary Chef, an expert culinary professional with decades of experience.
        Your task is to analyze food images with exceptional detail and precision.
        Provide structured, accurate information about the dish components, cooking methods, and presentation.
        """
        
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
        
        result = invoke_nova_agent(prompt_text, image_bytes, system_instruction)
        
        # Extract JSON from the response
        try:
            # Find JSON content between triple backticks if present
            if "```json" in result:
                json_str = result.split("```json")[1].split("```")[0].strip()
            elif "```" in result:
                json_str = result.split("```")[1].strip()
            else:
                # Try to find JSON-like content
                start_idx = result.find('{')
                end_idx = result.rfind('}') + 1
                if start_idx >= 0 and end_idx > start_idx:
                    json_str = result[start_idx:end_idx]
                else:
                    raise ValueError("Could not extract JSON from response")
            
            parsed_result = json.loads(json_str)
            return parsed_result
        except Exception as e:
            st.error(f"Error parsing Visionary Chef response: {str(e)}")
            # Return a fallback structure
            return {
                "items": [],
                "cooking_style": "unknown",
                "presentation": "unknown"
            }

class AuthenticatorAgent:
    """Validates that the dish description aligns with the main visual evidence"""
    
    def validate_name(self, dish_name, chef_analysis):
        """Validate the dish description against the identified components"""
        system_instruction = """
        You are the Authenticator, a quality control expert for food menus.
        Your task is to validate that the main dish type in the user's description is visible in the image.
        Trust user-provided details that cannot be visually verified (like fillings, cooking methods, or ingredients).
        Only flag major mismatches where the fundamental dish type is completely wrong.
        """
        
        # Convert chef analysis to a string representation
        chef_analysis_str = json.dumps(chef_analysis, indent=2)
        
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
        
        result = invoke_nova_agent(prompt_text, system_instruction=system_instruction)
        
        # Extract JSON from the response
        try:
            # Find JSON content between triple backticks if present
            if "```json" in result:
                json_str = result.split("```json")[1].split("```")[0].strip()
            elif "```" in result:
                json_str = result.split("```")[1].strip()
            else:
                # Try to find JSON-like content
                start_idx = result.find('{')
                end_idx = result.rfind('}') + 1
                if start_idx >= 0 and end_idx > start_idx:
                    json_str = result[start_idx:end_idx]
                else:
                    raise ValueError("Could not extract JSON from response")
            
            parsed_result = json.loads(json_str)
            return parsed_result
        except Exception as e:
            st.error(f"Error parsing Authenticator response: {str(e)}")
            # Return a fallback structure
            return {
                "validation_status": "Unknown",
                "reason": f"Error processing: {str(e)}",
                "suggested_name": dish_name
            }

class DietaryDetectiveAgent:
    """Identifies allergens and dietary classifications"""
    
    def analyze_dietary(self, chef_analysis):
        """Analyze the ingredients for allergens and dietary classifications"""
        system_instruction = """
        You are the Dietary Detective, an expert in food allergies, intolerances, and dietary restrictions.
        Your task is to thoroughly identify ALL potential allergens and classify dishes based on dietary restrictions.
        Be comprehensive and safety-focused, erring on the side of caution when identifying potential allergens.
        """
        
        # Convert chef analysis to a string representation
        chef_analysis_str = json.dumps(chef_analysis, indent=2)
        
        prompt_text = f"""
        Analyze the following ingredients list for ALL potential allergens and dietary classifications:
        
        {chef_analysis_str}
        
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
        
        Include a confidence-based disclaimer about the limitations of visual analysis for allergen detection.
        """
        
        result = invoke_nova_agent(prompt_text, system_instruction=system_instruction)
        
        # Extract JSON from the response
        try:
            # Find JSON content between triple backticks if present
            if "```json" in result:
                json_str = result.split("```json")[1].split("```")[0].strip()
            elif "```" in result:
                json_str = result.split("```")[1].strip()
            else:
                # Try to find JSON-like content
                start_idx = result.find('{')
                end_idx = result.rfind('}') + 1
                if start_idx >= 0 and end_idx > start_idx:
                    json_str = result[start_idx:end_idx]
                else:
                    raise ValueError("Could not extract JSON from response")
            
            parsed_result = json.loads(json_str)
            
            # Ensure the disclaimer is present
            if "disclaimer" not in parsed_result:
                parsed_result["disclaimer"] = "Allergen and dietary information is AI-generated based on visual analysis and may not account for hidden ingredients or cross-contamination. Please consult the restaurant for severe allergies."
                
            return parsed_result
        except Exception as e:
            st.error(f"Error parsing Dietary Detective response: {str(e)}")
            # Return a fallback structure
            return {
                "allergens": [],
                "dietary_tags": [],
                "disclaimer": "Allergen and dietary information is AI-generated based on visual analysis and may not account for hidden ingredients or cross-contamination. Please consult the restaurant for severe allergies."
            }

class CulinaryWordsmithAgent:
    """Generates engaging menu descriptions"""
    
    def generate_description(self, dish_name, chef_analysis, dietary_analysis, sides_analysis=None, feedback=None):
        """Generate an engaging menu description"""
        system_instruction = """
        You are the Culinary Wordsmith, a creative writer specializing in appetizing food descriptions.
        Your task is to transform ingredient lists and cooking notes into enticing marketing copy.
        Create descriptions that are engaging, descriptive, and make the reader's mouth water.
        """
        
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
        
        result = invoke_nova_agent(prompt_text, system_instruction=system_instruction)
        
        # Clean up the result - remove any markdown formatting or extra quotes
        result = result.replace('```', '').replace('"', '').strip()
        
        return result

def main():
    # App title and description
    st.title("🍽️ Menu Maestro")
    st.markdown("""
    Transform your food images into enticing menu descriptions with our AI-powered system.
    Upload an image of your dish, provide a name, and let our team of specialized AI agents do the rest!
    """)
    
    # Display current configuration
    st.sidebar.subheader("Configuration")
    st.sidebar.text(f"AWS Region: {AWS_REGION}")
    st.sidebar.text(f"Model ID: {BEDROCK_MODEL_ID}")
    
    # Initialize session state
    if 'result' not in st.session_state:
        st.session_state.result = None
    if 'feedback_history' not in st.session_state:
        st.session_state.feedback_history = []
    
    # Create two columns for layout
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Dish Information")
        
        # Dish description input
        dish_name = st.text_input("Dish Description", placeholder="Describe your dish in a few words (e.g., House Burger with caramelized onions)")
        
        # Image upload
        st.subheader("Dish Image")
        uploaded_file = st.file_uploader("Upload an image of your dish", type=["jpg", "jpeg", "png"])
        
        if uploaded_file is not None:
            # Display the uploaded image
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded Dish Image", use_container_width=True)
        
        # Spice level
        st.subheader("Spice Level")
        spice_level = st.select_slider(
            "Select the spice level of your dish",
            options=["No Spice", "Mild", "Medium", "Spicy", "Very Spicy", "Extremely Hot"]
        )
        
        # Generate button
        if st.button("Generate Menu Description") and uploaded_file is not None and dish_name:
            # Get image bytes
            image_bytes = uploaded_file.getvalue()
            
            # Create orchestrator and process the dish
            orchestrator = OrchestratorAgent()
            with st.spinner("🧠 Our AI chef team is analyzing your dish..."):
                result = orchestrator.process_dish(dish_name, image_bytes, spice_level)
                st.session_state.result = result
    
    with col2:
        st.subheader("Generated Menu Content")
        
        if st.session_state.result:
            result = st.session_state.result
            
            # Display the refined name
            st.markdown(f"## {result['refined_name']}")
            
            # Display the description
            st.markdown(f"*{result['generated_description']}*")
            
            # Display validation status
            validation_status = result['validation']['status']
            if validation_status == "Confirmed":
                st.success(f"✅ Name Validation: {validation_status}")
            else:
                st.warning(f"⚠️ Name Validation: {validation_status}")
                if result['validation']['notes']:
                    st.info(f"Note: {result['validation']['notes']}")
            
            # Display dietary information
            st.subheader("Dietary Information")
            
            # Display allergens
            if result['dietary_analysis']['allergens']:
                st.warning("Allergens: " + ", ".join(result['dietary_analysis']['allergens']))
            else:
                st.success("No major allergens detected")
                
            # Display potential allergens
            if result['dietary_analysis'].get('potential_allergens'):
                st.info("Potential Sensitivities: " + ", ".join(result['dietary_analysis']['potential_allergens']))
            
            # Display dietary tags
            if result['dietary_analysis']['tags']:
                tags_html = ""
                for tag in result['dietary_analysis']['tags']:
                    tags_html += f'<span style="background-color: #e6f3e6; color: #2e7d32; padding: 3px 8px; border-radius: 12px; margin-right: 6px;">{tag}</span>'
                st.markdown(f"Dietary Tags: {tags_html}", unsafe_allow_html=True)
            
            # Display disclaimer
            st.caption(result['dietary_analysis']['disclaimer'])
            
            # Expandable section for detailed analysis
            with st.expander("View Detailed Analysis"):
                # Display identified components
                st.subheader("Identified Components")
                components = result['identified_components']
                if isinstance(components, list):
                    for item in components:
                        if isinstance(item, dict) and 'item' in item and 'confidence' in item:
                            confidence = item['confidence']
                            confidence_color = "#4CAF50" if confidence > 0.8 else "#FFC107" if confidence > 0.6 else "#F44336"
                            st.markdown(f"- {item['item']} <span style='color:{confidence_color};'>({confidence:.2f})</span>", unsafe_allow_html=True)
                        else:
                            st.markdown(f"- {item}")
                else:
                    st.write("No detailed components available")
                
                # Display side items analysis
                st.subheader("Side Items Analysis")
                
                # Main dish components
                if result['sides_analysis']['main_dish_components']:
                    st.markdown("**Main Dish Components:**")
                    for item in result['sides_analysis']['main_dish_components']:
                        st.markdown(f"- {item}")
                
                # Side items
                if result['sides_analysis']['side_items']:
                    st.markdown("**Side Items:**")
                    for item in result['sides_analysis']['side_items']:
                        if isinstance(item, dict) and 'name' in item:
                            name = item['name']
                            description = item.get('description', '')
                            confidence = item.get('confidence', 0)
                            
                            if confidence > 0:
                                confidence_color = "#4CAF50" if confidence > 0.8 else "#FFC107" if confidence > 0.6 else "#F44336"
                                st.markdown(f"- **{name}** <span style='color:{confidence_color};'>({confidence:.2f})</span>: {description}", unsafe_allow_html=True)
                            else:
                                st.markdown(f"- **{name}**: {description}")
                        else:
                            st.markdown(f"- {item}")
                
                # Sauces and garnishes
                if result['sides_analysis']['sauces_and_garnishes']:
                    st.markdown("**Sauces & Garnishes:**")
                    for item in result['sides_analysis']['sauces_and_garnishes']:
                        st.markdown(f"- {item}")
                
                # Presentation notes
                if result['sides_analysis']['presentation_notes']:
                    st.markdown("**Presentation Notes:**")
                    st.markdown(result['sides_analysis']['presentation_notes'])
                
                # Display raw JSON
                st.subheader("Raw JSON Output")
                st.json(result)
            
            # Feedback section
            st.subheader("Provide Feedback")
            feedback = st.text_area("How can we improve this description?", height=100)
            
            if st.button("Submit Feedback & Regenerate"):
                if feedback:
                    # Add feedback to history
                    st.session_state.feedback_history.append({
                        "timestamp": datetime.datetime.now().isoformat(),
                        "description": result["generated_description"],
                        "feedback": feedback
                    })
                    
                    with st.spinner("Regenerating description based on your feedback..."):
                        # Get the orchestrator
                        orchestrator = OrchestratorAgent()
                        
                        # Regenerate the description using the Culinary Wordsmith
                        new_description = orchestrator.culinary_wordsmith.generate_description(
                            result["refined_name"],
                            {
                                "items": result["identified_components"],
                                "cooking_style": result.get("cooking_style", ""),
                                "presentation": result.get("presentation", ""),
                                "spice_level": spice_level
                            },
                            result["dietary_analysis"],
                            feedback
                        )
                        
                        # Update the result with the new description
                        result["generated_description"] = new_description
                        st.session_state.result = result
                        
                        st.success("Description updated based on your feedback!")
                        st.markdown(f"*{new_description}*")
                    
                    # Display feedback history
                    if len(st.session_state.feedback_history) > 0:
                        with st.expander("Feedback History"):
                            for i, item in enumerate(reversed(st.session_state.feedback_history)):
                                st.markdown(f"**Feedback {len(st.session_state.feedback_history)-i}** - {item['timestamp']}")
                                st.markdown(f"*Description:* {item['description']}")
                                st.markdown(f"*Feedback:* {item['feedback']}")
                                st.markdown("---")
                else:
                    st.warning("Please enter feedback before submitting.")
        else:
            st.info("Upload an image and provide a dish name to generate a menu description.")

if __name__ == "__main__":
    main()