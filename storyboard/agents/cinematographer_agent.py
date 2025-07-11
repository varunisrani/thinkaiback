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

class CinematographerAgent:
    """
    🚧 CinematographerAgent (SHOT LISTS) - NEEDS IMPLEMENTATION
    Model: Gemini 2.5 Flash
    
    Visual composition planning
    Very high fine-tuning on cinematography
    
    Responsibilities:
    - Shot list generation for each scene
    - Camera angle and movement specifications
    - Technical requirements planning
    """
    
    def __init__(self):
        self.client = genai.Client(api_key=os.environ.get("GOOGLE_API_KEY"))
        self.model_config = get_model_config()
        self.instructions = """You are a Cinematographer Agent for film production.
        Your expertise:
        1. Generate detailed shot lists for each scene
        2. Specify camera angles, movements, and compositions
        3. Plan technical requirements and equipment needs
        4. Estimate setup times and crew requirements
        5. Coordinate with other departments for visual execution"""
        logger.info("CinematographerAgent initialized")
    
    def generate_shot_lists(self, scenes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate detailed shot lists for scenes."""
        logger.info("Generating shot lists")
        
        shot_lists = {}
        
        for scene in scenes:
            scene_number = str(scene.get('scene_number', 0))
            description = scene.get('description', '')
            dialogues = scene.get('dialogues', [])
            
            scene_shots = {}
            shot_counter = 1
            
            # Establishing shot
            shot_id = f"shot_{scene_number}A"
            scene_shots[shot_id] = {
                "scene_number": scene_number,
                "shot_type": "Wide establishing shot",
                "camera_angle": "Eye level",
                "lens": "24mm",
                "movement": "Static",
                "estimated_setup": "30 minutes",
                "description": f"Establish location and context"
            }
            
            # Character shots based on dialogue
            if dialogues:
                for i, dialogue in enumerate(dialogues):
                    shot_counter += 1
                    shot_id = f"shot_{scene_number}{chr(64 + shot_counter)}"  # A, B, C, etc.
                    
                    scene_shots[shot_id] = {
                        "scene_number": scene_number,
                        "shot_type": "Medium shot" if i % 2 == 0 else "Close-up",
                        "camera_angle": "Eye level",
                        "lens": "50mm" if i % 2 == 0 else "85mm",
                        "movement": "Static",
                        "estimated_setup": "15 minutes",
                        "description": f"Character: {dialogue.get('character', 'Unknown')}"
                    }
            
            # Action shots if scene has action
            if any(word in description.lower() for word in ['action', 'fight', 'chase', 'run']):
                shot_counter += 1
                shot_id = f"shot_{scene_number}{chr(64 + shot_counter)}"
                
                scene_shots[shot_id] = {
                    "scene_number": scene_number,
                    "shot_type": "Tracking shot",
                    "camera_angle": "Dynamic",
                    "lens": "35mm",
                    "movement": "Handheld/Steadicam",
                    "estimated_setup": "45 minutes",
                    "description": "Action sequence coverage"
                }
            
            shot_lists[f"scene_{scene_number}"] = scene_shots
        
        return shot_lists
    
    def analyze_camera_requirements(self, scenes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze camera and equipment requirements."""
        logger.info("Analyzing camera requirements")
        
        # Determine camera needs based on scene complexity
        has_action = any('action' in scene.get('description', '').lower() for scene in scenes)
        has_night = any('night' in scene.get('time', '').lower() for scene in scenes)
        has_exteriors = any(scene.get('location', {}).get('type') == 'EXT' for scene in scenes)
        
        camera_requirements = {
            "primary_camera": "RED Komodo" if has_action else "ARRI Alexa Mini",
            "backup_camera": "ARRI Alexa Mini",
            "lens_package": "Zeiss CP.3 Prime Set",
            "additional_lenses": []
        }
        
        if has_action:
            camera_requirements["additional_lenses"].append("Zoom lens for coverage")
        if has_night:
            camera_requirements["additional_lenses"].append("Fast primes for low light")
        if has_exteriors:
            camera_requirements["additional_lenses"].append("Wide angle for landscapes")
        
        return camera_requirements
    
    def identify_technical_tests(self, scenes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Identify technical tests needed."""
        logger.info("Identifying technical tests")
        
        tests = {}
        
        # Check for specific technical challenges
        has_night_exteriors = any(
            scene.get('location', {}).get('type') == 'EXT' and 
            'night' in scene.get('time', '').lower()
            for scene in scenes
        )
        
        if has_night_exteriors:
            tests["low_light_performance"] = "Test needed for night exteriors"
        
        has_water_scenes = any(
            'water' in scene.get('description', '').lower() or
            'rain' in scene.get('description', '').lower()
            for scene in scenes
        )
        
        if has_water_scenes:
            tests["weather_protection"] = "Camera protection tests for water scenes"
        
        has_vehicle_scenes = any(
            'car' in scene.get('description', '').lower() or
            'vehicle' in scene.get('description', '').lower()
            for scene in scenes
        )
        
        if has_vehicle_scenes:
            tests["vehicle_rigging"] = "Camera mount and rigging tests"
        
        return tests or {"standard_tests": "No special technical tests required"}