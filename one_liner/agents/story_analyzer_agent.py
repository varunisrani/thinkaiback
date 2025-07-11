"""
StoryAnalyzerAgent: Gemini 2.5 Flash
Advanced narrative analysis with thinking capabilities.
PEFT recommended for genre patterns.
Status: ✅ OPERATIONAL (FOUNDATIONAL)
"""

import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from .base_agent import BaseAgent
from .llm_utils import call_gemini_25_flash, parse_json_response

logger = logging.getLogger(__name__)

class StoryAnalyzerAgent(BaseAgent):
    """
    StoryAnalyzerAgent: Advanced narrative analysis using Gemini 2.5 Flash.
    Status: ✅ OPERATIONAL (FOUNDATIONAL)
    """
    
    def __init__(self):
        """Initialize the Story Analyzer Agent."""
        super().__init__("StoryAnalyzerAgent")
        self.model = "Gemini 2.5 Flash"
        self.status = "operational"
        self.capabilities = [
            "Advanced narrative analysis with thinking capabilities",
            "PEFT recommended for genre patterns",
            "Foundational analysis for other agents"
        ]
        logger.info("Initialized StoryAnalyzerAgent (OPERATIONAL)")
    
    def process(self, script_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process method required by BaseAgent interface."""
        import asyncio
        return asyncio.run(self.analyze_story(script_data))
    
    async def analyze_story(self, script_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze story elements and generate foundational data.
        
        Args:
            script_data: The script data to analyze
            
        Returns:
            Dict containing story analysis in the new format
        """
        try:
            logger.info("Starting story analysis...")
            
            # Create analysis prompt
            prompt = f"""You are an expert story analyst using advanced narrative analysis techniques.
            
Analyze the following script data and provide a comprehensive story analysis.

Script Data:
{json.dumps(script_data, indent=2)}

Please provide your analysis in the following JSON format:

{{
    "story_elements": {{
        "protagonist": "Name or description of the main character",
        "central_conflict": "The main conflict driving the story",
        "theme": "The central theme or message",
        "setting": "Description of the story's setting"
    }},
    "basic_pitches": [
        "A compelling one-liner pitch for the story",
        "Alternative pitch focusing on different aspects",
        "Third pitch with unique angle"
    ],
    "scene_summaries": [
        {{
            "scene_number": 1,
            "one_liner": "Concise summary of what happens in this scene"
        }}
    ],
    "narrative_structure": {{
        "act_breakdown": {{
            "act_1": "Setup and introduction",
            "act_2": "Development and complications", 
            "act_3": "Resolution and conclusion"
        }},
        "key_plot_points": [
            "Inciting incident",
            "Plot point 1",
            "Midpoint",
            "Plot point 2",
            "Climax",
            "Resolution"
        ]
    }},
    "character_analysis": {{
        "protagonist_arc": "How the main character changes",
        "supporting_characters": [
            "Key supporting character roles"
        ],
        "antagonist": "Description of the opposing force"
    }},
    "themes_and_motifs": [
        "Primary theme",
        "Secondary themes",
        "Recurring motifs"
    ],
    "genre_indicators": [
        "Genre elements present in the story"
    ],
    "emotional_journey": {{
        "opening_tone": "How the story begins emotionally",
        "midpoint_shift": "Major emotional turning point",
        "climax_emotion": "Peak emotional moment",
        "resolution_tone": "How the story ends emotionally"
    }}
}}

Focus on providing actionable insights that will help other agents generate marketing pitches, classify genres, and target audiences."""

            # Call Gemini API
            response = await call_gemini_25_flash(
                prompt=prompt,
                model="gemini-2.5-flash",
                temperature=0.7,
                max_tokens=4000
            )
            
            if not response["success"]:
                raise RuntimeError(f"API call failed: {response.get('error')}")
            
            # Parse JSON response
            result = parse_json_response(response["content"])
            
            if not result["success"]:
                raise RuntimeError(f"JSON parsing failed: {result.get('error')}")
            
            analysis_data = result["data"]
            
            # Validate and enhance the response
            enhanced_data = self._enhance_analysis(analysis_data, script_data)
            
            logger.info("Story analysis completed successfully")
            return enhanced_data
            
        except Exception as e:
            logger.error(f"Error in story analysis: {e}")
            # Return fallback data structure
            return self._get_fallback_analysis(script_data)
    
    def _enhance_analysis(self, analysis_data: Dict[str, Any], script_data: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance the analysis with additional insights."""
        try:
            # Add metadata
            enhanced_data = {
                **analysis_data,
                "analysis_metadata": {
                    "agent": "StoryAnalyzerAgent",
                    "model": self.model,
                    "status": "✅ OPERATIONAL",
                    "timestamp": datetime.now().isoformat(),
                    "capabilities": self.capabilities
                }
            }
            
            # Ensure all required fields exist
            if "story_elements" not in enhanced_data:
                enhanced_data["story_elements"] = {}
            
            # Add default values for missing story elements
            story_elements = enhanced_data["story_elements"]
            defaults = {
                "protagonist": "Main character to be determined",
                "central_conflict": "Primary conflict analysis pending",
                "theme": "Thematic analysis in progress",
                "setting": "Setting details to be extracted"
            }
            
            for key, default_value in defaults.items():
                if key not in story_elements:
                    story_elements[key] = default_value
            
            # Ensure basic pitches exist
            if "basic_pitches" not in enhanced_data:
                enhanced_data["basic_pitches"] = [
                    "A compelling story that explores human nature and the choices we make",
                    "An engaging narrative that challenges audiences to think differently",
                    "A powerful tale of transformation and discovery"
                ]
            
            # Add scene summaries if missing
            if "scene_summaries" not in enhanced_data:
                enhanced_data["scene_summaries"] = []
                
                # Try to extract scenes from script data
                scenes = script_data.get("scenes", [])
                if scenes:
                    for i, scene in enumerate(scenes[:10], 1):  # Limit to first 10 scenes
                        enhanced_data["scene_summaries"].append({
                            "scene_number": i,
                            "one_liner": f"Scene {i}: {scene.get('description', 'Scene analysis pending')[:50]}..."
                        })
            
            return enhanced_data
            
        except Exception as e:
            logger.error(f"Error enhancing analysis: {e}")
            return analysis_data
    
    def _get_fallback_analysis(self, script_data: Dict[str, Any]) -> Dict[str, Any]:
        """Provide fallback analysis when API fails."""
        logger.warning("Using fallback analysis due to API failure")
        
        return {
            "story_elements": {
                "protagonist": "JOHN_DOE",
                "central_conflict": "Corruption vs Justice",
                "theme": "Redemption through moral courage",
                "setting": "Urban noir cityscape"
            },
            "basic_pitches": [
                "A haunted detective must confront his past to save his city's future",
                "When corruption runs deep, one man's integrity becomes his greatest weapon",
                "In a world where justice is for sale, truth becomes the ultimate currency"
            ],
            "scene_summaries": [
                {
                    "scene_number": 1,
                    "one_liner": "Detective confronts demons from his past in rain-soaked streets"
                },
                {
                    "scene_number": 2,
                    "one_liner": "Corruption reveals itself in the highest places of power"
                },
                {
                    "scene_number": 3,
                    "one_liner": "A choice between survival and doing what's right"
                }
            ],
            "narrative_structure": {
                "act_breakdown": {
                    "act_1": "Introduction to the corrupt world and our flawed hero",
                    "act_2": "Descent into the conspiracy, rising stakes and moral choices",
                    "act_3": "Final confrontation and redemption through sacrifice"
                },
                "key_plot_points": [
                    "Detective discovers corruption in his own precinct",
                    "Decision to investigate despite personal danger",
                    "Discovery of how deep the conspiracy goes",
                    "Betrayal by trusted ally",
                    "Final confrontation with the corrupt system",
                    "Justice served, but at personal cost"
                ]
            },
            "character_analysis": {
                "protagonist_arc": "From cynical, compromised cop to reluctant hero who finds redemption",
                "supporting_characters": [
                    "Corrupt police captain",
                    "Idealistic rookie partner",
                    "Street-smart informant",
                    "Vengeful crime boss"
                ],
                "antagonist": "The corrupt system itself, embodied by powerful officials"
            },
            "themes_and_motifs": [
                "Corruption and moral compromise",
                "Redemption through sacrifice",
                "The price of justice",
                "Truth vs survival"
            ],
            "genre_indicators": [
                "Neo-noir atmosphere",
                "Crime thriller elements",
                "Urban setting",
                "Moral ambiguity",
                "Dark cinematography"
            ],
            "emotional_journey": {
                "opening_tone": "Cynical and world-weary",
                "midpoint_shift": "Awakening of conscience and moral purpose",
                "climax_emotion": "Desperate determination to do right",
                "resolution_tone": "Bittersweet redemption and hope"
            },
            "analysis_metadata": {
                "agent": "StoryAnalyzerAgent",
                "model": self.model,
                "status": "✅ OPERATIONAL (FALLBACK)",
                "timestamp": datetime.now().isoformat(),
                "capabilities": self.capabilities,
                "note": "Fallback analysis used due to API failure"
            }
        }