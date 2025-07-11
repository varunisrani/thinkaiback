"""
Google ADK Implementation of EighthsCalculatorAgent
Converts custom methods to ADK tool functions for industry-standard eighths calculation
"""

from typing import Dict, Any, List
from pydantic import BaseModel, Field
import logging
from datetime import datetime
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Industry Standards Constants
INDUSTRY_STANDARDS = {
    "words_per_page": 250,
    "eighths_per_page": 8,
    "minutes_per_eighth": 9,
    "hours_per_eighth": 0.15,
    "standard_shoot_day_eighths": 60,
    "base_crew_hours": 12,
    "setup_time_percentage": 0.3,
    "wrap_time_percentage": 0.2,
    "minimum_scene_size": 0.125
}

# Complexity Factors
COMPLEXITY_FACTORS = {
    "base_factor": 1.0,
    "technical_cue_factor": 0.1,
    "exterior_factor": 0.2,
    "night_factor": 0.3,
    "dusk_dawn_factor": 0.2,
    "character_threshold": 3,
    "character_factor": 0.1,
    "dialogue_threshold": 10,
    "dialogue_factor": 0.1,
    "max_complexity": 3.0
}

# Pydantic Models for Type Safety
class SceneData(BaseModel):
    scene_number: str = Field(description="Scene number identifier")
    description: str = Field(description="Scene description text")
    location_type: str = Field(default="INT", description="INT or EXT")
    time_of_day: str = Field(default="DAY", description="Time of day")
    technical_cues: List[str] = Field(default_factory=list, description="Technical requirements")
    character_count: int = Field(default=0, description="Number of characters")
    dialogue_count: int = Field(default=0, description="Number of dialogue lines")

class SceneEighthsResult(BaseModel):
    scene_number: str
    word_count: int
    page_count: float
    base_eighths: float
    complexity_factor: float
    adjusted_eighths: float
    estimated_shoot_hours: float
    setup_hours: float
    wrap_hours: float
    total_hours: float

class ComplexityResult(BaseModel):
    base_factor: float
    technical_factor: float
    location_factor: float
    time_factor: float
    character_factor: float
    dialogue_factor: float
    total_complexity: float
    factors_applied: List[str]

class EighthsReport(BaseModel):
    total_scenes: int
    total_script_eighths: float
    total_adjusted_eighths: float
    estimated_shoot_days: float
    total_production_hours: float
    breakdown_by_complexity: Dict[str, int]
    industry_standards_used: Dict[str, Any]

# Tool Function 1: Calculate complexity factor for a scene
@ToolFunction
def determine_complexity_tool(scene: SceneData) -> ComplexityResult:
    """
    Calculates the complexity factor for a scene based on technical requirements.
    
    Args:
        scene: Scene data including location, time, technical cues, etc.
        
    Returns:
        ComplexityResult with detailed complexity breakdown
    """
    logger.info(f"Calculating complexity for scene {scene.scene_number}")
    
    complexity = COMPLEXITY_FACTORS["base_factor"]
    factors_applied = ["base_factor: 1.0"]
    
    # Technical cues complexity
    technical_factor = 0.0
    if scene.technical_cues:
        cue_count = len(scene.technical_cues)
        technical_factor = cue_count * COMPLEXITY_FACTORS["technical_cue_factor"]
        complexity += technical_factor
        factors_applied.append(f"technical_cues({cue_count}): +{technical_factor}")
    
    # Location complexity
    location_factor = 0.0
    if scene.location_type == "EXT":
        location_factor = COMPLEXITY_FACTORS["exterior_factor"]
        complexity += location_factor
        factors_applied.append(f"exterior: +{location_factor}")
    
    # Time of day complexity
    time_factor = 0.0
    if scene.time_of_day == "NIGHT":
        time_factor = COMPLEXITY_FACTORS["night_factor"]
        complexity += time_factor
        factors_applied.append(f"night: +{time_factor}")
    elif scene.time_of_day in ["DUSK", "DAWN"]:
        time_factor = COMPLEXITY_FACTORS["dusk_dawn_factor"]
        complexity += time_factor
        factors_applied.append(f"{scene.time_of_day.lower()}: +{time_factor}")
    
    # Character complexity
    character_factor = 0.0
    if scene.character_count > COMPLEXITY_FACTORS["character_threshold"]:
        extra_chars = scene.character_count - COMPLEXITY_FACTORS["character_threshold"]
        character_factor = extra_chars * COMPLEXITY_FACTORS["character_factor"]
        complexity += character_factor
        factors_applied.append(f"characters({scene.character_count}): +{character_factor}")
    
    # Dialogue complexity
    dialogue_factor = 0.0
    if scene.dialogue_count > COMPLEXITY_FACTORS["dialogue_threshold"]:
        dialogue_factor = COMPLEXITY_FACTORS["dialogue_factor"]
        complexity += dialogue_factor
        factors_applied.append(f"dialogue({scene.dialogue_count}): +{dialogue_factor}")
    
    # Cap complexity at maximum
    total_complexity = min(complexity, COMPLEXITY_FACTORS["max_complexity"])
    
    return ComplexityResult(
        base_factor=COMPLEXITY_FACTORS["base_factor"],
        technical_factor=technical_factor,
        location_factor=location_factor,
        time_factor=time_factor,
        character_factor=character_factor,
        dialogue_factor=dialogue_factor,
        total_complexity=total_complexity,
        factors_applied=factors_applied
    )

# Tool Function 2: Calculate eighths for a single scene
@ToolFunction
def calculate_single_scene_tool(
    page_count: float,
    scene: SceneData,
    complexity: ComplexityResult
) -> SceneEighthsResult:
    """
    Calculates eighths breakdown for a single scene with time estimates.
    
    Args:
        page_count: Number of pages for the scene
        scene: Scene data
        complexity: Pre-calculated complexity result
        
    Returns:
        SceneEighthsResult with detailed eighths and time breakdown
    """
    logger.info(f"Calculating eighths for scene {scene.scene_number}")
    
    # Calculate word count (reverse calculation from page count)
    word_count = int(page_count * INDUSTRY_STANDARDS["words_per_page"])
    
    # Calculate base eighths
    base_eighths = page_count * INDUSTRY_STANDARDS["eighths_per_page"]
    
    # Apply complexity to eighths
    adjusted_eighths = base_eighths * complexity.total_complexity
    
    # Calculate time estimates
    base_shoot_hours = adjusted_eighths * INDUSTRY_STANDARDS["hours_per_eighth"]
    setup_hours = base_shoot_hours * INDUSTRY_STANDARDS["setup_time_percentage"]
    wrap_hours = base_shoot_hours * INDUSTRY_STANDARDS["wrap_time_percentage"]
    total_hours = base_shoot_hours + setup_hours + wrap_hours
    
    return SceneEighthsResult(
        scene_number=scene.scene_number,
        word_count=word_count,
        page_count=page_count,
        base_eighths=base_eighths,
        complexity_factor=complexity.total_complexity,
        adjusted_eighths=adjusted_eighths,
        estimated_shoot_hours=base_shoot_hours,
        setup_hours=setup_hours,
        wrap_hours=wrap_hours,
        total_hours=total_hours
    )

# Tool Function 3: Main calculation function for all scenes
@ToolFunction
def calculate_scene_eighths_tool(scenes_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calculates eighths breakdown for all scenes in a script.
    
    Args:
        scenes_data: List of scene dictionaries with descriptions
        
    Returns:
        Complete eighths breakdown with per-scene and total calculations
    """
    logger.info(f"Processing eighths for {len(scenes_data)} scenes")
    
    scene_results = []
    total_script_eighths = 0.0
    total_adjusted_eighths = 0.0
    total_production_hours = 0.0
    complexity_breakdown = {"simple": 0, "moderate": 0, "complex": 0}
    
    for scene_dict in scenes_data:
        # Convert to SceneData model
        scene = SceneData(**scene_dict)
        
        # Calculate page count from description length
        word_count = len(scene.description.split())
        page_count = max(
            word_count / INDUSTRY_STANDARDS["words_per_page"],
            INDUSTRY_STANDARDS["minimum_scene_size"]
        )
        
        # Calculate complexity
        complexity = determine_complexity_tool(scene)
        
        # Calculate eighths
        eighths_result = calculate_single_scene_tool(page_count, scene, complexity)
        
        # Aggregate totals
        total_script_eighths += eighths_result.base_eighths
        total_adjusted_eighths += eighths_result.adjusted_eighths
        total_production_hours += eighths_result.total_hours
        
        # Categorize complexity
        if complexity.total_complexity <= 1.2:
            complexity_breakdown["simple"] += 1
        elif complexity.total_complexity <= 1.8:
            complexity_breakdown["moderate"] += 1
        else:
            complexity_breakdown["complex"] += 1
        
        # Store result
        scene_results.append({
            "scene": eighths_result.model_dump(),
            "complexity": complexity.model_dump()
        })
    
    # Calculate shoot days
    estimated_shoot_days = total_adjusted_eighths / INDUSTRY_STANDARDS["standard_shoot_day_eighths"]
    
    return {
        "timestamp": datetime.now().isoformat(),
        "scene_calculations": scene_results,
        "totals": {
            "total_scenes": len(scenes_data),
            "total_script_eighths": round(total_script_eighths, 2),
            "total_adjusted_eighths": round(total_adjusted_eighths, 2),
            "estimated_shoot_days": round(estimated_shoot_days, 1),
            "total_production_hours": round(total_production_hours, 2)
        },
        "breakdown_by_complexity": complexity_breakdown,
        "industry_standards_used": INDUSTRY_STANDARDS
    }

# Tool Function 4: Generate formatted report
@ToolFunction
def generate_report_tool(eighths_data: Dict[str, Any]) -> str:
    """
    Generates a formatted industry-standard eighths report.
    
    Args:
        eighths_data: Complete eighths calculation data
        
    Returns:
        Formatted text report following industry standards
    """
    logger.info("Generating eighths report")
    
    totals = eighths_data.get("totals", {})
    complexity = eighths_data.get("breakdown_by_complexity", {})
    
    report = []
    report.append("=" * 80)
    report.append("INDUSTRY STANDARD EIGHTHS BREAKDOWN REPORT")
    report.append("=" * 80)
    report.append(f"Generated: {eighths_data.get('timestamp', 'N/A')}")
    report.append("")
    
    # Summary Section
    report.append("SUMMARY")
    report.append("-" * 40)
    report.append(f"Total Scenes: {totals.get('total_scenes', 0)}")
    report.append(f"Script Eighths: {totals.get('total_script_eighths', 0)}")
    report.append(f"Adjusted Eighths (w/ complexity): {totals.get('total_adjusted_eighths', 0)}")
    report.append(f"Estimated Shoot Days: {totals.get('estimated_shoot_days', 0)}")
    report.append(f"Total Production Hours: {totals.get('total_production_hours', 0)}")
    report.append("")
    
    # Complexity Breakdown
    report.append("COMPLEXITY BREAKDOWN")
    report.append("-" * 40)
    report.append(f"Simple Scenes: {complexity.get('simple', 0)}")
    report.append(f"Moderate Scenes: {complexity.get('moderate', 0)}")
    report.append(f"Complex Scenes: {complexity.get('complex', 0)}")
    report.append("")
    
    # Industry Standards Used
    report.append("INDUSTRY STANDARDS APPLIED")
    report.append("-" * 40)
    standards = eighths_data.get("industry_standards_used", {})
    report.append(f"• 1 page = {standards.get('eighths_per_page', 8)} eighths")
    report.append(f"• 1 eighth = {standards.get('minutes_per_eighth', 9)} minutes")
    report.append(f"• Standard shoot day = {standards.get('standard_shoot_day_eighths', 60)} eighths")
    report.append(f"• Words per page = {standards.get('words_per_page', 250)}")
    report.append("")
    
    # Scene Details
    report.append("SCENE-BY-SCENE BREAKDOWN")
    report.append("-" * 40)
    
    for scene_calc in eighths_data.get("scene_calculations", []):
        scene = scene_calc["scene"]
        complexity = scene_calc["complexity"]
        
        report.append(f"\nScene {scene['scene_number']}:")
        report.append(f"  • Page Count: {scene['page_count']:.2f}")
        report.append(f"  • Base Eighths: {scene['base_eighths']:.1f}")
        report.append(f"  • Complexity Factor: {scene['complexity_factor']:.2f}x")
        report.append(f"  • Adjusted Eighths: {scene['adjusted_eighths']:.1f}")
        report.append(f"  • Estimated Hours: {scene['total_hours']:.1f}")
        report.append(f"  • Complexity Factors: {', '.join(complexity['factors_applied'])}")
    
    report.append("")
    report.append("=" * 80)
    report.append("END OF REPORT")
    report.append("=" * 80)
    
    return "\n".join(report)

# Agent instruction for the ADK implementation
EIGHTHS_CALCULATOR_INSTRUCTION = """You are an Industry Standards Eighths Calculator Agent for film production.

Your expertise:
1. Convert script pages to eighths (1 page = 8 eighths)
2. Calculate industry-standard time estimates (1 eighth = ~9 minutes)
3. Apply complexity factors based on technical requirements
4. Generate accurate shoot time predictions

Use the provided tool functions to:
- determine_complexity_tool: Calculate scene complexity factors
- calculate_single_scene_tool: Calculate eighths for individual scenes
- calculate_scene_eighths_tool: Process multiple scenes at once
- generate_report_tool: Create formatted industry reports

Always follow industry standards and provide detailed breakdowns for production planning."""