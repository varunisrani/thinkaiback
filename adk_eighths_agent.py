"""
Main ADK Agent Implementation for Eighths Calculator
Integrates all tool functions into a cohesive agent
"""

import os
import logging
from typing import Dict, Any, List
import google.generativeai as genai
from google.generativeai import types

# Import our tool functions
from adk_eighths_calculator import (
    determine_complexity_tool,
    calculate_single_scene_tool,
    calculate_scene_eighths_tool,
    generate_report_tool,
    EIGHTHS_CALCULATOR_INSTRUCTION,
    SceneData,
    ComplexityResult,
    SceneEighthsResult
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ADKEighthsCalculatorAgent:
    """
    Google ADK Implementation of EighthsCalculatorAgent
    Uses declarative tool functions instead of custom methods
    """
    
    def __init__(self):
        """Initialize the ADK agent with registered tools."""
        # Initialize Gemini client
        self.client = genai.Client(api_key=os.environ.get("GOOGLE_API_KEY"))
        
        # Register all tool functions
        self.tools = [
            register_tool(determine_complexity_tool),
            register_tool(calculate_single_scene_tool),
            register_tool(calculate_scene_eighths_tool),
            register_tool(generate_report_tool)
        ]
        
        # Model configuration
        self.model_config = types.GenerateContentConfig(
            temperature=0.1,  # Low temperature for consistent calculations
            top_p=0.95,
            top_k=20,
            max_output_tokens=8192,
            response_mime_type="application/json",
            response_schema={
                "type": "object",
                "properties": {
                    "status": {"type": "string"},
                    "message": {"type": "string"},
                    "eighths_data": {"type": "object"},
                    "report": {"type": "string"}
                }
            }
        )
        
        logger.info("ADKEighthsCalculatorAgent initialized with tools")
    
    def process_script_scenes(self, scenes_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Process script scenes using ADK tools to calculate eighths.
        
        Args:
            scenes_data: List of scene dictionaries
            
        Returns:
            Dictionary with eighths calculations and report
        """
        logger.info(f"Processing {len(scenes_data)} scenes with ADK agent")
        
        # Create the prompt for the agent
        prompt = f"""You are an eighths calculator agent. Process the following scenes and calculate eighths breakdown.

Use the tools in this order:
1. First use calculate_scene_eighths_tool with all the scenes data
2. Then use generate_report_tool with the eighths data

Scenes data:
{scenes_data}

Return a JSON object with:
- status: "success" or "error"
- message: Brief description
- eighths_data: The complete eighths calculation data
- report: The formatted text report
"""
        
        try:
            # Create chat session with tools
            chat = self.client.chats.create(
                model="gemini-2.0-flash-exp",
                config=self.model_config,
                tools=self.tools,
                system_instruction=EIGHTHS_CALCULATOR_INSTRUCTION
            )
            
            # Send the prompt
            response = chat.send_message(prompt)
            
            # Parse the response
            result = self._parse_response(response)
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing scenes: {e}")
            return {
                "status": "error",
                "message": str(e),
                "eighths_data": {},
                "report": ""
            }
    
    def process_single_scene(self, scene_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a single scene for detailed eighths calculation.
        
        Args:
            scene_data: Single scene dictionary
            
        Returns:
            Detailed eighths breakdown for the scene
        """
        logger.info(f"Processing single scene: {scene_data.get('scene_number', 'Unknown')}")
        
        prompt = f"""Calculate detailed eighths for this single scene.

Use the tools in this order:
1. First use determine_complexity_tool to calculate complexity
2. Then use calculate_single_scene_tool with the complexity result

Scene data:
{scene_data}

Assume page count is calculated from description length (250 words = 1 page).

Return a JSON object with:
- status: "success" or "error"
- scene_eighths: The scene eighths calculation
- complexity: The complexity calculation
- summary: Brief text summary
"""
        
        try:
            chat = self.client.chats.create(
                model="gemini-2.0-flash-exp",
                config=self.model_config,
                tools=self.tools,
                system_instruction=EIGHTHS_CALCULATOR_INSTRUCTION
            )
            
            response = chat.send_message(prompt)
            result = self._parse_response(response)
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing single scene: {e}")
            return {
                "status": "error",
                "message": str(e),
                "scene_eighths": {},
                "complexity": {},
                "summary": ""
            }
    
    def generate_comparison_report(self, original_data: Dict[str, Any], adk_data: Dict[str, Any]) -> str:
        """
        Generate a comparison report between original and ADK calculations.
        
        Args:
            original_data: Results from original agent
            adk_data: Results from ADK agent
            
        Returns:
            Formatted comparison report
        """
        report = []
        report.append("=" * 80)
        report.append("COMPARISON REPORT: Original vs ADK Implementation")
        report.append("=" * 80)
        
        # Compare totals
        orig_totals = original_data.get("totals", {})
        adk_totals = adk_data.get("eighths_data", {}).get("totals", {})
        
        report.append("\nTOTALS COMPARISON:")
        report.append("-" * 40)
        report.append(f"Total Scenes:")
        report.append(f"  Original: {orig_totals.get('total_scenes', 'N/A')}")
        report.append(f"  ADK:      {adk_totals.get('total_scenes', 'N/A')}")
        
        report.append(f"\nTotal Script Eighths:")
        report.append(f"  Original: {orig_totals.get('total_script_eighths', 'N/A')}")
        report.append(f"  ADK:      {adk_totals.get('total_script_eighths', 'N/A')}")
        
        report.append(f"\nEstimated Shoot Days:")
        report.append(f"  Original: {orig_totals.get('estimated_shoot_days', 'N/A')}")
        report.append(f"  ADK:      {adk_totals.get('estimated_shoot_days', 'N/A')}")
        
        report.append("\n" + "=" * 80)
        
        return "\n".join(report)
    
    def _parse_response(self, response) -> Dict[str, Any]:
        """Parse the agent response into structured data."""
        try:
            # Try to extract JSON from response
            if hasattr(response, 'text'):
                import json
                return json.loads(response.text)
            elif hasattr(response, 'candidates') and response.candidates:
                # Handle structured response
                candidate = response.candidates[0]
                if hasattr(candidate.content, 'parts') and candidate.content.parts:
                    text = candidate.content.parts[0].text
                    return json.loads(text)
            
            # Fallback
            return {
                "status": "error",
                "message": "Could not parse response",
                "eighths_data": {},
                "report": str(response)
            }
            
        except Exception as e:
            logger.error(f"Error parsing response: {e}")
            return {
                "status": "error",
                "message": str(e),
                "eighths_data": {},
                "report": ""
            }

# Utility function to create agent instance
def create_adk_eighths_agent() -> ADKEighthsCalculatorAgent:
    """Factory function to create an ADK eighths calculator agent."""
    return ADKEighthsCalculatorAgent()