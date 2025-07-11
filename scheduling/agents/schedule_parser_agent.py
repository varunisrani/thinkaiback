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

class ScheduleParserAgent:
    """
    ✅ ScheduleParserAgent (FOUNDATIONAL) - GPT-4.1 mini
    
    Specialized foundational agent for schedule parsing and element extraction.
    Responsibilities:
    - Parse scheduling elements from scene data
    - Extract cast requirements and roles
    - Identify location counts and complexity
    - Generate basic schedule structure
    - Create crew allocation foundations
    """
    
    def __init__(self):
        self.client = genai.Client(api_key=os.environ.get("GOOGLE_API_KEY"))
        self.model_config = get_model_config()
        self.instructions = """You are a Schedule Parser Agent for film production.
        Your expertise in structured data extraction:
        1. Extract scheduling elements (scenes, locations, cast)
        2. Identify cast requirements (principals, day players)
        3. Calculate location counts and complexity
        4. Generate basic schedule structure
        5. Create foundational crew allocation data
        
        Focus on excellent structured data extraction with precision."""
        logger.info("ScheduleParserAgent initialized")
    
    async def parse_schedule_elements(self, scene_data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse fundamental scheduling elements from scene data."""
        logger.info("Starting schedule parsing analysis")
        
        if not scene_data or not isinstance(scene_data, dict):
            logger.error("Invalid scene data received")
            return {"error": "Invalid scene data format"}
        
        scenes = scene_data.get('scenes', [])
        logger.info(f"Processing schedule parsing for {len(scenes)} scenes")
        
        # Extract scheduling elements
        scheduling_elements = self._extract_scheduling_elements(scenes)
        basic_schedule = self._generate_basic_schedule(scenes)
        crew_allocation = self._generate_basic_crew_allocation(scenes)
        
        result = {
            "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "scheduling_elements": scheduling_elements,
            "basic_schedule": basic_schedule,
            "crew_allocation": crew_allocation,
            "scene_count": len(scenes),
            "processing_status": "completed"
        }
        
        logger.info(f"Generated schedule parsing for {len(scenes)} scenes")
        return result
    
    def _extract_scheduling_elements(self, scenes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract core scheduling elements from scenes."""
        elements = {
            "total_scenes": len(scenes),
            "location_count": 0,
            "cast_requirements": {
                "principals": set(),
                "day_players": set(),
                "extras": set()
            },
            "location_breakdown": {},
            "time_periods": set(),
            "scene_complexity": {}
        }
        
        locations = set()
        
        for scene in scenes:
            scene_number = scene.get('scene_number', '0')
            
            # Location extraction
            location = scene.get('location', {})
            location_place = location.get('place', 'Unknown')
            location_type = location.get('type', 'INT')
            
            if location_place != 'Unknown':
                locations.add(location_place)
                
                if location_place not in elements["location_breakdown"]:
                    elements["location_breakdown"][location_place] = {
                        "type": location_type,
                        "scenes": [],
                        "estimated_shoot_days": 0
                    }
                
                elements["location_breakdown"][location_place]["scenes"].append(scene_number)
        
        elements["location_count"] = len(locations)
        
        # Calculate estimated shoot days for each location
        for location_name, location_data in elements["location_breakdown"].items():
            scene_count = len(location_data["scenes"])
            # Basic estimation: 1 day per 3-4 scenes, minimum 1 day
            elements["location_breakdown"][location_name]["estimated_shoot_days"] = max(1, round(scene_count / 3.5))
        
        # Cast requirements extraction
        for scene in scenes:
            characters = scene.get('main_characters', [])
            
            for character in characters:
                # Basic classification - this could be enhanced with character importance analysis
                dialogue_count = len([d for d in scene.get('dialogues', []) if d.get('character') == character])
                
                if dialogue_count > 5:  # Principal characters have significant dialogue
                    elements["cast_requirements"]["principals"].add(character)
                elif dialogue_count > 0:
                    elements["cast_requirements"]["day_players"].add(character)
                else:
                    elements["cast_requirements"]["extras"].add(character)
            
            # Time period extraction
            time_period = scene.get('time', 'DAY')
            elements["time_periods"].add(time_period)
            
            # Scene complexity assessment
            complexity_score = self._calculate_scene_complexity(scene)
            elements["scene_complexity"][scene.get('scene_number', '0')] = complexity_score
        
        # Convert sets to lists and counts for JSON serialization
        elements["cast_requirements"] = {
            "principals": len(elements["cast_requirements"]["principals"]),
            "day_players": len(elements["cast_requirements"]["day_players"]),
            "extras": len(elements["cast_requirements"]["extras"])
        }
        
        elements["time_periods"] = list(elements["time_periods"])
        
        return elements
    
    def _calculate_scene_complexity(self, scene: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate scene complexity for scheduling purposes."""
        complexity = {
            "score": 0,
            "factors": [],
            "category": "Standard"
        }
        
        # Dialogue complexity
        dialogue_count = len(scene.get('dialogues', []))
        if dialogue_count > 10:
            complexity["score"] += 3
            complexity["factors"].append("Heavy dialogue")
        elif dialogue_count > 5:
            complexity["score"] += 2
            complexity["factors"].append("Moderate dialogue")
        
        # Character count
        character_count = len(scene.get('main_characters', []))
        if character_count > 4:
            complexity["score"] += 3
            complexity["factors"].append("Multiple characters")
        elif character_count > 2:
            complexity["score"] += 1
            complexity["factors"].append("Several characters")
        
        # Technical requirements
        technical_cues = scene.get('technical_cues', [])
        if len(technical_cues) > 5:
            complexity["score"] += 3
            complexity["factors"].append("Complex technical requirements")
        elif len(technical_cues) > 2:
            complexity["score"] += 2
            complexity["factors"].append("Technical requirements")
        
        # Location type
        location_type = scene.get('location', {}).get('type', 'INT')
        if location_type == 'EXT':
            complexity["score"] += 1
            complexity["factors"].append("Exterior location")
        
        # Categorize complexity
        if complexity["score"] >= 7:
            complexity["category"] = "High"
        elif complexity["score"] >= 4:
            complexity["category"] = "Medium"
        else:
            complexity["category"] = "Standard"
        
        return complexity
    
    def _generate_basic_schedule(self, scenes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate basic schedule structure."""
        schedule = []
        current_date = datetime(2024, 3, 15)  # Base date
        
        # Group scenes by location for efficient scheduling
        location_groups = {}
        for scene in scenes:
            location = scene.get('location', {}).get('place', 'Unknown')
            if location not in location_groups:
                location_groups[location] = []
            location_groups[location].append(scene)
        
        day_counter = 1
        for location, location_scenes in location_groups.items():
            # Sort scenes by complexity (simpler first)
            sorted_scenes = sorted(location_scenes, 
                                 key=lambda s: self._calculate_scene_complexity(s)["score"])
            
            # Group scenes into shooting days (max 4 scenes per day)
            scenes_per_day = 4
            for i in range(0, len(sorted_scenes), scenes_per_day):
                day_scenes = sorted_scenes[i:i+scenes_per_day]
                
                schedule_day = {
                    "day": day_counter,
                    "date": current_date.strftime('%Y-%m-%d'),
                    "location": location,
                    "scenes": [s.get('scene_number', '0') for s in day_scenes],
                    "estimated_hours": self._estimate_shooting_hours(day_scenes),
                    "complexity_level": self._calculate_day_complexity(day_scenes)
                }
                
                schedule.append(schedule_day)
                
                # Advance date and day counter
                current_date = current_date.replace(day=current_date.day + 1)
                day_counter += 1
        
        return schedule
    
    def _estimate_shooting_hours(self, scenes: List[Dict[str, Any]]) -> float:
        """Estimate shooting hours for a day's scenes."""
        total_hours = 0
        
        for scene in scenes:
            # Base time per scene
            base_time = 1.5  # hours
            
            # Adjust for dialogue
            dialogue_count = len(scene.get('dialogues', []))
            dialogue_time = dialogue_count * 0.1  # 6 minutes per dialogue
            
            # Adjust for technical complexity
            technical_cues = len(scene.get('technical_cues', []))
            technical_time = technical_cues * 0.15  # 9 minutes per technical cue
            
            # Adjust for character count
            character_count = len(scene.get('main_characters', []))
            character_time = max(0, character_count - 1) * 0.2  # Additional time for multiple characters
            
            scene_time = base_time + dialogue_time + technical_time + character_time
            total_hours += scene_time
        
        # Add setup/breakdown time
        setup_time = 1.0  # 1 hour setup
        breakdown_time = 0.5  # 30 minutes breakdown
        
        return round(total_hours + setup_time + breakdown_time, 1)
    
    def _calculate_day_complexity(self, scenes: List[Dict[str, Any]]) -> str:
        """Calculate overall complexity for a shooting day."""
        total_complexity = sum(self._calculate_scene_complexity(scene)["score"] for scene in scenes)
        avg_complexity = total_complexity / len(scenes) if scenes else 0
        
        if avg_complexity >= 5:
            return "High"
        elif avg_complexity >= 3:
            return "Medium"
        else:
            return "Standard"
    
    def _generate_basic_crew_allocation(self, scenes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate basic crew allocation requirements."""
        crew_allocation = {
            "core_crew": {
                "director": "All shooting days",
                "dp": "All shooting days",
                "1st_ad": "All shooting days",
                "script_supervisor": "All shooting days"
            },
            "departmental_crew": {
                "camera_department": {
                    "camera_operator": "All shooting days",
                    "focus_puller": "All shooting days",
                    "additional_operators": 0
                },
                "sound_department": {
                    "sound_mixer": "All shooting days",
                    "boom_operator": "All shooting days"
                },
                "lighting_department": {
                    "gaffer": "All shooting days",
                    "electricians": 2
                },
                "grip_department": {
                    "key_grip": "All shooting days",
                    "grips": 2
                }
            },
            "specialized_crew": {},
            "crew_size_by_day": []
        }
        
        # Calculate specialized crew needs
        steadicam_days = []
        crane_days = []
        
        for scene in scenes:
            technical_cues = scene.get('technical_cues', [])
            scene_number = scene.get('scene_number', '0')
            
            for cue in technical_cues:
                cue_lower = cue.lower()
                if 'steadicam' in cue_lower:
                    steadicam_days.append(scene_number)
                if 'crane' in cue_lower:
                    crane_days.append(scene_number)
        
        if steadicam_days:
            crew_allocation["specialized_crew"]["steadicam_operator"] = {
                "required_scenes": steadicam_days,
                "estimated_days": len(set(steadicam_days))
            }
        
        if crane_days:
            crew_allocation["specialized_crew"]["crane_operator"] = {
                "required_scenes": crane_days,
                "estimated_days": len(set(crane_days))
            }
        
        # Estimate crew size per day based on scene complexity
        for i, scene in enumerate(scenes):
            complexity = self._calculate_scene_complexity(scene)["score"]
            
            base_crew_size = 15  # Core crew
            additional_crew = min(complexity, 5)  # Add crew based on complexity
            
            crew_allocation["crew_size_by_day"].append({
                "day": i + 1,
                "scene": scene.get('scene_number', '0'),
                "crew_size": base_crew_size + additional_crew,
                "complexity_factor": complexity
            })
        
        return crew_allocation