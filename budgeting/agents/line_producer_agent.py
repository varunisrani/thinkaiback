from typing import Dict, Any, List
import json
import logging
import os
from google import genai
from google.genai import types
from base_config import AGENT_INSTRUCTIONS, get_model_config

logger = logging.getLogger(__name__)

class LineProducerAgent:
    """Agent for Above/Below Line budget breakdown and scenario planning."""
    
    def __init__(self):
        self.client = genai.Client(api_key=os.environ.get("GOOGLE_API_KEY"))
        self.model_config = get_model_config()
        self.instructions = AGENT_INSTRUCTIONS.get("line_producer", "")
        
        # Above/Below Line templates
        self.line_templates = {
            "above_the_line": {
                "producer_fees": {"percentage": 17.6, "base_amount": 75000},
                "director_fee": {"percentage": 11.8, "base_amount": 50000},
                "cast": {
                    "lead_actor": {"base_amount": 60000, "days": 18},
                    "supporting_cast": {"base_amount": 25000, "days": 12},
                    "background": {"daily_rate": 150, "days": 8}
                }
            },
            "below_the_line": {
                "crew": {
                    "camera_department": {"base_amount": 45000},
                    "sound_department": {"base_amount": 25000},
                    "lighting_department": {"base_amount": 35000},
                    "production_department": {"base_amount": 28000}
                },
                "equipment": {
                    "camera_package": {"base_amount": 25000},
                    "sound_package": {"base_amount": 12000},
                    "lighting_package": {"base_amount": 18000},
                    "grip_package": {"base_amount": 15000}
                },
                "locations": {"base_amount": 35000},
                "catering": {"daily_rate": 500, "days": 18},
                "transportation": {"base_amount": 8000}
            },
            "contingency": {"percentage": 10}
        }
    
    async def analyze_above_below_line(
        self,
        production_data: Dict[str, Any],
        cast_data: Dict[str, Any] = None,
        crew_data: Dict[str, Any] = None,
        budget_scenario: str = "base"
    ) -> Dict[str, Any]:
        """Analyze and break down Above/Below Line budget structure."""
        try:
            # Generate the analysis
            prompt = self._generate_line_analysis_prompt(
                production_data, cast_data, crew_data, budget_scenario
            )
            
            full_prompt = f"{self.instructions}\n\n{prompt}"
            
            response = self.client.models.generate_content(
                model=self.model_config["model"],
                contents=full_prompt,
                config=types.GenerateContentConfig(
                    temperature=self.model_config["temperature"],
                    max_output_tokens=self.model_config["max_output_tokens"],
                    top_p=self.model_config["top_p"],
                    top_k=self.model_config["top_k"],
                    response_mime_type="application/json"
                )
            )
            
            response_text = self._extract_content_safely(response)
            analysis = self._extract_json(response_text)
            
            if not analysis:
                logger.warning("Failed to parse AI response, using fallback")
                return self._create_fallback_line_analysis(production_data, cast_data, crew_data, budget_scenario)
            
            return self._process_line_analysis(analysis, budget_scenario)
            
        except Exception as e:
            logger.error(f"Error in line producer analysis: {str(e)}")
            return self._create_fallback_line_analysis(production_data, cast_data, crew_data, budget_scenario)
    
    def _generate_line_analysis_prompt(
        self,
        production_data: Dict[str, Any],
        cast_data: Dict[str, Any],
        crew_data: Dict[str, Any],
        budget_scenario: str
    ) -> str:
        """Generate prompt for Above/Below Line analysis."""
        return f"""You are a professional line producer responsible for Above/Below Line budget analysis.
        
        Analyze the production data and provide a detailed Above/Below Line breakdown in JSON format.
        
        Required JSON structure:
        {{
            "above_the_line": {{
                "producer_fees": {{
                    "amount": float,
                    "percentage": float,
                    "breakdown": {{
                        "executive_producer": float,
                        "line_producer": float,
                        "associate_producer": float
                    }}
                }},
                "director_fee": {{
                    "amount": float,
                    "percentage": float,
                    "includes": ["prep", "production", "post"]
                }},
                "cast": {{
                    "lead_actor": {{
                        "amount": float,
                        "days": int,
                        "daily_rate": float
                    }},
                    "supporting_cast": {{
                        "amount": float,
                        "count": int,
                        "average_rate": float
                    }},
                    "background": {{
                        "amount": float,
                        "person_days": int,
                        "daily_rate": float
                    }}
                }},
                "subtotal": float
            }},
            "below_the_line": {{
                "crew": {{
                    "camera_department": {{
                        "amount": float,
                        "roles": ["dp", "camera_operator", "1st_ac", "2nd_ac"],
                        "breakdown": {{"role": float}}
                    }},
                    "sound_department": {{
                        "amount": float,
                        "roles": ["sound_mixer", "boom_operator"],
                        "breakdown": {{"role": float}}
                    }},
                    "lighting_department": {{
                        "amount": float,
                        "roles": ["gaffer", "electrician", "grip"],
                        "breakdown": {{"role": float}}
                    }},
                    "production_department": {{
                        "amount": float,
                        "roles": ["1st_ad", "2nd_ad", "script_supervisor"],
                        "breakdown": {{"role": float}}
                    }}
                }},
                "equipment": {{
                    "camera_package": {{
                        "amount": float,
                        "items": ["camera", "lenses", "accessories"],
                        "breakdown": {{"item": float}}
                    }},
                    "sound_package": {{
                        "amount": float,
                        "items": ["mixer", "microphones", "accessories"],
                        "breakdown": {{"item": float}}
                    }},
                    "lighting_package": {{
                        "amount": float,
                        "items": ["lights", "stands", "modifiers"],
                        "breakdown": {{"item": float}}
                    }},
                    "grip_package": {{
                        "amount": float,
                        "items": ["tripods", "dollies", "accessories"],
                        "breakdown": {{"item": float}}
                    }}
                }},
                "locations": {{
                    "amount": float,
                    "breakdown": {{"location": float}},
                    "permits": float
                }},
                "catering": {{
                    "amount": float,
                    "daily_rate": float,
                    "days": int
                }},
                "transportation": {{
                    "amount": float,
                    "breakdown": {{"type": float}}
                }},
                "subtotal": float
            }},
            "contingency": {{
                "amount": float,
                "percentage": float
            }},
            "total_budget": float,
            "scenario": "{budget_scenario}",
            "breakdown_ratios": {{
                "above_the_line_percentage": float,
                "below_the_line_percentage": float,
                "contingency_percentage": float
            }}
        }}
        
        Production Data:
        {json.dumps(production_data, indent=2)}
        
        Cast Data:
        {json.dumps(cast_data or {}, indent=2)}
        
        Crew Data:
        {json.dumps(crew_data or {}, indent=2)}
        
        Budget Scenario: {budget_scenario}
        
        IMPORTANT: Respond ONLY with valid JSON matching the structure above."""
    
    def _create_fallback_line_analysis(
        self,
        production_data: Dict[str, Any],
        cast_data: Dict[str, Any],
        crew_data: Dict[str, Any],
        budget_scenario: str
    ) -> Dict[str, Any]:
        """Create fallback Above/Below Line analysis."""
        logger.info("Creating fallback line producer analysis")
        
        # Scenario multipliers
        scenario_multipliers = {
            "optimistic": 0.85,
            "base": 1.0,
            "conservative": 1.25
        }
        
        multiplier = scenario_multipliers.get(budget_scenario, 1.0)
        
        # Calculate Above the Line
        above_the_line = {
            "producer_fees": {
                "amount": 75000 * multiplier,
                "percentage": 17.6,
                "breakdown": {
                    "executive_producer": 35000 * multiplier,
                    "line_producer": 25000 * multiplier,
                    "associate_producer": 15000 * multiplier
                }
            },
            "director_fee": {
                "amount": 50000 * multiplier,
                "percentage": 11.8,
                "includes": ["prep", "production", "post"]
            },
            "cast": {
                "lead_actor": {
                    "amount": 60000 * multiplier,
                    "days": 18,
                    "daily_rate": (60000 * multiplier) / 18
                },
                "supporting_cast": {
                    "amount": 25000 * multiplier,
                    "count": 3,
                    "average_rate": (25000 * multiplier) / 3
                },
                "background": {
                    "amount": 4800 * multiplier,
                    "person_days": 32,
                    "daily_rate": 150
                }
            }
        }
        
        above_subtotal = (
            above_the_line["producer_fees"]["amount"] +
            above_the_line["director_fee"]["amount"] +
            above_the_line["cast"]["lead_actor"]["amount"] +
            above_the_line["cast"]["supporting_cast"]["amount"] +
            above_the_line["cast"]["background"]["amount"]
        )
        above_the_line["subtotal"] = above_subtotal
        
        # Calculate Below the Line
        below_the_line = {
            "crew": {
                "camera_department": {
                    "amount": 45000 * multiplier,
                    "roles": ["dp", "camera_operator", "1st_ac", "2nd_ac"],
                    "breakdown": {
                        "dp": 20000 * multiplier,
                        "camera_operator": 12000 * multiplier,
                        "1st_ac": 8000 * multiplier,
                        "2nd_ac": 5000 * multiplier
                    }
                },
                "sound_department": {
                    "amount": 25000 * multiplier,
                    "roles": ["sound_mixer", "boom_operator"],
                    "breakdown": {
                        "sound_mixer": 15000 * multiplier,
                        "boom_operator": 10000 * multiplier
                    }
                },
                "lighting_department": {
                    "amount": 35000 * multiplier,
                    "roles": ["gaffer", "electrician", "grip"],
                    "breakdown": {
                        "gaffer": 18000 * multiplier,
                        "electrician": 10000 * multiplier,
                        "grip": 7000 * multiplier
                    }
                },
                "production_department": {
                    "amount": 28000 * multiplier,
                    "roles": ["1st_ad", "2nd_ad", "script_supervisor"],
                    "breakdown": {
                        "1st_ad": 15000 * multiplier,
                        "2nd_ad": 8000 * multiplier,
                        "script_supervisor": 5000 * multiplier
                    }
                }
            },
            "equipment": {
                "camera_package": {
                    "amount": 25000 * multiplier,
                    "items": ["camera", "lenses", "accessories"],
                    "breakdown": {
                        "camera": 15000 * multiplier,
                        "lenses": 8000 * multiplier,
                        "accessories": 2000 * multiplier
                    }
                },
                "sound_package": {
                    "amount": 12000 * multiplier,
                    "items": ["mixer", "microphones", "accessories"],
                    "breakdown": {
                        "mixer": 6000 * multiplier,
                        "microphones": 4000 * multiplier,
                        "accessories": 2000 * multiplier
                    }
                },
                "lighting_package": {
                    "amount": 18000 * multiplier,
                    "items": ["lights", "stands", "modifiers"],
                    "breakdown": {
                        "lights": 12000 * multiplier,
                        "stands": 4000 * multiplier,
                        "modifiers": 2000 * multiplier
                    }
                },
                "grip_package": {
                    "amount": 15000 * multiplier,
                    "items": ["tripods", "dollies", "accessories"],
                    "breakdown": {
                        "tripods": 8000 * multiplier,
                        "dollies": 5000 * multiplier,
                        "accessories": 2000 * multiplier
                    }
                }
            },
            "locations": {
                "amount": 35000 * multiplier,
                "breakdown": {
                    "studio": 20000 * multiplier,
                    "exterior": 10000 * multiplier,
                    "interior": 5000 * multiplier
                },
                "permits": 2000 * multiplier
            },
            "catering": {
                "amount": 9000 * multiplier,
                "daily_rate": 500,
                "days": 18
            },
            "transportation": {
                "amount": 8000 * multiplier,
                "breakdown": {
                    "vehicle_rentals": 5000 * multiplier,
                    "fuel": 2000 * multiplier,
                    "parking": 1000 * multiplier
                }
            }
        }
        
        below_subtotal = (
            sum(dept["amount"] for dept in below_the_line["crew"].values()) +
            sum(eq["amount"] for eq in below_the_line["equipment"].values()) +
            below_the_line["locations"]["amount"] +
            below_the_line["catering"]["amount"] +
            below_the_line["transportation"]["amount"]
        )
        below_the_line["subtotal"] = below_subtotal
        
        # Calculate contingency
        total_before_contingency = above_subtotal + below_subtotal
        contingency_amount = total_before_contingency * 0.1
        
        contingency = {
            "amount": contingency_amount,
            "percentage": 10.0
        }
        
        total_budget = total_before_contingency + contingency_amount
        
        return {
            "above_the_line": above_the_line,
            "below_the_line": below_the_line,
            "contingency": contingency,
            "total_budget": total_budget,
            "scenario": budget_scenario,
            "breakdown_ratios": {
                "above_the_line_percentage": (above_subtotal / total_budget) * 100,
                "below_the_line_percentage": (below_subtotal / total_budget) * 100,
                "contingency_percentage": (contingency_amount / total_budget) * 100
            }
        }
    
    def _process_line_analysis(self, analysis: Dict[str, Any], scenario: str) -> Dict[str, Any]:
        """Process and validate line analysis."""
        # Ensure all required fields are present
        if "above_the_line" not in analysis:
            analysis["above_the_line"] = {}
        if "below_the_line" not in analysis:
            analysis["below_the_line"] = {}
        if "scenario" not in analysis:
            analysis["scenario"] = scenario
            
        return analysis
    
    def _extract_content_safely(self, response):
        """Safely extract content from Gemini response."""
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
    
    def _extract_json(self, text: str) -> Dict[str, Any]:
        """Extract JSON from text response."""
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            import re
            matches = re.search(r'\{.*\}', text, re.DOTALL)
            if matches:
                try:
                    return json.loads(matches.group(0))
                except json.JSONDecodeError:
                    pass
            return {}