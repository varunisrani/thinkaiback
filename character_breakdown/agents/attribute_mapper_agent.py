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

class AttributeMapperAgent:
    def __init__(self):
        self.client = genai.Client(api_key=os.environ.get("GOOGLE_API_KEY"))
        self.model_config = get_model_config()
        self.instructions = AGENT_INSTRUCTIONS["attribute_mapper"]
        logger.info("Initialized AttributeMapperAgent")
    
    def _clean_response(self, response: str) -> str:
        """Clean and extract JSON from text response, handling various formats."""
        import re
        
        # First, try to find JSON between triple backticks
        matches = re.findall(r'```(?:json)?\s*(\{\s*.*?\s*\})\s*```', response, re.DOTALL)
        if matches:
            return matches[0]
        
        # Then try to find JSON between single backticks
        matches = re.findall(r'`(\{\s*.*?\s*\})`', response, re.DOTALL)
        if matches:
            return matches[0]
        
        # Try to find the largest JSON object in the response
        matches = re.findall(r'(\{[\s\S]*\})', response)
        if matches:
            # Sort by length and take the longest (most complete) JSON
            longest_match = max(matches, key=len)
            return longest_match
        
        # If no JSON objects found, try to clean basic markdown
        response = response.strip()
        if response.startswith("```json"):
            response = response[7:]
        elif response.startswith("```"):
            response = response[3:]
        if response.endswith("```"):
            response = response[:-3]
        
        return response.strip()
    
    async def map_attributes(
        self,
        character_analysis: Dict[str, Any],
        scene_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Map physical attributes and track character evolution."""
        # Define expected JSON format
        json_format = '''
{
    "characters": {
        "Character Name": {
            "basic_info": {
                "name": "character_name",
                "role_type": "role_description",
                "significance_score": 0.0
            },
            "physical": {
                "height": "height_description",
                "build": "build_description",
                "age": "age_description",
                "features": ["feature1", "feature2"]
            },
            "costume": {
                "base": {
                    "item": "description"
                },
                "timeline": [
                    {
                        "scene": "scene_number",
                        "changes": {"item": "description"},
                        "notes": "costume_notes"
                    }
                ]
            },
            "props": {
                "base": ["prop1", "prop2"],
                "timeline": [
                    {
                        "scene": "scene_number",
                        "additions": ["prop1"],
                        "removals": ["prop2"]
                    }
                ]
            },
            "makeup": {
                "base": {
                    "item": "description"
                },
                "timeline": [
                    {
                        "scene": "scene_number",
                        "changes": {"item": "description"},
                        "special_effects": ["effect1"]
                    }
                ]
            },
            "casting": {
                "requirements": ["requirement1"],
                "notes": "casting_notes",
                "audition_sides": ["scene1", "scene2"]
            },
            "scenes": [
                {
                    "scene": "scene_number",
                    "sequence": 1,
                    "importance": 0.0,
                    "notes": []
                }
            ]
        }
    },
    "timelines": {
        "Character Name": [
            {
                "scene_number": "1",
                "sequence": 1,
                "changes": ["change1"],
                "significance": 0.0
            }
        ]
    },
    "props_inventory": {
        "prop_name": {
            "quantity": 1,
            "scenes": ["scene1"],
            "characters": ["char1"],
            "requirements": ["req1"]
        }
    },
    "makeup_requirements": {
        "character": {
            "base": {},
            "special_effects": [],
            "scene_specific": {}
        }
    },
    "continuity_notes": [
        {
            "scene": "scene_number",
            "note": "continuity_note",
            "affected_characters": ["char1"]
        }
    ]
}'''
        
        prompt = f"""Analyze character appearances and create detailed profiles including:
        - Basic information and role significance
        - Physical attributes and descriptions
        - Costume and wardrobe requirements with timeline
        - Props and personal items with usage timeline
        - Character evolution timeline
        - Makeup and special effects needs with timeline
        - Casting requirements and audition notes
        
        Track all changes and continuity across scenes.
        Calculate significance scores based on:
        - Number of scenes
        - Dialogue importance
        - Plot impact
        - Character relationships
        
        IMPORTANT: Return the data in this exact JSON format:
        {json_format}
        
        Character Analysis:
        {json.dumps(character_analysis, indent=2)}
        
        Scene Data:
        {json.dumps(scene_data, indent=2)}
        """
        
        try:
            # Combine instructions with prompt
            full_prompt = f"{self.instructions}\n\n{prompt}"

            # Add specific JSON formatting instruction
            json_instruction = "\n\nIMPORTANT: Respond ONLY with valid JSON. No explanations, no markdown formatting, just the JSON object exactly as specified above."
            full_prompt_with_json = full_prompt + json_instruction
            
            response = self.client.models.generate_content(
                model=self.model_config["model"],
                contents=full_prompt_with_json,
                config=types.GenerateContentConfig(
                    temperature=0.3,  # Lower temperature for more consistent JSON
                    max_output_tokens=self.model_config["max_output_tokens"],
                    top_p=self.model_config["top_p"],
                    top_k=self.model_config["top_k"],
                    response_mime_type="application/json"
                )
            )

            # Safe content extraction
            def extract_content_safely(response):
                if not hasattr(response, 'candidates') or not response.candidates:
                    raise ValueError("No candidates in Gemini response")
                
                candidate = response.candidates[0]
                if not hasattr(candidate, 'content') or not candidate.content:
                    raise ValueError("Empty content in Gemini response")
                
                if not hasattr(candidate.content, 'parts') or not candidate.content.parts:
                    raise ValueError("No content parts in Gemini response")
                
                text_content = candidate.content.parts[0].text
                if not text_content:
                    raise ValueError("Empty text content in Gemini response")
                
                return text_content

            try:
                response_text = extract_content_safely(response)
                logger.info("Received response from agent")
                
                cleaned_response = self._clean_response(response_text)
                logger.debug(f"Cleaned response: {cleaned_response[:200]}...")
                
                # Try to parse JSON with multiple attempts
                mapping = None
                parsing_attempts = [
                    lambda: json.loads(cleaned_response),
                    lambda: self._try_fix_json(cleaned_response),
                    lambda: self._extract_partial_json(cleaned_response)
                ]
                
                for i, attempt in enumerate(parsing_attempts):
                    try:
                        mapping = attempt()
                        logger.info(f"Successfully parsed JSON on attempt {i + 1}")
                        break
                    except (json.JSONDecodeError, ValueError) as parse_error:
                        logger.warning(f"JSON parsing attempt {i + 1} failed: {str(parse_error)}")
                        if i == len(parsing_attempts) - 1:  # Last attempt
                            logger.error(f"All JSON parsing attempts failed. Last error: {str(parse_error)}")
                            logger.debug(f"Raw response: {response_text[:500]}...")
                            logger.info("Creating fallback attribute mapping")
                            
                            # Create a fallback mapping based on input data
                            fallback_mapping = self._create_fallback_mapping(character_analysis, scene_data)
                            return self._process_mapping(fallback_mapping)
                
                if mapping is None:
                    logger.error("No valid mapping found, creating fallback")
                    fallback_mapping = self._create_fallback_mapping(character_analysis, scene_data)
                    return self._process_mapping(fallback_mapping)
                
                processed_mapping = self._process_mapping(mapping)
                logger.info("Successfully processed attribute mapping")
                
                return processed_mapping
                
            except ValueError as e:
                logger.error(f"Validation error: {e}")
                logger.info("Creating fallback mapping due to validation error")
                fallback_mapping = self._create_fallback_mapping(character_analysis, scene_data)
                return self._process_mapping(fallback_mapping)
                
        except Exception as e:
            logger.error(f"Error in attribute mapping: {str(e)}")
            raise ValueError(f"Failed to process attribute mapping: {str(e)}")
    
    def _process_mapping(self, mapping: Dict[str, Any]) -> Dict[str, Any]:
        """Process and validate character attribute mapping."""
        processed = {
            "characters": {},
            "timelines": {},
            "costume_changes": {},
            "props_inventory": {},
            "makeup_requirements": {},
            "continuity_notes": [],
            "casting_requirements": {}
        }
        
        if "characters" in mapping:
            for char_name, char_data in mapping["characters"].items():
                char_profile = {
                    "basic_info": char_data.get("basic_info", {}),
                    "physical_attributes": char_data.get("physical", {}),
                    "costume_data": {
                        "base": char_data.get("costume", {}).get("base", {}),
                        "timeline": char_data.get("costume", {}).get("timeline", [])
                    },
                    "props": {
                        "base": char_data.get("props", {}).get("base", []),
                        "timeline": char_data.get("props", {}).get("timeline", [])
                    },
                    "makeup": {
                        "base": char_data.get("makeup", {}).get("base", {}),
                        "timeline": char_data.get("makeup", {}).get("timeline", [])
                    },
                    "casting": char_data.get("casting", {}),
                    "scene_appearances": sorted(
                        char_data.get("scenes", []),
                        key=lambda x: (int(x.get("scene", 0)), x.get("sequence", 0))
                    )
                }
                
                # Calculate additional metrics
                scenes = char_profile["scene_appearances"]
                char_profile["metrics"] = {
                    "total_scenes": len(scenes),
                    "importance_score": sum(scene.get("importance", 0) for scene in scenes) / len(scenes) if scenes else 0,
                    "costume_changes": len(char_profile["costume_data"]["timeline"]),
                    "prop_changes": len(char_profile["props"]["timeline"]),
                    "makeup_changes": len(char_profile["makeup"]["timeline"])
                }
                
                processed["characters"][char_name] = char_profile
        
        # Process timelines
        if "timelines" in mapping:
            processed["timelines"] = {
                char: sorted(timeline, key=lambda x: (int(x["scene_number"]), x.get("sequence", 0)))
                for char, timeline in mapping["timelines"].items()
            }
        
        # Process props inventory
        if "props_inventory" in mapping:
            processed["props_inventory"] = mapping["props_inventory"]
        
        # Process makeup requirements
        if "makeup_requirements" in mapping:
            processed["makeup_requirements"] = mapping["makeup_requirements"]
        
        # Process continuity notes
        if "continuity_notes" in mapping:
            processed["continuity_notes"] = sorted(
                mapping["continuity_notes"],
                key=lambda x: int(x.get("scene", 0))
            )
        
        return processed 
    
    def _create_fallback_mapping(self, character_analysis: Dict[str, Any], scene_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a fallback character mapping when JSON parsing fails."""
        logger.info("Creating fallback character attribute mapping")
        
        fallback = {
            "characters": {},
            "timelines": {},
            "props_inventory": {},
            "makeup_requirements": {},
            "continuity_notes": []
        }
        
        # Extract characters from the analysis
        characters = character_analysis.get("characters", {})
        if not characters and "data" in character_analysis:
            characters = character_analysis["data"].get("characters", {})
        
        for char_name, char_data in characters.items():
            fallback["characters"][char_name] = {
                "basic_info": {
                    "name": char_name,
                    "role_type": char_data.get("role_type", "Unknown"),
                    "significance_score": char_data.get("significance_score", 0.5)
                },
                "physical": {
                    "height": "Standard height",
                    "build": "Standard build", 
                    "age": "Age appropriate",
                    "features": ["Standard features"]
                },
                "costume": {
                    "base": {"outfit": "Standard costume"},
                    "timeline": []
                },
                "props": {
                    "base": [],
                    "timeline": []
                },
                "makeup": {
                    "base": {"base_makeup": "Standard makeup"},
                    "timeline": []
                },
                "casting": {
                    "requirements": ["Standard casting requirements"],
                    "notes": "Basic casting notes",
                    "audition_sides": []
                },
                "scenes": []
            }
            
            # Add scene information if available
            scenes = char_data.get("scenes", [])
            for i, scene in enumerate(scenes):
                scene_info = {
                    "scene": str(scene.get("scene_number", i + 1)),
                    "sequence": i + 1,
                    "importance": scene.get("importance", 0.5),
                    "notes": []
                }
                fallback["characters"][char_name]["scenes"].append(scene_info)
        
        # If no characters found, create a basic one
        if not fallback["characters"]:
            fallback["characters"]["Unknown Character"] = {
                "basic_info": {
                    "name": "Unknown Character",
                    "role_type": "Background",
                    "significance_score": 0.1
                },
                "physical": {
                    "height": "Standard height",
                    "build": "Standard build",
                    "age": "Adult",
                    "features": ["Basic features"]
                },
                "costume": {"base": {}, "timeline": []},
                "props": {"base": [], "timeline": []},
                "makeup": {"base": {}, "timeline": []},
                "casting": {"requirements": [], "notes": "", "audition_sides": []},
                "scenes": []
            }
        
        return fallback
    
    def _try_fix_json(self, json_str: str) -> Dict[str, Any]:
        """Try to fix common JSON issues."""
        import re
        
        # Remove trailing commas before closing braces/brackets
        json_str = re.sub(r',(\s*[}\]])', r'\1', json_str)
        
        # Fix unescaped quotes in strings
        json_str = re.sub(r'(?<!\\)"(?=[^,}\]]*[,}\]])', r'\\"', json_str)
        
        # Remove comments if any
        json_str = re.sub(r'//.*?\n', '\n', json_str)
        json_str = re.sub(r'/\*.*?\*/', '', json_str, flags=re.DOTALL)
        
        # Try to balance brackets/braces
        open_braces = json_str.count('{')
        close_braces = json_str.count('}')
        if open_braces > close_braces:
            json_str += '}' * (open_braces - close_braces)
        
        return json.loads(json_str)
    
    def _extract_partial_json(self, text: str) -> Dict[str, Any]:
        """Extract partial but valid JSON structure."""
        import re
        
        # Find the first complete JSON object
        brace_count = 0
        start_idx = None
        
        for i, char in enumerate(text):
            if char == '{':
                if start_idx is None:
                    start_idx = i
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count == 0 and start_idx is not None:
                    # Found a complete JSON object
                    json_candidate = text[start_idx:i+1]
                    try:
                        return json.loads(json_candidate)
                    except json.JSONDecodeError:
                        # Try the next one
                        brace_count = 0
                        start_idx = None
        
        # If no complete object found, try to build a minimal valid one
        return {
            "characters": {},
            "timelines": {},
            "props_inventory": {},
            "makeup_requirements": {},
            "continuity_notes": []
        }