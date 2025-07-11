from typing import Dict, Any, List
import json
import logging
import os
from google import genai
from google.genai import types
from ...base_config import AGENT_INSTRUCTIONS, get_model_config

logger = logging.getLogger(__name__)

class UnionComplianceAgent:
    """Agent for SAG-AFTRA and IATSE union compliance and rate calculations."""
    
    def __init__(self):
        self.client = genai.Client(api_key=os.environ.get("GOOGLE_API_KEY"))
        self.model_config = get_model_config()
        self.instructions = AGENT_INSTRUCTIONS.get("union_compliance", "")
        
        # Union rate templates (2024 rates)
        self.union_rates = {
            "sag_aftra": {
                "scale_rates": {
                    "lead_actor": {
                        "daily_rate": 1030,
                        "weekly_rate": 3575,
                        "overtime_rate": 1545  # 1.5x daily rate
                    },
                    "supporting_actor": {
                        "daily_rate": 630,
                        "weekly_rate": 2190,
                        "overtime_rate": 945
                    },
                    "background": {
                        "daily_rate": 150,
                        "weekly_rate": 525,
                        "overtime_rate": 225
                    },
                    "stunt_performer": {
                        "daily_rate": 1030,
                        "weekly_rate": 3575,
                        "hazard_pay": 500  # Additional per hazard
                    }
                },
                "benefits": {
                    "health_pension": {
                        "percentage": 18.5,
                        "minimum_contribution": 500
                    },
                    "vacation_holiday": {
                        "percentage": 8.0
                    }
                },
                "meal_penalties": {
                    "first_violation": 25,
                    "second_violation": 50,
                    "subsequent_violations": 100
                },
                "turnaround_violations": {
                    "less_than_12_hours": 100,
                    "less_than_10_hours": 200
                }
            },
            "iatse": {
                "department_minimums": {
                    "dp_rate": 550,  # per day
                    "gaffer_rate": 450,
                    "key_grip_rate": 400,
                    "sound_mixer_rate": 500,
                    "script_supervisor_rate": 450,
                    "first_ad_rate": 500,
                    "second_ad_rate": 350
                },
                "benefits": {
                    "health_welfare": {
                        "percentage": 25,
                        "minimum_hours": 300
                    },
                    "pension": {
                        "percentage": 15
                    },
                    "training": {
                        "percentage": 2
                    }
                },
                "overtime_rules": {
                    "daily_overtime": 12,  # hours before overtime
                    "weekly_overtime": 40,  # hours before weekly overtime
                    "overtime_multiplier": 1.5,
                    "double_time_hours": 16
                },
                "meal_requirements": {
                    "first_meal": 6,  # hours before first meal
                    "subsequent_meals": 6,  # hours between meals
                    "meal_penalty": 25
                }
            }
        }
    
    async def calculate_union_costs(
        self,
        cast_data: Dict[str, Any],
        crew_data: Dict[str, Any],
        schedule_data: Dict[str, Any],
        production_type: str = "independent"
    ) -> Dict[str, Any]:
        """Calculate union costs and compliance requirements."""
        try:
            prompt = self._generate_union_compliance_prompt(
                cast_data, crew_data, schedule_data, production_type
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
                return self._create_fallback_union_analysis(cast_data, crew_data, schedule_data)
            
            return self._process_union_analysis(analysis)
            
        except Exception as e:
            logger.error(f"Error in union compliance analysis: {str(e)}")
            return self._create_fallback_union_analysis(cast_data, crew_data, schedule_data)
    
    def _generate_union_compliance_prompt(
        self,
        cast_data: Dict[str, Any],
        crew_data: Dict[str, Any],
        schedule_data: Dict[str, Any],
        production_type: str
    ) -> str:
        """Generate prompt for union compliance analysis."""
        return f"""You are a professional union compliance specialist for film production.
        
        Analyze the production data and calculate SAG-AFTRA and IATSE union costs and compliance requirements.
        
        Required JSON structure:
        {{
            "sag_aftra": {{
                "scale_rates": {{
                    "lead_actor": {{
                        "daily_rate": float,
                        "weekly_rate": float,
                        "total_days": int,
                        "total_cost": float
                    }},
                    "supporting_actor": {{
                        "daily_rate": float,
                        "count": int,
                        "total_days": int,
                        "total_cost": float
                    }},
                    "background": {{
                        "daily_rate": float,
                        "person_days": int,
                        "total_cost": float
                    }},
                    "stunt_performer": {{
                        "daily_rate": float,
                        "hazard_pay": float,
                        "total_days": int,
                        "total_cost": float
                    }}
                }},
                "benefits": {{
                    "health_pension": {{
                        "percentage": float,
                        "calculated_amount": float
                    }},
                    "vacation_holiday": {{
                        "percentage": float,
                        "calculated_amount": float
                    }}
                }},
                "penalties": {{
                    "meal_penalties": {{
                        "estimated_violations": int,
                        "total_cost": float
                    }},
                    "turnaround_violations": {{
                        "estimated_violations": int,
                        "total_cost": float
                    }}
                }},
                "estimated_total": float
            }},
            "iatse": {{
                "department_minimums": {{
                    "dp_rate": float,
                    "gaffer_rate": float,
                    "key_grip_rate": float,
                    "sound_mixer_rate": float,
                    "script_supervisor_rate": float,
                    "first_ad_rate": float,
                    "second_ad_rate": float
                }},
                "crew_costs": {{
                    "department": {{
                        "base_cost": float,
                        "overtime_cost": float,
                        "total_cost": float
                    }}
                }},
                "benefits": {{
                    "health_welfare": {{
                        "percentage": float,
                        "calculated_amount": float
                    }},
                    "pension": {{
                        "percentage": float,
                        "calculated_amount": float
                    }},
                    "training": {{
                        "percentage": float,
                        "calculated_amount": float
                    }}
                }},
                "estimated_total": float
            }},
            "compliance_requirements": {{
                "sag_aftra": [
                    "requirement_description"
                ],
                "iatse": [
                    "requirement_description"
                ]
            }},
            "total_union_costs": float,
            "production_type": "{production_type}",
            "recommendations": [
                "recommendation"
            ]
        }}
        
        Cast Data:
        {json.dumps(cast_data, indent=2)}
        
        Crew Data:
        {json.dumps(crew_data, indent=2)}
        
        Schedule Data:
        {json.dumps(schedule_data, indent=2)}
        
        Production Type: {production_type}
        
        IMPORTANT: Respond ONLY with valid JSON matching the structure above."""
    
    def _create_fallback_union_analysis(
        self,
        cast_data: Dict[str, Any],
        crew_data: Dict[str, Any],
        schedule_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create fallback union compliance analysis."""
        logger.info("Creating fallback union compliance analysis")
        
        # Extract basic schedule info
        total_days = schedule_data.get("total_days", 18)
        
        # SAG-AFTRA calculations
        sag_costs = {
            "scale_rates": {
                "lead_actor": {
                    "daily_rate": 1030,
                    "weekly_rate": 3575,
                    "total_days": total_days,
                    "total_cost": 1030 * total_days
                },
                "supporting_actor": {
                    "daily_rate": 630,
                    "count": 3,
                    "total_days": total_days * 0.6,  # Not all days
                    "total_cost": 630 * total_days * 0.6 * 3
                },
                "background": {
                    "daily_rate": 150,
                    "person_days": total_days * 8,  # 8 background per day
                    "total_cost": 150 * total_days * 8
                },
                "stunt_performer": {
                    "daily_rate": 1030,
                    "hazard_pay": 500,
                    "total_days": 2,  # Estimate 2 stunt days
                    "total_cost": (1030 + 500) * 2
                }
            },
            "benefits": {
                "health_pension": {
                    "percentage": 18.5,
                    "calculated_amount": 0  # Will be calculated
                },
                "vacation_holiday": {
                    "percentage": 8.0,
                    "calculated_amount": 0  # Will be calculated
                }
            },
            "penalties": {
                "meal_penalties": {
                    "estimated_violations": 5,
                    "total_cost": 5 * 50  # Average penalty
                },
                "turnaround_violations": {
                    "estimated_violations": 2,
                    "total_cost": 2 * 150  # Average penalty
                }
            }
        }
        
        # Calculate SAG benefits
        sag_gross_wages = sum(
            item["total_cost"] for item in sag_costs["scale_rates"].values()
        )
        sag_costs["benefits"]["health_pension"]["calculated_amount"] = sag_gross_wages * 0.185
        sag_costs["benefits"]["vacation_holiday"]["calculated_amount"] = sag_gross_wages * 0.08
        
        sag_total = (
            sag_gross_wages +
            sag_costs["benefits"]["health_pension"]["calculated_amount"] +
            sag_costs["benefits"]["vacation_holiday"]["calculated_amount"] +
            sag_costs["penalties"]["meal_penalties"]["total_cost"] +
            sag_costs["penalties"]["turnaround_violations"]["total_cost"]
        )
        sag_costs["estimated_total"] = sag_total
        
        # IATSE calculations
        iatse_costs = {
            "department_minimums": {
                "dp_rate": 550,
                "gaffer_rate": 450,
                "key_grip_rate": 400,
                "sound_mixer_rate": 500,
                "script_supervisor_rate": 450,
                "first_ad_rate": 500,
                "second_ad_rate": 350
            },
            "crew_costs": {
                "camera_department": {
                    "base_cost": 550 * total_days,
                    "overtime_cost": 550 * total_days * 0.2,  # 20% overtime estimate
                    "total_cost": 550 * total_days * 1.2
                },
                "lighting_department": {
                    "base_cost": 450 * total_days,
                    "overtime_cost": 450 * total_days * 0.2,
                    "total_cost": 450 * total_days * 1.2
                },
                "sound_department": {
                    "base_cost": 500 * total_days,
                    "overtime_cost": 500 * total_days * 0.2,
                    "total_cost": 500 * total_days * 1.2
                },
                "production_department": {
                    "base_cost": (500 + 350) * total_days,  # 1st AD + 2nd AD
                    "overtime_cost": (500 + 350) * total_days * 0.2,
                    "total_cost": (500 + 350) * total_days * 1.2
                }
            },
            "benefits": {
                "health_welfare": {
                    "percentage": 25,
                    "calculated_amount": 0  # Will be calculated
                },
                "pension": {
                    "percentage": 15,
                    "calculated_amount": 0  # Will be calculated
                },
                "training": {
                    "percentage": 2,
                    "calculated_amount": 0  # Will be calculated
                }
            }
        }
        
        # Calculate IATSE benefits
        iatse_gross_wages = sum(
            dept["total_cost"] for dept in iatse_costs["crew_costs"].values()
        )
        iatse_costs["benefits"]["health_welfare"]["calculated_amount"] = iatse_gross_wages * 0.25
        iatse_costs["benefits"]["pension"]["calculated_amount"] = iatse_gross_wages * 0.15
        iatse_costs["benefits"]["training"]["calculated_amount"] = iatse_gross_wages * 0.02
        
        iatse_total = (
            iatse_gross_wages +
            iatse_costs["benefits"]["health_welfare"]["calculated_amount"] +
            iatse_costs["benefits"]["pension"]["calculated_amount"] +
            iatse_costs["benefits"]["training"]["calculated_amount"]
        )
        iatse_costs["estimated_total"] = iatse_total
        
        return {
            "sag_aftra": sag_costs,
            "iatse": iatse_costs,
            "compliance_requirements": {
                "sag_aftra": [
                    "Maintain detailed timesheets for all performers",
                    "Ensure proper meal breaks (6 hours maximum)",
                    "Provide 12-hour turnaround between wrap and call",
                    "Submit weekly payroll reports to SAG-AFTRA",
                    "Maintain workers' compensation insurance"
                ],
                "iatse": [
                    "Pay prevailing wage rates for all crew positions",
                    "Provide overtime pay after 8 hours daily, 40 hours weekly",
                    "Contribute to health and pension funds",
                    "Maintain safe working conditions per OSHA standards",
                    "Provide proper meal breaks every 6 hours"
                ]
            },
            "total_union_costs": sag_total + iatse_total,
            "production_type": "independent",
            "recommendations": [
                "Budget additional 15% for union compliance buffer",
                "Hire experienced 1st AD familiar with union rules",
                "Implement digital timekeeping system",
                "Schedule meal breaks precisely to avoid penalties",
                "Consider union rep on set for complex productions"
            ]
        }
    
    def _process_union_analysis(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Process and validate union analysis."""
        # Ensure all required fields are present
        if "sag_aftra" not in analysis:
            analysis["sag_aftra"] = {}
        if "iatse" not in analysis:
            analysis["iatse"] = {}
        if "compliance_requirements" not in analysis:
            analysis["compliance_requirements"] = {"sag_aftra": [], "iatse": []}
        if "total_union_costs" not in analysis:
            analysis["total_union_costs"] = 0
            
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