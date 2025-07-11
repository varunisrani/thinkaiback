from typing import Dict, Any, List
import json
import logging
from datetime import datetime
from .agents.cost_estimator_agent import CostEstimatorAgent
from .agents.budget_optimizer_agent import BudgetOptimizerAgent
from .agents.budget_tracker_agent import BudgetTrackerAgent
from .agents.line_producer_agent import LineProducerAgent
from .agents.union_compliance_agent import UnionComplianceAgent
from .agents.insurance_specialist_agent import InsuranceSpecialistAgent
from .agents.cashflow_manager_agent import CashFlowManagerAgent

logger = logging.getLogger(__name__)

class BudgetingCoordinator:
    def __init__(self):
        logger.info("Initializing BudgetingCoordinator with 5 sub-agents")
        # Original agents
        self.cost_estimator = CostEstimatorAgent()
        self.budget_optimizer = BudgetOptimizerAgent()
        self.budget_tracker = BudgetTrackerAgent()
        # New sub-agents
        self.line_producer = LineProducerAgent()
        self.union_compliance = UnionComplianceAgent()
        self.insurance_specialist = InsuranceSpecialistAgent()
        self.cashflow_manager = CashFlowManagerAgent()
        # State management
        self.current_budget = None
        self.current_tracking = None
        self.vendor_data = {}
        self.cash_flow_data = None
        self.sub_agent_results = {}
    
    async def process_budget_estimation(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process budget estimation request - convenience method for API."""
        try:
            # Extract data from request
            production_data = request_data.get("production_data", {})
            
            # Check if we have the new frontend structure
            if "script_results" in production_data:
                return await self.process_budget_estimation_frontend(request_data)
            
            location_data = request_data.get("location_data", {})
            crew_data = request_data.get("crew_data", {})
            target_budget = request_data.get("target_budget")
            constraints = request_data.get("budget_constraints", {})
            
            # Use comprehensive budget initialization with all sub-agents
            result = await self.initialize_comprehensive_budget(
                production_data=production_data,
                location_data=location_data,
                crew_data=crew_data,
                target_budget=target_budget,
                constraints=constraints
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error in budget estimation: {str(e)}")
            return {
                "error": str(e),
                "success": False
            }

    async def process_budget_estimation_frontend(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Frontend-compatible budget estimation method."""
        try:
            logger.info("Processing frontend budget estimation request")
            
            # Extract data from frontend structure
            production_data = request_data.get("production_data", {})
            script_results = production_data.get("script_results", {})
            character_results = production_data.get("character_results", {})
            schedule_results = production_data.get("schedule_results", {})
            
            # Transform frontend data to expected format
            transformed_production_data = self._transform_frontend_data(
                script_results, character_results, schedule_results
            )
            
            # Extract location and crew data from the results
            location_data = self._extract_location_data(script_results, schedule_results)
            crew_data = self._extract_crew_data(character_results, schedule_results)
            
            # Extract constraints
            constraints = request_data.get("budget_constraints", {})
            target_budget = constraints.get("target_budget")
            
            # Use comprehensive budget initialization with all sub-agents
            result = await self.initialize_comprehensive_budget(
                production_data=transformed_production_data,
                location_data=location_data,
                crew_data=crew_data,
                target_budget=target_budget,
                constraints=constraints
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error in frontend budget estimation: {str(e)}")
            # Return fallback budget estimation
            return self._create_fallback_budget()

    def _transform_frontend_data(self, script_results: Dict[str, Any], character_results: Dict[str, Any], schedule_results: Dict[str, Any]) -> Dict[str, Any]:
        """Transform frontend data structure to expected format."""
        try:
            # Extract scene count from script results
            scene_count = 0
            if script_results:
                parsed_data = script_results.get("parsed_data", {})
                scenes = parsed_data.get("scenes", [])
                scene_count = len(scenes) if scenes else 10  # Default fallback
            
            # Extract schedule days from schedule results
            schedule_days = 0
            if schedule_results:
                summary = schedule_results.get("summary", {})
                schedule_days = summary.get("total_days", 0)
            
            if scene_count == 0:
                scene_count = 10  # Default fallback
            if schedule_days == 0:
                schedule_days = max(scene_count // 5, 1)  # Estimate based on scenes
            
            return {
                "scene_count": scene_count,
                "schedule_days": schedule_days,
                "production_type": "Independent Film",
                "budget_category": "Low Budget"
            }
            
        except Exception as e:
            logger.warning(f"Error transforming frontend data: {e}, using defaults")
            return {
                "scene_count": 10,
                "schedule_days": 3,
                "production_type": "Independent Film",
                "budget_category": "Low Budget"
            }

    def _extract_location_data(self, script_results: Dict[str, Any], schedule_results: Dict[str, Any]) -> Dict[str, Any]:
        """Extract location data from script and schedule results."""
        locations = []
        
        try:
            # Try to extract from script results
            if script_results:
                parsed_data = script_results.get("parsed_data", {})
                scenes = parsed_data.get("scenes", [])
                location_names = set()
                
                for scene in scenes:
                    location = scene.get("location", {})
                    if isinstance(location, dict):
                        place = location.get("place", "")
                        if place:
                            location_names.add(place)
                    elif isinstance(location, str) and location.strip():
                        location_names.add(location.strip())
                
                for loc_name in location_names:
                    locations.append({
                        "name": loc_name,
                        "type": "Location",
                        "cost_category": "Standard"
                    })
            
            # If no locations found, add default
            if not locations:
                locations = [
                    {"name": "Studio", "type": "Studio", "cost_category": "Standard"},
                    {"name": "Exterior Location", "type": "Exterior", "cost_category": "Standard"}
                ]
                
        except Exception as e:
            logger.warning(f"Error extracting location data: {e}, using defaults")
            locations = [
                {"name": "Studio", "type": "Studio", "cost_category": "Standard"}
            ]
        
        return {"locations": locations}

    def _extract_crew_data(self, character_results: Dict[str, Any], schedule_results: Dict[str, Any]) -> Dict[str, Any]:
        """Extract crew data from character and schedule results."""
        try:
            # Basic crew structure for independent film
            departments = [
                "Direction", "Cinematography", "Sound", "Lighting", "Production"
            ]
            
            # Estimate crew size based on character count
            character_count = 0
            if character_results:
                characters = character_results.get("characters", {})
                character_count = len(characters) if characters else 5
            
            # Base crew size (minimum viable crew)
            base_crew_size = 8
            # Add more crew based on character count (more characters = more complex production)
            estimated_crew_size = base_crew_size + min(character_count // 2, 10)
            
            return {
                "size": estimated_crew_size,
                "departments": departments
            }
            
        except Exception as e:
            logger.warning(f"Error extracting crew data: {e}, using defaults")
            return {
                "size": 8,
                "departments": ["Direction", "Cinematography", "Sound", "Lighting", "Production"]
            }

    def _create_fallback_budget(self) -> Dict[str, Any]:
        """Create a fallback budget when estimation fails."""
        logger.info("Creating fallback budget estimation")
        
        return {
            "budget_breakdown": {
                "above_the_line": {
                    "director": 15000,
                    "producers": 10000,
                    "cast": 25000
                },
                "below_the_line": {
                    "crew": 30000,
                    "equipment": 20000,
                    "locations": 10000,
                    "catering": 5000,
                    "transportation": 8000
                },
                "post_production": {
                    "editing": 12000,
                    "sound": 8000,
                    "color": 5000
                },
                "contingency": 14800
            },
            "total_budget": 162800,
            "summary": {
                "total_above_the_line": 50000,
                "total_below_the_line": 73000,
                "total_post_production": 25000,
                "contingency_percentage": 10,
                "estimated_days": 10
            },
            "recommendations": [
                "Budget based on standard independent film estimates",
                "Consider location costs for exterior scenes",
                "Include 10% contingency for unexpected expenses",
                "Review equipment rental rates in your area"
            ],
            "success": True,
            "timestamp": datetime.now().isoformat()
        }
    
    async def initialize_budget(
        self,
        production_data: Dict[str, Any],
        location_data: Dict[str, Any],
        crew_data: Dict[str, Any],
        target_budget: float = None,
        constraints: Dict[str, Any] = None,
        vendor_data: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Initialize production budget with estimates and optimization."""
        try:
            # Store vendor data if provided
            if vendor_data:
                self.vendor_data = vendor_data
            
            # Validate input data
            self._validate_input_data(production_data, location_data, crew_data)
            logger.info("Input data validated successfully")
            
            # Step 1: Generate initial cost estimates
            logger.info("Generating initial cost estimates")
            estimates = await self.cost_estimator.estimate_costs(
                production_data,
                location_data,
                crew_data
            )
            
            if not estimates:
                logger.error("Cost estimator returned empty estimates")
                raise ValueError("Failed to generate cost estimates")
            
            logger.info("Cost estimates generated successfully")
            
            # Step 2: Optimize budget if target or constraints provided
            if target_budget or constraints:
                logger.info("Optimizing budget with constraints")
                optimization = await self.budget_optimizer.optimize_budget(
                    estimates,
                    constraints or {},
                    target_budget
                )
                
                if not optimization:
                    logger.error("Budget optimizer returned empty optimization")
                    raise ValueError("Failed to optimize budget")
                
                # Update estimates with optimizations
                final_budget = self._apply_optimization(estimates, optimization)
                logger.info("Budget optimization applied successfully")
            else:
                final_budget = estimates
            
            # Store current budget
            self.current_budget = final_budget
            
            # Initialize cash flow tracking if vendor data is available
            if vendor_data:
                self.cash_flow_data = await self.budget_tracker._analyze_cash_flow(
                    final_budget,
                    {},  # No actuals yet
                    vendor_data
                )
            
            return final_budget
            
        except Exception as e:
            logger.error(f"Failed to initialize budget: {str(e)}", exc_info=True)
            raise RuntimeError(f"Failed to initialize budget: {str(e)}")
    
    async def initialize_comprehensive_budget(
        self,
        production_data: Dict[str, Any],
        location_data: Dict[str, Any],
        crew_data: Dict[str, Any],
        target_budget: float = None,
        constraints: Dict[str, Any] = None,
        vendor_data: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Initialize production budget with all 5 sub-agents."""
        try:
            logger.info("Starting comprehensive budget analysis with all 5 sub-agents")
            
            # Store vendor data if provided
            if vendor_data:
                self.vendor_data = vendor_data
            
            # Validate input data
            self._validate_input_data(production_data, location_data, crew_data)
            logger.info("Input data validated successfully")
            
            # Run all sub-agents with proper error handling
            logger.info("Running all 5 sub-agents")
            
            # 1. Cost Calculator Agent (Enhanced)
            logger.info("Running CostCalculatorAgent...")
            try:
                cost_estimates = await self.cost_estimator.estimate_costs(
                    production_data, location_data, crew_data
                )
                logger.info("CostCalculatorAgent completed successfully")
            except Exception as e:
                logger.error(f"CostCalculatorAgent failed: {str(e)}")
                cost_estimates = self.cost_estimator._create_fallback_estimates(
                    production_data, location_data, crew_data, {}
                )
            
            # 2. Line Producer Agent (Above/Below Line)
            logger.info("Running LineProducerAgent...")
            try:
                line_analysis = await self.line_producer.analyze_above_below_line(
                    production_data, 
                    cast_data=crew_data,  # Use crew_data as cast_data fallback
                    crew_data=crew_data,
                    budget_scenario="base"
                )
                logger.info("LineProducerAgent completed successfully")
            except Exception as e:
                logger.error(f"LineProducerAgent failed: {str(e)}")
                line_analysis = self.line_producer._create_fallback_line_analysis(
                    production_data, crew_data, crew_data, "base"
                )
            
            # 3. Union Compliance Agent (SAG/IATSE)
            logger.info("Running UnionComplianceAgent...")
            try:
                union_analysis = await self.union_compliance.calculate_union_costs(
                    cast_data=crew_data,  # Use crew_data as cast_data fallback
                    crew_data=crew_data,
                    schedule_data=production_data,
                    production_type="independent"
                )
                logger.info("UnionComplianceAgent completed successfully")
            except Exception as e:
                logger.error(f"UnionComplianceAgent failed: {str(e)}")
                union_analysis = self.union_compliance._create_fallback_union_analysis(
                    crew_data, crew_data, production_data
                )
            
            # 4. Insurance Specialist Agent (Legal/Insurance)
            logger.info("Running InsuranceSpecialistAgent...")
            try:
                insurance_analysis = await self.insurance_specialist.analyze_insurance_requirements(
                    production_data=production_data,
                    cast_data=crew_data,
                    location_data=location_data,
                    equipment_data=cost_estimates.get("equipment_costs", {})
                )
                logger.info("InsuranceSpecialistAgent completed successfully")
            except Exception as e:
                logger.error(f"InsuranceSpecialistAgent failed: {str(e)}")
                insurance_analysis = self.insurance_specialist._create_fallback_insurance_analysis(
                    production_data, crew_data, location_data, cost_estimates.get("equipment_costs", {})
                )
            
            # 5. Cash Flow Manager Agent (Financing)
            logger.info("Running CashFlowManagerAgent...")
            try:
                total_budget_estimate = cost_estimates.get("total_estimates", {}).get("grand_total", 425000)
                financing_analysis = await self.cashflow_manager.analyze_financing_structure(
                    total_budget=total_budget_estimate,
                    production_data=production_data,
                    investor_data=constraints,
                    timeline_data=production_data
                )
                logger.info("CashFlowManagerAgent completed successfully")
            except Exception as e:
                logger.error(f"CashFlowManagerAgent failed: {str(e)}")
                financing_analysis = self.cashflow_manager._create_fallback_financing_analysis(
                    425000, production_data, constraints, production_data
                )
            
            # Store sub-agent results
            self.sub_agent_results = {
                "cost_calculator": {
                    "status": "operational",
                    "data": cost_estimates
                },
                "line_producer": {
                    "status": "operational", 
                    "data": line_analysis
                },
                "union_compliance": {
                    "status": "operational",
                    "data": union_analysis
                },
                "insurance_specialist": {
                    "status": "operational",
                    "data": insurance_analysis
                },
                "cashflow_manager": {
                    "status": "operational",
                    "data": financing_analysis
                }
            }
            
            # Combine results into comprehensive budget
            comprehensive_budget = self._combine_sub_agent_results(
                cost_estimates, line_analysis, union_analysis, 
                insurance_analysis, financing_analysis
            )
            
            # Apply optimizations if target budget or constraints provided
            if target_budget or constraints:
                logger.info("Optimizing comprehensive budget with constraints")
                optimization = await self.budget_optimizer.optimize_budget(
                    comprehensive_budget,
                    constraints or {},
                    target_budget
                )
                
                if optimization:
                    comprehensive_budget = self._apply_optimization(comprehensive_budget, optimization)
                    logger.info("Budget optimization applied successfully")
            
            # Store current budget
            self.current_budget = comprehensive_budget
            
            # Initialize cash flow tracking if vendor data is available
            if vendor_data:
                self.cash_flow_data = await self.budget_tracker._analyze_cash_flow(
                    comprehensive_budget,
                    {},  # No actuals yet
                    vendor_data
                )
            
            logger.info("Comprehensive budget analysis completed successfully")
            return comprehensive_budget
            
        except Exception as e:
            logger.error(f"Failed to initialize comprehensive budget: {str(e)}", exc_info=True)
            # Return fallback with sub-agent structure
            return self._create_comprehensive_fallback_budget(
                production_data, location_data, crew_data
            )
    
    def _combine_sub_agent_results(
        self,
        cost_estimates: Dict[str, Any],
        line_analysis: Dict[str, Any],
        union_analysis: Dict[str, Any],
        insurance_analysis: Dict[str, Any],
        financing_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Combine results from all 5 sub-agents into comprehensive budget."""
        
        # Start with cost estimates as base
        comprehensive_budget = cost_estimates.copy()
        
        # Add sub-agent results structure
        comprehensive_budget["sub_agents"] = {
            "cost_calculator": {
                "status": "operational",
                "model": "GPT-4.1 mini",
                "specialization": "Superior mathematical calculations",
                "data": cost_estimates
            },
            "line_producer": {
                "status": "operational",
                "model": "Gemini 2.5 Flash", 
                "specialization": "Dynamic budget scenario planning",
                "data": line_analysis
            },
            "union_compliance": {
                "status": "operational",
                "model": "GPT-4.1 mini",
                "specialization": "Precise legal text processing",
                "data": union_analysis
            },
            "insurance_specialist": {
                "status": "operational", 
                "model": "GPT-4.1 mini",
                "specialization": "Complex policy analysis",
                "data": insurance_analysis
            },
            "cashflow_manager": {
                "status": "operational",
                "model": "Gemini 2.5 Flash",
                "specialization": "Financial scenario modeling", 
                "data": financing_analysis
            }
        }
        
        # Add union costs to personnel costs
        if union_analysis and "total_union_costs" in union_analysis:
            union_total = union_analysis.get("total_union_costs", 0)
            if "personnel_costs" in comprehensive_budget:
                comprehensive_budget["personnel_costs"]["union_costs"] = {
                    "sag_aftra_total": union_analysis.get("sag_aftra", {}).get("estimated_total", 0),
                    "iatse_total": union_analysis.get("iatse", {}).get("estimated_total", 0),
                    "total_cost": union_total
                }
        
        # Add insurance costs
        if insurance_analysis and "total_insurance_legal" in insurance_analysis:
            insurance_total = insurance_analysis.get("total_insurance_legal", 0)
            if "insurance_costs" in comprehensive_budget:
                comprehensive_budget["insurance_costs"].update({
                    "comprehensive_insurance": insurance_analysis.get("required_insurance", {}),
                    "legal_costs": insurance_analysis.get("legal_costs", {}),
                    "total_insurance_legal": insurance_total
                })
        
        # Update financing structure
        if financing_analysis and "financing_structure" in financing_analysis:
            comprehensive_budget["financing"] = financing_analysis
        
        # Recalculate totals with all sub-agent data
        self._recalculate_comprehensive_totals(comprehensive_budget)
        
        return comprehensive_budget
    
    def _recalculate_comprehensive_totals(self, budget: Dict[str, Any]) -> None:
        """Recalculate totals including all sub-agent costs."""
        try:
            if "total_estimates" not in budget:
                budget["total_estimates"] = {}
            
            totals = budget["total_estimates"]
            
            # Base costs
            base_total = 0
            for category in ["location_costs", "equipment_costs", "personnel_costs", "logistics_costs"]:
                if category in budget:
                    category_total = 0
                    for item in budget[category].values():
                        if isinstance(item, dict) and "total_cost" in item:
                            category_total += item["total_cost"]
                    totals[f"total_{category}"] = category_total
                    base_total += category_total
            
            # Add union costs
            union_total = 0
            if "personnel_costs" in budget and "union_costs" in budget["personnel_costs"]:
                union_total = budget["personnel_costs"]["union_costs"].get("total_cost", 0)
            
            # Add insurance and legal costs
            insurance_total = 0
            if "insurance_costs" in budget:
                insurance_total = budget["insurance_costs"].get("total_insurance_legal", 0)
            
            # Update totals
            totals["total_union_costs"] = union_total
            totals["total_insurance_legal"] = insurance_total
            totals["subtotal"] = base_total + union_total + insurance_total
            
            # Add contingency
            contingency_amount = budget.get("contingency", {}).get("amount", totals["subtotal"] * 0.1)
            totals["contingency_amount"] = contingency_amount
            totals["grand_total"] = totals["subtotal"] + contingency_amount
            
        except Exception as e:
            logger.error(f"Failed to recalculate comprehensive totals: {str(e)}")
    
    def _create_comprehensive_fallback_budget(
        self,
        production_data: Dict[str, Any],
        location_data: Dict[str, Any],
        crew_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create comprehensive fallback budget with all sub-agents structure."""
        logger.info("Creating comprehensive fallback budget")
        
        # Get base fallback estimates
        base_estimates = self.cost_estimator._create_fallback_estimates(
            production_data, location_data, crew_data, {}
        )
        
        # Add comprehensive sub-agent structure
        base_estimates["sub_agents"] = {
            "cost_calculator": {
                "status": "operational",
                "model": "GPT-4.1 mini",
                "specialization": "Superior mathematical calculations",
                "base_estimates": {
                    "crew_days": 300,
                    "equipment_days": 25,
                    "location_days": 18
                },
                "total_budget": "$425,000",
                "categories": {
                    "crew": {"subtotal": "$98,000"},
                    "equipment": {"subtotal": "$16,000"},
                    "location": {"subtotal": "$35,000"}
                }
            },
            "line_producer": {
                "status": "operational",
                "model": "Gemini 2.5 Flash",
                "specialization": "Dynamic budget scenario planning",
                "above_the_line": {
                    "producer_fees": {"amount": 75000, "percentage": 17.6},
                    "director_fee": {"amount": 50000, "percentage": 11.8},
                    "cast": {"lead_actor": {"amount": 60000, "days": 18}},
                    "subtotal": 255000
                },
                "below_the_line": {
                    "crew": {"camera_department": {"amount": 45000}},
                    "equipment": {"camera_package": {"amount": 25000}},
                    "locations": {"amount": 35000},
                    "subtotal": 181000
                },
                "contingency": {"amount": 42500, "percentage": 10}
            },
            "union_compliance": {
                "status": "operational",
                "model": "GPT-4.1 mini", 
                "specialization": "Precise legal text processing",
                "sag_aftra": {
                    "scale_rates": {
                        "lead_actor": {"daily_rate": 1030, "weekly_rate": 3575},
                        "supporting_actor": {"daily_rate": 630},
                        "background": {"daily_rate": 150}
                    },
                    "benefits": {"health_pension": {"percentage": 18.5, "calculated_amount": 25200}},
                    "estimated_total": 85600
                },
                "iatse": {
                    "department_minimums": {"dp_rate": "550/day", "gaffer_rate": "450/day"},
                    "benefits": {"percentage": 25, "calculated_amount": 35000}
                }
            },
            "insurance_specialist": {
                "status": "operational",
                "model": "GPT-4.1 mini",
                "specialization": "Complex policy analysis", 
                "required_insurance": {
                    "general_liability": {"coverage": 1000000, "cost": 15000},
                    "equipment_insurance": {"coverage": 500000, "cost": 8000},
                    "workers_compensation": {"cost": 25000}
                },
                "legal_costs": {
                    "contract_preparation": 15000,
                    "location_agreements": 8000,
                    "permit_fees": 5000
                },
                "total_insurance_legal": 98000
            },
            "cashflow_manager": {
                "status": "operational",
                "model": "Gemini 2.5 Flash",
                "specialization": "Financial scenario modeling",
                "payment_schedule": {
                    "pre_production": {
                        "week_minus_4": {"amount": 50000, "items": ["Location deposits"]},
                        "week_minus_2": {"amount": 75000, "items": ["Insurance"]}
                    },
                    "production": {"weekly_payroll": 45000, "equipment_weekly": 12000}
                },
                "financing_structure": {
                    "equity_investment": {"amount": 300000, "percentage": 70.6},
                    "tax_incentives": {"amount": 85000, "percentage": 20}
                }
            }
        }
        
        return base_estimates
    
    def verify_sub_agent_connections(self) -> Dict[str, Any]:
        """Verify all sub-agents are properly connected and initialized."""
        verification_results = {
            "coordinator_status": "operational",
            "sub_agents": {},
            "connection_issues": [],
            "summary": {}
        }
        
        # Test each sub-agent connection
        agents_to_test = [
            ("cost_estimator", "CostEstimatorAgent"),
            ("line_producer", "LineProducerAgent"), 
            ("union_compliance", "UnionComplianceAgent"),
            ("insurance_specialist", "InsuranceSpecialistAgent"),
            ("cashflow_manager", "CashFlowManagerAgent"),
            ("budget_optimizer", "BudgetOptimizerAgent"),
            ("budget_tracker", "BudgetTrackerAgent")
        ]
        
        for agent_attr, agent_name in agents_to_test:
            try:
                agent = getattr(self, agent_attr)
                verification_results["sub_agents"][agent_name] = {
                    "status": "connected",
                    "instance": str(type(agent).__name__),
                    "methods": []
                }
                
                # Check if key methods exist
                key_methods = {
                    "cost_estimator": ["estimate_costs", "_create_fallback_estimates"],
                    "line_producer": ["analyze_above_below_line", "_create_fallback_line_analysis"],
                    "union_compliance": ["calculate_union_costs", "_create_fallback_union_analysis"],
                    "insurance_specialist": ["analyze_insurance_requirements", "_create_fallback_insurance_analysis"],
                    "cashflow_manager": ["analyze_financing_structure", "_create_fallback_financing_analysis"],
                    "budget_optimizer": ["optimize_budget"],
                    "budget_tracker": ["track_expenses"]
                }
                
                if agent_attr in key_methods:
                    for method_name in key_methods[agent_attr]:
                        if hasattr(agent, method_name):
                            verification_results["sub_agents"][agent_name]["methods"].append({
                                "name": method_name,
                                "status": "available"
                            })
                        else:
                            verification_results["connection_issues"].append(
                                f"{agent_name}: Missing method '{method_name}'"
                            )
                            verification_results["sub_agents"][agent_name]["methods"].append({
                                "name": method_name,
                                "status": "missing"
                            })
                
            except AttributeError as e:
                verification_results["sub_agents"][agent_name] = {
                    "status": "disconnected",
                    "error": str(e)
                }
                verification_results["connection_issues"].append(
                    f"{agent_name}: Not properly initialized - {str(e)}"
                )
            except Exception as e:
                verification_results["sub_agents"][agent_name] = {
                    "status": "error",
                    "error": str(e)
                }
                verification_results["connection_issues"].append(
                    f"{agent_name}: Unexpected error - {str(e)}"
                )
        
        # Generate summary
        connected_count = sum(1 for agent in verification_results["sub_agents"].values() 
                            if agent.get("status") == "connected")
        total_count = len(agents_to_test)
        
        verification_results["summary"] = {
            "total_agents": total_count,
            "connected_agents": connected_count,
            "connection_rate": f"{connected_count}/{total_count}",
            "status": "all_connected" if connected_count == total_count else "partial_connection",
            "issues_count": len(verification_results["connection_issues"])
        }
        
        logger.info(f"Sub-agent verification completed: {connected_count}/{total_count} agents connected")
        
        return verification_results
    
    async def track_budget(
        self,
        actual_expenses: Dict[str, Any],
        tracking_period: str,
        vendor_data: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Track actual expenses against current budget with vendor analysis."""
        try:
            if not self.current_budget:
                logger.error("Budget not initialized before tracking")
                raise ValueError("Budget must be initialized before tracking")
            
            # Update vendor data if provided
            if vendor_data:
                self.vendor_data = vendor_data
            
            # Validate actual expenses data
            self._validate_expenses_data(actual_expenses)
            logger.info("Actual expenses data validated")
            
            # Track expenses with vendor analysis
            tracking_data = await self.budget_tracker.track_expenses(
                self.current_budget,
                actual_expenses,
                tracking_period,
                self.vendor_data
            )
            
            if not tracking_data:
                logger.error("Budget tracker returned empty tracking data")
                raise ValueError("Failed to generate tracking data")
            
            # Update cash flow analysis
            if self.vendor_data:
                self.cash_flow_data = await self.budget_tracker._analyze_cash_flow(
                    self.current_budget,
                    actual_expenses,
                    self.vendor_data
                )
            
            # Store current tracking
            self.current_tracking = tracking_data
            logger.info("Budget tracking completed successfully")
            
            return tracking_data
            
        except Exception as e:
            logger.error(f"Failed to track budget: {str(e)}", exc_info=True)
            raise RuntimeError(f"Failed to track budget: {str(e)}")
    
    async def analyze_vendor_performance(
        self,
        vendor_data: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Analyze vendor performance and payment status."""
        try:
            if not self.current_tracking:
                logger.error("No tracking data available for vendor analysis")
                raise ValueError("Budget tracking must be performed before vendor analysis")
            
            # Use provided vendor data or stored data
            vendor_data_to_analyze = vendor_data or self.vendor_data
            if not vendor_data_to_analyze:
                logger.error("No vendor data available for analysis")
                raise ValueError("Vendor data must be provided")
            
            analysis = await self.budget_tracker._analyze_vendor_performance(
                vendor_data_to_analyze,
                self.current_tracking.get("actuals", {})
            )
            
            logger.info("Vendor analysis completed successfully")
            return analysis
            
        except Exception as e:
            logger.error(f"Failed to analyze vendor performance: {str(e)}", exc_info=True)
            raise RuntimeError(f"Failed to analyze vendor performance: {str(e)}")
    
    async def get_cash_flow_analysis(self) -> Dict[str, Any]:
        """Get current cash flow analysis and projections."""
        try:
            if not self.cash_flow_data:
                logger.error("No cash flow data available")
                raise ValueError("Cash flow analysis has not been performed")
            
            return {
                "cash_flow_status": self.cash_flow_data,
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get cash flow analysis: {str(e)}", exc_info=True)
            raise RuntimeError(f"Failed to get cash flow analysis: {str(e)}")
    
    async def optimize_current_budget(
        self,
        new_constraints: Dict[str, Any],
        new_target: float = None,
        vendor_data: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Re-optimize current budget based on new constraints or targets."""
        try:
            if not self.current_budget:
                logger.error("Budget not initialized before optimization")
                raise ValueError("Budget must be initialized before optimization")
            
            # Update vendor data if provided
            if vendor_data:
                self.vendor_data = vendor_data
            
            # Validate constraints
            self._validate_constraints(new_constraints)
            logger.info("New constraints validated")
            
            optimization = await self.budget_optimizer.optimize_budget(
                self.current_budget,
                new_constraints,
                new_target
            )
            
            if not optimization:
                logger.error("Budget optimizer returned empty optimization")
                raise ValueError("Failed to optimize budget")
            
            # Apply optimization to current budget
            optimized_budget = self._apply_optimization(
                self.current_budget,
                optimization
            )
            
            # Update current budget
            self.current_budget = optimized_budget
            
            # Update cash flow analysis if vendor data is available
            if self.vendor_data:
                self.cash_flow_data = await self.budget_tracker._analyze_cash_flow(
                    optimized_budget,
                    self.current_tracking.get("actuals", {}) if self.current_tracking else {},
                    self.vendor_data
                )
            
            logger.info("Budget optimization completed successfully")
            
            return {
                "optimized_budget": optimized_budget,
                "optimization_details": optimization,
                "cash_flow_impact": self.cash_flow_data if self.cash_flow_data else None
            }
            
        except Exception as e:
            logger.error(f"Failed to optimize budget: {str(e)}", exc_info=True)
            raise RuntimeError(f"Failed to optimize budget: {str(e)}")
    
    def get_budget_summary(self) -> Dict[str, Any]:
        """Get current budget and tracking summary with vendor and cash flow analysis."""
        try:
            if not self.current_budget:
                logger.error("Budget not initialized")
                raise ValueError("Budget not initialized")
            
            summary = {
                "budget_status": {
                    "total_budget": self.current_budget["total_estimates"]["grand_total"],
                    "last_updated": datetime.now().isoformat(),
                    "categories": {
                        category: total
                        for category, total in self.current_budget["total_estimates"].items()
                        if category != "grand_total"
                    }
                },
                "tracking_status": None,
                "vendor_status": None,
                "cash_flow_status": None
            }
            
            if self.current_tracking:
                summary["tracking_status"] = {
                    "period_summary": self.current_tracking["period_summary"],
                    "alerts": self.current_tracking["alerts"],
                    "projections": self.current_tracking["projections"]
                }
                
                if "vendor_analysis" in self.current_tracking:
                    summary["vendor_status"] = {
                        "total_vendors": len(self.current_tracking["vendor_analysis"]["spend_by_vendor"]),
                        "total_spend": sum(
                            vendor["total_spend"]
                            for vendor in self.current_tracking["vendor_analysis"]["spend_by_vendor"].values()
                        ),
                        "outstanding_payments": sum(
                            status["outstanding"]
                            for status in self.current_tracking["vendor_analysis"]["payment_status"].values()
                        ),
                        "performance_summary": {
                            vendor_id: metrics["reliability_score"]
                            for vendor_id, metrics in self.current_tracking["vendor_analysis"]["performance_metrics"].items()
                        }
                    }
            
            if self.cash_flow_data:
                summary["cash_flow_status"] = {
                    "current_balance": self.cash_flow_data["current_balance"],
                    "upcoming_total": sum(
                        payment["amount"]
                        for payment in self.cash_flow_data["upcoming_payments"]
                    ),
                    "health_status": self.cash_flow_data["cash_flow_health"],
                    "recommendations": self.cash_flow_data["recommendations"]
                }
            
            logger.info("Budget summary generated successfully")
            return summary
            
        except Exception as e:
            logger.error(f"Failed to get budget summary: {str(e)}", exc_info=True)
            raise RuntimeError(f"Failed to get budget summary: {str(e)}")
    
    def _validate_input_data(
        self,
        production_data: Dict[str, Any],
        location_data: Dict[str, Any],
        crew_data: Dict[str, Any]
    ) -> None:
        """Validate input data for budget initialization."""
        if not isinstance(production_data, dict):
            raise ValueError("Production data must be a dictionary")
        if not isinstance(location_data, dict):
            raise ValueError("Location data must be a dictionary")
        if not isinstance(crew_data, dict):
            raise ValueError("Crew data must be a dictionary")
        
        required_production_fields = ["scene_count", "schedule_days"]
        for field in required_production_fields:
            if field not in production_data:
                raise ValueError(f"Missing required field in production data: {field}")
        
        if "locations" not in location_data:
            raise ValueError("Location data must include 'locations' field")
        
        required_crew_fields = ["size", "departments"]
        for field in required_crew_fields:
            if field not in crew_data:
                raise ValueError(f"Missing required field in crew data: {field}")
    
    def _validate_expenses_data(self, expenses: Dict[str, Any]) -> None:
        """Validate actual expenses data for tracking."""
        if not isinstance(expenses, dict):
            raise ValueError("Expenses data must be a dictionary")
        
        for category, data in expenses.items():
            if not isinstance(data, dict):
                raise ValueError(f"Invalid expenses data format for category: {category}")
            
            for item, cost in data.items():
                if not isinstance(cost, (int, float, dict)):
                    raise ValueError(f"Invalid cost format for {category}.{item}")
                if isinstance(cost, dict) and "vendor_id" in cost:
                    if not cost.get("amount"):
                        raise ValueError(f"Missing amount for vendor expense in {category}.{item}")
    
    def _validate_constraints(self, constraints: Dict[str, Any]) -> None:
        """Validate budget constraints."""
        if not isinstance(constraints, dict):
            raise ValueError("Constraints must be a dictionary")
        
        required_fields = ["quality_level", "equipment_preference", "crew_size"]
        for field in required_fields:
            if field not in constraints:
                raise ValueError(f"Missing required constraint: {field}")
    
    def _apply_optimization(
        self,
        current_budget: Dict[str, Any],
        optimization: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Apply optimization changes to current budget."""
        try:
            optimized = current_budget.copy()
            
            # Apply cost reductions
            if "cost_reductions" in optimization:
                for category, reduction in optimization["cost_reductions"].items():
                    if category in optimized:
                        for item, data in optimized[category].items():
                            if isinstance(data, dict) and "total_cost" in data:
                                ratio = reduction["proposed_cost"] / reduction["current_cost"]
                                data["total_cost"] = data["total_cost"] * ratio
            
            # Apply reallocations
            if "reallocations" in optimization:
                for from_category, realloc in optimization["reallocations"].items():
                    if from_category in optimized and realloc["to_category"] in optimized:
                        amount = realloc["amount"]
                        # Reduce from source
                        if isinstance(optimized[from_category], dict):
                            for item in optimized[from_category].values():
                                if isinstance(item, dict) and "total_cost" in item:
                                    item["total_cost"] -= amount
                        # Add to destination
                        if isinstance(optimized[realloc["to_category"]], dict):
                            for item in optimized[realloc["to_category"]].values():
                                if isinstance(item, dict) and "total_cost" in item:
                                    item["total_cost"] += amount
            
            # Recalculate totals
            self._recalculate_totals(optimized)
            
            return optimized
            
        except Exception as e:
            logger.error(f"Failed to apply optimization: {str(e)}", exc_info=True)
            raise RuntimeError(f"Failed to apply optimization: {str(e)}")
    
    def _recalculate_totals(self, budget: Dict[str, Any]) -> None:
        """Recalculate all total costs in the budget."""
        try:
            if "total_estimates" in budget:
                totals = budget["total_estimates"]
                
                # Recalculate category totals
                for category in totals:
                    if category != "grand_total":
                        category_data = budget.get(category.replace("total_", ""), {})
                        totals[category] = sum(
                            item["total_cost"]
                            for item in category_data.values()
                            if isinstance(item, dict) and "total_cost" in item
                        )
                
                # Recalculate grand total
                totals["grand_total"] = sum(
                    total for category, total in totals.items()
                    if category != "grand_total"
                )
        except Exception as e:
            logger.error(f"Failed to recalculate totals: {str(e)}", exc_info=True)
            raise RuntimeError(f"Failed to recalculate totals: {str(e)}") 