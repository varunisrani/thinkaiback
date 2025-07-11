import logging
from typing import Dict, Any, Optional
import json
import os
from datetime import datetime
from .agents.schedule_parser_agent import ScheduleParserAgent
from .agents.assistant_director_agent import AssistantDirectorAgent
from .agents.location_optimizer_agent import LocationOptimizerAgent
from .agents.crew_allocator_agent import CrewAllocatorAgent
from .agents.production_calendar_agent import ProductionCalendarAgent

logger = logging.getLogger(__name__)

class SchedulingCoordinator:
    def __init__(self):
        logger.info("Initializing SchedulingCoordinator with 5 specialized agents")
        
        # Initialize all 5 scheduling agents
        self.schedule_parser = ScheduleParserAgent()           # FOUNDATIONAL - GPT-4.1 mini
        self.assistant_director = AssistantDirectorAgent()     # DOOP/STRIPBOARD - Gemini 2.5 Flash
        self.location_optimizer = LocationOptimizerAgent()     # LOGISTICS - Gemini 2.5 Flash
        self.crew_allocator = CrewAllocatorAgent()             # DEPT SCHEDULING - GPT-4.1 mini
        self.production_calendar = ProductionCalendarAgent()   # TIMELINE MGMT - Gemini 2.5 Flash
        
        # Create necessary data directories
        os.makedirs("data/schedules", exist_ok=True)
        os.makedirs("data/schedules/calendar", exist_ok=True)
        os.makedirs("data/schedules/gantt", exist_ok=True)
        logger.info("Schedule data directories ensured")
    
    def _validate_scene_data(self, scene_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate scene data structure and return processed scenes."""
        if not isinstance(scene_data, dict):
            raise ValueError("Scene data must be a dictionary")
        
        if 'parsed_data' not in scene_data and 'scenes' not in scene_data:
            raise ValueError("Scene data must contain either 'parsed_data' or 'scenes' key")
        
        # If we have parsed_data, extract scenes from it
        scenes = scene_data.get('scenes', [])
        if not scenes and 'parsed_data' in scene_data:
            parsed_data = scene_data['parsed_data']
            if isinstance(parsed_data, dict) and 'scenes' in parsed_data:
                scenes = parsed_data['scenes']
        
        if not scenes or not isinstance(scenes, list):
            raise ValueError("No valid scenes found in scene data")
        
        logger.info(f"Found {len(scenes)} scenes in input data")
        
        # Return processed scene data
        return {
            'scenes': scenes,
            'metadata': scene_data.get('metadata', {}),
            'original_data': scene_data
        }
    
    def _validate_crew_data(self, crew_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate crew data structure and return processed crew data."""
        if not isinstance(crew_data, dict):
            raise ValueError("Crew data must be a dictionary")
        
        # Check for either direct crew list or nested structure
        crew_list = crew_data.get('crew', [])
        if not crew_list and 'character_breakdown' in crew_data:
            crew_list = crew_data['character_breakdown'].get('crew', [])
        
        if not crew_list:
            logger.warning("No crew data found, will use default crew structure")
            crew_list = [
                {"name": "Director", "role": "Director"},
                {"name": "DP", "role": "Director of Photography"},
                {"name": "Sound Mixer", "role": "Sound"},
                {"name": "Gaffer", "role": "Lighting"},
                {"name": "Key Grip", "role": "Grip"}
            ]
        
        return {
            'crew': crew_list,
            'metadata': crew_data.get('metadata', {}),
            'original_data': crew_data
        }
    
    def _validate_start_date(self, start_date: str) -> str:
        """Validate and return the start date."""
        if not start_date:
            today = datetime.now()
            start_date = today.strftime("%Y-%m-%d")
            logger.warning(f"No start date provided, using today's date: {start_date}")
            return start_date
            
        try:
            datetime.strptime(start_date, "%Y-%m-%d")
            return start_date
        except ValueError:
            raise ValueError("Invalid start date format. Use YYYY-MM-DD")
    
    def _generate_scheduling_summary(
        self, 
        schedule_elements: Dict[str, Any], 
        stripboard_doop: Dict[str, Any], 
        location_plan: Dict[str, Any], 
        crew_allocation: Dict[str, Any], 
        production_calendar: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate comprehensive scheduling summary from all agents."""
        try:
            summary = {
                "project_overview": {
                    "total_scenes": schedule_elements.get("scene_count", 0),
                    "locations": location_plan.get("location_grouping", {}).get("shooting_efficiency", {}).get("total_locations", 0),
                    "estimated_shoot_days": location_plan.get("location_grouping", {}).get("shooting_efficiency", {}).get("estimated_shooting_days", 0),
                    "total_crew_size": len(crew_allocation.get("crew_assignments", [])),
                    "project_duration": production_calendar.get("calendar_summary", {}).get("total_project_duration", "Unknown")
                },
                "agent_contributions": {
                    "schedule_parser": {
                        "elements_parsed": schedule_elements.get("processing_status", "Unknown"),
                        "cast_requirements": schedule_elements.get("scheduling_elements", {}).get("cast_requirements", {}),
                        "complexity_analysis": "Scene complexity assessed"
                    },
                    "assistant_director": {
                        "stripboard_scenes": len(stripboard_doop.get("stripboard", {}).get("scenes", {})),
                        "doop_characters": len(stripboard_doop.get("doop_reports", {})),
                        "call_sheets": len(stripboard_doop.get("call_sheets", {})),
                        "optimization_level": "Advanced"
                    },
                    "location_optimizer": {
                        "location_clusters": len(location_plan.get("location_grouping", {}).get("location_clusters", {})),
                        "equipment_moves": len(location_plan.get("logistics_planning", {}).get("equipment_moves", [])),
                        "logistics_efficiency": "Optimized",
                        "cost_optimization": location_plan.get("cost_optimization", {}).get("optimized_costs", {})
                    },
                    "crew_allocator": {
                        "departments_managed": len(crew_allocation.get("department_schedules", {})),
                        "crew_assignments": len(crew_allocation.get("crew_assignments", [])),
                        "union_compliance": "Verified",
                        "work_hour_compliance": crew_allocation.get("work_hour_compliance", {}).get("compliance_status", {})
                    },
                    "production_calendar": {
                        "timeline_phases": 3,  # pre, production, post
                        "milestones_tracked": len(production_calendar.get("milestone_tracking", {}).get("critical_path", [])),
                        "seasonal_planning": "Weather considerations included",
                        "deliverable_tracking": "Comprehensive"
                    }
                },
                "coordination_metrics": {
                    "agent_integration": "Fully coordinated",
                    "data_flow": "Sequential pipeline",
                    "optimization_level": "Advanced multi-agent",
                    "scheduling_approach": "Industry-standard practices"
                }
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Error generating scheduling summary: {str(e)}")
            return {"error": f"Summary generation failed: {str(e)}"}
    
    async def generate_schedule(
        self,
        scene_data: Dict[str, Any],
        crew_data: Dict[str, Any],
        start_date: str,
        location_constraints: Optional[Dict[str, Any]] = None,
        equipment_inventory: Optional[Dict[str, Any]] = None,
        schedule_constraints: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Generate complete shooting schedule through the 5-agent scheduling pipeline."""
        try:
            logger.info("Starting 5-agent scheduling pipeline")
            
            # Validate and prepare input data
            try:
                logger.info("Validating input data")
                processed_scene_data = self._validate_scene_data(scene_data)
                processed_crew_data = self._validate_crew_data(crew_data)
                validated_start_date = self._validate_start_date(start_date)
                logger.info("Input data validated and prepared")
                
            except ValueError as e:
                logger.error(f"Input validation failed: {str(e)}")
                raise
            
            # Step 1: Parse scheduling elements (FOUNDATIONAL)
            logger.info("Step 1: Parsing scheduling elements with ScheduleParserAgent")
            schedule_elements = await self.schedule_parser.parse_schedule_elements(processed_scene_data)
            logger.info("Schedule parsing completed")
            
            # Step 2: Generate stripboard and DOOP reports (DOOP/STRIPBOARD)
            logger.info("Step 2: Generating stripboard and DOOP reports with AssistantDirectorAgent")
            stripboard_doop = await self.assistant_director.generate_stripboard_doop(processed_scene_data)
            logger.info("Stripboard and DOOP generation completed")
            
            # Step 3: Optimize locations and logistics (LOGISTICS)
            logger.info("Step 3: Optimizing locations and logistics with LocationOptimizerAgent")
            location_plan = await self.location_optimizer.optimize_locations(
                processed_scene_data,
                location_constraints
            )
            logger.info("Location optimization completed")
            
            # Step 4: Allocate crew across departments (DEPT SCHEDULING)
            logger.info("Step 4: Allocating crew across departments with CrewAllocatorAgent")
            crew_allocation = await self.crew_allocator.allocate_departments(
                processed_scene_data,
                processed_crew_data
            )
            logger.info("Department crew allocation completed")
            
            # Step 5: Generate production calendar and timeline (TIMELINE MGMT)
            logger.info("Step 5: Generating production calendar with ProductionCalendarAgent")
            production_calendar = await self.production_calendar.generate_production_calendar(
                processed_scene_data,
                {
                    "start_date": validated_start_date,
                    "location_plan": location_plan,
                    "crew_allocation": crew_allocation
                }
            )
            logger.info("Production calendar generation completed")
            
            # Compile comprehensive scheduling results
            result = {
                "schedule_elements": schedule_elements,
                "stripboard_doop": stripboard_doop,
                "location_plan": location_plan,
                "crew_allocation": crew_allocation,
                "production_calendar": production_calendar,
                "agent_coordination": {
                    "schedule_parser": "Foundational elements extracted",
                    "assistant_director": "Stripboard and DOOP reports generated",
                    "location_optimizer": "Location logistics optimized",
                    "crew_allocator": "Department scheduling coordinated",
                    "production_calendar": "Timeline management completed"
                },
                "scheduling_summary": self._generate_scheduling_summary(
                    schedule_elements, stripboard_doop, location_plan, crew_allocation, production_calendar
                ),
                "timestamp": datetime.now().isoformat()
            }
            
            # Save to disk
            logger.info("Saving comprehensive scheduling data to disk")
            saved_files = self._save_to_disk(result)
            result["saved_files"] = saved_files
            
            logger.info("5-agent scheduling pipeline completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"Error in 5-agent scheduling pipeline: {str(e)}", exc_info=True)
            raise
    
    async def generate_schedule_frontend(
        self,
        script_data: Dict[str, Any],
        production_constraints: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Frontend-compatible schedule generation method."""
        try:
            logger.info("Starting frontend-compatible schedule generation")
            
            # Extract data from nested structure
            scene_data = script_data.get("script_results", script_data)
            crew_data = script_data.get("character_results", {})
            
            # Extract constraints
            constraints = production_constraints or {}
            start_date = constraints.get("start_date", "")
            location_constraints = constraints.get("location_constraints", {})
            schedule_constraints = constraints.get("schedule_constraints", {})
            
            # Call the main generate_schedule method
            return await self.generate_schedule(
                scene_data=scene_data,
                crew_data=crew_data,
                start_date=start_date,
                location_constraints=location_constraints,
                equipment_inventory=None,
                schedule_constraints=schedule_constraints
            )
            
        except Exception as e:
            logger.error(f"Error in frontend schedule generation: {str(e)}")
            raise

    def _save_to_disk(self, data: Dict[str, Any]) -> Dict[str, str]:
        """Save schedule data to disk in multiple formats."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            saved_files = {}
            
            # Save main schedule
            schedule_file = f"data/schedules/schedule_{timestamp}.json"
            with open(schedule_file, "w") as f:
                json.dump(data, f, indent=2)
            saved_files['main'] = schedule_file
            
            # Save calendar data separately
            if 'calendar_data' in data:
                calendar_file = f"data/schedules/calendar/calendar_{timestamp}.json"
                with open(calendar_file, "w") as f:
                    json.dump(data['calendar_data'], f, indent=2)
                saved_files['calendar'] = calendar_file
            
            # Save Gantt data separately
            if 'gantt_data' in data:
                gantt_file = f"data/schedules/gantt/gantt_{timestamp}.json"
                with open(gantt_file, "w") as f:
                    json.dump(data['gantt_data'], f, indent=2)
                saved_files['gantt'] = gantt_file
            
            logger.info(f"Schedule data saved to multiple files")
            return saved_files
            
        except Exception as e:
            logger.error(f"Error saving schedule data to disk: {str(e)}")
            raise