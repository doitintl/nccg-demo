import uuid
import datetime
from app.visionary_chef import VisionaryChefAgent
from app.authenticator import AuthenticatorAgent
from app.dietary_detective import DietaryDetectiveAgent
from app.side_item_analyzer import SideItemAnalyzerAgent
from app.culinary_wordsmith import CulinaryWordsmithAgent
from app.storage import StorageService

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
        chef_analysis["dish_name"] = dish_name
        
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
                "dietary_tags": dietary_analysis["dietary_tags"],
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