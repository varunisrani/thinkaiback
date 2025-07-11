import os
import json
import logging
from typing import Dict, Any, List
from datetime import datetime
from .agents.character_parser_agent import CharacterParserAgent
from .agents.dialogue_profiler_agent import DialogueProfilerAgent
from .agents.casting_director_agent import CastingDirectorAgent
from .agents.relationship_mapper_agent import RelationshipMapperAgent
from .agents.actor_scheduler_agent import ActorSchedulerAgent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CharacterBreakdownCoordinator:
    """
    👤 Agent 2: Character Breakdown Coordinator (Main Orchestrator)
    
    Coordinates 5 specialized sub-agents:
    ├── 👤 CharacterParserAgent (FOUNDATIONAL)
    ├── 👤 DialogueProfilerAgent (SPEECH ANALYSIS)
    ├── 👤 CastingDirectorAgent (GA BREAKDOWN)
    ├── 👤 RelationshipMapperAgent (CHARACTER DYNAMICS)
    └── 👤 ActorSchedulerAgent (DOOP REPORTS)
    """
    
    def __init__(self, data_dir: str = "data"):
        """Initialize the coordinator with 5 specialized agents and data paths."""
        logger.info("Initializing CharacterBreakdownCoordinator with 5 specialized agents")
        
        self.data_dir = data_dir
        
        # Initialize all 5 specialized agents
        self.character_parser = CharacterParserAgent()
        self.dialogue_profiler = DialogueProfilerAgent()
        self.casting_director = CastingDirectorAgent()
        self.relationship_mapper = RelationshipMapperAgent()
        self.actor_scheduler = ActorSchedulerAgent()
        
        # Ensure required directories exist
        self.character_data_dir = os.path.join(data_dir, "character_profiles")
        self.relationship_data_dir = os.path.join(data_dir, "relationship_maps")
        self.scene_data_dir = os.path.join(data_dir, "scene_matrices")
        self.casting_data_dir = os.path.join(data_dir, "casting_breakdowns")
        self.scheduling_data_dir = os.path.join(data_dir, "actor_schedules")
        
        for directory in [self.character_data_dir, self.relationship_data_dir, 
                         self.scene_data_dir, self.casting_data_dir, self.scheduling_data_dir]:
            os.makedirs(directory, exist_ok=True)
        
        logger.info("All 5 specialized agents initialized successfully")
        logger.info("CharacterBreakdownCoordinator initialization complete")
    
    async def process_character_breakdown(self, script_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process character breakdown analysis through 5-agent pipeline."""
        logger.info("Starting 5-agent character breakdown processing pipeline")
        processing_start = datetime.now()
        
        try:
            # Initialize processing status
            processing_status = {
                "started_at": processing_start.isoformat(),
                "current_stage": "character_parsing",
                "completed_stages": [],
                "errors": [],
                "warnings": [],
                "agents_used": ["CharacterParserAgent", "DialogueProfilerAgent", 
                               "CastingDirectorAgent", "RelationshipMapperAgent", 
                               "ActorSchedulerAgent"]
            }
            
            # 👤 STAGE 1: Character Parsing (FOUNDATIONAL)
            logger.info("👤 Stage 1: Character Parsing with CharacterParserAgent")
            try:
                character_data = self.character_parser.parse_characters(script_data)
                if "error" in character_data:
                    raise ValueError(f"Character parsing failed: {character_data['error']}")
                
                processing_status["completed_stages"].append({
                    "stage": "character_parsing",
                    "agent": "CharacterParserAgent",
                    "completed_at": datetime.now().isoformat(),
                    "success": True
                })
                logger.info("✅ Character parsing completed successfully")
            except Exception as e:
                logger.error(f"❌ Error in character parsing stage: {str(e)}")
                processing_status["errors"].append({
                    "stage": "character_parsing",
                    "agent": "CharacterParserAgent",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                })
                raise
            
            # 👤 STAGE 2: Dialogue Profiling (SPEECH ANALYSIS)
            logger.info("👤 Stage 2: Dialogue Profiling with DialogueProfilerAgent")
            processing_status["current_stage"] = "dialogue_profiling"
            try:
                dialogue_data = self.dialogue_profiler.profile_dialogue(script_data, character_data)
                if "error" in dialogue_data:
                    raise ValueError(f"Dialogue profiling failed: {dialogue_data['error']}")
                
                processing_status["completed_stages"].append({
                    "stage": "dialogue_profiling",
                    "agent": "DialogueProfilerAgent",
                    "completed_at": datetime.now().isoformat(),
                    "success": True
                })
                logger.info("✅ Dialogue profiling completed successfully")
            except Exception as e:
                logger.error(f"❌ Error in dialogue profiling stage: {str(e)}")
                processing_status["errors"].append({
                    "stage": "dialogue_profiling",
                    "agent": "DialogueProfilerAgent",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                })
                # Continue with fallback data
                dialogue_data = {"error": str(e)}
            
            # 👤 STAGE 3: Casting Analysis (GA BREAKDOWN)
            logger.info("👤 Stage 3: Casting Analysis with CastingDirectorAgent")
            processing_status["current_stage"] = "casting_analysis"
            try:
                casting_data = self.casting_director.analyze_casting_requirements(script_data, character_data)
                if "error" in casting_data:
                    raise ValueError(f"Casting analysis failed: {casting_data['error']}")
                
                processing_status["completed_stages"].append({
                    "stage": "casting_analysis",
                    "agent": "CastingDirectorAgent",
                    "completed_at": datetime.now().isoformat(),
                    "success": True
                })
                logger.info("✅ Casting analysis completed successfully")
            except Exception as e:
                logger.error(f"❌ Error in casting analysis stage: {str(e)}")
                processing_status["errors"].append({
                    "stage": "casting_analysis",
                    "agent": "CastingDirectorAgent",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                })
                casting_data = {"error": str(e)}
            
            # 👤 STAGE 4: Relationship Mapping (CHARACTER DYNAMICS)
            logger.info("👤 Stage 4: Relationship Mapping with RelationshipMapperAgent")
            processing_status["current_stage"] = "relationship_mapping"
            try:
                relationship_data = self.relationship_mapper.map_relationships(script_data, character_data)
                if "error" in relationship_data:
                    raise ValueError(f"Relationship mapping failed: {relationship_data['error']}")
                
                processing_status["completed_stages"].append({
                    "stage": "relationship_mapping",
                    "agent": "RelationshipMapperAgent",
                    "completed_at": datetime.now().isoformat(),
                    "success": True
                })
                logger.info("✅ Relationship mapping completed successfully")
            except Exception as e:
                logger.error(f"❌ Error in relationship mapping stage: {str(e)}")
                processing_status["errors"].append({
                    "stage": "relationship_mapping",
                    "agent": "RelationshipMapperAgent",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                })
                relationship_data = {"error": str(e)}
            
            # 👤 STAGE 5: Actor Scheduling (DOOP REPORTS)
            logger.info("👤 Stage 5: Actor Scheduling with ActorSchedulerAgent")
            processing_status["current_stage"] = "actor_scheduling"
            try:
                scheduling_data = self.actor_scheduler.generate_actor_schedule(script_data, character_data, casting_data)
                if "error" in scheduling_data:
                    raise ValueError(f"Actor scheduling failed: {scheduling_data['error']}")
                
                processing_status["completed_stages"].append({
                    "stage": "actor_scheduling",
                    "agent": "ActorSchedulerAgent",
                    "completed_at": datetime.now().isoformat(),
                    "success": True
                })
                logger.info("✅ Actor scheduling completed successfully")
            except Exception as e:
                logger.error(f"❌ Error in actor scheduling stage: {str(e)}")
                processing_status["errors"].append({
                    "stage": "actor_scheduling",
                    "agent": "ActorSchedulerAgent",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                })
                scheduling_data = {"error": str(e)}
            
            # 👤 STAGE 6: Data Integration and Finalization
            logger.info("🎯 Stage 6: Integrating all agent outputs")
            processing_status["current_stage"] = "data_integration"
            
            # Create comprehensive result structure
            result = {
                "character_data": character_data,
                "dialogue_analysis": dialogue_data,
                "casting_breakdown": casting_data,
                "relationship_mapping": relationship_data,
                "actor_scheduling": scheduling_data,
                "integrated_analysis": self._integrate_character_analysis(
                    character_data, dialogue_data, casting_data, relationship_data, scheduling_data),
                "agent_outputs": {
                    "character_parser": character_data,
                    "dialogue_profiler": dialogue_data,
                    "casting_director": casting_data,
                    "relationship_mapper": relationship_data,
                    "actor_scheduler": scheduling_data
                },
                "processing_status": processing_status,
                "statistics": self._generate_comprehensive_statistics(
                    character_data, dialogue_data, casting_data, relationship_data, scheduling_data),
                "ui_metadata": self._generate_ui_metadata(
                    character_data, dialogue_data, casting_data, relationship_data, scheduling_data)
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
            
            logger.info("🎉 5-agent character breakdown processing completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"❌ 5-agent character breakdown processing failed: {str(e)}", exc_info=True)
            if processing_status:
                processing_status["current_stage"] = "failed"
                processing_status["failed_at"] = datetime.now().isoformat()
                processing_status["final_error"] = str(e)
            
            return {
                "error": str(e),
                "status": "failed",
                "processing_status": processing_status
            }
    
    def _integrate_character_analysis(self, character_data: Dict[str, Any],
                                    dialogue_data: Dict[str, Any],
                                    casting_data: Dict[str, Any],
                                    relationship_data: Dict[str, Any],
                                    scheduling_data: Dict[str, Any]) -> Dict[str, Any]:
        """Integrate analysis from all 5 agents into unified character profiles."""
        integrated_analysis = {
            "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "agent_integration": "5-agent specialized pipeline",
            "character_profiles": {},
            "production_summary": {},
            "casting_summary": {},
            "scheduling_summary": {}
        }
        
        # Get character list from character parser
        characters = character_data.get("characters", [])
        
        # Build integrated character profiles
        for char in characters:
            char_name = char.get("name", "")
            
            # Extract data from each agent
            casting_info = self._extract_character_casting_info(char_name, casting_data)
            dialogue_info = self._extract_character_dialogue_info(char_name, dialogue_data)
            relationship_info = self._extract_character_relationship_info(char_name, relationship_data)
            scheduling_info = self._extract_character_scheduling_info(char_name, scheduling_data)
            
            integrated_analysis["character_profiles"][char_name] = {
                # Foundational data from CharacterParserAgent
                "basic_info": {
                    "name": char_name,
                    "first_appearance": char.get("first_appearance"),
                    "total_scenes": char.get("total_scenes"),
                    "dialogue_count": char.get("dialogue_count"),
                    "scene_numbers": char.get("scene_numbers", [])
                },
                
                # Speech analysis from DialogueProfilerAgent
                "dialogue_profile": dialogue_info,
                
                # Casting breakdown from CastingDirectorAgent
                "casting_info": casting_info,
                
                # Relationship dynamics from RelationshipMapperAgent
                "relationships": relationship_info,
                
                # Scheduling from ActorSchedulerAgent
                "scheduling": scheduling_info
            }
        
        # Generate production summaries
        integrated_analysis["production_summary"] = self._generate_production_summary(
            characters, casting_data, scheduling_data)
        
        return integrated_analysis
    
    def _extract_character_casting_info(self, char_name: str, casting_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract casting info for a specific character."""
        casting_categories = casting_data.get("casting_categories", {})
        audition_requirements = casting_data.get("audition_requirements", {})
        
        # Find character in casting categories
        casting_info = {"category": "Background", "requirements": {}}
        
        for category, actors in casting_categories.items():
            for actor_info in actors:
                if actor_info.get("character") == char_name:
                    casting_info = {
                        "category": actor_info.get("category", category),
                        "union_status": actor_info.get("union_status"),
                        "day_rate_range": actor_info.get("day_rate_range"),
                        "estimated_shoot_days": actor_info.get("estimated_shoot_days"),
                        "contract_type": actor_info.get("contract_type")
                    }
                    break
        
        # Add audition requirements
        if char_name in audition_requirements:
            casting_info["audition_requirements"] = audition_requirements[char_name]
        
        return casting_info
    
    def _extract_character_dialogue_info(self, char_name: str, dialogue_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract dialogue analysis for a specific character."""
        voice_profiles = dialogue_data.get("voice_profiles", {})
        return voice_profiles.get(char_name, {})
    
    def _extract_character_relationship_info(self, char_name: str, relationship_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract relationship info for a specific character."""
        relationship_network = relationship_data.get("relationship_network", {})
        character_arcs = relationship_data.get("character_arcs", {})
        
        # Find relationships involving this character
        character_relationships = {}
        for rel_type, relationships in relationship_network.items():
            char_relationships = []
            for relationship in relationships:
                if len(relationship) >= 2 and char_name in relationship[:2]:
                    other_char = relationship[1] if relationship[0] == char_name else relationship[0]
                    char_relationships.append(other_char)
            if char_relationships:
                character_relationships[rel_type] = char_relationships
        
        return {
            "relationships": character_relationships,
            "character_arc": character_arcs.get(char_name, {})
        }
    
    def _extract_character_scheduling_info(self, char_name: str, scheduling_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract scheduling info for a specific character."""
        doop_reports = scheduling_data.get("doop_reports", {})
        return doop_reports.get(char_name, {})
    
    def _generate_production_summary(self, characters: List[Dict[str, Any]], 
                                   casting_data: Dict[str, Any],
                                   scheduling_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate overall production summary."""
        return {
            "total_characters": len(characters),
            "total_speaking_characters": sum(1 for char in characters if char.get("dialogue_count", 0) > 0),
            "casting_budget_estimate": casting_data.get("budget_estimates", {}).get("total_estimated_cost", 0),
            "total_actor_days": scheduling_data.get("cost_analysis", {}).get("total_actor_days", 0),
            "scheduling_efficiency": "High" if len(scheduling_data.get("availability_conflicts", [])) < 3 else "Medium"
        }
    
    def _generate_comprehensive_statistics(self, character_data: Dict[str, Any],
                                         dialogue_data: Dict[str, Any],
                                         casting_data: Dict[str, Any],
                                         relationship_data: Dict[str, Any],
                                         scheduling_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive statistics from all agent outputs."""
        stats = {
            "agent_summary": {
                "total_agents": 5,
                "successful_agents": sum(1 for data in [character_data, dialogue_data, 
                                                      casting_data, relationship_data, scheduling_data] 
                                       if "error" not in data)
            }
        }
        
        # Character statistics
        characters = character_data.get("characters", [])
        stats["character_stats"] = {
            "total_characters": len(characters),
            "speaking_characters": sum(1 for char in characters if char.get("dialogue_count", 0) > 0),
            "main_characters": sum(1 for char in characters if char.get("total_scenes", 0) > 5)
        }
        
        # Casting statistics
        if "casting_categories" in casting_data:
            casting_categories = casting_data["casting_categories"]
            stats["casting_stats"] = {
                "lead_cast": len(casting_categories.get("lead_cast", [])),
                "supporting_cast": len(casting_categories.get("supporting_lead", [])),
                "total_estimated_cost": casting_data.get("budget_estimates", {}).get("total_estimated_cost", 0)
            }
        
        # Relationship statistics
        if "relationship_network" in relationship_data:
            network = relationship_data["relationship_network"]
            stats["relationship_stats"] = {
                "total_relationships": sum(len(relationships) for relationships in network.values()),
                "relationship_types": len([k for k, v in network.items() if v])
            }
        
        # Scheduling statistics
        if "doop_reports" in scheduling_data:
            doop_reports = scheduling_data["doop_reports"]
            stats["scheduling_stats"] = {
                "total_actors_scheduled": len(doop_reports),
                "average_efficiency": round(sum(doop.get("scheduling_efficiency", 0) for doop in doop_reports.values()) / len(doop_reports), 1) if doop_reports else 0,
                "total_conflicts": len(scheduling_data.get("availability_conflicts", []))
            }
        
        return stats
    
    def _generate_ui_metadata(self, character_data: Dict[str, Any],
                            dialogue_data: Dict[str, Any],
                            casting_data: Dict[str, Any],
                            relationship_data: Dict[str, Any],
                            scheduling_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate metadata specifically for UI rendering."""
        ui_metadata = {
            "agent_status": {
                "character_parser": "error" not in character_data,
                "dialogue_profiler": "error" not in dialogue_data,
                "casting_director": "error" not in casting_data,
                "relationship_mapper": "error" not in relationship_data,
                "actor_scheduler": "error" not in scheduling_data
            },
            "dashboard_summary": {},
            "visualization_data": {}
        }
        
        # Dashboard summary
        characters = character_data.get("characters", [])
        ui_metadata["dashboard_summary"] = {
            "total_characters": len(characters),
            "agents_completed": sum(ui_metadata["agent_status"].values()),
            "processing_complete": all(ui_metadata["agent_status"].values())
        }
        
        # Visualization data for charts
        if "casting_categories" in casting_data:
            ui_metadata["visualization_data"]["casting_breakdown"] = {
                category: len(actors) for category, actors in casting_data["casting_categories"].items()
            }
        
        return ui_metadata
    
    def _save_to_disk(self, data: Dict[str, Any]) -> Dict[str, str]:
        """Save processed data to disk in organized structure."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            paths = {}
            
            # Save main data with agent outputs
            main_path = os.path.join(self.data_dir, f"character_breakdown_{timestamp}.json")
            with open(main_path, "w") as f:
                json.dump({
                    "character_data": data["character_data"],
                    "processing_status": data["processing_status"],
                    "statistics": data["statistics"],
                    "agent_outputs": data["agent_outputs"]
                }, f, indent=2)
            paths["main"] = main_path
            
            # Save integrated analysis
            integrated_path = os.path.join(self.data_dir, f"integrated_analysis_{timestamp}.json")
            with open(integrated_path, "w") as f:
                json.dump({
                    "integrated_analysis": data["integrated_analysis"],
                    "ui_metadata": data["ui_metadata"]
                }, f, indent=2)
            paths["integrated"] = integrated_path
            
            # Save individual agent outputs
            agents_path = os.path.join(self.data_dir, f"character_agents_{timestamp}.json")
            with open(agents_path, "w") as f:
                json.dump(data["agent_outputs"], f, indent=2)
            paths["agents"] = agents_path
            
            logger.info(f"Character breakdown data saved successfully to {len(paths)} files")
            return paths
            
        except Exception as e:
            logger.error(f"Failed to save character breakdown data to disk: {str(e)}")
            raise
    
    # Legacy method for backward compatibility
    async def process_script(self, script_data: Dict[str, Any]) -> Dict[str, Any]:
        """Legacy method - redirects to process_character_breakdown."""
        return await self.process_character_breakdown(script_data)