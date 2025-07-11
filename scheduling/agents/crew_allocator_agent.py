from typing import Dict, Any, List
import json
import logging
from datetime import datetime, timedelta
from base_config import AGENT_INSTRUCTIONS, get_model_config
from google import genai
from google.genai import types
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CrewAllocatorAgent:
    """
    🚧 CrewAllocatorAgent (DEPARTMENT SCHEDULING) - GPT-4.1 mini
    
    Advanced department scheduling coordination agent.
    Responsibilities:
    - Coordinate department-specific scheduling (Camera, Sound, Lighting, Grip)
    - Manage crew availability and work hour restrictions
    - Optimize crew assignments across departments
    - Handle union rules and labor compliance
    - Generate detailed crew call sheets
    """
    
    def __init__(self):
        self.client = genai.Client(api_key=os.environ.get("GOOGLE_API_KEY"))
        self.model_config = get_model_config()
        self.instructions = """You are a Crew Allocator Agent for film production.
        Your expertise in advanced department scheduling coordination:
        1. Coordinate department-specific scheduling across Camera, Sound, Lighting, Grip
        2. Manage crew availability windows and work hour restrictions
        3. Optimize crew assignments for maximum efficiency
        4. Ensure union rules and labor compliance
        5. Generate detailed crew call sheets and schedules
        
        Focus on advanced department scheduling coordination with union compliance."""
        logger.info("CrewAllocatorAgent initialized")
    
    async def allocate_departments(self, scene_data: Dict[str, Any], crew_availability: Dict[str, Any] = None) -> Dict[str, Any]:
        """Allocate crew across departments with union compliance."""
        logger.info("Starting department crew allocation")
        
        if not scene_data or not isinstance(scene_data, dict):
            logger.error("Invalid scene data received")
            return {"error": "Invalid scene data format"}
        
        scenes = scene_data.get('scenes', [])
        logger.info(f"Processing crew allocation for {len(scenes)} scenes")
        
        # Generate department schedules
        department_schedules = self._generate_department_schedules(scenes)
        
        # Create crew assignments
        crew_assignments = self._create_crew_assignments(scenes, department_schedules)
        
        # Generate work hour compliance
        work_hour_compliance = self._generate_work_hour_compliance(crew_assignments)
        
        # Create call sheet details
        call_sheet_details = self._create_call_sheet_details(scenes, crew_assignments)
        
        # Calculate department efficiency
        department_efficiency = self._calculate_department_efficiency(department_schedules, crew_assignments)
        
        result = {
            "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "department_schedules": department_schedules,
            "crew_assignments": crew_assignments,
            "work_hour_compliance": work_hour_compliance,
            "call_sheet_details": call_sheet_details,
            "department_efficiency": department_efficiency,
            "union_compliance_notes": self._generate_union_compliance_notes(crew_assignments)
        }
        
        logger.info(f"Generated department allocation for {len(scenes)} scenes")
        return result
    
    def _generate_department_schedules(self, scenes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate department-specific schedules."""
        departments = {
            "camera": {
                "crew_requirements": {},
                "equipment_schedule": {},
                "scene_coverage": [],
                "daily_assignments": []
            },
            "sound": {
                "crew_requirements": {},
                "equipment_schedule": {},
                "scene_coverage": [],
                "daily_assignments": []
            },
            "lighting": {
                "crew_requirements": {},
                "equipment_schedule": {},
                "scene_coverage": [],
                "daily_assignments": []
            },
            "grip": {
                "crew_requirements": {},
                "equipment_schedule": {},
                "scene_coverage": [],
                "daily_assignments": []
            }
        }
        
        for day_index, scene in enumerate(scenes):
            scene_number = scene.get('scene_number', '0')
            
            # Camera department requirements
            camera_complexity = self._assess_camera_complexity(scene)
            departments["camera"]["scene_coverage"].append({
                "scene": scene_number,
                "day": day_index + 1,
                "complexity": camera_complexity,
                "crew_needed": self._calculate_camera_crew_needed(camera_complexity)
            })
            
            # Sound department requirements
            sound_complexity = self._assess_sound_complexity(scene)
            departments["sound"]["scene_coverage"].append({
                "scene": scene_number,
                "day": day_index + 1,
                "complexity": sound_complexity,
                "crew_needed": self._calculate_sound_crew_needed(sound_complexity)
            })
            
            # Lighting department requirements
            lighting_complexity = self._assess_lighting_complexity(scene)
            departments["lighting"]["scene_coverage"].append({
                "scene": scene_number,
                "day": day_index + 1,
                "complexity": lighting_complexity,
                "crew_needed": self._calculate_lighting_crew_needed(lighting_complexity)
            })
            
            # Grip department requirements
            grip_complexity = self._assess_grip_complexity(scene)
            departments["grip"]["scene_coverage"].append({
                "scene": scene_number,
                "day": day_index + 1,
                "complexity": grip_complexity,
                "crew_needed": self._calculate_grip_crew_needed(grip_complexity)
            })
        
        return departments
    
    def _clean_and_extract_json(self, text: str) -> str:
        """Clean and extract JSON from text response."""
        # First, try to find JSON between triple backticks
        matches = re.findall(r'```(?:json)?\s*({\s*.*?\s*})\s*```', text, re.DOTALL)
        if matches:
            return matches[0]
        
        # Then try to find JSON between single backticks
        matches = re.findall(r'`({\s*.*?\s*})`', text, re.DOTALL)
        if matches:
            return matches[0]
        
        # Then try to find any JSON object
        matches = re.findall(r'({\s*"[^"]+"\s*:[\s\S]*})', text)
        if matches:
            return matches[0]
        
        # Try to find anything that looks like JSON
        matches = re.findall(r'({[\s\S]*})', text)
        if matches:
            return matches[0]
        
        # If we can't find JSON, return the original text
        return text.strip()
    
    def _generate_fallback_allocation(self, scenes: List[Dict[str, Any]], crew_availability: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a basic valid crew allocation when the API response fails."""
        logger.info("Generating fallback crew allocation")
        
        # Extract available crew members
        crew_members = []
        if isinstance(crew_availability, dict):
            crew_members = crew_availability.get('crew', [])
            if not crew_members and 'character_breakdown' in crew_availability:
                crew_members = crew_availability['character_breakdown'].get('crew', [])
        
        if not crew_members:
            # Create basic crew structure
            crew_members = [
                {"name": "Director", "role": "Director"},
                {"name": "DP", "role": "Director of Photography"},
                {"name": "Sound Mixer", "role": "Sound"},
                {"name": "Gaffer", "role": "Lighting"},
                {"name": "Key Grip", "role": "Grip"}
            ]
        
        # Create basic allocation
        crew_assignments = []
        for crew in crew_members:
            crew_name = crew.get('name', crew) if isinstance(crew, dict) else crew
            crew_role = crew.get('role', 'Crew') if isinstance(crew, dict) else 'Crew'
            
            crew_assignments.append({
                "crew_member": crew_name,
                "role": crew_role,
                "assigned_scenes": [scene.get('id', 'unknown') for scene in scenes],
                "work_hours": 12,
                "turnaround_hours": 12,
                "meal_break_interval": 6,
                "equipment_assigned": []
            })
        
        return {
            "crew_assignments": crew_assignments,
            "equipment_assignments": [],
            "department_schedules": {
                "camera": {"crew": [], "equipment": [], "notes": ["Fallback schedule"]},
                "sound": {"crew": [], "equipment": [], "notes": ["Fallback schedule"]},
                "lighting": {"crew": [], "equipment": [], "notes": ["Fallback schedule"]}
            },
            "allocation_notes": ["Generated fallback allocation due to API parsing error"],
            "is_fallback": True
        }
    
    def _validate_crew_assignments(self, allocation: Dict[str, Any]) -> None:
        """Validate crew assignments against common union rules."""
        try:
            logger.info("Starting crew assignment validation")
            violations = []
            
            if "crew_assignments" not in allocation:
                logger.warning("No crew assignments found in allocation data")
                return
            
            for assignment in allocation["crew_assignments"]:
                crew_member = assignment.get('crew_member', 'Unknown crew member')
                
                # Check for minimum turnaround time (typically 10 hours)
                if assignment.get("turnaround_hours", 10) < 10:
                    msg = f"Insufficient turnaround time for {crew_member}"
                    logger.warning(msg)
                    violations.append(msg)
                
                # Check for maximum work hours (typically 12 hours)
                if assignment.get("work_hours", 0) > 12:
                    msg = f"Excessive work hours for {crew_member}"
                    logger.warning(msg)
                    violations.append(msg)
                
                # Check for meal breaks (every 6 hours)
                if assignment.get("meal_break_interval", 6) > 6:
                    msg = f"Missing meal break for {crew_member}"
                    logger.warning(msg)
                    violations.append(msg)
            
            if violations:
                logger.warning(f"Found {len(violations)} union rule violations")
                allocation["union_rule_violations"] = violations 
            else:
                logger.info("No union rule violations found")
        except Exception as e:
            logger.error(f"Error during crew assignment validation: {str(e)}", exc_info=True)
            raise 