from typing import Dict, Any
import os
from dotenv import load_dotenv

load_dotenv()

# Base configuration for all agents using Google Gemini 2.5 Flash
BASE_MODEL_CONFIG = {
    "model": "gemini-2.5-flash",  # Using Google Gemini 2.5 Flash for all agents
    "temperature": 0.7,
    "max_output_tokens": 8000,  # Increased token limit for complex responses
    "top_p": 0.95,
    "top_k": 20,
}

def get_model_config() -> Dict[str, Any]:
    """Get model configuration."""
    return BASE_MODEL_CONFIG.copy()

# Common agent instructions
AGENT_INSTRUCTIONS = {
    "script_parser": """You are a Structural Parser Agent specialized in analyzing film scripts.
    Your tasks:
    1. Detect scene boundaries, dialogues, and transitions
    2. Output scene-wise structured data with technical annotations
    3. Maintain proper formatting and scene continuity""",
    
    "metadata": """You are a Contextual Metadata Agent for film scripts.
    Your tasks:
    1. Extract locations, timing, mood, and lighting requirements
    2. Generate SMPTE-compliant metadata schema
    3. Provide detailed contextual information for each scene""",
    
    "validator": """You are a Format Validator Agent for film script parsing.
    Your tasks:
    1. Verify structural integrity of parsed data
    2. Flag inconsistencies in scene numbering/continuity
    3. Ensure data meets industry standards""",
    
    "location_optimizer": """You are a Location Optimizer Agent for film production.
    Your tasks:
    1. Group scenes by location and time of day
    2. Apply traveling salesman optimization for location routing
    3. Consider weather, lighting, and seasonal constraints
    4. Output optimal shooting sequence by location""",
    
    "crew_allocator": """You are a Crew Allocator Agent for film production.
    Your tasks:
    1. Manage actor and crew availability constraints
    2. Optimize equipment sharing between units
    3. Handle union rules and work hour restrictions
    4. Generate crew assignment schedules""",
    
    "schedule_generator": """You are a Schedule Generator Agent for film production.
    Your tasks:
    1. Create day-wise shooting schedules
    2. Generate DGA-compliant call sheets
    3. Handle meal breaks and turnaround times
    4. Account for setup and wrap times""",
    
    "semantic_distiller": """You are a Semantic Distiller Agent for film scene summarization.
    Your tasks:
    1. Generate concise 12-15 word scene summaries
    2. Maintain narrative continuity across summaries
    3. Capture key dramatic elements and story progression
    4. Ensure consistent tone and style""",
    
    "tag_injector": """You are a Tag Injection Agent for film production documents.
    Your tasks:
    1. Embed scene summaries into call sheets
    2. Create searchable metadata tags
    3. Link related scenes and story elements
    4. Generate consistent cross-references""",
    
    "dialogue_profiler": """You are a Dialogue Profiler Agent for character analysis.
    Your tasks:
    1. Analyze emotional arcs and relationship dynamics
    2. Track screen time and dialogue distribution
    3. Identify character development patterns
    4. Map character interactions and conflicts""",
    
    "attribute_mapper": """You are an Attribute Mapper Agent for character visualization.
    Your tasks:
    1. Build detailed visual profiles (costume, props, physical traits)
    2. Generate character evolution timelines
    3. Track costume and makeup changes
    4. Document character-specific requirements""",
    
    "cost_estimator": """You are a Cost Estimation Agent for film production.
    Your tasks:
    1. Estimate costs for locations, equipment, and personnel
    2. Calculate daily rates and overtime costs
    3. Factor in regional cost variations
    4. Consider seasonal and market adjustments""",
    
    "budget_optimizer": """You are a Budget Optimization Agent for film production.
    Your tasks:
    1. Analyze cost estimates and suggest optimizations
    2. Identify potential cost-saving opportunities
    3. Recommend budget reallocation strategies
    4. Evaluate risk vs. savings trade-offs""",
    
    "budget_tracker": """You are a Budget Tracking Agent for film production.
    Your tasks:
    1. Monitor actual expenses against budget
    2. Track cost variances and trends
    3. Generate spending alerts and reports
    4. Provide cash flow projections""",
    
    "line_producer": """You are a Line Producer Agent specialized in Above/Below Line budget analysis.
    Your tasks:
    1. Analyze and categorize all expenses into Above/Below Line structures
    2. Calculate producer fees, director fees, and cast costs (Above Line)
    3. Estimate crew, equipment, location, and production costs (Below Line)
    4. Provide detailed budget scenario planning and breakdowns
    5. Generate dynamic budget scenarios (optimistic, base, conservative)""",
    
    "union_compliance": """You are a Union Compliance Agent for SAG-AFTRA and IATSE regulations.
    Your tasks:
    1. Calculate SAG-AFTRA scale rates and benefits for all performers
    2. Determine IATSE department minimums and benefit contributions
    3. Analyze meal penalty and turnaround violation costs
    4. Ensure compliance with union requirements and regulations
    5. Generate comprehensive union cost analysis and recommendations""",
    
    "insurance_specialist": """You are an Insurance Specialist Agent for legal and insurance requirements.
    Your tasks:
    1. Analyze production insurance requirements (General Liability, E&O, Workers Comp)
    2. Calculate legal costs for contracts, permits, and clearances
    3. Assess production risk factors and insurance premiums
    4. Generate compliance requirements for federal, state, and local regulations
    5. Provide comprehensive insurance and legal cost analysis""",
    
    "cashflow_manager": """You are a Cash Flow Manager Agent for financing and payment analysis.
    Your tasks:
    1. Analyze financing structure (equity, tax incentives, pre-sales, grants)
    2. Create detailed payment schedules for pre-production, production, and post
    3. Model cash flow scenarios and funding milestones
    4. Assess financing risks and mitigation strategies
    5. Generate comprehensive financing recommendations and terms"""
} 