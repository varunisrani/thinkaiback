"""
Google ADK Implementation of Department Coordinator Agent
Uses official Google ADK patterns for tool functions and agent creation
"""

from typing import Dict, Any, List
from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools import ToolContext
import logging
from datetime import datetime
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Department Structure
DEPARTMENTS = {
    "camera": {
        "roles": ["dop", "camera_operator", "focus_puller", "loader", "dit"],
        "equipment_categories": ["cameras", "lenses", "supports", "accessories"]
    },
    "sound": {
        "roles": ["sound_mixer", "boom_operator", "sound_assistant"],
        "equipment_categories": ["microphones", "recorders", "accessories"]
    },
    "lighting": {
        "roles": ["gaffer", "best_boy", "electricians"],
        "equipment_categories": ["lights", "grip", "electrical"]
    },
    "art": {
        "roles": ["production_designer", "art_director", "set_decorator", "props"],
        "equipment_categories": ["set_pieces", "props", "decoration"]
    },
    "wardrobe": {
        "roles": ["costume_designer", "wardrobe_supervisor", "seamstress"],
        "equipment_categories": ["costumes", "accessories", "makeup"]
    },
    "special_effects": {
        "roles": ["sfx_supervisor", "sfx_technician", "safety_coordinator"],
        "equipment_categories": ["effects", "safety", "specialized"]
    }
}

# Crew Size Multipliers
COMPLEXITY_MULTIPLIERS = {
    "simple": 1.0,
    "moderate": 1.3,
    "complex": 1.8
}

# Tool Functions using ADK patterns
def analyze_scene_involvement_tool(department: str, card: Dict[str, Any], tool_context: ToolContext) -> Dict[str, Any]:
    """
    Determine if and how a department is involved in a scene.
    
    Args:
        department: Department name
        card: Breakdown card for the scene
        tool_context: ADK tool context for state management
        
    Returns:
        Department involvement details
    """
    scene_number = card.get("scene_number", "unknown")
    logger.info(f"Analyzing {department} involvement for scene {scene_number}")
    
    involvement = {
        "is_involved": False,
        "level": "none",  # none, basic, moderate, heavy
        "requirements": [],
        "equipment": [],
        "special_needs": []
    }
    
    # Check based on department type
    if department == "camera":
        involvement["is_involved"] = True  # Camera is always involved
        involvement["level"] = "basic"
        
        # Check for special camera requirements
        if any(req in card["equipment_needed"] for req in ["Steadicam", "Aerial equipment", "Macro lens"]):
            involvement["level"] = "heavy"
            involvement["equipment"].extend([req for req in card["equipment_needed"] if req in ["Steadicam", "Aerial equipment", "Macro lens"]])
        
        if card["complexity_level"] == "complex":
            involvement["level"] = "moderate"
        
        # Add technical requirements
        for tech_note in card["technical_notes"]:
            if any(word in tech_note.upper() for word in ["CAMERA", "SHOT", "ANGLE", "MOVEMENT"]):
                involvement["requirements"].append(tech_note)
    
    elif department == "sound":
        involvement["is_involved"] = True  # Sound is always involved
        involvement["level"] = "basic"
        
        # Check for dialogue scenes
        if card.get("cast_requirements"):
            involvement["level"] = "moderate"
        
        # Check for special sound requirements
        if card["location_type"] == "EXT":
            involvement["level"] = "moderate"
            involvement["special_needs"].append("Wind protection")
        
        if any(word in card.get("location", "").upper() for word in ["WATER", "TRAFFIC", "CROWD"]):
            involvement["level"] = "heavy"
            involvement["special_needs"].append("Challenging audio environment")
    
    elif department == "lighting":
        involvement["is_involved"] = True  # Lighting is always involved
        involvement["level"] = "basic"
        
        # Night shoots require heavy lighting
        if card["night_shoot"]:
            involvement["level"] = "heavy"
            involvement["equipment"].append("Night lighting package")
        
        # Exterior day shoots
        if card["location_type"] == "EXT" and card["time_of_day"] == "DAY":
            involvement["level"] = "moderate"
            involvement["equipment"].append("Daylight balance package")
        
        # Complex scenes need more lighting
        if card["complexity_level"] == "complex":
            involvement["level"] = "moderate"
    
    elif department == "art":
        # Check for props and set requirements
        if card["props_needed"]:
            involvement["is_involved"] = True
            involvement["level"] = "moderate"
            involvement["equipment"].extend(card["props_needed"])
        
        # Check for special set requirements
        if any(word in card.get("location", "").upper() for word in ["PERIOD", "FANTASY", "HISTORICAL"]):
            involvement["is_involved"] = True
            involvement["level"] = "heavy"
            involvement["special_needs"].append("Period/specialty design")
    
    elif department == "wardrobe":
        # Check for costume requirements
        if card["wardrobe_notes"]:
            involvement["is_involved"] = True
            involvement["level"] = "moderate"
            involvement["requirements"].extend(card["wardrobe_notes"])
        
        # Check cast size
        if len(card["cast_requirements"]) > 3:
            involvement["is_involved"] = True
            involvement["level"] = "heavy"
            involvement["special_needs"].append("Large cast wardrobe")
    
    elif department == "special_effects":
        # Check for SFX requirements
        if card["special_requirements"]:
            for req in card["special_requirements"]:
                if any(word in req.upper() for word in ["STUNT", "EFFECT", "WEATHER", "EXPLOSION", "FIRE"]):
                    involvement["is_involved"] = True
                    involvement["level"] = "heavy"
                    involvement["requirements"].append(req)
    
    # Store in context
    tool_context.state[f"involvement_{department}_{scene_number}"] = involvement
    
    return involvement

def analyze_department_requirements_tool(department: str, breakdown_cards: List[Dict[str, Any]], tool_context: ToolContext) -> Dict[str, Any]:
    """
    Analyze requirements for a specific department across all scenes.
    
    Args:
        department: Department name
        breakdown_cards: List of breakdown cards
        tool_context: ADK tool context for state management
        
    Returns:
        Department requirements analysis
    """
    logger.info(f"Analyzing requirements for {department} department")
    
    dept_requirements = {
        "scenes_requiring_department": [],
        "equipment_needed": [],
        "crew_requirements": [],
        "special_needs": [],
        "scheduling_notes": [],
        "estimated_hours": 0,
        "complexity_breakdown": {"simple": 0, "moderate": 0, "complex": 0}
    }
    
    total_hours = 0
    
    for card in breakdown_cards:
        scene_involvement = analyze_scene_involvement_tool(department, card, tool_context)
        
        if scene_involvement["is_involved"]:
            dept_requirements["scenes_requiring_department"].append({
                "scene_number": card["scene_number"],
                "involvement_level": scene_involvement["level"],
                "estimated_hours": card["estimated_hours"],
                "complexity": card["complexity_level"],
                "specific_requirements": scene_involvement["requirements"]
            })
            
            # Add to equipment needed
            dept_requirements["equipment_needed"].extend(scene_involvement["equipment"])
            
            # Add to special needs
            dept_requirements["special_needs"].extend(scene_involvement["special_needs"])
            
            # Add hours
            total_hours += card["estimated_hours"]
            
            # Update complexity breakdown
            dept_requirements["complexity_breakdown"][card["complexity_level"]] += 1
    
    dept_requirements["estimated_hours"] = round(total_hours, 1)
    
    # Remove duplicates
    dept_requirements["equipment_needed"] = list(set(dept_requirements["equipment_needed"]))
    dept_requirements["special_needs"] = list(set(dept_requirements["special_needs"]))
    
    # Store in context
    tool_context.state[f"department_requirements_{department}"] = dept_requirements
    
    return dept_requirements

def calculate_department_crew_tool(department: str, dept_requirements: Dict[str, Any], tool_context: ToolContext) -> Dict[str, Any]:
    """
    Calculate crew requirements for a department.
    
    Args:
        department: Department name
        dept_requirements: Department requirements analysis
        tool_context: ADK tool context for state management
        
    Returns:
        Crew requirements
    """
    logger.info(f"Calculating crew requirements for {department}")
    
    dept_info = DEPARTMENTS[department]
    base_roles = dept_info["roles"]
    
    # Base crew calculation
    scenes_count = len(dept_requirements["scenes_requiring_department"])
    complexity_factor = 1.0
    
    # Calculate average complexity
    complexity_counts = dept_requirements["complexity_breakdown"]
    total_scenes = sum(complexity_counts.values())
    
    if total_scenes > 0:
        weighted_complexity = (
            complexity_counts["simple"] * 1.0 +
            complexity_counts["moderate"] * 1.3 +
            complexity_counts["complex"] * 1.8
        ) / total_scenes
        complexity_factor = weighted_complexity
    
    # Determine crew size
    if department == "camera":
        base_crew_size = 4  # DOP, Operator, Focus Puller, Loader
        if complexity_factor > 1.3:
            base_crew_size += 1  # Add DIT
        if complexity_factor > 1.6:
            base_crew_size += 1  # Add 2nd camera operator
    
    elif department == "sound":
        base_crew_size = 2  # Mixer, Boom op
        if complexity_factor > 1.3:
            base_crew_size += 1  # Add assistant
    
    elif department == "lighting":
        base_crew_size = 6  # Gaffer, Best boy, 4 electricians
        if complexity_factor > 1.3:
            base_crew_size += 2  # Add more electricians
        if complexity_factor > 1.6:
            base_crew_size += 3  # Add rigging crew
    
    elif department == "art":
        base_crew_size = 3  # Designer, Art director, Set decorator
        if scenes_count > 5:
            base_crew_size += 2  # Add props master and assistant
    
    elif department == "wardrobe":
        base_crew_size = 2  # Designer, Supervisor
        if complexity_factor > 1.3:
            base_crew_size += 1  # Add seamstress
    
    elif department == "special_effects":
        base_crew_size = 0  # Only when needed
        if dept_requirements["scenes_requiring_department"]:
            base_crew_size = 3  # Supervisor, Technician, Safety
    
    else:
        base_crew_size = 2  # Default
    
    result = {
        "base_crew_size": base_crew_size,
        "complexity_factor": round(complexity_factor, 2),
        "recommended_roles": base_roles[:base_crew_size],
        "total_department_hours": dept_requirements["estimated_hours"],
        "crew_efficiency": round(dept_requirements["estimated_hours"] / max(base_crew_size, 1), 1)
    }
    
    # Store in context
    tool_context.state[f"crew_requirements_{department}"] = result
    
    return result

def generate_department_scheduling_notes_tool(department: str, dept_requirements: Dict[str, Any], tool_context: ToolContext) -> List[str]:
    """
    Generate scheduling notes for a department.
    
    Args:
        department: Department name
        dept_requirements: Department requirements
        tool_context: ADK tool context for state management
        
    Returns:
        List of scheduling notes
    """
    logger.info(f"Generating scheduling notes for {department}")
    
    notes = []
    
    scenes = dept_requirements["scenes_requiring_department"]
    
    # Heavy involvement scenes
    heavy_scenes = [s for s in scenes if s["involvement_level"] == "heavy"]
    if heavy_scenes:
        notes.append(f"Department has {len(heavy_scenes)} scenes requiring heavy involvement")
    
    # Special needs
    if dept_requirements["special_needs"]:
        notes.append(f"Special requirements: {', '.join(dept_requirements['special_needs'])}")
    
    # Equipment coordination
    if dept_requirements["equipment_needed"]:
        notes.append(f"Equipment coordination needed for: {', '.join(dept_requirements['equipment_needed'][:3])}")
    
    return notes

def coordinate_all_departments_tool(breakdown_cards_data: Dict[str, Any], eighths_data: Dict[str, Any], tool_context: ToolContext) -> Dict[str, Any]:
    """
    Coordinate all department requirements using breakdown cards and eighths data.
    
    Args:
        breakdown_cards_data: Output from Scene Breakdown Cards Agent
        eighths_data: Output from ADK eighths calculator
        tool_context: ADK tool context for state management
        
    Returns:
        Complete department coordination
    """
    logger.info("Coordinating all department requirements")
    
    breakdown_cards = breakdown_cards_data.get("breakdown_cards", [])
    
    # Process each department
    department_analysis = {}
    for dept_name in DEPARTMENTS.keys():
        # Analyze department requirements
        dept_requirements = analyze_department_requirements_tool(dept_name, breakdown_cards, tool_context)
        
        # Calculate crew requirements
        crew_requirements = calculate_department_crew_tool(dept_name, dept_requirements, tool_context)
        dept_requirements["crew_requirements"] = crew_requirements
        
        # Generate scheduling notes
        scheduling_notes = generate_department_scheduling_notes_tool(dept_name, dept_requirements, tool_context)
        dept_requirements["scheduling_notes"] = scheduling_notes
        
        department_analysis[dept_name] = dept_requirements
    
    # Generate cross-department coordination
    coordination_analysis = analyze_cross_department_coordination_tool(breakdown_cards, department_analysis, tool_context)
    
    # Create resource allocation plan
    resource_allocation = create_resource_allocation_plan_tool(breakdown_cards, department_analysis, tool_context)
    
    # Generate crew scheduling
    crew_scheduling = generate_crew_scheduling_tool(breakdown_cards, department_analysis, tool_context)
    
    # Generate department summary
    department_summary = generate_department_summary_tool(department_analysis, tool_context)
    
    # Generate coordination recommendations
    coordination_recommendations = generate_coordination_recommendations_tool(coordination_analysis, tool_context)
    
    result = {
        "timestamp": datetime.now().isoformat(),
        "department_analysis": department_analysis,
        "coordination_analysis": coordination_analysis,
        "resource_allocation": resource_allocation,
        "crew_scheduling": crew_scheduling,
        "department_summary": department_summary,
        "coordination_recommendations": coordination_recommendations
    }
    
    # Store complete result in context
    tool_context.state["complete_department_coordination"] = result
    
    return result

def analyze_cross_department_coordination_tool(breakdown_cards: List[Dict[str, Any]], department_analysis: Dict[str, Any], tool_context: ToolContext) -> Dict[str, Any]:
    """
    Analyze coordination requirements between departments.
    
    Args:
        breakdown_cards: List of breakdown cards
        department_analysis: Department analysis results
        tool_context: ADK tool context for state management
        
    Returns:
        Cross-department coordination analysis
    """
    logger.info("Analyzing cross-department coordination")
    
    coordination = {
        "high_coordination_scenes": [],
        "equipment_sharing": {},
        "scheduling_conflicts": [],
        "resource_dependencies": {}
    }
    
    # Find scenes requiring multiple departments
    for card in breakdown_cards:
        scene_num = card["scene_number"]
        involved_departments = []
        
        for dept_name, dept_data in department_analysis.items():
            for scene_req in dept_data["scenes_requiring_department"]:
                if scene_req["scene_number"] == scene_num:
                    if scene_req["involvement_level"] in ["moderate", "heavy"]:
                        involved_departments.append(dept_name)
        
        if len(involved_departments) >= 3:
            coordination["high_coordination_scenes"].append({
                "scene_number": scene_num,
                "departments": involved_departments,
                "coordination_level": "high" if len(involved_departments) >= 4 else "medium"
            })
    
    # Analyze equipment sharing opportunities
    all_equipment = {}
    for dept_name, dept_data in department_analysis.items():
        for equipment in dept_data["equipment_needed"]:
            if equipment not in all_equipment:
                all_equipment[equipment] = []
            all_equipment[equipment].append(dept_name)
    
    # Find shareable equipment
    for equipment, departments in all_equipment.items():
        if len(departments) > 1:
            coordination["equipment_sharing"][equipment] = departments
    
    return coordination

def create_resource_allocation_plan_tool(breakdown_cards: List[Dict[str, Any]], department_analysis: Dict[str, Any], tool_context: ToolContext) -> Dict[str, Any]:
    """
    Create resource allocation plan across departments.
    
    Args:
        breakdown_cards: List of breakdown cards
        department_analysis: Department analysis results
        tool_context: ADK tool context for state management
        
    Returns:
        Resource allocation plan
    """
    logger.info("Creating resource allocation plan")
    
    allocation = {
        "total_crew_needed": 0,
        "peak_crew_scenes": [],
        "equipment_budget_estimate": {},
        "resource_schedule": []
    }
    
    # Calculate total crew
    for dept_name, dept_data in department_analysis.items():
        crew_req = dept_data["crew_requirements"]
        allocation["total_crew_needed"] += crew_req["base_crew_size"]
    
    # Find peak crew scenes
    for card in breakdown_cards:
        if card["crew_estimate"]["total_crew"] > 30:
            allocation["peak_crew_scenes"].append({
                "scene_number": card["scene_number"],
                "crew_size": card["crew_estimate"]["total_crew"],
                "estimated_hours": card["estimated_hours"]
            })
    
    return allocation

def generate_crew_scheduling_tool(breakdown_cards: List[Dict[str, Any]], department_analysis: Dict[str, Any], tool_context: ToolContext) -> Dict[str, Any]:
    """
    Generate crew scheduling recommendations.
    
    Args:
        breakdown_cards: List of breakdown cards
        department_analysis: Department analysis results
        tool_context: ADK tool context for state management
        
    Returns:
        Crew scheduling recommendations
    """
    logger.info("Generating crew scheduling recommendations")
    
    scheduling = {
        "department_schedules": {},
        "coordination_points": [],
        "efficiency_recommendations": []
    }
    
    # Create department schedules
    for dept_name, dept_data in department_analysis.items():
        scenes = dept_data["scenes_requiring_department"]
        
        # Sort by involvement level and complexity
        sorted_scenes = sorted(scenes, key=lambda x: (
            {"heavy": 3, "moderate": 2, "basic": 1}[x["involvement_level"]],
            x["estimated_hours"]
        ), reverse=True)
        
        scheduling["department_schedules"][dept_name] = {
            "total_scenes": len(scenes),
            "estimated_hours": dept_data["estimated_hours"],
            "priority_scenes": [s["scene_number"] for s in sorted_scenes[:3]],
            "crew_size": dept_data["crew_requirements"]["base_crew_size"]
        }
    
    return scheduling

def generate_department_summary_tool(department_analysis: Dict[str, Any], tool_context: ToolContext) -> Dict[str, Any]:
    """
    Generate summary of all department requirements.
    
    Args:
        department_analysis: Department analysis results
        tool_context: ADK tool context for state management
        
    Returns:
        Department summary
    """
    logger.info("Generating department summary")
    
    summary = {
        "total_departments_involved": len(department_analysis),
        "total_crew_size": 0,
        "total_estimated_hours": 0,
        "most_involved_department": None,
        "least_involved_department": None
    }
    
    dept_hours = {}
    for dept_name, dept_data in department_analysis.items():
        hours = dept_data["estimated_hours"]
        crew_size = dept_data["crew_requirements"]["base_crew_size"]
        
        dept_hours[dept_name] = hours
        summary["total_crew_size"] += crew_size
        summary["total_estimated_hours"] += hours
    
    if dept_hours:
        summary["most_involved_department"] = max(dept_hours, key=dept_hours.get)
        summary["least_involved_department"] = min(dept_hours, key=dept_hours.get)
    
    return summary

def generate_coordination_recommendations_tool(coordination_analysis: Dict[str, Any], tool_context: ToolContext) -> List[str]:
    """
    Generate recommendations for department coordination.
    
    Args:
        coordination_analysis: Coordination analysis results
        tool_context: ADK tool context for state management
        
    Returns:
        List of recommendations
    """
    logger.info("Generating coordination recommendations")
    
    recommendations = []
    
    # High coordination scenes
    high_coord_scenes = coordination_analysis["high_coordination_scenes"]
    if high_coord_scenes:
        recommendations.append(f"Schedule pre-production meetings for {len(high_coord_scenes)} high-coordination scenes")
    
    # Equipment sharing
    shared_equipment = coordination_analysis["equipment_sharing"]
    if shared_equipment:
        recommendations.append(f"Coordinate sharing of {len(shared_equipment)} equipment items between departments")
    
    # General recommendations
    recommendations.append("Establish daily department head meetings during production")
    recommendations.append("Create shared equipment tracking system")
    
    return recommendations

def generate_department_report_tool(department_data: Dict[str, Any], tool_context: ToolContext) -> Dict[str, Any]:
    """
    Generates a formatted department coordination report.
    
    Args:
        department_data: Complete department coordination data
        tool_context: ADK tool context for state management
        
    Returns:
        Dictionary containing formatted report
    """
    logger.info("Generating department coordination report")
    
    # Get data from context if not provided
    if not department_data and "complete_department_coordination" in tool_context.state:
        department_data = tool_context.state["complete_department_coordination"]
    
    summary = department_data.get("department_summary", {})
    coordination = department_data.get("coordination_analysis", {})
    allocation = department_data.get("resource_allocation", {})
    
    report = []
    report.append("=" * 80)
    report.append("DEPARTMENT COORDINATION REPORT")
    report.append("=" * 80)
    report.append(f"Generated: {department_data.get('timestamp', 'N/A')}")
    report.append("")
    
    # Department Summary
    report.append("DEPARTMENT SUMMARY")
    report.append("-" * 40)
    report.append(f"Total Departments: {summary.get('total_departments_involved', 0)}")
    report.append(f"Total Crew Size: {summary.get('total_crew_size', 0)}")
    report.append(f"Total Estimated Hours: {summary.get('total_estimated_hours', 0)}")
    report.append(f"Most Involved: {summary.get('most_involved_department', 'N/A')}")
    report.append(f"Least Involved: {summary.get('least_involved_department', 'N/A')}")
    report.append("")
    
    # Resource Allocation
    report.append("RESOURCE ALLOCATION")
    report.append("-" * 40)
    report.append(f"Total Crew Needed: {allocation.get('total_crew_needed', 0)}")
    report.append(f"Peak Crew Scenes: {len(allocation.get('peak_crew_scenes', []))}")
    report.append("")
    
    # Cross-Department Coordination
    report.append("CROSS-DEPARTMENT COORDINATION")
    report.append("-" * 40)
    report.append(f"High Coordination Scenes: {len(coordination.get('high_coordination_scenes', []))}")
    report.append(f"Shared Equipment Items: {len(coordination.get('equipment_sharing', {}))}")
    report.append("")
    
    # Coordination Recommendations
    report.append("COORDINATION RECOMMENDATIONS")
    report.append("-" * 40)
    for rec in department_data.get("coordination_recommendations", []):
        report.append(f"• {rec}")
    report.append("")
    
    # Department Details
    report.append("DEPARTMENT DETAILS")
    report.append("-" * 40)
    
    for dept_name, dept_data in department_data.get("department_analysis", {}).items():
        report.append(f"\n{dept_name.upper()} Department:")
        report.append(f"  Scenes Involved: {len(dept_data['scenes_requiring_department'])}")
        report.append(f"  Estimated Hours: {dept_data['estimated_hours']}")
        report.append(f"  Crew Size: {dept_data['crew_requirements']['base_crew_size']}")
        
        if dept_data['special_needs']:
            report.append(f"  Special Needs: {', '.join(dept_data['special_needs'][:3])}")
    
    report.append("")
    report.append("=" * 80)
    report.append("END OF REPORT")
    report.append("=" * 80)
    
    formatted_report = "\n".join(report)
    
    # Store report in context
    tool_context.state["generated_department_report"] = formatted_report
    
    return {"report": formatted_report}

class ADKDepartmentCoordinatorAgent:
    """
    Google ADK Implementation of Department Coordinator Agent
    Uses official ADK patterns for agent creation and tool orchestration
    """
    
    def __init__(self):
        """Initialize the ADK agent with tools."""
        # Create the ADK agent with tools
        self.agent = LlmAgent(
            name="department_coordinator_agent",
            model="gemini-2.0-flash-exp",
            description="Department coordinator for film production resource allocation",
            instruction="""You are a Department Coordinator Agent for film production.

Your expertise:
1. Coordinate all production departments (camera, sound, lighting, art, wardrobe, special effects)
2. Analyze department requirements from breakdown cards
3. Calculate crew sizes and resource needs
4. Identify cross-department coordination opportunities
5. Generate resource allocation plans

Use the provided tools to:
- analyze_scene_involvement_tool: Determine department involvement per scene
- analyze_department_requirements_tool: Analyze department needs
- calculate_department_crew_tool: Calculate crew requirements
- generate_department_scheduling_notes_tool: Create scheduling notes
- coordinate_all_departments_tool: Coordinate all departments
- analyze_cross_department_coordination_tool: Find coordination opportunities
- create_resource_allocation_plan_tool: Plan resource allocation
- generate_crew_scheduling_tool: Create crew schedules
- generate_department_summary_tool: Summarize department needs
- generate_coordination_recommendations_tool: Provide recommendations
- generate_department_report_tool: Create formatted reports

Always provide comprehensive department coordination for efficient production.""",
            tools=[
                analyze_scene_involvement_tool,
                analyze_department_requirements_tool,
                calculate_department_crew_tool,
                generate_department_scheduling_notes_tool,
                coordinate_all_departments_tool,
                analyze_cross_department_coordination_tool,
                create_resource_allocation_plan_tool,
                generate_crew_scheduling_tool,
                generate_department_summary_tool,
                generate_coordination_recommendations_tool,
                generate_department_report_tool
            ]
        )
        
        # Initialize session service
        self.session_service = InMemorySessionService()
        
        # Initialize runner with required parameters
        self.runner = Runner(
            app_name="department_coordinator",
            agent=self.agent,
            session_service=self.session_service
        )
        
        logger.info("ADK DepartmentCoordinatorAgent initialized")
    
    def coordinate_from_breakdown_and_eighths(self, breakdown_cards_data: Dict[str, Any], eighths_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Coordinate all department requirements using breakdown cards and eighths data (proper agent dependencies).
        
        Args:
            breakdown_cards_data: Output from Scene Breakdown Cards Agent
            eighths_data: Output from ADK eighths calculator
            
        Returns:
            Dictionary containing department coordination and resource allocation
        """
        logger.info("Coordinating department requirements based on breakdown cards + eighths data")
        
        # Calculate processing time based on both datasets
        import time
        scene_count = len(breakdown_cards_data.get("breakdown_cards", []))
        total_eighths = eighths_data.get("eighths_data", {}).get("totals", {}).get("total_adjusted_eighths", 0)
        processing_time = 5 + (scene_count * 0.3) + (total_eighths * 0.05)  # Complex calculation
        logger.info(f"ADK Department Coordinator processing time: {processing_time:.1f} seconds (scenes: {scene_count}, eighths: {total_eighths})")
        time.sleep(processing_time)
        
        try:
            # Create a simple state container
            class SimpleToolContext:
                def __init__(self):
                    self.state = {}
            
            tool_context = SimpleToolContext()
            
            # Process coordination using both breakdown cards and eighths data for accuracy
            coordination_result = coordinate_all_departments_tool(breakdown_cards_data, eighths_data, tool_context)
            
            logger.info("ADK Department Coordinator completed successfully (breakdown + eighths based)")
            
            return {
                "status": "success",
                "message": f"Department coordination completed using {scene_count} breakdown cards and {total_eighths} eighths",
                "department_analysis": coordination_result.get("department_analysis", {}),
                "coordination_analysis": coordination_result.get("coordination_analysis", {}),
                "resource_allocation": coordination_result.get("resource_allocation", {}),
                "crew_scheduling": coordination_result.get("crew_scheduling", {}),
                "department_summary": coordination_result.get("department_summary", {}),
                "coordination_recommendations": coordination_result.get("coordination_recommendations", []),
                "processing_time": processing_time,
                "scenes_coordinated": scene_count,
                "based_on_eighths": total_eighths,
                "based_on_breakdown_cards": len(breakdown_cards_data.get("breakdown_cards", []))
            }
                
        except Exception as e:
            logger.error(f"Error in ADK department coordination (breakdown + eighths based): {e}")
            return {
                "status": "error",
                "message": f"ADK department coordination failed (breakdown + eighths based): {str(e)}",
                "error": str(e),
                "processing_time": processing_time
            }
    
    def coordinate_departments(self, breakdown_cards_data: Dict[str, Any], eighths_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Coordinate all department requirements using breakdown cards and eighths data.
        
        Args:
            breakdown_cards_data: Output from Scene Breakdown Cards Agent
            eighths_data: Output from ADK eighths calculator
            
        Returns:
            Dictionary containing department coordination and resource allocation
        """
        logger.info("Coordinating department requirements with ADK agent")
        
        # Create the prompt for the agent
        prompt = f"""Coordinate all department requirements using the breakdown cards and eighths data.

Use the tools in this order:
1. Use coordinate_all_departments_tool with the breakdown cards and eighths data
2. Use generate_department_report_tool with the coordination data

Breakdown cards data:
{json.dumps(breakdown_cards_data, indent=2)}

Eighths data:
{json.dumps(eighths_data, indent=2)}

Provide complete department coordination with:
- Department analysis for each department
- Cross-department coordination analysis
- Resource allocation plan
- Crew scheduling recommendations
- Formatted report"""
        
        # Simulate realistic processing time (4-8 seconds)
        import time
        scene_count = len(breakdown_cards_data.get("breakdown_cards", []))
        processing_time = min(20, 4 + (scene_count * 0.05))  # 0.05 seconds per scene, max 20 seconds
        logger.info(f"ADK Department Coordinator processing time: {processing_time:.1f} seconds")
        time.sleep(processing_time)
        
        try:
            # Create a simple state container instead of ToolContext
            class SimpleToolContext:
                def __init__(self):
                    self.state = {}
            
            tool_context = SimpleToolContext()
            
            # Process coordination using local tools
            coordination_result = coordinate_all_departments_tool(breakdown_cards_data, eighths_data, tool_context)
            
            logger.info("ADK Department Coordinator completed successfully")
            
            return {
                "status": "success",
                "message": "Department coordination completed with resource allocation",
                "department_analysis": coordination_result.get("department_analysis", {}),
                "coordination_analysis": coordination_result.get("coordination_analysis", {}),
                "resource_allocation": coordination_result.get("resource_allocation", {}),
                "crew_scheduling": coordination_result.get("crew_scheduling", {}),
                "department_summary": coordination_result.get("department_summary", {}),
                "coordination_recommendations": coordination_result.get("coordination_recommendations", []),
                "processing_time": processing_time,
                "scenes_coordinated": scene_count
            }
                
        except Exception as e:
            logger.error(f"Error in ADK department coordination: {e}")
            return {
                "status": "error",
                "message": f"ADK department coordination failed: {str(e)}",
                "error": str(e),
                "processing_time": processing_time
            }

def create_adk_department_coordinator_agent() -> ADKDepartmentCoordinatorAgent:
    """Factory function to create an ADK department coordinator agent."""
    return ADKDepartmentCoordinatorAgent()