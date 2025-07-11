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

class ProductionCalendarAgent:
    """
    🚧 ProductionCalendarAgent (TIMELINE MANAGEMENT) - Gemini 2.5 Flash
    
    Advanced timeline management and calendar coordination agent.
    Responsibilities:
    - Create comprehensive production calendars
    - Manage pre-production, production, and post-production phases
    - Coordinate deliverable deadlines and milestones
    - Handle seasonal and weather-dependent scheduling
    - Generate timeline visualizations and reports
    """
    
    def __init__(self):
        self.client = genai.Client(api_key=os.environ.get("GOOGLE_API_KEY"))
        self.model_config = get_model_config()
        self.instructions = """You are a Production Calendar Agent for film production.
        Your expertise in advanced timeline management:
        1. Create comprehensive production calendars with all phases
        2. Manage deliverable deadlines and milestone tracking
        3. Coordinate seasonal and weather-dependent scheduling
        4. Handle resource allocation across timeline phases
        5. Generate timeline visualizations and progress reports
        
        Focus on advanced timeline management with comprehensive milestone tracking."""
        logger.info("ProductionCalendarAgent initialized")
    
    async def generate_production_calendar(self, scene_data: Dict[str, Any], project_parameters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate comprehensive production calendar with timeline management."""
        logger.info("Starting production calendar generation")
        
        if not scene_data or not isinstance(scene_data, dict):
            logger.error("Invalid scene data received")
            return {"error": "Invalid scene data format"}
        
        scenes = scene_data.get('scenes', [])
        logger.info(f"Processing production calendar for {len(scenes)} scenes")
        
        # Generate pre-production timeline
        pre_production = self._generate_pre_production_timeline(scenes, project_parameters)
        
        # Generate production timeline
        production_timeline = self._generate_production_timeline(scenes)
        
        # Generate post-production timeline
        post_production = self._generate_post_production_timeline(scenes, project_parameters)
        
        # Create deliverable schedule
        deliverable_schedule = self._create_deliverable_schedule(project_parameters)
        
        # Generate milestone tracking
        milestone_tracking = self._generate_milestone_tracking(pre_production, production_timeline, post_production)
        
        # Weather and seasonal considerations
        seasonal_planning = self._generate_seasonal_planning(scenes, production_timeline)
        
        result = {
            "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "pre_production": pre_production,
            "production_timeline": production_timeline,
            "post_production": post_production,
            "deliverable_schedule": deliverable_schedule,
            "milestone_tracking": milestone_tracking,
            "seasonal_planning": seasonal_planning,
            "calendar_summary": self._generate_calendar_summary(pre_production, production_timeline, post_production)
        }
        
        logger.info(f"Generated production calendar for {len(scenes)} scenes")
        return result
    
    def _generate_pre_production_timeline(self, scenes: List[Dict[str, Any]], project_parameters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate pre-production timeline with all necessary phases."""
        pre_production = {
            "phase_duration": "12 weeks",
            "key_phases": {},
            "departmental_prep": {},
            "casting_schedule": {},
            "location_preparation": {}
        }
        
        # Base start date (12 weeks before production)
        production_start = datetime(2024, 3, 15)
        prep_start = production_start - timedelta(weeks=12)
        
        # Key phases
        pre_production["key_phases"] = {
            "script_development": {
                "start_date": (prep_start).strftime('%Y-%m-%d'),
                "end_date": (prep_start + timedelta(weeks=2)).strftime('%Y-%m-%d'),
                "duration": "2 weeks",
                "deliverables": ["Final script", "Script breakdown", "Scene analysis"]
            },
            "pre_visualization": {
                "start_date": (prep_start + timedelta(weeks=2)).strftime('%Y-%m-%d'),
                "end_date": (prep_start + timedelta(weeks=4)).strftime('%Y-%m-%d'),
                "duration": "2 weeks",
                "deliverables": ["Storyboards", "Shot lists", "Technical previsualization"]
            },
            "casting": {
                "start_date": (prep_start + timedelta(weeks=1)).strftime('%Y-%m-%d'),
                "end_date": (prep_start + timedelta(weeks=6)).strftime('%Y-%m-%d'),
                "duration": "5 weeks",
                "deliverables": ["Cast finalization", "Wardrobe fittings", "Rehearsals"]
            },
            "location_scouting": {
                "start_date": (prep_start + timedelta(weeks=3)).strftime('%Y-%m-%d'),
                "end_date": (prep_start + timedelta(weeks=8)).strftime('%Y-%m-%d'),
                "duration": "5 weeks",
                "deliverables": ["Location agreements", "Permits", "Tech scouts"]
            },
            "technical_preparation": {
                "start_date": (prep_start + timedelta(weeks=6)).strftime('%Y-%m-%d'),
                "end_date": (prep_start + timedelta(weeks=11)).strftime('%Y-%m-%d'),
                "duration": "5 weeks",
                "deliverables": ["Equipment booking", "Crew contracts", "Call sheets"]
            },
            "final_preparation": {
                "start_date": (prep_start + timedelta(weeks=11)).strftime('%Y-%m-%d'),
                "end_date": production_start.strftime('%Y-%m-%d'),
                "duration": "1 week",
                "deliverables": ["Final rehearsals", "Equipment check", "Production meeting"]
            }
        }
        
        # Departmental preparation
        pre_production["departmental_prep"] = {
            "camera_department": {
                "equipment_tests": (prep_start + timedelta(weeks=8)).strftime('%Y-%m-%d'),
                "lens_tests": (prep_start + timedelta(weeks=9)).strftime('%Y-%m-%d'),
                "camera_prep": (prep_start + timedelta(weeks=11)).strftime('%Y-%m-%d')
            },
            "sound_department": {
                "location_acoustics": (prep_start + timedelta(weeks=7)).strftime('%Y-%m-%d'),
                "equipment_prep": (prep_start + timedelta(weeks=10)).strftime('%Y-%m-%d'),
                "sound_design_prep": (prep_start + timedelta(weeks=6)).strftime('%Y-%m-%d')
            },
            "production_design": {
                "concept_development": (prep_start + timedelta(weeks=2)).strftime('%Y-%m-%d'),
                "set_construction": (prep_start + timedelta(weeks=5)).strftime('%Y-%m-%d'),
                "prop_acquisition": (prep_start + timedelta(weeks=8)).strftime('%Y-%m-%d')
            }
        }
        
        # Casting schedule
        unique_characters = set()
        for scene in scenes:
            unique_characters.update(scene.get('main_characters', []))
        
        pre_production["casting_schedule"] = {
            "principal_casting": {
                "auditions": (prep_start + timedelta(weeks=1)).strftime('%Y-%m-%d'),
                "callbacks": (prep_start + timedelta(weeks=3)).strftime('%Y-%m-%d'),
                "final_selections": (prep_start + timedelta(weeks=4)).strftime('%Y-%m-%d'),
                "characters_count": len(unique_characters)
            },
            "supporting_casting": {
                "auditions": (prep_start + timedelta(weeks=4)).strftime('%Y-%m-%d'),
                "selections": (prep_start + timedelta(weeks=5)).strftime('%Y-%m-%d')
            },
            "wardrobe_fittings": {
                "principals": (prep_start + timedelta(weeks=6)).strftime('%Y-%m-%d'),
                "supporting": (prep_start + timedelta(weeks=7)).strftime('%Y-%m-%d')
            }
        }
        
        # Location preparation
        unique_locations = set()
        for scene in scenes:
            location = scene.get('location', {})
            if location.get('place'):
                unique_locations.add(location['place'])
        
        pre_production["location_preparation"] = {
            "location_count": len(unique_locations),
            "scouting_phase": {
                "initial_scout": (prep_start + timedelta(weeks=3)).strftime('%Y-%m-%d'),
                "technical_scout": (prep_start + timedelta(weeks=7)).strftime('%Y-%m-%d'),
                "final_scout": (prep_start + timedelta(weeks=10)).strftime('%Y-%m-%d')
            },
            "permits_and_agreements": {
                "permit_applications": (prep_start + timedelta(weeks=6)).strftime('%Y-%m-%d'),
                "location_agreements": (prep_start + timedelta(weeks=8)).strftime('%Y-%m-%d'),
                "insurance_finalization": (prep_start + timedelta(weeks=9)).strftime('%Y-%m-%d')
            }
        }
        
        return pre_production
    
    def _generate_production_timeline(self, scenes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate detailed production phase timeline."""
        production_start = datetime(2024, 3, 15)
        
        # Group scenes by location for scheduling efficiency
        location_groups = {}
        for scene in scenes:
            location = scene.get('location', {}).get('place', 'Unknown')
            if location not in location_groups:
                location_groups[location] = []
            location_groups[location].append(scene)
        
        # Calculate estimated shooting days
        total_shooting_days = 0
        location_schedule = {}
        
        current_date = production_start
        for location, location_scenes in location_groups.items():
            days_needed = max(1, len(location_scenes) // 3 + (1 if len(location_scenes) % 3 else 0))
            total_shooting_days += days_needed
            
            location_schedule[location] = {
                "start_date": current_date.strftime('%Y-%m-%d'),
                "end_date": (current_date + timedelta(days=days_needed - 1)).strftime('%Y-%m-%d'),
                "shooting_days": days_needed,
                "scene_count": len(location_scenes),
                "scenes": [s.get('scene_number', '0') for s in location_scenes]
            }
            
            current_date += timedelta(days=days_needed)
        
        production_end = production_start + timedelta(days=total_shooting_days - 1)
        
        timeline = {
            "start_date": production_start.strftime('%Y-%m-%d'),
            "end_date": production_end.strftime('%Y-%m-%d'),
            "total_shooting_days": total_shooting_days,
            "location_schedule": location_schedule,
            "weekly_breakdown": self._generate_weekly_breakdown(production_start, total_shooting_days),
            "contingency_days": max(2, total_shooting_days // 10),  # 10% contingency
            "weather_days": self._calculate_weather_days(scenes)
        }
        
        return timeline
    
    def _generate_weekly_breakdown(self, start_date: datetime, total_days: int) -> Dict[str, Any]:
        """Generate weekly breakdown of production schedule."""
        weeks = {}
        current_date = start_date
        week_number = 1
        
        while (current_date - start_date).days < total_days:
            week_start = current_date
            week_end = min(current_date + timedelta(days=4), start_date + timedelta(days=total_days - 1))
            
            weeks[f"week_{week_number}"] = {
                "start_date": week_start.strftime('%Y-%m-%d'),
                "end_date": week_end.strftime('%Y-%m-%d'),
                "shooting_days": min(5, (week_end - week_start).days + 1),
                "weekend_break": week_end < start_date + timedelta(days=total_days - 1)
            }
            
            current_date += timedelta(days=7)  # Move to next week
            week_number += 1
        
        return weeks
    
    def _calculate_weather_days(self, scenes: List[Dict[str, Any]]) -> int:
        """Calculate weather contingency days for exterior scenes."""
        exterior_scenes = sum(1 for scene in scenes if scene.get('location', {}).get('type') == 'EXT')
        return max(1, exterior_scenes // 5)  # 1 weather day per 5 exterior scenes
    
    def _generate_post_production_timeline(self, scenes: List[Dict[str, Any]], project_parameters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate post-production timeline."""
        # Estimate post-production duration based on project scope
        scene_count = len(scenes)
        estimated_duration_weeks = max(8, scene_count // 10)  # Minimum 8 weeks, scale with complexity
        
        production_end = datetime(2024, 3, 15) + timedelta(days=len(scenes) // 3)
        post_start = production_end + timedelta(days=1)
        
        post_production = {
            "start_date": post_start.strftime('%Y-%m-%d'),
            "estimated_duration": f"{estimated_duration_weeks} weeks",
            "phases": {
                "assembly_edit": {
                    "start_date": post_start.strftime('%Y-%m-%d'),
                    "duration": "2 weeks",
                    "deliverable": "Rough cut"
                },
                "rough_cut": {
                    "start_date": (post_start + timedelta(weeks=2)).strftime('%Y-%m-%d'),
                    "duration": "3 weeks",
                    "deliverable": "Director's cut"
                },
                "fine_cut": {
                    "start_date": (post_start + timedelta(weeks=5)).strftime('%Y-%m-%d'),
                    "duration": "2 weeks",
                    "deliverable": "Picture lock"
                },
                "sound_design": {
                    "start_date": (post_start + timedelta(weeks=4)).strftime('%Y-%m-%d'),
                    "duration": "4 weeks",
                    "deliverable": "Sound mix"
                },
                "color_correction": {
                    "start_date": (post_start + timedelta(weeks=6)).strftime('%Y-%m-%d'),
                    "duration": "2 weeks",
                    "deliverable": "Color graded master"
                },
                "final_mix": {
                    "start_date": (post_start + timedelta(weeks=7)).strftime('%Y-%m-%d'),
                    "duration": "1 week",
                    "deliverable": "Final mix"
                }
            },
            "final_delivery": (post_start + timedelta(weeks=estimated_duration_weeks)).strftime('%Y-%m-%d')
        }
        
        return post_production
    
    def _create_deliverable_schedule(self, project_parameters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create schedule of project deliverables."""
        deliverables = {
            "pre_production": [
                {"item": "Final script", "deadline": "12 weeks before production"},
                {"item": "Cast finalization", "deadline": "6 weeks before production"},
                {"item": "Location agreements", "deadline": "4 weeks before production"},
                {"item": "Equipment contracts", "deadline": "2 weeks before production"}
            ],
            "production": [
                {"item": "Daily rushes", "deadline": "24 hours after shooting"},
                {"item": "Backup footage", "deadline": "End of each shooting day"},
                {"item": "Production reports", "deadline": "Weekly during production"}
            ],
            "post_production": [
                {"item": "Rough cut", "deadline": "2 weeks after wrap"},
                {"item": "Director's cut", "deadline": "5 weeks after wrap"},
                {"item": "Picture lock", "deadline": "7 weeks after wrap"},
                {"item": "Final master", "deadline": "12 weeks after wrap"}
            ],
            "distribution": [
                {"item": "Festival submissions", "deadline": "14 weeks after wrap"},
                {"item": "Marketing materials", "deadline": "16 weeks after wrap"},
                {"item": "Distribution master", "deadline": "18 weeks after wrap"}
            ]
        }
        
        return deliverables
    
    def _generate_milestone_tracking(self, pre_production: Dict[str, Any], production: Dict[str, Any], post_production: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive milestone tracking system."""
        milestones = {
            "critical_path": [
                {
                    "milestone": "Script finalization",
                    "date": "10 weeks before production",
                    "dependencies": ["Script development"],
                    "impact": "High"
                },
                {
                    "milestone": "Cast locked",
                    "date": "6 weeks before production",
                    "dependencies": ["Casting complete"],
                    "impact": "Critical"
                },
                {
                    "milestone": "Locations secured",
                    "date": "4 weeks before production",
                    "dependencies": ["Location agreements", "Permits"],
                    "impact": "Critical"
                },
                {
                    "milestone": "Principal photography start",
                    "date": production["start_date"],
                    "dependencies": ["All pre-production complete"],
                    "impact": "Critical"
                },
                {
                    "milestone": "Principal photography wrap",
                    "date": production["end_date"],
                    "dependencies": ["All scenes completed"],
                    "impact": "Critical"
                },
                {
                    "milestone": "Picture lock",
                    "date": "7 weeks after wrap",
                    "dependencies": ["Editing complete"],
                    "impact": "High"
                },
                {
                    "milestone": "Final delivery",
                    "date": post_production["final_delivery"],
                    "dependencies": ["All post-production complete"],
                    "impact": "Critical"
                }
            ],
            "progress_tracking": {
                "completion_criteria": "Milestone deliverables approved",
                "review_frequency": "Weekly",
                "escalation_procedure": "24-hour notification for delays"
            }
        }
        
        return milestones
    
    def _generate_seasonal_planning(self, scenes: List[Dict[str, Any]], production_timeline: Dict[str, Any]) -> Dict[str, Any]:
        """Generate seasonal and weather-dependent planning."""
        seasonal_planning = {
            "weather_considerations": {},
            "seasonal_factors": {},
            "contingency_planning": {}
        }
        
        # Analyze exterior scenes for weather dependency
        exterior_scenes = [s for s in scenes if s.get('location', {}).get('type') == 'EXT']
        
        seasonal_planning["weather_considerations"] = {
            "exterior_scene_count": len(exterior_scenes),
            "weather_dependent_days": production_timeline.get("weather_days", 1),
            "recommended_seasons": ["Spring", "Early Fall"],
            "avoid_periods": ["Winter storms", "Hurricane season"],
            "backup_locations": "Indoor alternatives identified"
        }
        
        # Production timing analysis
        start_date = datetime.strptime(production_timeline["start_date"], '%Y-%m-%d')
        month = start_date.month
        
        if month in [12, 1, 2]:  # Winter
            season_notes = ["Short daylight hours", "Weather delays likely", "Heating costs"]
        elif month in [3, 4, 5]:  # Spring
            season_notes = ["Moderate weather", "Good daylight", "Occasional rain"]
        elif month in [6, 7, 8]:  # Summer
            season_notes = ["Long daylight hours", "Heat considerations", "Vacation schedules"]
        else:  # Fall
            season_notes = ["Moderate weather", "Shorter days", "Good conditions"]
        
        seasonal_planning["seasonal_factors"] = {
            "production_season": ["Winter", "Spring", "Summer", "Fall"][month // 3],
            "daylight_hours": self._estimate_daylight_hours(month),
            "weather_risks": season_notes,
            "crew_availability": "Standard" if month not in [7, 12] else "Holiday considerations"
        }
        
        # Contingency planning
        seasonal_planning["contingency_planning"] = {
            "weather_delays": {
                "cover_sets": "Interior locations identified",
                "schedule_buffer": f"{production_timeline.get('contingency_days', 2)} days",
                "crew_standby": "Weather watch protocols"
            },
            "equipment_protection": {
                "weather_covers": "Rain protection available",
                "temperature_control": "Climate-controlled storage",
                "backup_equipment": "20% equipment redundancy"
            }
        }
        
        return seasonal_planning
    
    def _estimate_daylight_hours(self, month: int) -> str:
        """Estimate daylight hours based on month."""
        daylight_hours = {
            1: "9-10 hours", 2: "10-11 hours", 3: "11-12 hours",
            4: "12-13 hours", 5: "13-14 hours", 6: "14-15 hours",
            7: "14-15 hours", 8: "13-14 hours", 9: "12-13 hours",
            10: "11-12 hours", 11: "10-11 hours", 12: "9-10 hours"
        }
        return daylight_hours.get(month, "11-12 hours")
    
    def _generate_calendar_summary(self, pre_production: Dict[str, Any], production: Dict[str, Any], post_production: Dict[str, Any]) -> Dict[str, Any]:
        """Generate overall calendar summary."""
        # Calculate total project duration
        pre_prod_weeks = 12
        production_days = production["total_shooting_days"]
        post_prod_weeks = int(post_production["estimated_duration"].split()[0])
        
        total_weeks = pre_prod_weeks + (production_days // 7) + 1 + post_prod_weeks
        
        summary = {
            "total_project_duration": f"{total_weeks} weeks",
            "phase_breakdown": {
                "pre_production": f"{pre_prod_weeks} weeks",
                "production": f"{production_days} shooting days",
                "post_production": f"{post_prod_weeks} weeks"
            },
            "key_dates": {
                "project_start": pre_production["key_phases"]["script_development"]["start_date"],
                "production_start": production["start_date"],
                "production_wrap": production["end_date"],
                "final_delivery": post_production["final_delivery"]
            },
            "resource_requirements": {
                "locations": len(production["location_schedule"]),
                "shooting_days": production_days,
                "contingency_days": production.get("contingency_days", 2),
                "weather_days": production.get("weather_days", 1)
            },
            "critical_success_factors": [
                "Weather-dependent scheduling for exterior scenes",
                "Cast availability coordination",
                "Location permit timing",
                "Equipment availability windows",
                "Post-production facility booking"
            ]
        }
        
        return summary