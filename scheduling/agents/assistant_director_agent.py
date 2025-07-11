from typing import Dict, Any, List
import json
import logging
from datetime import datetime, timedelta
from ...base_config import AGENT_INSTRUCTIONS, get_model_config
from google import genai
from google.genai import types
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AssistantDirectorAgent:
    """
    🚧 AssistantDirectorAgent (DOOP/STRIPBOARD) - Gemini 2.5 Flash
    
    Advanced scheduling optimization agent for assistant director functions.
    Responsibilities:
    - Create stripboard with color-coded scenes
    - Generate DOOP (Day Out of Days) reports
    - Produce call sheets for cast and crew
    - Optimize shooting schedules
    - Handle cast availability and conflicts
    """
    
    def __init__(self):
        self.client = genai.Client(api_key=os.environ.get("GOOGLE_API_KEY"))
        self.model_config = get_model_config()
        self.instructions = """You are an Assistant Director Agent for film production.
        Your expertise in advanced scheduling optimization:
        1. Create detailed stripboards with color-coded scenes
        2. Generate comprehensive DOOP reports for cast scheduling
        3. Produce daily call sheets with precise timing
        4. Optimize shooting schedules for efficiency
        5. Handle cast availability and scheduling conflicts
        
        Focus on advanced scheduling optimization with StudioBinder-level precision."""
        logger.info("AssistantDirectorAgent initialized")
    
    async def generate_stripboard_doop(self, scene_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate stripboard and DOOP reports for scheduling optimization."""
        logger.info("Starting stripboard and DOOP generation")
        
        if not scene_data or not isinstance(scene_data, dict):
            logger.error("Invalid scene data received")
            return {"error": "Invalid scene data format"}
        
        scenes = scene_data.get('scenes', [])
        logger.info(f"Processing stripboard/DOOP for {len(scenes)} scenes")
        
        # Generate stripboard
        stripboard = self._generate_stripboard(scenes)
        
        # Generate DOOP reports
        doop_reports = self._generate_doop_reports(scenes)
        
        # Generate call sheets
        call_sheets = self._generate_call_sheets(scenes, doop_reports)
        
        # Schedule optimization
        optimized_schedule = self._optimize_schedule(scenes, stripboard)
        
        result = {
            "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "stripboard": stripboard,
            "doop_reports": doop_reports,
            "call_sheets": call_sheets,
            "optimized_schedule": optimized_schedule,
            "scheduling_statistics": self._generate_scheduling_stats(scenes, doop_reports)
        }
        
        logger.info(f"Generated stripboard/DOOP for {len(scenes)} scenes")
        return result
    
    def _generate_stripboard(self, scenes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate color-coded stripboard for scene organization."""
        stripboard = {
            "scenes": {},
            "color_legend": {
                "blue": "Interior Day",
                "yellow": "Exterior Day",
                "green": "Interior Night",
                "red": "Exterior Night",
                "white": "Special/Effects",
                "pink": "Flashback/Dream"
            },
            "shooting_order": [],
            "location_groups": {}
        }
        
        for scene in scenes:
            scene_number = scene.get('scene_number', '0')
            location = scene.get('location', {})
            location_type = location.get('type', 'INT')
            time_period = scene.get('time', 'DAY')
            
            # Determine color code
            color_code = self._determine_scene_color(location_type, time_period)
            
            # Calculate scene pages (estimate based on content)
            pages = self._estimate_scene_pages(scene)
            
            # Extract cast for this scene
            cast_list = scene.get('main_characters', [])
            
            # Identify special equipment
            special_equipment = self._identify_special_equipment(scene)
            
            scene_strip = {
                "color_code": color_code,
                "scene_number": scene_number,
                "location": f"{location.get('place', 'Unknown')} - {location_type}",
                "time": time_period,
                "pages": pages,
                "cast": cast_list,
                "special_equipment": special_equipment,
                "description": scene.get('description', '')[:100] + "..." if len(scene.get('description', '')) > 100 else scene.get('description', ''),
                "estimated_shoot_time": self._estimate_scene_shoot_time(scene)
            }
            
            stripboard["scenes"][scene_number] = scene_strip
            
            # Group by location for shooting order optimization
            location_key = location.get('place', 'Unknown')
            if location_key not in stripboard["location_groups"]:
                stripboard["location_groups"][location_key] = []
            stripboard["location_groups"][location_key].append(scene_number)
        
        # Generate optimized shooting order
        stripboard["shooting_order"] = self._generate_shooting_order(stripboard["location_groups"], stripboard["scenes"])
        
        return stripboard
    
    def _determine_scene_color(self, location_type: str, time_period: str) -> str:
        """Determine stripboard color based on location type and time."""
        if location_type.upper() == 'INT':
            return "blue" if 'DAY' in time_period.upper() else "green"
        else:  # EXT
            return "yellow" if 'DAY' in time_period.upper() else "red"
    
    def _estimate_scene_pages(self, scene: Dict[str, Any]) -> str:
        """Estimate scene pages based on content."""
        description_length = len(scene.get('description', ''))
        dialogue_count = len(scene.get('dialogues', []))
        
        # Rough estimation: 250 words per page
        estimated_pages = (description_length + dialogue_count * 50) / 250
        
        # Convert to fraction format
        if estimated_pages < 0.25:
            return "1/8"
        elif estimated_pages < 0.5:
            return "1/4"
        elif estimated_pages < 0.75:
            return "1/2"
        elif estimated_pages < 1.25:
            return "1"
        elif estimated_pages < 1.75:
            return "1 1/2"
        elif estimated_pages < 2.25:
            return "2"
        else:
            return f"{int(estimated_pages)} {int((estimated_pages % 1) * 8)}/8"
    
    def _identify_special_equipment(self, scene: Dict[str, Any]) -> List[str]:
        """Identify special equipment needed for scene."""
        equipment = []
        technical_cues = scene.get('technical_cues', [])
        
        for cue in technical_cues:
            cue_lower = cue.lower()
            if 'steadicam' in cue_lower:
                equipment.append("Steadicam")
            if 'crane' in cue_lower:
                equipment.append("Camera crane")
            if 'dolly' in cue_lower or 'track' in cue_lower:
                equipment.append("Dolly/Track")
            if 'drone' in cue_lower:
                equipment.append("Drone")
            if 'underwater' in cue_lower:
                equipment.append("Underwater housing")
        
        return equipment
    
    def _estimate_scene_shoot_time(self, scene: Dict[str, Any]) -> float:
        """Estimate shooting time for scene in hours."""
        base_time = 1.0  # Base hour per scene
        
        # Adjust for dialogue
        dialogue_count = len(scene.get('dialogues', []))
        dialogue_time = dialogue_count * 0.1  # 6 minutes per dialogue
        
        # Adjust for technical complexity
        technical_cues = len(scene.get('technical_cues', []))
        technical_time = technical_cues * 0.15  # 9 minutes per technical cue
        
        # Adjust for cast size
        cast_count = len(scene.get('main_characters', []))
        cast_time = max(0, cast_count - 1) * 0.2  # Additional time for multiple actors
        
        return round(base_time + dialogue_time + technical_time + cast_time, 1)
    
    def _generate_shooting_order(self, location_groups: Dict[str, List[str]], scenes: Dict[str, Any]) -> List[str]:
        """Generate optimized shooting order based on location and complexity."""
        shooting_order = []
        
        # Sort locations by number of scenes (shoot locations with more scenes first)
        sorted_locations = sorted(location_groups.items(), key=lambda x: len(x[1]), reverse=True)
        
        for location, scene_numbers in sorted_locations:
            # Sort scenes within location by complexity (simpler first)
            location_scenes = [(num, scenes[num]) for num in scene_numbers]
            location_scenes.sort(key=lambda x: len(x[1].get('special_equipment', [])))
            
            shooting_order.extend([scene[0] for scene in location_scenes])
        
        return shooting_order
    
    def _generate_doop_reports(self, scenes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate Day Out of Days reports for cast scheduling."""
        doop_reports = {}
        
        # Collect all characters
        all_characters = set()
        for scene in scenes:
            all_characters.update(scene.get('main_characters', []))
        
        # Generate DOOP for each character
        for character in all_characters:
            character_scenes = []
            work_days = []
            
            for i, scene in enumerate(scenes):
                if character in scene.get('main_characters', []):
                    character_scenes.append(scene.get('scene_number', '0'))
                    work_days.append(i + 1)  # Day number
            
            # Generate weekly layout
            weekly_layout = self._generate_weekly_layout(work_days)
            
            # Calculate character statistics
            total_work_days = len(work_days)
            start_day = min(work_days) if work_days else 0
            end_day = max(work_days) if work_days else 0
            
            doop_reports[character] = {
                "work_days": work_days,
                "scenes": character_scenes,
                "total_work_days": total_work_days,
                "start_day": start_day,
                "end_day": end_day,
                "weekly_layout": weekly_layout,
                "travel_days": self._calculate_travel_days(work_days),
                "hold_days": self._calculate_hold_days(work_days)
            }
        
        return doop_reports
    
    def _generate_weekly_layout(self, work_days: List[int]) -> Dict[str, Dict[str, str]]:
        """Generate weekly layout showing work/travel/hold days."""
        weekly_layout = {}
        
        # Assume 5-day work week (Monday-Friday)
        days_of_week = ['mon', 'tue', 'wed', 'thu', 'fri']
        
        if not work_days:
            return weekly_layout
        
        max_day = max(work_days)
        weeks = (max_day - 1) // 5 + 1
        
        for week in range(1, weeks + 1):
            week_key = f"week_{week}"
            weekly_layout[week_key] = {}
            
            for day_index, day_name in enumerate(days_of_week):
                day_number = (week - 1) * 5 + day_index + 1
                
                if day_number in work_days:
                    weekly_layout[week_key][day_name] = "Work"
                elif day_number < min(work_days):
                    weekly_layout[week_key][day_name] = "Pre-call"
                elif day_number > max(work_days):
                    weekly_layout[week_key][day_name] = "Wrapped"
                else:
                    # Check if it's a travel day or hold day
                    if self._is_travel_day(day_number, work_days):
                        weekly_layout[week_key][day_name] = "Travel"
                    else:
                        weekly_layout[week_key][day_name] = "Hold"
        
        return weekly_layout
    
    def _calculate_travel_days(self, work_days: List[int]) -> List[int]:
        """Calculate travel days between work periods."""
        if len(work_days) < 2:
            return []
        
        travel_days = []
        work_days_sorted = sorted(work_days)
        
        for i in range(1, len(work_days_sorted)):
            gap = work_days_sorted[i] - work_days_sorted[i-1]
            if gap > 1:
                # Add travel days in gaps
                travel_days.extend(range(work_days_sorted[i-1] + 1, work_days_sorted[i]))
        
        return travel_days
    
    def _calculate_hold_days(self, work_days: List[int]) -> List[int]:
        """Calculate hold days when actor is on call but not working."""
        if len(work_days) < 2:
            return []
        
        hold_days = []
        work_days_sorted = sorted(work_days)
        
        # Hold days are typically 1-2 days between work days
        for i in range(1, len(work_days_sorted)):
            gap = work_days_sorted[i] - work_days_sorted[i-1]
            if gap == 2:  # One day gap = hold day
                hold_days.append(work_days_sorted[i-1] + 1)
        
        return hold_days
    
    def _is_travel_day(self, day_number: int, work_days: List[int]) -> bool:
        """Determine if a day is a travel day."""
        work_days_sorted = sorted(work_days)
        
        for i in range(1, len(work_days_sorted)):
            gap_start = work_days_sorted[i-1] + 1
            gap_end = work_days_sorted[i] - 1
            
            if gap_start <= day_number <= gap_end:
                # First and last days of gaps are typically travel days
                return day_number == gap_start or day_number == gap_end
        
        return False
    
    def _generate_call_sheets(self, scenes: List[Dict[str, Any]], doop_reports: Dict[str, Any]) -> Dict[str, Any]:
        """Generate call sheets for each shooting day."""
        call_sheets = {}
        
        for day_index, scene in enumerate(scenes):
            day_number = day_index + 1
            scene_number = scene.get('scene_number', '0')
            
            # Base call sheet information
            call_sheet = {
                "day": day_number,
                "date": (datetime(2024, 3, 15) + timedelta(days=day_index)).strftime('%B %d, %Y'),
                "scenes": [scene_number],
                "location": scene.get('location', {}).get('place', 'Unknown'),
                "cast_call_times": {},
                "crew_call_times": {},
                "equipment_list": [],
                "special_notes": []
            }
            
            # Generate cast call times
            cast_members = scene.get('main_characters', [])
            base_call_time = "07:00"  # 7:00 AM base call
            
            for cast_member in cast_members:
                # Stagger call times based on scene requirements
                dialogue_count = len([d for d in scene.get('dialogues', []) if d.get('character') == cast_member])
                
                if dialogue_count > 5:  # Lead characters arrive earlier
                    call_sheet["cast_call_times"][cast_member] = base_call_time
                else:
                    call_sheet["cast_call_times"][cast_member] = "07:30"
            
            # Generate crew call times
            crew_call_times = {
                "Director": "06:30",
                "DP": "06:30",
                "1st AD": "06:00",
                "Gaffer": "06:00",
                "Key Grip": "06:00",
                "Sound Mixer": "07:00",
                "Script Supervisor": "07:00"
            }
            
            call_sheet["crew_call_times"] = crew_call_times
            
            # Equipment list
            call_sheet["equipment_list"] = self._identify_special_equipment(scene)
            
            # Special notes
            technical_cues = scene.get('technical_cues', [])
            if technical_cues:
                call_sheet["special_notes"].append(f"Technical requirements: {', '.join(technical_cues[:3])}")
            
            location_type = scene.get('location', {}).get('type', 'INT')
            if location_type == 'EXT':
                call_sheet["special_notes"].append("Weather dependent - check forecast")
            
            call_sheets[f"day_{day_number}"] = call_sheet
        
        return call_sheets
    
    def _optimize_schedule(self, scenes: List[Dict[str, Any]], stripboard: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize shooting schedule for efficiency."""
        optimization = {
            "current_schedule_days": len(scenes),
            "optimized_schedule_days": 0,
            "location_efficiency": {},
            "cast_efficiency": {},
            "recommendations": []
        }
        
        # Location-based optimization
        location_groups = stripboard.get("location_groups", {})
        total_location_days = sum(len(scenes) for scenes in location_groups.values())
        
        # Calculate optimized days (group by location)
        optimized_days = 0
        for location, location_scenes in location_groups.items():
            # Assume 3-4 scenes per day maximum
            days_needed = (len(location_scenes) + 2) // 3  # Ceiling division
            optimized_days += days_needed
            
            optimization["location_efficiency"][location] = {
                "scenes": len(location_scenes),
                "current_days": len(location_scenes),
                "optimized_days": days_needed,
                "efficiency_gain": len(location_scenes) - days_needed
            }
        
        optimization["optimized_schedule_days"] = optimized_days
        
        # Generate recommendations
        if optimized_days < len(scenes):
            optimization["recommendations"].append(
                f"Group scenes by location to reduce shooting days from {len(scenes)} to {optimized_days}"
            )
        
        # Cast efficiency recommendations
        cast_conflicts = self._identify_cast_conflicts(scenes)
        if cast_conflicts:
            optimization["recommendations"].append(
                f"Resolve {len(cast_conflicts)} cast scheduling conflicts"
            )
        
        return optimization
    
    def _identify_cast_conflicts(self, scenes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify potential cast scheduling conflicts."""
        conflicts = []
        
        # This is a simplified conflict detection
        # In a real system, this would check actor availability, union rules, etc.
        
        return conflicts
    
    def _generate_scheduling_stats(self, scenes: List[Dict[str, Any]], doop_reports: Dict[str, Any]) -> Dict[str, Any]:
        """Generate overall scheduling statistics."""
        stats = {
            "total_scenes": len(scenes),
            "total_cast_members": len(doop_reports),
            "average_work_days_per_actor": 0,
            "location_count": 0,
            "estimated_total_shoot_days": 0,
            "complexity_distribution": {
                "high": 0,
                "medium": 0,
                "standard": 0
            }
        }
        
        # Calculate average work days per actor
        if doop_reports:
            total_work_days = sum(report["total_work_days"] for report in doop_reports.values())
            stats["average_work_days_per_actor"] = round(total_work_days / len(doop_reports), 1)
        
        # Location count
        locations = set()
        for scene in scenes:
            locations.add(scene.get('location', {}).get('place', 'Unknown'))
        stats["location_count"] = len(locations)
        
        # Complexity distribution
        for scene in scenes:
            complexity_score = len(scene.get('technical_cues', []))
            if complexity_score >= 5:
                stats["complexity_distribution"]["high"] += 1
            elif complexity_score >= 2:
                stats["complexity_distribution"]["medium"] += 1
            else:
                stats["complexity_distribution"]["standard"] += 1
        
        # Estimated total shoot days (scenes grouped by location)
        stats["estimated_total_shoot_days"] = (len(scenes) + 2) // 3  # Rough estimate
        
        return stats