import os
import json
import uuid
import datetime
import streamlit as st
from PIL import Image
import sys

# Add the app directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import modules using direct imports
from visionary_chef import VisionaryChefAgent
from authenticator import AuthenticatorAgent
from dietary_detective import DietaryDetectiveAgent
from side_item_analyzer import SideItemAnalyzerAgent
from culinary_wordsmith import CulinaryWordsmithAgent
from storage import StorageService
import bedrock_utils
import config

# Set page configuration
st.set_page_config(
    page_title="Menu Maestro",
    page_icon="🍽️",
    layout="wide"
)

# Create uploads folder if it doesn't exist
os.makedirs(config.UPLOAD_FOLDER, exist_ok=True)

# Initialize services
storage_service = StorageService()

class OrchestratorAgent:
    """Manages the workflow between specialized agents"""
    
    def __init__(self):
        self.visionary_chef = VisionaryChefAgent()
        self.authenticator = AuthenticatorAgent()
        self.dietary_detective = DietaryDetectiveAgent()
        self.side_item_analyzer = SideItemAnalyzerAgent()
        self.culinary_wordsmith = CulinaryWordsmithAgent()
        self.storage = StorageService()
    
    def process_dish(self, dish_name, image_bytes, spice_level="Medium"):
        """Process a dish through the entire agent pipeline"""
        workflow_id = str(uuid.uuid4())
        
        # Step 1: Save the image
        image_path = self.storage.save_image(image_bytes, workflow_id)
        
        # Step 2: Analyze the image with the Visionary Chef
        chef_analysis = self.visionary_chef.analyze_image(dish_name, image_bytes)
        chef_analysis["spice_level"] = spice_level
        
        # Check if the image contains food
        if not chef_analysis.get("is_food", True):
            return {
                "error": "The uploaded image does not appear to contain food. Please upload an image of a food dish."
            }
        
        # Step 3: Validate the dish name with the Authenticator
        auth_result = self.authenticator.validate_name(dish_name, chef_analysis)
        
        # Step 4: Analyze dietary aspects with the Dietary Detective
        dietary_analysis = self.dietary_detective.analyze_dietary(chef_analysis)
        
        # Step 5: Analyze side items with the Side Item Analyzer
        sides_analysis = self.side_item_analyzer.analyze_sides(dish_name, image_bytes, chef_analysis)
        
        # Step 6: Generate the description with the Culinary Wordsmith
        description = self.culinary_wordsmith.generate_description(
            auth_result["suggested_name"], 
            chef_analysis, 
            dietary_analysis,
            sides_analysis
        )
        
        # Compile the final result
        result = {
            "dish_id": workflow_id,
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

def main():
    # App title and description
    st.title("🍽️ Menu Maestro")
    st.markdown("""
    Transform your food images into comprehensive menu descriptions using our AI-powered system.
    Upload an image of your dish, provide a description, and let our team of specialized AI agents do the rest!
    """)
    
    # Display current configuration
    st.sidebar.subheader("Configuration")
    st.sidebar.text(f"Environment: {config.ENVIRONMENT}")
    st.sidebar.text(f"AWS Region: {config.AWS_REGION}")
    st.sidebar.text(f"Model ID: {config.BEDROCK_MODEL_ID}")
    
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
            st.image(image, caption="Uploaded Dish Image", width=None)
        
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
            
            # Step 1: Analyze the image with the Visionary Chef
            with st.spinner("🧑‍🍳 Visionary Chef is analyzing the image..."):
                chef_analysis = orchestrator.visionary_chef.analyze_image(dish_name, image_bytes)
                chef_analysis["spice_level"] = spice_level
                chef_analysis["dish_name"] = dish_name
                
                # Check if the image contains food
                if not chef_analysis.get("is_food", True):
                    st.error("⚠️ The uploaded image does not appear to contain food. Please upload an image of a food dish.")
                    st.stop()
                
                # Show a preview of identified components
                with st.expander("🔍 Visionary Chef Analysis", expanded=False):
                    st.write("Identified Components:")
                    for item in chef_analysis["items"][:5]:  # Show top 5 items
                        confidence = item['confidence']
                        confidence_color = "#4CAF50" if confidence > 0.8 else "#FFC107" if confidence > 0.6 else "#F44336"
                        st.markdown(f"- {item['item']} <span style='color:{confidence_color};'>({confidence:.2f})</span>", unsafe_allow_html=True)
                    if len(chef_analysis["items"]) > 5:
                        st.write(f"...and {len(chef_analysis['items']) - 5} more items")
            
            # Step 2: Validate the dish name with the Authenticator
            with st.spinner("🔍 Authenticator is validating the dish description..."):
                auth_result = orchestrator.authenticator.validate_name(dish_name, chef_analysis)
                
                # Show validation result
                with st.expander("✅ Authenticator Result", expanded=False):
                    st.write(f"Validation Status: {auth_result['validation_status']}")
                    if auth_result.get("reason"):
                        st.write(f"Reason: {auth_result['reason']}")
                    st.write(f"Suggested Name: {auth_result['suggested_name']}")
            
            # Step 3: Analyze dietary aspects with the Dietary Detective
            with st.spinner("🥗 Dietary Detective is identifying allergens and dietary tags..."):
                dietary_analysis = orchestrator.dietary_detective.analyze_dietary(chef_analysis)
                
                # Show dietary analysis preview
                with st.expander("🍽️ Dietary Analysis", expanded=False):
                    if dietary_analysis["allergens"]:
                        st.write("Allergens:", ", ".join(dietary_analysis["allergens"]))
                    else:
                        st.write("No major allergens detected")
                    st.write("Dietary Tags:", ", ".join(dietary_analysis["dietary_tags"]))
            
            # Step 4: Analyze side items with the Side Item Analyzer
            with st.spinner("🍟 Side Item Analyzer is identifying accompaniments..."):
                sides_analysis = orchestrator.side_item_analyzer.analyze_sides(dish_name, image_bytes, chef_analysis)
                
                # Show sides analysis preview
                with st.expander("🍽️ Side Item Analysis", expanded=False):
                    if sides_analysis.get("main_dish_components"):
                        st.write("Main Dish Components:", ", ".join(sides_analysis["main_dish_components"][:3]))
                    if sides_analysis.get("side_items"):
                        st.write("Side Items:", ", ".join([item["name"] for item in sides_analysis["side_items"][:3]]))
            
            # Step 5: Generate the description with the Culinary Wordsmith
            with st.spinner("✍️ Culinary Wordsmith is crafting the perfect description..."):
                description = orchestrator.culinary_wordsmith.generate_description(
                    auth_result["suggested_name"], 
                    chef_analysis, 
                    dietary_analysis,
                    sides_analysis
                )
                
                # Compile the final result
                result = {
                    "dish_id": str(uuid.uuid4()),
                    "input_name": dish_name,
                    "processed_timestamp": datetime.datetime.now().isoformat(),
                    "refined_name": auth_result["suggested_name"],
                    "generated_description": description,
                    "validation": {
                        "status": auth_result["validation_status"],
                        "notes": auth_result.get("reason", "")
                    },
                    "dietary_analysis": dietary_analysis,
                    "sides_analysis": sides_analysis,
                    "identified_components": chef_analysis["items"]
                }
                
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
            
            # Major allergens to check
            major_allergens = [
                "Dairy", "Milk", "Lactose", 
                "Eggs", 
                "Peanuts", 
                "Tree Nuts", "Nuts", "Almonds", "Walnuts", "Cashews",
                "Fish", 
                "Shellfish", "Shrimp", "Crab", "Lobster",
                "Wheat", "Gluten",
                "Soy", "Soybeans"
            ]
            
            # Check for allergen-free status
            allergen_free = []
            detected_allergens = [a.lower() for a in result['dietary_analysis']['allergens']]
            potential_allergens = [a.lower() for a in result['dietary_analysis'].get('potential_allergens', [])]
            
            for allergen in major_allergens:
                if not any(allergen.lower() in a for a in detected_allergens) and not any(allergen.lower() in a for a in potential_allergens):
                    # Add to allergen-free list, but avoid duplicates (e.g., if "Dairy" is free, don't also add "Milk")
                    if allergen.lower() == "dairy" and "Dairy-free" not in allergen_free:
                        allergen_free.append("Dairy-free")
                    elif allergen.lower() == "milk" and "Dairy-free" not in allergen_free:
                        allergen_free.append("Dairy-free")
                    elif allergen.lower() == "lactose" and "Dairy-free" not in allergen_free:
                        allergen_free.append("Dairy-free")
                    elif allergen.lower() == "eggs" and "Egg-free" not in allergen_free:
                        allergen_free.append("Egg-free")
                    elif allergen.lower() == "peanuts" and "Peanut-free" not in allergen_free:
                        allergen_free.append("Peanut-free")
                    elif allergen.lower() in ["tree nuts", "nuts", "almonds", "walnuts", "cashews"] and "Tree Nut-free" not in allergen_free:
                        allergen_free.append("Tree Nut-free")
                    elif allergen.lower() == "fish" and "Fish-free" not in allergen_free:
                        allergen_free.append("Fish-free")
                    elif allergen.lower() in ["shellfish", "shrimp", "crab", "lobster"] and "Shellfish-free" not in allergen_free:
                        allergen_free.append("Shellfish-free")
                    elif allergen.lower() in ["wheat", "gluten"] and "Gluten-free" not in allergen_free:
                        allergen_free.append("Gluten-free")
                    elif allergen.lower() in ["soy", "soybeans"] and "Soy-free" not in allergen_free:
                        allergen_free.append("Soy-free")
            
            # Display allergen-free status
            if allergen_free:
                st.success("✅ " + ", ".join(allergen_free))
            
            # Display allergens
            if result['dietary_analysis']['allergens']:
                st.warning("⚠️ Allergens: " + ", ".join(result['dietary_analysis']['allergens']))
            else:
                st.success("No major allergens detected")
                
            # Display potential allergens
            if result['dietary_analysis'].get('potential_allergens'):
                st.info("ℹ️ Potential Sensitivities: " + ", ".join(result['dietary_analysis']['potential_allergens']))
            
            # Display dietary tags
            if result['dietary_analysis']['dietary_tags']:
                tags_html = ""
                for tag in result['dietary_analysis']['dietary_tags']:
                    tags_html += f'<span style="background-color: #e6f3e6; color: #2e7d32; padding: 3px 8px; border-radius: 12px; margin-right: 6px;">{tag}</span>'
                st.markdown(f"Dietary Tags: {tags_html}", unsafe_allow_html=True)
            
            # Display disclaimer
            st.caption(result['dietary_analysis']['disclaimer'])
            
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
                            result["sides_analysis"],
                            feedback
                        )
                        
                        # Update the result with the new description
                        result["generated_description"] = new_description
                        st.session_state.result = result
                        
                        st.success("Description updated based on your feedback!")
                        st.markdown(f"*{new_description}*")
                else:
                    st.warning("Please enter feedback before submitting.")
        else:
            st.info("Upload an image and provide a dish description to generate a menu description.")

if __name__ == "__main__":
    main()