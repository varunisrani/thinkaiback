from typing import Dict, Any, Optional, List, Union
import json
import os
import logging
from datetime import datetime
import sys
import PyPDF2
import io
from .agents.adk_eighths_calculator_proper import create_adk_eighths_agent
from .agents.adk_scene_breakdown_cards_agent import create_adk_scene_breakdown_cards_agent
from .agents.adk_department_coordinator_agent import create_adk_department_coordinator_agent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ScriptIngestionCoordinator:
    """
    🎬 Script Ingestion Coordinator (Main Orchestrator)
    
    Coordinates sequential 3-agent pipeline:
    1. ADK Eighths Calculator Agent (timing and complexity)
    2. Scene Breakdown Cards Agent (production requirements)
    3. Department Coordinator Agent (crew and resources)
    """
    
    def __init__(self):
        logger.info("Initializing ScriptIngestionCoordinator with 3-agent sequential pipeline")
        
        # Initialize all 3 ADK agents in sequence
        self.eighths_calculator = create_adk_eighths_agent()
        self.breakdown_cards_agent = create_adk_scene_breakdown_cards_agent()
        self.department_coordinator = create_adk_department_coordinator_agent()
        
        # Create necessary directories
        os.makedirs("data/scripts", exist_ok=True)
        os.makedirs("data/scripts/metadata", exist_ok=True)
        os.makedirs("data/scripts/validation", exist_ok=True)
        os.makedirs("data/scripts/reports", exist_ok=True)
        logger.info("Data directories ensured")
        logger.info("3-agent sequential pipeline initialized successfully")
    
    async def process_script(
        self,
        script_input: Union[str, bytes],
        input_type: str = "text",
        department_focus: Optional[list] = None,
        validation_level: str = "lenient"
    ) -> Dict[str, Any]:
        """
        Process a script through the 3-agent sequential pipeline.
        
        Args:
            script_input: The input script (text string or PDF bytes)
            input_type: Type of input ('text' or 'pdf')
            department_focus: Optional list of departments to focus analysis on
            validation_level: Validation strictness ('strict' or 'lenient')
            
        Returns:
            Dict containing processed results from all 3 agents
        """
        logger.info("Starting 3-agent sequential processing pipeline")
        processing_start = datetime.now()
        
        try:
            # Initialize processing status
            processing_status = {
                "started_at": processing_start.isoformat(),
                "current_stage": "script_parsing",
                "completed_stages": [],
                "errors": [],
                "warnings": [],
                "agents_used": ["ADKEighthsCalculatorAgent", "SceneBreakdownCardsAgent", "DepartmentCoordinatorAgent"]
            }
            
            # Extract text from PDF if needed
            if input_type == "pdf":
                logger.info("📄 Extracting text from PDF for page-by-page analysis")
                script_text = self._extract_text_from_pdf(script_input)
            else:
                script_text = script_input
            
            logger.info("🎬 Preparing full script for ADK Eighths Calculator (page-by-page analysis)")
            logger.info(f"📄 Script length: {len(script_text)} characters")
            
            # Create script data package for agents
            script_data = {
                "full_text": script_text,
                "input_type": input_type,
                "timestamp": datetime.now().isoformat(),
                "character_count": len(script_text),
                "estimated_pages": len(script_text) / 1500  # Rough page estimate
            }
            
            # 🎬 STAGE 1: Eighths Calculation with ADK Agent (Page-by-Page Analysis)
            logger.info("✅ Stage 1: ADK Eighths Calculator - Page-by-Page Script Analysis")
            processing_status["current_stage"] = "eighths_calculation"
            try:
                # Pass full script text to ADK agent for page-by-page analysis
                eighths_result = self.eighths_calculator.process_full_script(script_data)
                
                if eighths_result["status"] == "error":
                    raise ValueError(f"Eighths calculation failed: {eighths_result['message']}")
                
                eighths_data = eighths_result
                
                processing_status["completed_stages"].append({
                    "stage": "eighths_calculation",
                    "agent": "ADKEighthsCalculatorAgent",
                    "completed_at": datetime.now().isoformat(),
                    "success": True
                })
                logger.info("✅ Eighths calculation completed successfully")
            except Exception as e:
                logger.error(f"❌ Error in eighths calculation stage: {str(e)}")
                processing_status["errors"].append({
                    "stage": "eighths_calculation",
                    "agent": "ADKEighthsCalculatorAgent",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                })
                if validation_level == "strict":
                    raise
                eighths_data = {"error": str(e)}
            
            # 🎬 STAGE 2: Scene Breakdown Cards Generation (Based on Eighths Data)
            logger.info("✅ Stage 2: Generating Scene Breakdown Cards (depends on eighths data)")
            processing_status["current_stage"] = "scene_breakdown_cards"
            try:
                # Extract scenes from eighths calculation for breakdown cards
                scenes_from_eighths = []
                if "eighths_data" in eighths_data and "scene_calculations" in eighths_data["eighths_data"]:
                    scenes_from_eighths = [calc["scene"] for calc in eighths_data["eighths_data"]["scene_calculations"]]
                
                # Generate breakdown cards using eighths data and extracted scenes
                breakdown_data = self.breakdown_cards_agent.generate_breakdown_cards_from_eighths(eighths_data, scenes_from_eighths)
                
                if "error" in breakdown_data:
                    raise ValueError(f"Scene breakdown cards generation failed: {breakdown_data['error']}")
                
                processing_status["completed_stages"].append({
                    "stage": "scene_breakdown_cards",
                    "agent": "SceneBreakdownCardsAgent",
                    "completed_at": datetime.now().isoformat(),
                    "success": True
                })
                logger.info("✅ Scene breakdown cards generated successfully")
            except Exception as e:
                logger.error(f"❌ Error in scene breakdown cards stage: {str(e)}")
                processing_status["errors"].append({
                    "stage": "scene_breakdown_cards",
                    "agent": "SceneBreakdownCardsAgent",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                })
                if validation_level == "strict":
                    raise
                breakdown_data = {"error": str(e)}
            
            # 🎬 STAGE 3: Department Coordination (Based on Breakdown Cards + Eighths Data)
            logger.info("✅ Stage 3: Coordinating Department Requirements (depends on breakdown cards + eighths)")
            processing_status["current_stage"] = "department_coordination"
            try:
                # Coordinate departments using breakdown cards and eighths data for maximum accuracy
                department_data = self.department_coordinator.coordinate_from_breakdown_and_eighths(breakdown_data, eighths_data)
                
                if "error" in department_data:
                    raise ValueError(f"Department coordination failed: {department_data['error']}")
                
                processing_status["completed_stages"].append({
                    "stage": "department_coordination",
                    "agent": "DepartmentCoordinatorAgent",
                    "completed_at": datetime.now().isoformat(),
                    "success": True
                })
                logger.info("✅ Department coordination completed successfully")
            except Exception as e:
                logger.error(f"❌ Error in department coordination stage: {str(e)}")
                processing_status["errors"].append({
                    "stage": "department_coordination",
                    "agent": "DepartmentCoordinatorAgent",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                })
                if validation_level == "strict":
                    raise
                department_data = {"error": str(e)}
            
            # Placeholder for additional analysis
            production_analysis = {}
            
            # 🎬 STAGE 4: Data Integration and Finalization
            logger.info("🎯 Stage 4: Integrating all 3 agent outputs with proper dependencies")
            processing_status["current_stage"] = "data_integration"
            
            # Extract parsed scenes from eighths data for consistency
            parsed_scenes = []
            if "eighths_data" in eighths_data and "scene_calculations" in eighths_data["eighths_data"]:
                parsed_scenes = [calc["scene"] for calc in eighths_data["eighths_data"]["scene_calculations"]]
            
            parsed_data = {
                "scenes": parsed_scenes,
                "timestamp": datetime.now().isoformat(),
                "source": "eighths_calculator_page_analysis"
            }
            
            # Create comprehensive result structure with proper agent dependencies
            result = {
                "parsed_data": parsed_data,
                "metadata": self._integrate_metadata(
                    eighths_data, breakdown_data, department_data, {}),
                "agent_outputs": {
                    "adk_eighths_calculator": eighths_data,
                    "scene_breakdown_cards": breakdown_data,
                    "department_coordinator": department_data
                },
                "processing_status": processing_status,
                "statistics": self._generate_comprehensive_statistics(
                    parsed_data, eighths_data, breakdown_data, department_data, {}),
                "ui_metadata": self._generate_ui_metadata(
                    parsed_data, eighths_data, breakdown_data, department_data, {})
            }
            
            # Add department-specific metadata if focus specified
            if department_focus and "department_analysis" in department_data:
                result["metadata"]["department_focus"] = {
                    dept: department_data["department_analysis"].get(dept, {})
                    for dept in department_focus
                    if dept in department_data["department_analysis"]
                }
            
            # Save results
            try:
                saved_paths = self._save_to_disk(result)
                result["saved_paths"] = saved_paths
            except Exception as e:
                logger.error(f"Error saving to disk: {str(e)}")
                processing_status["warnings"].append({
                    "type": "storage",
                    "message": "Failed to save results to disk",
                    "details": str(e)
                })
            
            # Mark processing as complete
            processing_status["current_stage"] = "completed"
            processing_status["completed_at"] = datetime.now().isoformat()
            processing_status["duration"] = str(datetime.now() - processing_start)
            
            # Format data for frontend with 3 clean sections
            formatted_result = self._format_for_frontend(
                eighths_data, breakdown_data, department_data, 
                parsed_data, processing_status
            )
            
            # Add saved paths
            if "saved_paths" in result:
                formatted_result["saved_paths"] = result["saved_paths"]
            
            logger.info("🎉 3-agent sequential pipeline processing completed successfully")
            return formatted_result
            
        except Exception as e:
            logger.error(f"❌ 3-agent sequential pipeline processing failed: {str(e)}", exc_info=True)
            if processing_status:
                processing_status["current_stage"] = "failed"
                processing_status["failed_at"] = datetime.now().isoformat()
                processing_status["final_error"] = str(e)
            
            return {
                "error": str(e),
                "status": "failed",
                "processing_status": processing_status
            }
    
    def _parse_script_to_scenes(self, script_text: str) -> List[Dict[str, Any]]:
        """Parse script text into scenes format for ADK agent."""
        scenes = []
        
        # Simple parsing - split by common scene headers
        lines = script_text.split('\n')
        current_scene = None
        scene_number = 1
        
        for line in lines:
            line_upper = line.strip().upper()
            
            # Check for scene headers (INT., EXT., INT/EXT)
            if any(line_upper.startswith(prefix) for prefix in ['INT.', 'EXT.', 'INT/EXT']):
                # Save previous scene if exists
                if current_scene:
                    scenes.append(current_scene)
                
                # Parse location and time
                parts = line.split('-')
                location = parts[0].strip() if parts else line.strip()
                time_of_day = parts[-1].strip() if len(parts) > 1 else "DAY"
                
                # Determine location type
                location_type = "INT" if line_upper.startswith('INT') else "EXT"
                
                current_scene = {
                    "scene_number": str(scene_number),
                    "location": location,
                    "location_type": location_type,
                    "time_of_day": time_of_day,
                    "description": "",
                    "character_count": 0,
                    "dialogue_count": 0,
                    "technical_cues": []
                }
                scene_number += 1
            elif current_scene:
                # Add to current scene description
                current_scene["description"] += line + "\n"
                
                # Count characters (simple heuristic: uppercase lines)
                if line.strip() and line.strip() == line.strip().upper() and len(line.strip()) > 2:
                    current_scene["character_count"] += 1
                
                # Count dialogue (lines after character names)
                if line.strip() and not line.strip().startswith('(') and current_scene["character_count"] > 0:
                    current_scene["dialogue_count"] += 1
                
                # Check for technical cues
                if any(cue in line.upper() for cue in ['CAMERA', 'CLOSE-UP', 'WIDE', 'PAN', 'ZOOM', 'CUT TO', 'FADE']):
                    current_scene["technical_cues"].append(line.strip())
        
        # Add last scene
        if current_scene:
            scenes.append(current_scene)
        
        return scenes
    
    def _integrate_metadata(self, eighths_data: Dict[str, Any], 
                           breakdown_data: Dict[str, Any],
                           department_data: Dict[str, Any],
                           production_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Integrate metadata from ADK agent into unified structure."""
        integrated_metadata = {
            "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "agent_integration": "3-agent sequential pipeline"
        }
        
        # Integrate eighths data from ADK agent
        if "eighths_data" in eighths_data:
            integrated_metadata["eighths_breakdown"] = eighths_data.get("eighths_data", {})
            integrated_metadata["eighths_report"] = eighths_data.get("report", "")
        elif "report" in eighths_data:
            integrated_metadata["eighths_report"] = eighths_data["report"]
        
        integrated_metadata["eighths_status"] = eighths_data.get("status", "unknown")
        integrated_metadata["eighths_message"] = eighths_data.get("message", "")
        
        # Integrate breakdown cards data
        if "breakdown_cards" in breakdown_data:
            integrated_metadata["breakdown_cards"] = breakdown_data.get("breakdown_cards", [])
            integrated_metadata["breakdown_summary"] = breakdown_data.get("summary_statistics", {})
            integrated_metadata["scheduling_analysis"] = breakdown_data.get("scheduling_analysis", {})
        
        # Integrate department coordination data
        if "department_analysis" in department_data:
            integrated_metadata["department_analysis"] = department_data.get("department_analysis", {})
            integrated_metadata["resource_allocation"] = department_data.get("resource_allocation", {})
            integrated_metadata["crew_scheduling"] = department_data.get("crew_scheduling", {})
            integrated_metadata["coordination_recommendations"] = department_data.get("coordination_recommendations", [])
        
        return integrated_metadata
    
    
    def _generate_comprehensive_statistics(self, parsed_data: Dict[str, Any],
                                         eighths_data: Dict[str, Any],
                                         breakdown_data: Dict[str, Any],
                                         department_data: Dict[str, Any],
                                         production_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive statistics from ADK agent outputs."""
        stats = {
            "agent_summary": {
                "total_agents": 3,
                "successful_agents": sum([
                    1 if eighths_data.get("status") == "success" else 0,
                    1 if "error" not in breakdown_data else 0,
                    1 if "error" not in department_data else 0
                ])
            }
        }
        
        # Basic scene statistics
        scenes = parsed_data.get("scenes", [])
        stats.update({
            "total_scenes": len(scenes),
            "total_characters": sum(scene.get("character_count", 0) for scene in scenes),
            "total_locations": len(set(scene.get("location", "") for scene in scenes))
        })
        
        # Eighths statistics from ADK agent
        if "eighths_data" in eighths_data and eighths_data["eighths_data"]:
            data = eighths_data["eighths_data"]
            if "totals" in data:
                stats["eighths_summary"] = {
                    "total_eighths": data["totals"].get("total_adjusted_eighths", 0),
                    "estimated_days": data["totals"].get("estimated_shoot_days", 0)
                }
        
        # Add reports if available
        if "report" in eighths_data:
            stats["eighths_report"] = eighths_data["report"]
        
        # Breakdown cards statistics
        if "summary_statistics" in breakdown_data:
            breakdown_summary = breakdown_data["summary_statistics"]
            stats["breakdown_summary"] = {
                "total_cards": breakdown_summary.get("total_cards", 0),
                "complexity_distribution": breakdown_summary.get("complexity_distribution", {}),
                "estimated_crew_days": breakdown_summary.get("estimated_crew_days", 0)
            }
        
        # Department coordination statistics
        if "department_summary" in department_data:
            dept_summary = department_data["department_summary"]
            stats["department_summary"] = {
                "total_departments": dept_summary.get("total_departments_involved", 0),
                "total_crew_size": dept_summary.get("total_crew_size", 0),
                "most_involved_department": dept_summary.get("most_involved_department", "")
            }
        
        return stats
    
    def _generate_ui_metadata(self, parsed_data: Dict[str, Any],
                            eighths_data: Dict[str, Any],
                            breakdown_data: Dict[str, Any],
                            department_data: Dict[str, Any],
                            production_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate metadata specifically for UI rendering."""
        ui_metadata = {
            "agent_status": {
                "adk_eighths_calculator": eighths_data.get("status") == "success",
                "scene_breakdown_cards": "error" not in breakdown_data,
                "department_coordinator": "error" not in department_data
            },
            "visualization_data": {},
            "dashboard_summary": {}
        }
        
        # Add visualization data from all agents
        if "eighths_data" in eighths_data and eighths_data["eighths_data"]:
            data = eighths_data["eighths_data"]
            if "scene_calculations" in data:
                ui_metadata["visualization_data"]["scene_eighths"] = {
                    calc["scene"]["scene_number"]: calc["scene"]["adjusted_eighths"]
                    for calc in data["scene_calculations"]
                    if "scene" in calc and "scene_number" in calc["scene"]
                }
        
        # Add breakdown cards visualization
        if "breakdown_cards" in breakdown_data:
            ui_metadata["visualization_data"]["scene_complexity"] = {
                card["scene_number"]: card["complexity_level"]
                for card in breakdown_data["breakdown_cards"]
            }
            ui_metadata["visualization_data"]["crew_estimates"] = {
                card["scene_number"]: card["crew_estimate"]["total_crew"]
                for card in breakdown_data["breakdown_cards"]
            }
        
        # Add department data visualization
        if "department_analysis" in department_data:
            dept_analysis = department_data["department_analysis"]
            ui_metadata["visualization_data"]["department_involvement"] = {
                dept_name: len(dept_data["scenes_requiring_department"])
                for dept_name, dept_data in dept_analysis.items()
            }
        
        # Timeline data
        ui_metadata["timeline_data"] = parsed_data.get("timeline", {})
        
        # Dashboard summary
        scenes_count = len(parsed_data.get("scenes", []))
        ui_metadata["dashboard_summary"] = {
            "total_scenes": scenes_count,
            "agents_completed": sum(ui_metadata["agent_status"].values()),
            "processing_complete": all(ui_metadata["agent_status"].values())
        }
        
        return ui_metadata
    
    def _format_for_frontend(self, eighths_data: Dict[str, Any], 
                           breakdown_data: Dict[str, Any],
                           department_data: Dict[str, Any],
                           parsed_data: Dict[str, Any],
                           processing_status: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format data specifically for frontend consumption in 3 clean sections:
        1. Breakdown Cards
        2. Department Analysis  
        3. Reports
        """
        logger.info("📊 Formatting data for frontend with 3-section structure")
        
        # Section 1: Breakdown Cards
        breakdown_cards = []
        if "breakdown_cards" in breakdown_data:
            breakdown_cards = breakdown_data["breakdown_cards"]
        
        # Section 2: Department Analysis
        department_analysis = {}
        if "department_analysis" in department_data:
            department_analysis = department_data["department_analysis"]
        
        # Section 3: Reports (Eighths + Summary Data)
        reports = {
            "eighths_calculator": {},
            "timing_analysis": {},
            "department_summary": {},
            "processing_summary": {}
        }
        
        # Extract eighths data for reports
        if "eighths_data" in eighths_data:
            eighths_calc_data = eighths_data["eighths_data"]
            if "totals" in eighths_calc_data:
                reports["eighths_calculator"] = {
                    "total_scenes": len(eighths_calc_data.get("scene_calculations", [])),
                    "total_eighths": eighths_calc_data["totals"].get("total_adjusted_eighths", 0),
                    "estimated_shoot_days": eighths_calc_data["totals"].get("estimated_shoot_days", 0),
                    "total_pages": eighths_calc_data["totals"].get("total_pages", 0),
                    "complexity_breakdown": eighths_calc_data.get("breakdown_by_complexity", {})
                }
                
                # Add enhanced scene details from the eighths calculator
                if "scene_calculations" in eighths_calc_data:
                    scene_details = []
                    for calc in eighths_calc_data["scene_calculations"]:
                        if "scene" in calc:
                            scene = calc["scene"]
                            scene_detail = {
                                "scene_number": scene.get("scene_number", ""),
                                "location": scene.get("location", ""),
                                "scene_summary": scene.get("scene_summary", ""),
                                "characters_in_scene": scene.get("characters_in_scene", []),
                                "adjusted_eighths": scene.get("adjusted_eighths", 0),
                                "estimated_hours": scene.get("estimated_shoot_hours", 0),
                                "complexity_level": calc.get("complexity", {}).get("total_complexity", 1.0),
                                "shooting_notes": scene.get("shooting_notes", [])
                            }
                            scene_details.append(scene_detail)
                    
                    if scene_details:
                        reports["eighths_calculator"]["scene_details"] = scene_details
            
            # Timing analysis
            reports["timing_analysis"] = {
                "processing_time": eighths_data.get("processing_time", 0),
                "scenes_processed": len(eighths_calc_data.get("scene_calculations", [])),
                "average_time_per_scene": 0
            }
            
            if reports["timing_analysis"]["scenes_processed"] > 0:
                reports["timing_analysis"]["average_time_per_scene"] = round(
                    reports["timing_analysis"]["processing_time"] / reports["timing_analysis"]["scenes_processed"], 2
                )
        
        # Extract department summary for reports
        if "department_summary" in department_data:
            reports["department_summary"] = department_data["department_summary"]
        
        # Processing summary
        reports["processing_summary"] = {
            "total_processing_time": processing_status.get("duration", "Unknown"),
            "agents_used": len(processing_status.get("agents_used", [])),
            "completed_stages": len(processing_status.get("completed_stages", [])),
            "status": processing_status.get("current_stage", "unknown"),
            "timestamp": processing_status.get("completed_at", "")
        }
        
        # Extract summary statistics from breakdown data
        summary_statistics = {}
        if "summary_statistics" in breakdown_data:
            summary_statistics = breakdown_data["summary_statistics"]
        
        # Extract scheduling analysis
        scheduling_analysis = {}
        if "scheduling_analysis" in breakdown_data:
            scheduling_analysis = breakdown_data["scheduling_analysis"]
        
        # Extract crew requirements summary
        crew_requirements_summary = {}
        if "crew_requirements_summary" in breakdown_data:
            crew_requirements_summary = breakdown_data["crew_requirements_summary"]
        
        # Extract resource allocation
        resource_allocation = {}
        if "resource_allocation" in department_data:
            resource_allocation = department_data["resource_allocation"]
        
        # Extract coordination recommendations
        coordination_recommendations = []
        if "coordination_recommendations" in department_data:
            coordination_recommendations = department_data["coordination_recommendations"]
        
        # Format final result for frontend
        formatted_result = {
            "success": True,
            "message": "3-agent sequential processing completed successfully",
            "timestamp": processing_status.get("completed_at", ""),
            
            # Section 1: Breakdown Cards
            "breakdown_cards": breakdown_cards,
            "breakdown_summary": {
                "summary_statistics": summary_statistics,
                "scheduling_analysis": scheduling_analysis,
                "crew_requirements_summary": crew_requirements_summary
            },
            
            # Section 2: Department Analysis
            "department_analysis": department_analysis,
            "department_coordination": {
                "resource_allocation": resource_allocation,
                "coordination_recommendations": coordination_recommendations
            },
            
            # Section 3: Reports
            "reports": reports,
            
            # Additional metadata for compatibility
            "parsed_data": parsed_data,
            "processing_status": processing_status,
            "agent_outputs": {
                "adk_eighths_calculator": eighths_data,
                "adk_scene_breakdown_cards": breakdown_data,
                "adk_department_coordinator": department_data
            }
        }
        
        logger.info("✅ Data formatted for frontend 3-section structure")
        return formatted_result
    
    def _save_to_disk(self, data: Dict[str, Any]) -> Dict[str, str]:
        """Save processed data to disk in organized structure."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            paths = {}
            
            # Save main data with agent outputs
            main_path = f"data/scripts/script_{timestamp}.json"
            with open(main_path, "w") as f:
                json.dump({
                    "parsed_data": data["parsed_data"],
                    "processing_status": data["processing_status"],
                    "statistics": data["statistics"],
                    "agent_outputs": data["agent_outputs"]
                }, f, indent=2)
            paths["main"] = main_path
            
            # Save integrated metadata
            metadata_path = f"data/scripts/metadata/metadata_{timestamp}.json"
            with open(metadata_path, "w") as f:
                json.dump({
                    "metadata": data["metadata"],
                    "ui_metadata": data["ui_metadata"]
                }, f, indent=2)
            paths["metadata"] = metadata_path
            
            # Save individual agent outputs as separate JSON files
            agents_dir = "data/scripts/agents"
            os.makedirs(agents_dir, exist_ok=True)
            
            # Save ADK Eighths Calculator output
            if "adk_eighths_calculator" in data["agent_outputs"]:
                eighths_path = f"{agents_dir}/adk_eighths_calculator_{timestamp}.json"
                with open(eighths_path, "w") as f:
                    json.dump(data["agent_outputs"]["adk_eighths_calculator"], f, indent=2)
                paths["adk_eighths_calculator"] = eighths_path
            
            # Save Scene Breakdown Cards output  
            if "scene_breakdown_cards" in data["agent_outputs"]:
                breakdown_path = f"{agents_dir}/adk_scene_breakdown_cards_{timestamp}.json"
                with open(breakdown_path, "w") as f:
                    json.dump(data["agent_outputs"]["scene_breakdown_cards"], f, indent=2)
                paths["adk_scene_breakdown_cards"] = breakdown_path
            
            # Save Department Coordinator output
            if "department_coordinator" in data["agent_outputs"]:
                dept_path = f"{agents_dir}/adk_department_coordinator_{timestamp}.json"
                with open(dept_path, "w") as f:
                    json.dump(data["agent_outputs"]["department_coordinator"], f, indent=2)
                paths["adk_department_coordinator"] = dept_path
            
            # Save all agent reports
            reports_dir = "data/scripts/reports"
            os.makedirs(reports_dir, exist_ok=True)
            
            # Save eighths report
            if "eighths_report" in data["metadata"]:
                report_path = f"{reports_dir}/eighths_report_{timestamp}.txt"
                with open(report_path, "w") as f:
                    f.write(data["metadata"]["eighths_report"])
                paths["eighths_report"] = report_path
            
            # Save breakdown cards as JSON
            if "breakdown_cards" in data["metadata"]:
                breakdown_path = f"{reports_dir}/breakdown_cards_{timestamp}.json"
                with open(breakdown_path, "w") as f:
                    json.dump(data["metadata"]["breakdown_cards"], f, indent=2)
                paths["breakdown_cards"] = breakdown_path
            
            # Save department analysis
            if "department_analysis" in data["metadata"]:
                dept_path = f"{reports_dir}/department_analysis_{timestamp}.json"
                with open(dept_path, "w") as f:
                    json.dump(data["metadata"]["department_analysis"], f, indent=2)
                paths["department_analysis"] = dept_path
            
            logger.info(f"Data saved successfully to {len(paths)} files")
            return paths
            
        except Exception as e:
            logger.error(f"Failed to save data to disk: {str(e)}")
            raise
    
    def _extract_text_from_pdf(self, pdf_bytes: bytes) -> str:
        """Extract text from PDF bytes with fallback methods.
        
        Args:
            pdf_bytes: PDF file content as bytes
            
        Returns:
            Extracted text from PDF
        """
        methods_tried = []
        
        # Method 1: PyPDF2 (primary)
        try:
            logger.info("Attempting PDF extraction with PyPDF2...")
            pdf_file = io.BytesIO(pdf_bytes)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            # Check if PDF is encrypted
            if pdf_reader.is_encrypted:
                logger.warning("PDF is encrypted, attempting to decrypt...")
                pdf_reader.decrypt("")  # Try empty password
            
            # Extract text from all pages
            text = ""
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                page_text = page.extract_text()
                if page_text.strip():  # Only add non-empty pages
                    text += f"\n=== PAGE {page_num + 1} ===\n"
                    text += page_text
                    text += "\n\n"
            
            if text.strip():
                logger.info(f"Successfully extracted text from {len(pdf_reader.pages)} PDF pages using PyPDF2")
                return text
            else:
                methods_tried.append("PyPDF2 (no text content)")
                
        except Exception as e:
            methods_tried.append(f"PyPDF2 ({str(e)})")
            logger.warning(f"PyPDF2 extraction failed: {str(e)}")
        
        # Method 2: Try pdfplumber (if available)
        try:
            import pdfplumber
            logger.info("Attempting PDF extraction with pdfplumber...")
            
            pdf_file = io.BytesIO(pdf_bytes)
            text = ""
            with pdfplumber.open(pdf_file) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    page_text = page.extract_text()
                    if page_text and page_text.strip():
                        text += f"\n=== PAGE {page_num + 1} ===\n"
                        text += page_text
                        text += "\n\n"
            
            if text.strip():
                logger.info(f"Successfully extracted text using pdfplumber")
                return text
            else:
                methods_tried.append("pdfplumber (no text content)")
                
        except ImportError:
            methods_tried.append("pdfplumber (not installed)")
            logger.info("pdfplumber not available")
        except Exception as e:
            methods_tried.append(f"pdfplumber ({str(e)})")
            logger.warning(f"pdfplumber extraction failed: {str(e)}")
        
        # Method 3: Try PyMuPDF (if available)
        try:
            import fitz  # PyMuPDF
            logger.info("Attempting PDF extraction with PyMuPDF...")
            
            pdf_file = io.BytesIO(pdf_bytes)
            doc = fitz.open(stream=pdf_file, filetype="pdf")
            text = ""
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                page_text = page.get_text()
                if page_text and page_text.strip():
                    text += f"\n=== PAGE {page_num + 1} ===\n"
                    text += page_text
                    text += "\n\n"
            
            doc.close()
            
            if text.strip():
                logger.info(f"Successfully extracted text using PyMuPDF")
                return text
            else:
                methods_tried.append("PyMuPDF (no text content)")
                
        except ImportError:
            methods_tried.append("PyMuPDF (not installed)")
            logger.info("PyMuPDF not available")
        except Exception as e:
            methods_tried.append(f"PyMuPDF ({str(e)})")
            logger.warning(f"PyMuPDF extraction failed: {str(e)}")
        
        # If all methods failed
        error_msg = f"Failed to extract text from PDF. Methods tried: {', '.join(methods_tried)}"
        logger.error(error_msg)
        raise ValueError(error_msg)
    
    def process_pdf_file(self, pdf_path: str, department_focus: Optional[list] = None, validation_level: str = "lenient") -> Dict[str, Any]:
        """Process a PDF script file.
        
        Args:
            pdf_path: Path to the PDF file
            department_focus: Optional list of departments to focus analysis on
            validation_level: Validation strictness ('strict' or 'lenient')
            
        Returns:
            Dict containing processed results from all 3 agents
        """
        try:
            # Read PDF file
            with open(pdf_path, 'rb') as f:
                pdf_bytes = f.read()
            
            logger.info(f"Read PDF file: {pdf_path}")
            
            # Process through the pipeline
            return self.process_script(
                script_input=pdf_bytes,
                input_type="pdf",
                department_focus=department_focus,
                validation_level=validation_level
            )
            
        except Exception as e:
            logger.error(f"Error processing PDF file: {str(e)}")
            raise