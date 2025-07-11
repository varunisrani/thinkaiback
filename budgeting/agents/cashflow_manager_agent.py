from typing import Dict, Any, List
import json
import logging
import os
from datetime import datetime, timedelta
from google import genai
from google.genai import types
from ...base_config import AGENT_INSTRUCTIONS, get_model_config

logger = logging.getLogger(__name__)

class CashFlowManagerAgent:
    """Agent for financing structure analysis and cash flow management."""
    
    def __init__(self):
        self.client = genai.Client(api_key=os.environ.get("GOOGLE_API_KEY"))
        self.model_config = get_model_config()
        self.instructions = AGENT_INSTRUCTIONS.get("cashflow_manager", "")
        
        # Financing and payment templates
        self.financing_templates = {
            "financing_sources": {
                "equity_investment": {
                    "typical_percentage": 70.6,
                    "description": "Private investors and production company funding"
                },
                "tax_incentives": {
                    "typical_percentage": 20.0,
                    "description": "State and local tax incentives"
                },
                "pre_sales": {
                    "typical_percentage": 15.0,
                    "description": "Distribution agreements and pre-sales"
                },
                "grants": {
                    "typical_percentage": 5.0,
                    "description": "Arts grants and foundation funding"
                },
                "crowdfunding": {
                    "typical_percentage": 3.0,
                    "description": "Crowdfunding and fan financing"
                }
            },
            "payment_schedule": {
                "pre_production": {
                    "week_minus_8": {
                        "percentage": 15,
                        "typical_items": ["Development costs", "Pre-production salaries"]
                    },
                    "week_minus_4": {
                        "percentage": 20,
                        "typical_items": ["Location deposits", "Equipment deposits"]
                    },
                    "week_minus_2": {
                        "percentage": 25,
                        "typical_items": ["Insurance", "Final pre-production costs"]
                    }
                },
                "production": {
                    "weekly_payroll": {
                        "percentage": 30,
                        "typical_items": ["Cast salaries", "Crew salaries", "Daily expenses"]
                    },
                    "equipment_weekly": {
                        "percentage": 15,
                        "typical_items": ["Equipment rentals", "Catering", "Transportation"]
                    }
                },
                "post_production": {
                    "final_payments": {
                        "percentage": 10,
                        "typical_items": ["Post-production", "Final expenses", "Contingency"]
                    }
                }
            }
        }
    
    async def analyze_financing_structure(
        self,
        total_budget: float,
        production_data: Dict[str, Any],
        investor_data: Dict[str, Any] = None,
        timeline_data: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Analyze financing structure and create payment schedule."""
        try:
            prompt = self._generate_financing_analysis_prompt(
                total_budget, production_data, investor_data, timeline_data
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
                return self._create_fallback_financing_analysis(
                    total_budget, production_data, investor_data, timeline_data
                )
            
            return self._process_financing_analysis(analysis)
            
        except Exception as e:
            logger.error(f"Error in financing analysis: {str(e)}")
            return self._create_fallback_financing_analysis(
                total_budget, production_data, investor_data, timeline_data
            )
    
    def _generate_financing_analysis_prompt(
        self,
        total_budget: float,
        production_data: Dict[str, Any],
        investor_data: Dict[str, Any],
        timeline_data: Dict[str, Any]
    ) -> str:
        """Generate prompt for financing analysis."""
        return f"""You are a professional film financing and cash flow specialist.
        
        Analyze the production data and create a comprehensive financing structure and payment schedule.
        
        Required JSON structure:
        {{
            "financing_structure": {{
                "equity_investment": {{
                    "amount": float,
                    "percentage": float,
                    "sources": ["source1", "source2"]
                }},
                "tax_incentives": {{
                    "amount": float,
                    "percentage": float,
                    "sources": ["source1", "source2"]
                }},
                "pre_sales": {{
                    "amount": float,
                    "percentage": float,
                    "sources": ["source1", "source2"]
                }},
                "grants": {{
                    "amount": float,
                    "percentage": float,
                    "sources": ["source1", "source2"]
                }},
                "gap_financing": {{
                    "amount": float,
                    "percentage": float,
                    "sources": ["source1", "source2"]
                }}
            }},
            "payment_schedule": {{
                "pre_production": {{
                    "week_minus_8": {{
                        "amount": float,
                        "items": ["item1", "item2"],
                        "cash_flow_impact": float
                    }},
                    "week_minus_4": {{
                        "amount": float,
                        "items": ["item1", "item2"],
                        "cash_flow_impact": float
                    }},
                    "week_minus_2": {{
                        "amount": float,
                        "items": ["item1", "item2"],
                        "cash_flow_impact": float
                    }}
                }},
                "production": {{
                    "weekly_payroll": {{
                        "amount": float,
                        "frequency": "weekly",
                        "items": ["item1", "item2"],
                        "total_weeks": int
                    }},
                    "equipment_weekly": {{
                        "amount": float,
                        "frequency": "weekly",
                        "items": ["item1", "item2"],
                        "total_weeks": int
                    }},
                    "daily_expenses": {{
                        "amount": float,
                        "frequency": "daily",
                        "items": ["item1", "item2"],
                        "total_days": int
                    }}
                }},
                "post_production": {{
                    "final_payments": {{
                        "amount": float,
                        "items": ["item1", "item2"],
                        "payment_terms": "string"
                    }}
                }}
            }},
            "cash_flow_analysis": {{
                "peak_funding_requirement": float,
                "minimum_cash_balance": float,
                "funding_milestones": [
                    {{
                        "milestone": "string",
                        "amount_required": float,
                        "deadline": "string"
                    }}
                ],
                "risk_factors": [
                    {{
                        "risk": "string",
                        "probability": "low|medium|high",
                        "impact": float,
                        "mitigation": "string"
                    }}
                ]
            }},
            "financing_terms": {{
                "equity_terms": {{
                    "investor_percentage": float,
                    "profit_sharing": "string",
                    "recoupment_order": ["first", "second"]
                }},
                "debt_terms": {{
                    "interest_rate": float,
                    "repayment_schedule": "string",
                    "collateral": "string"
                }}
            }},
            "total_budget": float,
            "recommendations": [
                "recommendation1",
                "recommendation2"
            ]
        }}
        
        Total Budget: ${total_budget}
        
        Production Data:
        {json.dumps(production_data, indent=2)}
        
        Investor Data:
        {json.dumps(investor_data or {}, indent=2)}
        
        Timeline Data:
        {json.dumps(timeline_data or {}, indent=2)}
        
        IMPORTANT: Respond ONLY with valid JSON matching the structure above."""
    
    def _create_fallback_financing_analysis(
        self,
        total_budget: float,
        production_data: Dict[str, Any],
        investor_data: Dict[str, Any],
        timeline_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create fallback financing analysis."""
        logger.info("Creating fallback financing analysis")
        
        # Calculate financing structure
        financing_structure = {
            "equity_investment": {
                "amount": total_budget * 0.706,
                "percentage": 70.6,
                "sources": ["Private investors", "Production company", "Executive producers"]
            },
            "tax_incentives": {
                "amount": total_budget * 0.20,
                "percentage": 20.0,
                "sources": ["State tax credits", "Local incentives", "Federal programs"]
            },
            "pre_sales": {
                "amount": total_budget * 0.10,
                "percentage": 10.0,
                "sources": ["Distribution agreements", "International pre-sales"]
            },
            "grants": {
                "amount": total_budget * 0.05,
                "percentage": 5.0,
                "sources": ["Arts councils", "Foundation grants", "Cultural programs"]
            },
            "gap_financing": {
                "amount": total_budget * 0.044,
                "percentage": 4.4,
                "sources": ["Bridge loans", "Completion bonds", "Contingency funding"]
            }
        }
        
        # Calculate payment schedule
        schedule_days = production_data.get("schedule_days", 18)
        production_weeks = max(1, schedule_days // 7)
        
        payment_schedule = {
            "pre_production": {
                "week_minus_8": {
                    "amount": total_budget * 0.15,
                    "items": ["Development costs", "Pre-production salaries", "Office setup"],
                    "cash_flow_impact": -total_budget * 0.15
                },
                "week_minus_4": {
                    "amount": total_budget * 0.20,
                    "items": ["Location deposits", "Equipment deposits", "Insurance premiums"],
                    "cash_flow_impact": -total_budget * 0.20
                },
                "week_minus_2": {
                    "amount": total_budget * 0.25,
                    "items": ["Final insurance", "Equipment prep", "Cast prep payments"],
                    "cash_flow_impact": -total_budget * 0.25
                }
            },
            "production": {
                "weekly_payroll": {
                    "amount": (total_budget * 0.30) / production_weeks,
                    "frequency": "weekly",
                    "items": ["Cast salaries", "Crew salaries", "Producer fees"],
                    "total_weeks": production_weeks
                },
                "equipment_weekly": {
                    "amount": (total_budget * 0.15) / production_weeks,
                    "frequency": "weekly",
                    "items": ["Equipment rentals", "Catering", "Transportation"],
                    "total_weeks": production_weeks
                },
                "daily_expenses": {
                    "amount": (total_budget * 0.05) / schedule_days,
                    "frequency": "daily",
                    "items": ["Petty cash", "Miscellaneous expenses", "Emergency costs"],
                    "total_days": schedule_days
                }
            },
            "post_production": {
                "final_payments": {
                    "amount": total_budget * 0.10,
                    "items": ["Post-production", "Final crew payments", "Contingency"],
                    "payment_terms": "Net 30 days after wrap"
                }
            }
        }
        
        # Calculate cash flow analysis
        peak_funding = total_budget * 0.60  # Peak during production
        minimum_balance = total_budget * 0.10  # Minimum cash buffer
        
        cash_flow_analysis = {
            "peak_funding_requirement": peak_funding,
            "minimum_cash_balance": minimum_balance,
            "funding_milestones": [
                {
                    "milestone": "Pre-production funding",
                    "amount_required": total_budget * 0.40,
                    "deadline": "8 weeks before principal photography"
                },
                {
                    "milestone": "Production funding",
                    "amount_required": total_budget * 0.70,
                    "deadline": "2 weeks before principal photography"
                },
                {
                    "milestone": "Post-production funding",
                    "amount_required": total_budget * 0.10,
                    "deadline": "End of principal photography"
                }
            ],
            "risk_factors": [
                {
                    "risk": "Funding delays",
                    "probability": "medium",
                    "impact": total_budget * 0.05,
                    "mitigation": "Secure bridge financing and maintain investor relationships"
                },
                {
                    "risk": "Cost overruns",
                    "probability": "medium",
                    "impact": total_budget * 0.10,
                    "mitigation": "Maintain 10% contingency and strict budget monitoring"
                },
                {
                    "risk": "Tax credit delays",
                    "probability": "high",
                    "impact": total_budget * 0.20,
                    "mitigation": "Secure tax credit bridge financing or factoring"
                }
            ]
        }
        
        # Define financing terms
        financing_terms = {
            "equity_terms": {
                "investor_percentage": 60.0,
                "profit_sharing": "50/50 after investor recoupment",
                "recoupment_order": ["First position", "Pari passu with production company"]
            },
            "debt_terms": {
                "interest_rate": 8.5,
                "repayment_schedule": "Interest only during production, principal at distribution",
                "collateral": "Film negative and distribution rights"
            }
        }
        
        return {
            "financing_structure": financing_structure,
            "payment_schedule": payment_schedule,
            "cash_flow_analysis": cash_flow_analysis,
            "financing_terms": financing_terms,
            "total_budget": total_budget,
            "recommendations": [
                "Secure equity funding before pre-production begins",
                "Establish relationships with tax credit lenders early",
                "Maintain 15% cash buffer for unexpected expenses",
                "Consider completion bond for larger investors",
                "Negotiate favorable payment terms with major vendors",
                "Implement weekly cash flow monitoring during production",
                "Secure distribution agreements to support financing",
                "Consider revenue-based financing for gap funding"
            ]
        }
    
    def _process_financing_analysis(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Process and validate financing analysis."""
        # Ensure all required fields are present
        if "financing_structure" not in analysis:
            analysis["financing_structure"] = {}
        if "payment_schedule" not in analysis:
            analysis["payment_schedule"] = {}
        if "cash_flow_analysis" not in analysis:
            analysis["cash_flow_analysis"] = {}
        if "financing_terms" not in analysis:
            analysis["financing_terms"] = {}
        if "total_budget" not in analysis:
            analysis["total_budget"] = 0
            
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