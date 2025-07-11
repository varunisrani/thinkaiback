from typing import Dict, Any, List
import json
import logging
import os
from google import genai
from google.genai import types
from base_config import AGENT_INSTRUCTIONS, get_model_config

logger = logging.getLogger(__name__)

class InsuranceSpecialistAgent:
    """Agent for insurance requirements, legal costs, and risk management."""
    
    def __init__(self):
        self.client = genai.Client(api_key=os.environ.get("GOOGLE_API_KEY"))
        self.model_config = get_model_config()
        self.instructions = AGENT_INSTRUCTIONS.get("insurance_specialist", "")
        
        # Insurance and legal templates
        self.insurance_templates = {
            "required_insurance": {
                "general_liability": {
                    "coverage_amount": 1000000,
                    "base_cost": 15000,
                    "description": "Protects against bodily injury and property damage claims"
                },
                "equipment_insurance": {
                    "coverage_amount": 500000,
                    "base_cost": 8000,
                    "description": "Covers rental and owned equipment against damage/theft"
                },
                "workers_compensation": {
                    "coverage_amount": 1000000,
                    "base_cost": 25000,
                    "description": "Required for all cast and crew members"
                },
                "errors_omissions": {
                    "coverage_amount": 2000000,
                    "base_cost": 12000,
                    "description": "Protects against copyright and content claims"
                },
                "auto_liability": {
                    "coverage_amount": 1000000,
                    "base_cost": 5000,
                    "description": "Required for production vehicles"
                }
            },
            "legal_costs": {
                "contract_preparation": {
                    "base_cost": 15000,
                    "description": "Cast and crew contracts, location agreements"
                },
                "location_agreements": {
                    "base_cost": 8000,
                    "description": "Location releases and permits"
                },
                "permit_fees": {
                    "base_cost": 5000,
                    "description": "Filming permits and municipal fees"
                },
                "clearance_costs": {
                    "base_cost": 10000,
                    "description": "Music, trademark, and copyright clearances"
                },
                "legal_consultation": {
                    "base_cost": 7500,
                    "description": "General legal advisory during production"
                }
            },
            "risk_factors": {
                "stunts": {"multiplier": 1.5, "additional_cost": 10000},
                "water_scenes": {"multiplier": 1.3, "additional_cost": 5000},
                "night_shoots": {"multiplier": 1.2, "additional_cost": 3000},
                "special_effects": {"multiplier": 1.4, "additional_cost": 8000},
                "celebrity_cast": {"multiplier": 1.3, "additional_cost": 7500},
                "international_locations": {"multiplier": 1.6, "additional_cost": 12000}
            }
        }
    
    async def analyze_insurance_requirements(
        self,
        production_data: Dict[str, Any],
        cast_data: Dict[str, Any] = None,
        location_data: Dict[str, Any] = None,
        equipment_data: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Analyze insurance requirements and legal costs."""
        try:
            prompt = self._generate_insurance_analysis_prompt(
                production_data, cast_data, location_data, equipment_data
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
                return self._create_fallback_insurance_analysis(
                    production_data, cast_data, location_data, equipment_data
                )
            
            return self._process_insurance_analysis(analysis)
            
        except Exception as e:
            logger.error(f"Error in insurance analysis: {str(e)}")
            return self._create_fallback_insurance_analysis(
                production_data, cast_data, location_data, equipment_data
            )
    
    def _generate_insurance_analysis_prompt(
        self,
        production_data: Dict[str, Any],
        cast_data: Dict[str, Any],
        location_data: Dict[str, Any],
        equipment_data: Dict[str, Any]
    ) -> str:
        """Generate prompt for insurance and legal analysis."""
        return f"""You are a professional insurance specialist for film production.
        
        Analyze the production data and determine insurance requirements and legal costs.
        
        Required JSON structure:
        {{
            "required_insurance": {{
                "general_liability": {{
                    "coverage": int,
                    "cost": float,
                    "description": "string",
                    "required": true
                }},
                "equipment_insurance": {{
                    "coverage": int,
                    "cost": float,
                    "description": "string",
                    "required": true
                }},
                "workers_compensation": {{
                    "coverage": int,
                    "cost": float,
                    "description": "string",
                    "required": true
                }},
                "errors_omissions": {{
                    "coverage": int,
                    "cost": float,
                    "description": "string",
                    "required": true
                }},
                "auto_liability": {{
                    "coverage": int,
                    "cost": float,
                    "description": "string",
                    "required": boolean
                }}
            }},
            "legal_costs": {{
                "contract_preparation": {{
                    "cost": float,
                    "description": "string",
                    "items": ["item1", "item2"]
                }},
                "location_agreements": {{
                    "cost": float,
                    "description": "string",
                    "items": ["item1", "item2"]
                }},
                "permit_fees": {{
                    "cost": float,
                    "description": "string",
                    "items": ["item1", "item2"]
                }},
                "clearance_costs": {{
                    "cost": float,
                    "description": "string",
                    "items": ["item1", "item2"]
                }},
                "legal_consultation": {{
                    "cost": float,
                    "description": "string",
                    "items": ["item1", "item2"]
                }}
            }},
            "risk_assessment": {{
                "identified_risks": [
                    {{
                        "risk_type": "string",
                        "severity": "low|medium|high",
                        "mitigation": "string",
                        "cost_impact": float
                    }}
                ],
                "total_risk_premium": float
            }},
            "compliance_requirements": {{
                "federal": ["requirement1", "requirement2"],
                "state": ["requirement1", "requirement2"],
                "local": ["requirement1", "requirement2"],
                "union": ["requirement1", "requirement2"]
            }},
            "total_insurance_cost": float,
            "total_legal_cost": float,
            "total_insurance_legal": float,
            "recommendations": [
                "recommendation1",
                "recommendation2"
            ]
        }}
        
        Production Data:
        {json.dumps(production_data, indent=2)}
        
        Cast Data:
        {json.dumps(cast_data or {}, indent=2)}
        
        Location Data:
        {json.dumps(location_data or {}, indent=2)}
        
        Equipment Data:
        {json.dumps(equipment_data or {}, indent=2)}
        
        IMPORTANT: Respond ONLY with valid JSON matching the structure above."""
    
    def _create_fallback_insurance_analysis(
        self,
        production_data: Dict[str, Any],
        cast_data: Dict[str, Any],
        location_data: Dict[str, Any],
        equipment_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create fallback insurance and legal analysis."""
        logger.info("Creating fallback insurance analysis")
        
        # Extract production details for risk assessment
        budget_range = production_data.get("budget_category", "Low Budget")
        scene_count = production_data.get("scene_count", 10)
        schedule_days = production_data.get("schedule_days", 18)
        
        # Calculate risk multiplier
        risk_multiplier = 1.0
        identified_risks = []
        
        # Assess risks based on production data
        if scene_count > 50:
            risk_multiplier += 0.2
            identified_risks.append({
                "risk_type": "Complex Production",
                "severity": "medium",
                "mitigation": "Detailed planning and experienced crew",
                "cost_impact": 5000
            })
        
        if schedule_days > 30:
            risk_multiplier += 0.3
            identified_risks.append({
                "risk_type": "Extended Schedule",
                "severity": "medium",
                "mitigation": "Comprehensive coverage and contingency planning",
                "cost_impact": 7500
            })
        
        # Check for high-risk elements
        if location_data:
            locations = location_data.get("locations", [])
            if any("exterior" in str(loc).lower() for loc in locations):
                risk_multiplier += 0.1
                identified_risks.append({
                    "risk_type": "Outdoor Filming",
                    "severity": "low",
                    "mitigation": "Weather contingency and safety protocols",
                    "cost_impact": 2500
                })
        
        # Calculate base insurance costs
        base_insurance = {
            "general_liability": {
                "coverage": 1000000,
                "cost": 15000 * risk_multiplier,
                "description": "Protects against bodily injury and property damage claims",
                "required": True
            },
            "equipment_insurance": {
                "coverage": 500000,
                "cost": 8000 * risk_multiplier,
                "description": "Covers rental and owned equipment against damage/theft",
                "required": True
            },
            "workers_compensation": {
                "coverage": 1000000,
                "cost": 25000 * risk_multiplier,
                "description": "Required for all cast and crew members",
                "required": True
            },
            "errors_omissions": {
                "coverage": 2000000,
                "cost": 12000 * risk_multiplier,
                "description": "Protects against copyright and content claims",
                "required": True
            },
            "auto_liability": {
                "coverage": 1000000,
                "cost": 5000 * risk_multiplier,
                "description": "Required for production vehicles",
                "required": True  # Assume vehicles needed
            }
        }
        
        # Calculate legal costs
        legal_costs = {
            "contract_preparation": {
                "cost": 15000,
                "description": "Cast and crew contracts, location agreements",
                "items": ["Cast contracts", "Crew agreements", "Producer contracts"]
            },
            "location_agreements": {
                "cost": 8000,
                "description": "Location releases and permits",
                "items": ["Location releases", "Filming permits", "Municipal fees"]
            },
            "permit_fees": {
                "cost": 5000,
                "description": "Filming permits and municipal fees",
                "items": ["City permits", "County permits", "Special event permits"]
            },
            "clearance_costs": {
                "cost": 10000,
                "description": "Music, trademark, and copyright clearances",
                "items": ["Music clearances", "Trademark clearances", "Stock footage"]
            },
            "legal_consultation": {
                "cost": 7500,
                "description": "General legal advisory during production",
                "items": ["Contract review", "Legal consultation", "Compliance advisory"]
            }
        }
        
        # Calculate totals
        total_insurance_cost = sum(ins["cost"] for ins in base_insurance.values())
        total_legal_cost = sum(legal["cost"] for legal in legal_costs.values())
        total_risk_premium = sum(risk["cost_impact"] for risk in identified_risks)
        
        return {
            "required_insurance": base_insurance,
            "legal_costs": legal_costs,
            "risk_assessment": {
                "identified_risks": identified_risks,
                "total_risk_premium": total_risk_premium
            },
            "compliance_requirements": {
                "federal": [
                    "Workers' Compensation compliance",
                    "OSHA safety standards",
                    "Equal Employment Opportunity compliance"
                ],
                "state": [
                    "State filming tax incentive compliance",
                    "State labor law compliance",
                    "Professional licensing requirements"
                ],
                "local": [
                    "Local filming permits",
                    "Noise ordinance compliance",
                    "Traffic control permits"
                ],
                "union": [
                    "SAG-AFTRA compliance",
                    "IATSE compliance",
                    "DGA compliance if applicable"
                ]
            },
            "total_insurance_cost": total_insurance_cost,
            "total_legal_cost": total_legal_cost,
            "total_insurance_legal": total_insurance_cost + total_legal_cost + total_risk_premium,
            "recommendations": [
                "Obtain insurance quotes 60 days before production start",
                "Work with entertainment insurance broker familiar with film production",
                "Ensure all vendors carry adequate insurance and provide certificates",
                "Maintain detailed risk assessment throughout production",
                "Consider umbrella policy for additional protection",
                "Review all contracts with qualified entertainment attorney",
                "Obtain all necessary permits well in advance of filming",
                "Ensure proper documentation for all clearances and releases"
            ]
        }
    
    def _process_insurance_analysis(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Process and validate insurance analysis."""
        # Ensure all required fields are present
        if "required_insurance" not in analysis:
            analysis["required_insurance"] = {}
        if "legal_costs" not in analysis:
            analysis["legal_costs"] = {}
        if "risk_assessment" not in analysis:
            analysis["risk_assessment"] = {"identified_risks": [], "total_risk_premium": 0}
        if "compliance_requirements" not in analysis:
            analysis["compliance_requirements"] = {
                "federal": [], "state": [], "local": [], "union": []
            }
        if "total_insurance_legal" not in analysis:
            analysis["total_insurance_legal"] = 0
            
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