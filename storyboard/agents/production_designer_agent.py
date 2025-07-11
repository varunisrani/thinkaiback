from typing import Dict, Any, List
import json
import logging
from datetime import datetime
from base_config import AGENT_INSTRUCTIONS, get_model_config
from google import genai
from google.genai import types
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProductionDesignerAgent:
    """
    🚧 ProductionDesignerAgent (STYLE COORDINATION) - NEEDS IMPLEMENTATION
    Model: Gemini 2.5 Flash
    
    Visual style development
    High fine-tuning on design principles
    
    Responsibilities:
    - Visual style guide development
    - Department coordination
    - Construction requirements analysis
    """
    
    def __init__(self):
        self.client = genai.Client(api_key=os.environ.get("GOOGLE_API_KEY"))
        self.model_config = get_model_config()
        self.instructions = """You are a Production Designer Agent for film production.
        Your expertise:
        1. Develop comprehensive visual style guides
        2. Coordinate between departments (set dec, costume, makeup)
        3. Analyze construction and build requirements
        4. Manage color palettes and visual consistency
        5. Create production design documentation"""
        logger.info("ProductionDesignerAgent initialized")
    
    def generate_visual_style_guide(self, scenes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate comprehensive visual style guide."""
        logger.info("Generating visual style guide")
        
        # Analyze overall visual themes
        primary_colors = []
        forbidden_colors = []
        texture_themes = []
        
        for scene in scenes:
            description = scene.get('description', '').lower()
            time_of_day = scene.get('time', 'DAY').lower()
            location = scene.get('location', {})
            
            # Determine color palette based on content
            if 'night' in time_of_day or 'dark' in description:
                primary_colors.extend(['Deep blues', 'Charcoal grays'])
            if 'neon' in description or 'city' in description:
                primary_colors.extend(['Amber highlights', 'Electric blue'])
            if 'office' in description:
                primary_colors.extend(['Cool grays', 'Corporate blue'])
            
            # Identify forbidden colors that would clash
            if 'noir' in description or 'thriller' in description:
                forbidden_colors.extend(['Bright reds', 'Saturated greens'])
            
            # Texture analysis
            if 'urban' in description or 'city' in description:
                texture_themes.append('Industrial textures')
            if 'office' in description:
                texture_themes.append('Corporate sleek')
            if 'alley' in description:
                texture_themes.append('Weathered surfaces')
        
        return {
            "color_palette": {
                "primary": list(set(primary_colors)) or ["Neutral tones", "Natural colors"],
                "secondary": ["Muted earth tones", "Subdued accents"],
                "forbidden": list(set(forbidden_colors)) or ["Overly saturated colors"]
            },
            "texture_themes": list(set(texture_themes)) or ["Contemporary textures"],
            "style_principles": [
                "Maintain visual consistency across locations",
                "Support narrative through design choices",
                "Coordinate with lighting department"
            ],
            "reference_materials": self._generate_reference_materials(scenes)
        }
    
    def analyze_department_coordination(self, scenes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze coordination needs between departments."""
        logger.info("Analyzing department coordination")
        
        set_decoration = []
        costume_integration = []
        makeup_coordination = []
        
        for scene in scenes:
            description = scene.get('description', '').lower()
            location = scene.get('location', {})
            time_of_day = scene.get('time', 'DAY').lower()
            
            # Set decoration requirements
            if 'office' in description:
                set_decoration.append("Corporate office furnishings")
            if 'alley' in description:
                set_decoration.append("Urban decay elements")
            if 'neon' in description:
                set_decoration.append("Practical neon elements")
            
            # Costume coordination
            if 'night' in time_of_day:
                costume_integration.append("Dark, muted colors")
            if 'office' in description:
                costume_integration.append("Professional attire")
            if 'action' in description:
                costume_integration.append("Practical action wear")
            
            # Makeup coordination
            if 'night' in time_of_day:
                makeup_coordination.append("Low-light compatible makeup")
            if 'action' in description:
                makeup_coordination.append("Sweat-resistant makeup")
        
        return {
            "set_decoration": list(set(set_decoration)) or ["Standard set dressing"],
            "costume_integration": list(set(costume_integration)) or ["Contemporary wardrobe"],
            "makeup_coordination": list(set(makeup_coordination)) or ["Standard makeup"],
            "props_coordination": self._analyze_props_coordination(scenes),
            "lighting_coordination": "Coordinate with gaffer for practical elements"
        }
    
    def analyze_construction_requirements(self, scenes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze construction and build requirements."""
        logger.info("Analyzing construction requirements")
        
        built_sets = []
        location_modifications = []
        special_builds = []
        
        for scene in scenes:
            description = scene.get('description', '').lower()
            location = scene.get('location', {})
            location_type = location.get('type', 'INT')
            place = location.get('place', '').lower()
            
            # Identify sets that need building
            if location_type == 'INT':
                if 'office' in place:
                    built_sets.append("Corporate office interior")
                elif 'apartment' in place:
                    built_sets.append("Residential interior")
                elif 'police' in place:
                    built_sets.append("Police station interior")
                elif 'restaurant' in place:
                    built_sets.append("Restaurant interior")
            
            # Special construction needs
            if 'destruction' in description or 'damage' in description:
                special_builds.append("Breakaway elements")
            if 'water' in description:
                special_builds.append("Water-safe construction")
            if 'fire' in description:
                special_builds.append("Fire-safe materials")
            
            # Location modifications
            if 'neon' in description:
                location_modifications.append("Neon installation")
            if 'period' in description:
                location_modifications.append("Period-appropriate modifications")
        
        return {
            "built_sets": list(set(built_sets)) or ["No major set builds required"],
            "location_modifications": list(set(location_modifications)) or ["Minimal modifications"],
            "special_builds": list(set(special_builds)) or ["Standard construction"],
            "construction_timeline": self._estimate_construction_timeline(built_sets, special_builds),
            "budget_considerations": self._analyze_construction_budget(built_sets, special_builds)
        }
    
    def _generate_reference_materials(self, scenes: List[Dict[str, Any]]) -> List[str]:
        """Generate reference material suggestions."""
        references = []
        
        for scene in scenes:
            description = scene.get('description', '').lower()
            
            if 'noir' in description or 'detective' in description:
                references.append("Classic film noir production design")
            if 'contemporary' in description:
                references.append("Modern architectural references")
            if 'urban' in description:
                references.append("Urban decay photography")
            if 'office' in description:
                references.append("Corporate interior design")
        
        return list(set(references)) or ["Contemporary design references"]
    
    def _analyze_props_coordination(self, scenes: List[Dict[str, Any]]) -> List[str]:
        """Analyze props coordination needs."""
        props_needs = []
        
        for scene in scenes:
            description = scene.get('description', '').lower()
            
            if 'phone' in description:
                props_needs.append("Period-appropriate phones")
            if 'car' in description:
                props_needs.append("Vehicle coordination")
            if 'weapon' in description:
                props_needs.append("Weapon props and safety")
            if 'food' in description:
                props_needs.append("Food styling coordination")
        
        return list(set(props_needs)) or ["Standard props coordination"]
    
    def _estimate_construction_timeline(self, built_sets: List[str], special_builds: List[str]) -> Dict[str, str]:
        """Estimate construction timeline."""
        weeks_needed = len(built_sets) * 2 + len(special_builds) * 1
        
        return {
            "estimated_weeks": str(max(weeks_needed, 2)),
            "pre_production_start": "8 weeks before principal photography",
            "completion_target": "1 week before principal photography"
        }
    
    def _analyze_construction_budget(self, built_sets: List[str], special_builds: List[str]) -> Dict[str, str]:
        """Analyze construction budget considerations."""
        base_cost = len(built_sets) * 25000  # $25k per set estimate
        special_cost = len(special_builds) * 10000  # $10k per special build
        
        return {
            "estimated_budget": f"${base_cost + special_cost:,}",
            "cost_factors": [
                "Materials and labor",
                "Special effects integration",
                "Safety requirements"
            ],
            "budget_priority": "High" if base_cost + special_cost > 100000 else "Medium"
        }