"""
One-Liner Generation Coordinator with 5 specialized sub-agents.
Agent 3: One-Liner Generation Coordinator
5 Sub-Agents: 1 Operational + 4 To Be Implemented
"""

import json
import os
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from .agents.story_analyzer_agent import StoryAnalyzerAgent
from .agents.pitch_specialist_agent import PitchSpecialistAgent
from .agents.marketing_strategist_agent import MarketingStrategistAgent
from .agents.genre_classifier_agent import GenreClassifierAgent
from .agents.audience_targeting_agent import AudienceTargetingAgent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class AgentConfig:
    """Configuration for individual agents."""
    name: str
    model: str
    description: str
    status: str  # "operational", "needs_implementation"
    capabilities: List[str]

class OneLinerCoordinator:
    """
    Agent 3: One-Liner Generation Coordinator
    Coordinates 5 specialized sub-agents for comprehensive one-liner generation.
    """
    
    def __init__(self):
        """Initialize the coordinator with all sub-agents."""
        self.agent_configs = {
            "story_analyzer": AgentConfig(
                name="StoryAnalyzerAgent",
                model="Gemini 2.5 Flash",
                description="Advanced narrative analysis with thinking capabilities",
                status="operational",
                capabilities=["PEFT recommended for genre patterns", "Foundational analysis"]
            ),
            "pitch_specialist": AgentConfig(
                name="PitchSpecialistAgent", 
                model="GPT-4.1 mini",
                description="Exceptional creative writing performance",
                status="needs_implementation",
                capabilities=["SFT on successful pitch datasets", "Logline generation"]
            ),
            "marketing_strategist": AgentConfig(
                name="MarketingStrategistAgent",
                model="Gemini 2.5 Flash", 
                description="Complex strategic planning capabilities",
                status="needs_implementation",
                capabilities=["Full fine-tuning for campaign optimization", "Campaign strategy"]
            ),
            "genre_classifier": AgentConfig(
                name="GenreClassifierAgent",
                model="Gemini 2.5 Flash",
                description="Excellent classification performance", 
                status="needs_implementation",
                capabilities=["PEFT for genre evolution patterns", "Positioning analysis"]
            ),
            "audience_targeting": AgentConfig(
                name="AudienceTargetingAgent",
                model="GPT-4.1 mini",
                description="Strong demographic analysis",
                status="needs_implementation", 
                capabilities=["SFT on audience behavior data", "Demographics analysis"]
            )
        }
        
        # Initialize agents
        self.story_analyzer = StoryAnalyzerAgent()
        self.pitch_specialist = PitchSpecialistAgent()
        self.marketing_strategist = MarketingStrategistAgent()
        self.genre_classifier = GenreClassifierAgent()
        self.audience_targeting = AudienceTargetingAgent()
        
        # Create data directory
        os.makedirs("data/one_liner", exist_ok=True)
        logger.info("Initialized OneLinerCoordinator with 5 sub-agents")
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Get the status of all sub-agents."""
        status = {
            "coordinator": "Agent 3: One-Liner Generation Coordinator",
            "total_agents": 5,
            "operational": 1,
            "needs_implementation": 4,
            "agents": {}
        }
        
        for agent_id, config in self.agent_configs.items():
            status["agents"][agent_id] = {
                "name": config.name,
                "model": config.model,
                "description": config.description,
                "status": config.status,
                "capabilities": config.capabilities,
                "status_indicator": "✅" if config.status == "operational" else "🚧"
            }
        
        return status
    
    async def generate_comprehensive_one_liner(self, script_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate comprehensive one-liner analysis using all sub-agents.
        
        Args:
            script_data: The script data to analyze
            
        Returns:
            Dict containing results from all sub-agents
        """
        try:
            logger.info("Starting comprehensive one-liner generation")
            
            # Initialize results structure
            results = {
                "timestamp": datetime.now().isoformat(),
                "coordinator_info": {
                    "name": "Agent 3: One-Liner Generation Coordinator",
                    "total_agents": 5,
                    "operational": 1,
                    "needs_implementation": 4
                },
                "agent_results": {},
                "combined_analysis": {},
                "status": "in_progress"
            }
            
            # 1. Story Analyzer Agent (OPERATIONAL)
            try:
                logger.info("Running StoryAnalyzerAgent...")
                story_analysis = await self.story_analyzer.analyze_story(script_data)
                results["agent_results"]["story_analyzer"] = {
                    "status": "✅ OPERATIONAL",
                    "model": "Gemini 2.5 Flash",
                    "data": story_analysis
                }
                logger.info("StoryAnalyzerAgent completed successfully")
            except Exception as e:
                logger.error(f"StoryAnalyzerAgent failed: {e}")
                results["agent_results"]["story_analyzer"] = {
                    "status": "❌ FAILED",
                    "error": str(e)
                }
            
            # 2. Pitch Specialist Agent (NEEDS IMPLEMENTATION)
            try:
                logger.info("Running PitchSpecialistAgent...")
                pitch_analysis = await self.pitch_specialist.generate_pitches(script_data)
                results["agent_results"]["pitch_specialist"] = {
                    "status": "🚧 NEEDS IMPLEMENTATION",
                    "model": "GPT-4.1 mini",
                    "data": pitch_analysis
                }
                logger.info("PitchSpecialistAgent completed")
            except Exception as e:
                logger.error(f"PitchSpecialistAgent failed: {e}")
                results["agent_results"]["pitch_specialist"] = {
                    "status": "❌ FAILED",
                    "error": str(e)
                }
            
            # 3. Marketing Strategist Agent (NEEDS IMPLEMENTATION)
            try:
                logger.info("Running MarketingStrategistAgent...")
                marketing_analysis = await self.marketing_strategist.generate_strategy(script_data)
                results["agent_results"]["marketing_strategist"] = {
                    "status": "🚧 NEEDS IMPLEMENTATION",
                    "model": "Gemini 2.5 Flash",
                    "data": marketing_analysis
                }
                logger.info("MarketingStrategistAgent completed")
            except Exception as e:
                logger.error(f"MarketingStrategistAgent failed: {e}")
                results["agent_results"]["marketing_strategist"] = {
                    "status": "❌ FAILED",
                    "error": str(e)
                }
            
            # 4. Genre Classifier Agent (NEEDS IMPLEMENTATION)
            try:
                logger.info("Running GenreClassifierAgent...")
                genre_analysis = await self.genre_classifier.classify_genre(script_data)
                results["agent_results"]["genre_classifier"] = {
                    "status": "🚧 NEEDS IMPLEMENTATION",
                    "model": "Gemini 2.5 Flash",
                    "data": genre_analysis
                }
                logger.info("GenreClassifierAgent completed")
            except Exception as e:
                logger.error(f"GenreClassifierAgent failed: {e}")
                results["agent_results"]["genre_classifier"] = {
                    "status": "❌ FAILED",
                    "error": str(e)
                }
            
            # 5. Audience Targeting Agent (NEEDS IMPLEMENTATION)
            try:
                logger.info("Running AudienceTargetingAgent...")
                audience_analysis = await self.audience_targeting.analyze_audience(script_data)
                results["agent_results"]["audience_targeting"] = {
                    "status": "🚧 NEEDS IMPLEMENTATION",
                    "model": "GPT-4.1 mini",
                    "data": audience_analysis
                }
                logger.info("AudienceTargetingAgent completed")
            except Exception as e:
                logger.error(f"AudienceTargetingAgent failed: {e}")
                results["agent_results"]["audience_targeting"] = {
                    "status": "❌ FAILED",
                    "error": str(e)
                }
            
            # Generate combined analysis
            results["combined_analysis"] = self._generate_combined_analysis(results["agent_results"])
            results["status"] = "completed"
            
            # Save results
            self._save_results(results)
            
            logger.info("Comprehensive one-liner generation completed")
            return results
            
        except Exception as e:
            logger.error(f"Error in comprehensive one-liner generation: {e}")
            return {
                "error": str(e),
                "status": "failed",
                "timestamp": datetime.now().isoformat()
            }
    
    def _generate_combined_analysis(self, agent_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate combined analysis from all agent results."""
        combined = {
            "executive_summary": {
                "one_liner_concepts": [],
                "key_themes": [],
                "target_audience": "To be determined",
                "genre_positioning": "To be determined",
                "marketing_hooks": []
            },
            "production_summary": {
                "story_essence": "Advanced narrative analysis pending",
                "marketability": "Campaign strategy pending",
                "audience_fit": "Demographic analysis pending",
                "genre_strength": "Classification pending"
            },
            "recommendations": {
                "primary_pitch": "Awaiting pitch specialist analysis",
                "secondary_pitches": [],
                "marketing_strategy": "Strategy development pending",
                "target_demographics": "Analysis pending"
            }
        }
        
        # Extract data from successful agents
        for agent_name, result in agent_results.items():
            if result.get("status") == "✅ OPERATIONAL" and "data" in result:
                data = result["data"]
                
                if agent_name == "story_analyzer":
                    combined["executive_summary"]["key_themes"] = data.get("story_elements", {}).get("themes", [])
                    combined["production_summary"]["story_essence"] = data.get("basic_pitches", ["Advanced narrative analysis complete"])[0]
        
        return combined
    
    def _save_results(self, results: Dict[str, Any]) -> None:
        """Save results to disk."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"data/one_liner/comprehensive_analysis_{timestamp}.json"
            
            with open(filename, 'w') as f:
                json.dump(results, f, indent=2)
            
            logger.info(f"Results saved to {filename}")
            
        except Exception as e:
            logger.error(f"Error saving results: {e}")
    
    async def generate_one_liner(self, script_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main entry point for one-liner generation (backward compatibility).
        
        Args:
            script_data: The script data to analyze
            
        Returns:
            Dict containing one-liner results
        """
        try:
            # Get comprehensive analysis
            comprehensive_results = await self.generate_comprehensive_one_liner(script_data)
            
            # Format for backward compatibility
            formatted_results = {
                "status": comprehensive_results.get("status", "completed"),
                "timestamp": comprehensive_results.get("timestamp"),
                "coordinator_info": comprehensive_results.get("coordinator_info"),
                "agent_status": self.get_agent_status(),
                "results": comprehensive_results.get("agent_results", {}),
                "combined_analysis": comprehensive_results.get("combined_analysis", {}),
                "formatted_text": self._format_for_ui(comprehensive_results)
            }
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error in one-liner generation: {e}")
            return {
                "error": str(e),
                "status": "failed",
                "timestamp": datetime.now().isoformat(),
                "formatted_text": f"Error: {str(e)}"
            }
    
    def _format_for_ui(self, results: Dict[str, Any]) -> str:
        """Format results for UI display."""
        output = []
        
        # Header
        output.append("AGENT 3: ONE-LINER GENERATION COORDINATOR")
        output.append("=" * 60)
        output.append(f"Generated: {results.get('timestamp', 'Unknown')}")
        output.append(f"Status: {results.get('status', 'Unknown')}")
        output.append("")
        
        # Agent Status
        output.append("SUB-AGENT STATUS:")
        output.append("-" * 30)
        
        agent_results = results.get("agent_results", {})
        for agent_name, result in agent_results.items():
            status = result.get("status", "Unknown")
            model = result.get("model", "Unknown")
            output.append(f"{agent_name}: {status} ({model})")
        
        output.append("")
        
        # Results from operational agents
        if "story_analyzer" in agent_results:
            story_data = agent_results["story_analyzer"].get("data", {})
            if story_data:
                output.append("STORY ANALYSIS RESULTS:")
                output.append("-" * 30)
                
                story_elements = story_data.get("story_elements", {})
                if story_elements:
                    output.append(f"Protagonist: {story_elements.get('protagonist', 'Unknown')}")
                    output.append(f"Conflict: {story_elements.get('central_conflict', 'Unknown')}")
                    output.append(f"Theme: {story_elements.get('theme', 'Unknown')}")
                    output.append(f"Setting: {story_elements.get('setting', 'Unknown')}")
                
                basic_pitches = story_data.get("basic_pitches", [])
                if basic_pitches:
                    output.append("\nBasic Pitches:")
                    for i, pitch in enumerate(basic_pitches, 1):
                        output.append(f"{i}. {pitch}")
                
                output.append("")
        
        # Implementation status
        output.append("IMPLEMENTATION STATUS:")
        output.append("-" * 30)
        output.append("✅ StoryAnalyzerAgent: OPERATIONAL")
        output.append("🚧 PitchSpecialistAgent: NEEDS IMPLEMENTATION")
        output.append("🚧 MarketingStrategistAgent: NEEDS IMPLEMENTATION") 
        output.append("🚧 GenreClassifierAgent: NEEDS IMPLEMENTATION")
        output.append("🚧 AudienceTargetingAgent: NEEDS IMPLEMENTATION")
        
        return "\n".join(output)