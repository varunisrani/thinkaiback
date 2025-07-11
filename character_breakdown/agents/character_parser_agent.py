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

class CharacterParserAgent:
    """
    👤 CharacterParserAgent (FOUNDATIONAL)
    
    Specialized agent for foundational character parsing and entity recognition.
    Responsibilities:
    - Named entity recognition for characters
    - First appearance tracking
    - Character type classification (protagonist, antagonist, etc.)
    - Basic dialogue distribution analysis
    - Character scene presence mapping
    """
    
    def __init__(self):
        self.client = genai.Client(api_key=os.environ.get("GOOGLE_API_KEY"))
        self.model_config = get_model_config()
        self.instructions = """You are a Character Parser Agent for film production.
        Your expertise:
        1. Extract and identify all characters from script data
        2. Classify character types (protagonist, antagonist, supporting, etc.)
        3. Track first appearances and scene presence
        4. Calculate basic dialogue distribution
        5. Build foundational character profiles"""
        logger.info("CharacterParserAgent initialized")
    
    def parse_characters(self, scene_data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse characters from scene data to create foundational character profiles."""
        logger.info("Starting character parsing analysis")
        
        if not scene_data or not isinstance(scene_data, dict):
            logger.error("Invalid scene data received")
            return {"error": "Invalid scene data format"}
        
        scenes = scene_data.get('scenes', [])
        logger.info(f"Processing character parsing for {len(scenes)} scenes")
        
        # Core character parsing
        character_profiles = self._extract_character_profiles(scenes)
        character_types = self._classify_character_types(character_profiles, scenes)
        dialogue_distribution = self._calculate_dialogue_distribution(scenes)
        scene_presence = self._map_scene_presence(scenes)
        basic_relationships = self._identify_basic_relationships(scenes)
        
        result = {
            "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "characters": character_profiles,
            "character_types": character_types,
            "dialogue_distribution": dialogue_distribution,
            "scene_presence": scene_presence,
            "basic_relationships": basic_relationships,
            "parsing_statistics": self._generate_parsing_statistics(character_profiles, scenes)
        }
        
        logger.info(f"Generated character parsing for {len(character_profiles)} characters")
        return result
    
    def _extract_character_profiles(self, scenes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract foundational character profiles from scenes."""
        character_data = {}
        
        for scene_idx, scene in enumerate(scenes):
            scene_number = scene.get('scene_number', scene_idx + 1)
            
            # Extract characters from main_characters field
            main_characters = scene.get('main_characters', [])
            for char_name in main_characters:
                if char_name not in character_data:
                    character_data[char_name] = {
                        "name": char_name,
                        "first_appearance": scene_number,
                        "total_scenes": 0,
                        "dialogue_count": 0,
                        "scene_numbers": []
                    }
                
                character_data[char_name]["total_scenes"] += 1
                character_data[char_name]["scene_numbers"].append(scene_number)
            
            # Extract characters from dialogues
            dialogues = scene.get('dialogues', [])
            for dialogue in dialogues:
                char_name = dialogue.get('character', '')
                if char_name and char_name not in character_data:
                    character_data[char_name] = {
                        "name": char_name,
                        "first_appearance": scene_number,
                        "total_scenes": 0,
                        "dialogue_count": 0,
                        "scene_numbers": []
                    }
                
                if char_name:
                    character_data[char_name]["dialogue_count"] += 1
                    if scene_number not in character_data[char_name]["scene_numbers"]:
                        character_data[char_name]["total_scenes"] += 1
                        character_data[char_name]["scene_numbers"].append(scene_number)
        
        # Convert to list and sort by first appearance
        characters = list(character_data.values())
        characters.sort(key=lambda x: x["first_appearance"])
        
        return characters
    
    def _classify_character_types(self, character_profiles: List[Dict[str, Any]], 
                                 scenes: List[Dict[str, Any]]) -> Dict[str, str]:
        """Classify characters by type based on scene presence and dialogue."""
        character_types = {}
        total_scenes = len(scenes)
        
        # Sort characters by scene presence and dialogue count
        sorted_chars = sorted(character_profiles, 
                            key=lambda x: (x["total_scenes"], x["dialogue_count"]), 
                            reverse=True)
        
        for i, char in enumerate(sorted_chars):
            char_name = char["name"]
            scene_percentage = (char["total_scenes"] / total_scenes) * 100
            dialogue_count = char["dialogue_count"]
            
            # Classification logic
            if i == 0 and scene_percentage > 50:
                character_types[char_name] = "PROTAGONIST"
            elif scene_percentage > 40 and dialogue_count > 20:
                character_types[char_name] = "LEAD"
            elif scene_percentage > 25 and dialogue_count > 10:
                character_types[char_name] = "SUPPORTING_LEAD"
            elif scene_percentage > 15 or dialogue_count > 5:
                character_types[char_name] = "SUPPORTING"
            elif dialogue_count > 0:
                character_types[char_name] = "FEATURED"
            else:
                character_types[char_name] = "BACKGROUND"
        
        return character_types
    
    def _calculate_dialogue_distribution(self, scenes: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate dialogue distribution percentages across characters."""
        dialogue_counts = {}
        total_dialogues = 0
        
        for scene in scenes:
            dialogues = scene.get('dialogues', [])
            for dialogue in dialogues:
                char_name = dialogue.get('character', '')
                if char_name:
                    dialogue_counts[char_name] = dialogue_counts.get(char_name, 0) + 1
                    total_dialogues += 1
        
        # Calculate percentages
        dialogue_distribution = {}
        for char_name, count in dialogue_counts.items():
            dialogue_distribution[char_name] = round((count / total_dialogues) * 100, 1)
        
        return dialogue_distribution
    
    def _map_scene_presence(self, scenes: List[Dict[str, Any]]) -> Dict[str, List[int]]:
        """Map which scenes each character appears in."""
        scene_presence = {}
        
        for scene_idx, scene in enumerate(scenes):
            scene_number = scene.get('scene_number', scene_idx + 1)
            
            # From main_characters
            main_characters = scene.get('main_characters', [])
            for char_name in main_characters:
                if char_name not in scene_presence:
                    scene_presence[char_name] = []
                if scene_number not in scene_presence[char_name]:
                    scene_presence[char_name].append(scene_number)
            
            # From dialogues
            dialogues = scene.get('dialogues', [])
            speaking_chars = set([d.get('character', '') for d in dialogues if d.get('character')])
            for char_name in speaking_chars:
                if char_name not in scene_presence:
                    scene_presence[char_name] = []
                if scene_number not in scene_presence[char_name]:
                    scene_presence[char_name].append(scene_number)
        
        # Sort scene numbers for each character
        for char_name in scene_presence:
            scene_presence[char_name].sort()
        
        return scene_presence
    
    def _identify_basic_relationships(self, scenes: List[Dict[str, Any]]) -> List[List[str]]:
        """Identify basic character relationships from scene co-appearances."""
        relationships = []
        character_pairs = {}
        
        for scene in scenes:
            # Get all characters in this scene
            scene_characters = set(scene.get('main_characters', []))
            
            # Add speaking characters
            dialogues = scene.get('dialogues', [])
            speaking_chars = set([d.get('character', '') for d in dialogues if d.get('character')])
            scene_characters.update(speaking_chars)
            
            # Create pairs for characters appearing together
            scene_chars_list = list(scene_characters)
            for i in range(len(scene_chars_list)):
                for j in range(i + 1, len(scene_chars_list)):
                    char1, char2 = scene_chars_list[i], scene_chars_list[j]
                    pair_key = tuple(sorted([char1, char2]))
                    character_pairs[pair_key] = character_pairs.get(pair_key, 0) + 1
        
        # Extract significant relationships (appear together in 3+ scenes)
        for (char1, char2), count in character_pairs.items():
            if count >= 3:
                relationships.append([char1, char2, "frequent_interaction"])
        
        return relationships
    
    def _generate_parsing_statistics(self, character_profiles: List[Dict[str, Any]], 
                                   scenes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate parsing statistics for the character analysis."""
        total_characters = len(character_profiles)
        total_scenes = len(scenes)
        
        # Calculate speaking vs non-speaking characters
        speaking_chars = sum(1 for char in character_profiles if char["dialogue_count"] > 0)
        non_speaking_chars = total_characters - speaking_chars
        
        # Calculate scene coverage
        scene_coverage = {}
        for char in character_profiles:
            coverage = (char["total_scenes"] / total_scenes) * 100
            scene_coverage[char["name"]] = round(coverage, 1)
        
        # Top characters by dialogue
        top_speakers = sorted(character_profiles, key=lambda x: x["dialogue_count"], reverse=True)[:5]
        
        return {
            "total_characters": total_characters,
            "speaking_characters": speaking_chars,
            "non_speaking_characters": non_speaking_chars,
            "average_scenes_per_character": round(sum(char["total_scenes"] for char in character_profiles) / total_characters, 1),
            "scene_coverage": scene_coverage,
            "top_speakers": [{"name": char["name"], "dialogue_count": char["dialogue_count"]} for char in top_speakers]
        }