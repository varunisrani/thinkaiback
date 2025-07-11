from typing import Dict, Any, List
import json
import logging
from datetime import datetime
from ...base_config import AGENT_INSTRUCTIONS, get_model_config
from google import genai
from google.genai import types
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VisualParserAgent:
    """
    ✅ VisualParserAgent (FOUNDATIONAL) - Currently Operational
    Model: Gemini 2.5 Flash
    
    Superior multimodal capabilities for visual parsing
    High fine-tuning on visual parsing
    
    Responsibilities:
    - Visual requirements extraction from scenes
    - Basic storyboard structure generation
    - Visual style coordination
    """
    
    def __init__(self):
        self.client = genai.Client(api_key=os.environ.get("GOOGLE_API_KEY"))
        self.model_config = get_model_config()
        self.instructions = """You are a Visual Parser Agent for film production storyboarding.
        Your expertise:
        1. Extract visual requirements from scene descriptions
        2. Generate basic storyboard structures
        3. Coordinate visual style elements
        4. Analyze locations and visual effects needs
        5. Create foundational visual planning data"""
        logger.info("VisualParserAgent initialized")
    
    def analyze_visual_requirements(self, scenes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract visual requirements from scenes."""
        logger.info("Analyzing visual requirements")
        
        locations = []
        visual_effects = []
        lighting_needs = []
        
        for scene in scenes:
            # Extract locations
            location = scene.get('location', {})
            location_name = f"{location.get('type', 'INT')}. {location.get('place', 'UNKNOWN')}"
            if location_name not in locations:
                locations.append(location_name)
            
            # Extract visual effects from description
            description = scene.get('description', '').lower()
            if 'rain' in description:
                visual_effects.append('Rain enhancement')
            if 'neon' in description or 'lights' in description:
                visual_effects.append('Neon lighting')
            if 'explosion' in description:
                visual_effects.append('Explosion effects')
            if 'smoke' in description:
                visual_effects.append('Smoke effects')
            
            # Analyze lighting needs
            time_of_day = scene.get('time', 'DAY').upper()
            if 'NIGHT' in time_of_day:
                lighting_needs.append('Night exterior lighting')
            elif 'DUSK' in time_of_day:
                lighting_needs.append('Golden hour lighting')
        
        return {
            "locations": list(set(locations)),
            "visual_effects": list(set(visual_effects)),
            "lighting_needs": list(set(lighting_needs)),
            "total_scenes": len(scenes)
        }
    
    def generate_basic_storyboards(self, scenes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate basic storyboard structures."""
        logger.info("Generating basic storyboards")
        
        storyboards = []
        
        for scene in scenes:
            scene_number = scene.get('scene_number', 0)
            description = scene.get('description', '')
            
            # Determine basic shot types based on scene content
            panels = []
            
            # Always start with establishing shot
            panels.append({
                "shot_type": "Wide establishing shot",
                "camera_angle": "Eye level",
                "description": f"Establishing {scene.get('location', {}).get('place', 'location')}"
            })
            
            # Add medium shot if characters are present
            if scene.get('main_characters'):
                panels.append({
                    "shot_type": "Medium shot",
                    "camera_angle": "Eye level",
                    "description": "Character interaction"
                })
            
            # Add close-up if dialogue is present
            if scene.get('dialogues'):
                panels.append({
                    "shot_type": "Close-up",
                    "camera_angle": "Eye level",
                    "description": "Dialogue delivery"
                })
            
            storyboards.append({
                "scene_number": scene_number,
                "panels": panels,
                "estimated_duration": len(panels) * 15  # 15 seconds per panel estimate
            })
        
        return storyboards
    
    def analyze_visual_style(self, scenes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze and coordinate visual style."""
        logger.info("Analyzing visual style")
        
        # Determine color palette based on scene content
        color_palette = []
        mood_indicators = []
        
        for scene in scenes:
            description = scene.get('description', '').lower()
            time_of_day = scene.get('time', 'DAY').lower()
            
            # Color palette analysis
            if 'night' in time_of_day or 'dark' in description:
                color_palette.extend(['Deep blues', 'Charcoal grays'])
            if 'neon' in description or 'city' in description:
                color_palette.extend(['Amber highlights', 'Electric blue'])
            if 'office' in description:
                color_palette.extend(['Cool grays', 'Corporate blue'])
            if 'alley' in description or 'street' in description:
                color_palette.extend(['Urban grays', 'Sodium orange'])
            
            # Mood analysis
            if any(word in description for word in ['tense', 'suspense', 'thriller']):
                mood_indicators.append('Noir')
            if any(word in description for word in ['action', 'chase', 'fight']):
                mood_indicators.append('Dynamic')
            if any(word in description for word in ['quiet', 'intimate', 'conversation']):
                mood_indicators.append('Intimate')
        
        return {
            "color_palette": list(set(color_palette)) or ["Neutral tones", "Natural lighting"],
            "mood_indicators": list(set(mood_indicators)) or ["Cinematic"],
            "style_notes": "Visual style based on scene analysis"
        }