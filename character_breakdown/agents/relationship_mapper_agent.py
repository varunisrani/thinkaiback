from typing import Dict, Any, List, Tuple, Set
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

class RelationshipMapperAgent:
    """
    👤 RelationshipMapperAgent (CHARACTER DYNAMICS)
    
    Specialized agent for character relationship analysis and dynamics mapping.
    Responsibilities:
    - Relationship network construction (romantic, professional, adversarial)
    - Scene interaction analysis with power dynamics
    - Character arc progression tracking
    - Conflict mapping and resolution patterns
    - Social hierarchy and influence analysis
    """
    
    def __init__(self):
        self.client = genai.Client(api_key=os.environ.get("GOOGLE_API_KEY"))
        self.model_config = get_model_config()
        self.instructions = """You are a Relationship Mapper Agent for film production.
        Your expertise:
        1. Map complex character relationships and social networks
        2. Analyze power dynamics and emotional connections
        3. Track character growth and relationship evolution
        4. Identify conflict patterns and resolution strategies
        5. Generate comprehensive relationship charts for directors and actors"""
        logger.info("RelationshipMapperAgent initialized")
    
    def map_relationships(self, scene_data: Dict[str, Any], 
                         character_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate comprehensive relationship mapping and dynamics analysis."""
        logger.info("Starting relationship mapping analysis")
        
        if not scene_data or not isinstance(scene_data, dict):
            logger.error("Invalid scene data received")
            return {"error": "Invalid scene data format"}
        
        scenes = scene_data.get('scenes', [])
        characters = character_data.get('characters', []) if character_data else []
        logger.info(f"Processing relationship mapping for {len(characters)} characters across {len(scenes)} scenes")
        
        # Core relationship analysis
        relationship_network = self._build_relationship_network(characters, scenes)
        scene_interactions = self._analyze_scene_interactions(scenes)
        character_arcs = self._track_character_arcs(characters, scenes)
        power_dynamics = self._analyze_power_dynamics(scenes)
        conflict_analysis = self._map_conflicts_and_resolutions(scenes)
        
        result = {
            "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "relationship_network": relationship_network,
            "scene_interactions": scene_interactions,
            "character_arcs": character_arcs,
            "power_dynamics": power_dynamics,
            "conflict_analysis": conflict_analysis,
            "social_hierarchy": self._generate_social_hierarchy(relationship_network, power_dynamics)
        }
        
        logger.info(f"Generated relationship mapping for {len(relationship_network)} relationship types")
        return result
    
    def _build_relationship_network(self, characters: List[Dict[str, Any]], 
                                   scenes: List[Dict[str, Any]]) -> Dict[str, List[List[str]]]:
        """Build comprehensive relationship network between characters."""
        relationships = {
            "romantic": [],
            "family": [],
            "professional": [],
            "friendship": [],
            "adversarial": [],
            "mentor_student": [],
            "alliance": [],
            "rivalry": []
        }
        
        # Track character co-appearances and interaction patterns
        character_interactions = {}
        character_names = [char.get('name', '') for char in characters]
        
        for scene in scenes:
            scene_number = scene.get('scene_number', '0')
            main_characters = scene.get('main_characters', [])
            dialogues = scene.get('dialogues', [])
            description = scene.get('description', '').lower()
            
            # Get speaking characters in this scene
            speaking_chars = set([d.get('character', '') for d in dialogues if d.get('character')])
            all_scene_chars = set(main_characters) | speaking_chars
            
            # Analyze pairs of characters in scenes
            scene_chars_list = list(all_scene_chars)
            for i in range(len(scene_chars_list)):
                for j in range(i + 1, len(scene_chars_list)):
                    char1, char2 = scene_chars_list[i], scene_chars_list[j]
                    pair_key = tuple(sorted([char1, char2]))
                    
                    if pair_key not in character_interactions:
                        character_interactions[pair_key] = {
                            "scenes": [],
                            "dialogue_exchanges": 0,
                            "relationship_indicators": []
                        }
                    
                    character_interactions[pair_key]["scenes"].append(scene_number)
                    
                    # Count dialogue exchanges between these characters
                    for k, dialogue in enumerate(dialogues):
                        if (dialogue.get('character') == char1 and 
                            k + 1 < len(dialogues) and 
                            dialogues[k + 1].get('character') == char2):
                            character_interactions[pair_key]["dialogue_exchanges"] += 1
                    
                    # Analyze relationship indicators from scene description
                    relationship_indicators = self._extract_relationship_indicators(
                        description, char1, char2)
                    character_interactions[pair_key]["relationship_indicators"].extend(
                        relationship_indicators)
        
        # Classify relationships based on interaction patterns
        for (char1, char2), interaction_data in character_interactions.items():
            scenes_together = len(interaction_data["scenes"])
            dialogue_exchanges = interaction_data["dialogue_exchanges"]
            indicators = interaction_data["relationship_indicators"]
            
            if scenes_together >= 3:  # Characters with significant interaction
                relationship_type = self._classify_relationship(indicators, dialogue_exchanges)
                if relationship_type:
                    relationships[relationship_type].append([char1, char2])
        
        return relationships
    
    def _extract_relationship_indicators(self, description: str, char1: str, char2: str) -> List[str]:
        """Extract relationship indicators from scene descriptions."""
        indicators = []
        
        # Romantic indicators
        if any(keyword in description for keyword in ['kiss', 'love', 'romantic', 'date', 'couple']):
            indicators.append('romantic')
        
        # Professional indicators
        if any(keyword in description for keyword in ['boss', 'employee', 'work', 'office', 'meeting']):
            indicators.append('professional')
        
        # Family indicators
        if any(keyword in description for keyword in ['father', 'mother', 'son', 'daughter', 'family', 'brother', 'sister']):
            indicators.append('family')
        
        # Adversarial indicators
        if any(keyword in description for keyword in ['fight', 'argue', 'enemy', 'conflict', 'angry']):
            indicators.append('adversarial')
        
        # Friendship indicators
        if any(keyword in description for keyword in ['friend', 'buddy', 'pal', 'laugh', 'fun']):
            indicators.append('friendship')
        
        # Mentor/student indicators
        if any(keyword in description for keyword in ['teach', 'learn', 'mentor', 'student', 'guide']):
            indicators.append('mentor_student')
        
        return indicators
    
    def _classify_relationship(self, indicators: List[str], dialogue_exchanges: int) -> str:
        """Classify relationship type based on indicators."""
        indicator_counts = {}
        for indicator in indicators:
            indicator_counts[indicator] = indicator_counts.get(indicator, 0) + 1
        
        if not indicator_counts:
            if dialogue_exchanges >= 5:
                return 'professional'  # Default for high interaction
            return None
        
        # Return the most frequent relationship type
        return max(indicator_counts, key=indicator_counts.get)
    
    def _analyze_scene_interactions(self, scenes: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """Analyze character interactions within each scene."""
        scene_interactions = {}
        
        for scene in scenes:
            scene_number = scene.get('scene_number', '0')
            main_characters = scene.get('main_characters', [])
            dialogues = scene.get('dialogues', [])
            description = scene.get('description', '').lower()
            
            # Analyze power dynamics in scene
            power_balance = self._analyze_scene_power_balance(dialogues, main_characters)
            
            # Identify emotional tone
            emotional_tone = self._identify_emotional_tone(description, dialogues)
            
            # Map character interactions
            interactions = []
            for i, dialogue in enumerate(dialogues):
                if i + 1 < len(dialogues):
                    current_char = dialogue.get('character', '')
                    next_char = dialogues[i + 1].get('character', '')
                    if current_char != next_char and current_char and next_char:
                        interactions.append({
                            "from": current_char,
                            "to": next_char,
                            "exchange_type": self._classify_dialogue_exchange(
                                dialogue.get('text', ''), dialogues[i + 1].get('text', ''))
                        })
            
            scene_interactions[scene_number] = {
                "characters_present": main_characters,
                "power_balance": power_balance,
                "emotional_tone": emotional_tone,
                "interactions": interactions,
                "dynamics": self._summarize_scene_dynamics(description, main_characters)
            }
        
        return scene_interactions
    
    def _analyze_scene_power_balance(self, dialogues: List[Dict[str, Any]], 
                                   characters: List[str]) -> str:
        """Analyze power balance in scene based on dialogue patterns."""
        if len(characters) < 2:
            return "Single character"
        
        # Count dialogue distribution
        dialogue_counts = {}
        for dialogue in dialogues:
            char = dialogue.get('character', '')
            if char:
                dialogue_counts[char] = dialogue_counts.get(char, 0) + 1
        
        if not dialogue_counts:
            return "Equal"
        
        max_count = max(dialogue_counts.values())
        min_count = min(dialogue_counts.values()) if len(dialogue_counts) > 1 else max_count
        
        # Determine power balance
        if max_count > min_count * 2:
            dominant_char = max(dialogue_counts, key=dialogue_counts.get)
            return f"Dominated by {dominant_char}"
        else:
            return "Equal"
    
    def _identify_emotional_tone(self, description: str, dialogues: List[Dict[str, Any]]) -> str:
        """Identify the emotional tone of the scene."""
        # Analyze description for emotional keywords
        emotional_keywords = {
            'tense': ['tension', 'tense', 'uncomfortable', 'awkward'],
            'romantic': ['romantic', 'love', 'intimate', 'tender'],
            'confrontational': ['argue', 'fight', 'angry', 'yell', 'shout'],
            'friendly': ['laugh', 'smile', 'joke', 'happy', 'cheerful'],
            'dramatic': ['dramatic', 'intense', 'serious', 'grave'],
            'mysterious': ['mysterious', 'secret', 'hidden', 'whisper']
        }
        
        for tone, keywords in emotional_keywords.items():
            if any(keyword in description for keyword in keywords):
                return tone
        
        # Analyze dialogue text for emotional content
        dialogue_text = ' '.join([d.get('text', '') for d in dialogues]).lower()
        for tone, keywords in emotional_keywords.items():
            if any(keyword in dialogue_text for keyword in keywords):
                return tone
        
        return 'neutral'
    
    def _classify_dialogue_exchange(self, text1: str, text2: str) -> str:
        """Classify the type of dialogue exchange between characters."""
        text1_lower = text1.lower()
        text2_lower = text2.lower()
        
        # Question-answer pattern
        if '?' in text1 and not '?' in text2:
            return 'question_answer'
        
        # Command-response pattern
        if any(word in text1_lower for word in ['go', 'come', 'stop', 'wait', 'do']):
            return 'command_response'
        
        # Emotional exchange
        if any(word in text1_lower + text2_lower for word in ['love', 'hate', 'angry', 'sad']):
            return 'emotional'
        
        # Information exchange
        return 'information'
    
    def _summarize_scene_dynamics(self, description: str, characters: List[str]) -> str:
        """Summarize the overall dynamics of the scene."""
        if len(characters) == 1:
            return "Monologue or internal scene"
        elif len(characters) == 2:
            if any(keyword in description for keyword in ['romantic', 'love', 'intimate']):
                return "Intimate conversation"
            elif any(keyword in description for keyword in ['argue', 'fight', 'conflict']):
                return "Confrontational exchange"
            else:
                return "Two-person dialogue"
        else:
            return "Group interaction"
    
    def _track_character_arcs(self, characters: List[Dict[str, Any]], 
                            scenes: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """Track character development arcs throughout the story."""
        character_arcs = {}
        
        for char in characters:
            char_name = char.get('name', '')
            scene_numbers = char.get('scene_numbers', [])
            
            if scene_numbers:
                # Analyze character progression through scenes
                arc_analysis = self._analyze_character_progression(char_name, scenes)
                
                character_arcs[char_name] = {
                    "arc_type": arc_analysis.get('arc_type', 'Static'),
                    "growth_trajectory": arc_analysis.get('growth_trajectory', 'Neutral'),
                    "key_turning_points": arc_analysis.get('turning_points', []),
                    "emotional_journey": arc_analysis.get('emotional_journey', []),
                    "relationship_changes": arc_analysis.get('relationship_changes', [])
                }
        
        return character_arcs
    
    def _analyze_character_progression(self, character: str, scenes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze how a character progresses through the story."""
        character_scenes = []
        
        for scene in scenes:
            main_characters = scene.get('main_characters', [])
            if character in main_characters:
                character_scenes.append({
                    "scene_number": scene.get('scene_number', '0'),
                    "description": scene.get('description', ''),
                    "dialogues": [d for d in scene.get('dialogues', []) if d.get('character') == character]
                })
        
        if len(character_scenes) < 2:
            return {"arc_type": "Static", "growth_trajectory": "Neutral"}
        
        # Simple arc analysis based on scene progression
        first_scene = character_scenes[0]
        last_scene = character_scenes[-1]
        
        # Determine arc type based on scene content
        arc_types = ["Heroic Journey", "Redemption", "Fall from Grace", "Coming of Age", "Static"]
        growth_trajectories = ["Positive", "Negative", "Cyclical", "Neutral"]
        
        # Basic heuristic - this would be enhanced with more sophisticated analysis
        if len(character_scenes) > len(scenes) * 0.5:  # Main character
            arc_type = "Heroic Journey"
            growth_trajectory = "Positive"
        else:
            arc_type = "Static"
            growth_trajectory = "Neutral"
        
        return {
            "arc_type": arc_type,
            "growth_trajectory": growth_trajectory,
            "turning_points": [character_scenes[len(character_scenes)//2]["scene_number"]] if len(character_scenes) > 3 else [],
            "emotional_journey": [],
            "relationship_changes": []
        }
    
    def _analyze_power_dynamics(self, scenes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze power dynamics across all scenes."""
        power_analysis = {
            "dominant_characters": {},
            "power_shifts": [],
            "hierarchy_indicators": {}
        }
        
        character_dominance = {}
        
        for scene in scenes:
            scene_number = scene.get('scene_number', '0')
            dialogues = scene.get('dialogues', [])
            
            # Count dialogue per character
            scene_dialogue_counts = {}
            for dialogue in dialogues:
                char = dialogue.get('character', '')
                if char:
                    scene_dialogue_counts[char] = scene_dialogue_counts.get(char, 0) + 1
            
            # Track overall dominance
            if scene_dialogue_counts:
                dominant_char = max(scene_dialogue_counts, key=scene_dialogue_counts.get)
                character_dominance[dominant_char] = character_dominance.get(dominant_char, 0) + 1
        
        power_analysis["dominant_characters"] = dict(sorted(
            character_dominance.items(), key=lambda x: x[1], reverse=True))
        
        return power_analysis
    
    def _map_conflicts_and_resolutions(self, scenes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Map conflicts and their resolutions throughout the story."""
        conflict_analysis = {
            "major_conflicts": [],
            "conflict_patterns": {},
            "resolution_strategies": []
        }
        
        conflicts = []
        
        for scene in scenes:
            scene_number = scene.get('scene_number', '0')
            description = scene.get('description', '').lower()
            
            # Identify conflict indicators
            conflict_keywords = ['fight', 'argue', 'conflict', 'disagree', 'angry', 'yell']
            if any(keyword in description for keyword in conflict_keywords):
                conflicts.append({
                    "scene": scene_number,
                    "type": "interpersonal",
                    "description": description[:100]
                })
        
        conflict_analysis["major_conflicts"] = conflicts
        
        return conflict_analysis
    
    def _generate_social_hierarchy(self, relationship_network: Dict[str, List], 
                                  power_dynamics: Dict[str, Any]) -> Dict[str, Any]:
        """Generate social hierarchy analysis."""
        hierarchy = {
            "power_ranking": [],
            "social_clusters": [],
            "influence_network": {}
        }
        
        # Use power dynamics to create ranking
        dominant_chars = power_dynamics.get("dominant_characters", {})
        hierarchy["power_ranking"] = list(dominant_chars.keys())
        
        return hierarchy