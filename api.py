"""
FastAPI server for SD1 Film Production AI System
"""
from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import asyncio
import logging
import os
from datetime import datetime

# Import coordinators
from script_ingestion.coordinator import ScriptIngestionCoordinator
from character_breakdown.coordinator import CharacterBreakdownCoordinator
from scheduling.coordinator import SchedulingCoordinator
from budgeting.coordinator import BudgetingCoordinator
from storyboard.coordinator import StoryboardCoordinator
from one_liner.agents.one_linear_agent import OneLinerAgent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="SD1 Film Production AI System",
    description="AI-powered system for film production planning and management",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize coordinators
try:
    script_coordinator = ScriptIngestionCoordinator()
    character_coordinator = CharacterBreakdownCoordinator()
    scheduling_coordinator = SchedulingCoordinator()
    budgeting_coordinator = BudgetingCoordinator()
    storyboard_coordinator = StoryboardCoordinator()
    one_liner_agent = OneLinerAgent()
    logger.info("All coordinators initialized successfully")
except Exception as e:
    logger.error(f"Error initializing coordinators: {e}")
    raise

# Pydantic models for API requests
class ScriptRequest(BaseModel):
    script_text: str
    department_focus: Optional[List[str]] = None
    validation_level: str = "lenient"

class StoryboardRequest(BaseModel):
    scene_data: Dict[str, Any]
    shot_settings: Optional[Dict[str, Any]] = None

class BudgetRequest(BaseModel):
    production_data: Dict[str, Any]
    budget_constraints: Optional[Dict[str, Any]] = None

class ScheduleRequest(BaseModel):
    script_data: Dict[str, Any]
    production_constraints: Optional[Dict[str, Any]] = None

class OneLinerRequest(BaseModel):
    scene_descriptions: List[str]

# Health check endpoint
@app.get("/")
async def root():
    return {
        "message": "SD1 Film Production AI System API",
        "status": "running",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "endpoints": {
            "script_ingestion": "/api/script/ingest",
            "character_analysis": "/api/characters",
            "schedule_generation": "/api/schedule",
            "budget_estimation": "/api/budget",
            "one_liner_generation": "/api/one-liner",
            "storyboard_generation": "/api/storyboard",
            "docs": "/docs"
        }
    }

@app.get("/health")
async def health_check():
    """Comprehensive health check for all system components."""
    try:
        health_status = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0",
            "components": {
                "script_coordinator": "healthy",
                "character_coordinator": "healthy", 
                "scheduling_coordinator": "healthy",
                "budgeting_coordinator": "healthy",
                "storyboard_coordinator": "healthy",
                "one_liner_agent": "healthy"
            },
            "environment": {
                "google_api_configured": bool(os.environ.get("GOOGLE_API_KEY")),
                "replicate_api_configured": bool(os.environ.get("REPLICATE_API_TOKEN"))
            }
        }
        
        # Quick test of coordinators
        try:
            test_data = {"test": True}
            # Test if coordinators are properly initialized
            assert script_coordinator is not None
            assert character_coordinator is not None
            assert scheduling_coordinator is not None
            assert budgeting_coordinator is not None
            assert storyboard_coordinator is not None
            assert one_liner_agent is not None
        except Exception as e:
            health_status["components"]["initialization_error"] = str(e)
            health_status["status"] = "degraded"
        
        return health_status
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "error": str(e)
        }

# Script ingestion endpoints
@app.post("/api/script/ingest")
async def ingest_script(request: ScriptRequest):
    """Process a script through the complete ingestion pipeline."""
    try:
        result = await script_coordinator.process_script(
            request.script_text,
            request.department_focus,
            request.validation_level
        )
        return {"success": True, "data": result}
    except Exception as e:
        logger.error(f"Error in script ingestion: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/script/process")
async def process_script_frontend(request: dict):
    """Frontend-optimized script processing endpoint with 3-section data structure."""
    try:
        # Extract script data
        script_text = request.get("script", "")
        input_type = request.get("input_type", "text")
        validation_level = request.get("validation_level", "lenient")
        department_focus = request.get("department_focus", None)
        
        logger.info(f"Processing script for frontend: {len(script_text)} characters, type: {input_type}")
        
        # Process through 3-agent pipeline
        result = await script_coordinator.process_script(
            script_input=script_text,
            input_type=input_type,
            department_focus=department_focus,
            validation_level=validation_level
        )
        
        # Return formatted result (already formatted by _format_for_frontend)
        return result
        
    except Exception as e:
        logger.error(f"Error in frontend script processing: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Frontend-compatible endpoints
@app.post("/api/script/text")
async def process_script_text(request: dict):
    """Process script text (frontend-compatible endpoint)."""
    try:
        script_text = request.get("script", "")
        validation_level = request.get("validation_level", "lenient")
        
        result = await script_coordinator.process_script(
            script_text,
            None,  # department_focus
            validation_level
        )
        return {"success": True, "data": result}
    except Exception as e:
        logger.error(f"Error in script text processing: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/script/upload")
async def upload_script_file(file: UploadFile = File(...), validation_level: str = "lenient"):
    """Upload and process script file (frontend-compatible endpoint)."""
    try:
        # Read file content
        content = await file.read()
        
        # Determine input type based on file extension
        file_extension = file.filename.lower().split('.')[-1] if file.filename else ""
        input_type = "pdf" if file_extension == "pdf" else "text"
        
        logger.info(f"Processing uploaded file: {file.filename}, type: {input_type}, size: {len(content)} bytes")
        
        # Process through 3-agent pipeline with proper PDF handling
        if input_type == "pdf":
            result = await script_coordinator.process_script(
                script_input=content,  # Pass raw bytes for PDF
                input_type="pdf",
                department_focus=None,
                validation_level=validation_level
            )
        else:
            # Decode text files
            script_text = content.decode('utf-8')
            result = await script_coordinator.process_script(
                script_input=script_text,
                input_type="text",
                department_focus=None,
                validation_level=validation_level
            )
        
        return result  # Return formatted result directly
        
    except Exception as e:
        logger.error(f"Error in script file upload: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Character breakdown endpoints
@app.post("/api/character/analyze")
async def analyze_characters(script_data: Dict[str, Any]):
    """Analyze characters from processed script data."""
    try:
        result = await character_coordinator.process_character_breakdown(script_data)
        return {"success": True, "data": result}
    except Exception as e:
        logger.error(f"Error in character analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/characters")
async def analyze_characters_frontend(request: dict):
    """Frontend-compatible character analysis endpoint."""
    try:
        script_data = request.get("script_data", {})
        result = await character_coordinator.process_character_breakdown(script_data)
        return {"success": True, "data": result}
    except Exception as e:
        logger.error(f"Error in character analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Scheduling endpoints
@app.post("/api/schedule/generate")
async def generate_schedule(request: ScheduleRequest):
    """Generate optimized production schedule."""
    try:
        result = await scheduling_coordinator.generate_schedule(
            request.script_data,
            request.production_constraints
        )
        return {"success": True, "data": result}
    except Exception as e:
        logger.error(f"Error in schedule generation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/schedule")
async def generate_schedule_frontend(request: dict):
    """Frontend-compatible schedule generation endpoint."""
    try:
        script_results = request.get("script_results", {})
        character_results = request.get("character_results", {})
        start_date = request.get("start_date", "")
        location_constraints = request.get("location_constraints", {})
        schedule_constraints = request.get("schedule_constraints", {})
        
        # Combine script and character data
        combined_data = {
            "script_results": script_results,
            "character_results": character_results
        }
        
        production_constraints = {
            "start_date": start_date,
            "location_constraints": location_constraints,
            "schedule_constraints": schedule_constraints
        }
        
        result = await scheduling_coordinator.generate_schedule_frontend(
            combined_data,
            production_constraints
        )
        return {"success": True, "data": result}
    except Exception as e:
        logger.error(f"Error in schedule generation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Budgeting endpoints
@app.post("/api/budget/estimate")
async def estimate_budget(request: BudgetRequest):
    """Generate budget estimation for production."""
    try:
        result = await budgeting_coordinator.process_budget_estimation({
            "production_data": request.production_data,
            "budget_constraints": request.budget_constraints
        })
        return {"success": True, "data": result}
    except Exception as e:
        logger.error(f"Error in budget estimation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/budget")
async def estimate_budget_frontend(request: dict):
    """Frontend-compatible budget estimation endpoint with comprehensive sub-agent support."""
    try:
        # Handle both nested and flat request structures
        if "production_data" in request:
            # New nested structure from updated frontend
            production_data = request.get("production_data", {})
            budget_constraints = request.get("budget_constraints", {})
        else:
            # Legacy flat structure for backwards compatibility
            script_results = request.get("script_results", {})
            character_results = request.get("character_results", {})
            schedule_results = request.get("schedule_results", {})
            
            production_data = {
                "script_results": script_results,
                "character_results": character_results,
                "schedule_results": schedule_results
            }
            budget_constraints = request.get("budget_constraints", {})
        
        result = await budgeting_coordinator.process_budget_estimation({
            "production_data": production_data,
            "budget_constraints": budget_constraints
        })
        return {"success": True, "data": result}
    except Exception as e:
        logger.error(f"Error in budget estimation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/budget/verify-agents")
async def verify_budget_agents():
    """Verify all budget sub-agents are properly connected."""
    try:
        verification_results = budgeting_coordinator.verify_sub_agent_connections()
        return {"success": True, "data": verification_results}
    except Exception as e:
        logger.error(f"Error in budget agent verification: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Storyboard endpoints
@app.post("/api/storyboard/generate")
async def generate_storyboard(request: StoryboardRequest):
    """Generate storyboard images for scenes."""
    try:
        result = await storyboard_coordinator.generate_storyboard(
            request.scene_data,
            request.shot_settings
        )
        return {"success": True, "data": result}
    except Exception as e:
        logger.error(f"Error in storyboard generation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# One-liner endpoints
@app.post("/api/oneliners/generate")
async def generate_oneliners(request: OneLinerRequest):
    """Generate one-liner summaries for scenes."""
    try:
        result = await one_liner_agent.process_scenes(request.scene_descriptions)
        return {"success": True, "data": result}
    except Exception as e:
        logger.error(f"Error in one-liner generation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/one-liner")
async def generate_oneliners_frontend(request_data: dict):
    """Frontend-compatible one-liner generation endpoint."""
    try:
        logger.info(f"Received request_data keys: {list(request_data.keys())}")
        logger.info(f"Full request_data structure: {request_data}")
        
        # Handle nested script_data structure
        script_data = request_data.get("script_data", request_data)
        logger.info(f"Script_data keys: {list(script_data.keys()) if isinstance(script_data, dict) else 'Not a dict'}")
        
        # Extract scene descriptions from script data with better error handling
        parsed_data = script_data.get("parsed_data", {})
        if not parsed_data:
            # Try alternative structure
            parsed_data = script_data.get("data", {}).get("parsed_data", {})
            if not parsed_data:
                raise ValueError(f"No parsed_data found. Available keys: {list(script_data.keys())}")
        
        scenes = parsed_data.get("scenes", [])
        if not scenes:
            raise ValueError("No scenes found in parsed_data")
        
        logger.info(f"Found {len(scenes)} scenes in parsed data")
        
        # Extract descriptions, trying multiple possible field names
        scene_descriptions = []
        for i, scene in enumerate(scenes):
            description = None
            # Try different field names for scene description
            for field in ["description", "scene_description", "action", "content", "scene_action"]:
                if field in scene and scene[field] and str(scene[field]).strip():
                    description = str(scene[field]).strip()
                    break
            
            if description:
                scene_descriptions.append(description)
            else:
                # Create a fallback description from other scene data
                fallback_desc = f"Scene {scene.get('scene_number', i+1)}"
                location = scene.get('location', {})
                if isinstance(location, dict):
                    place = location.get('place', '')
                    time = scene.get('time', '')
                    if place:
                        fallback_desc += f" at {place}"
                    if time:
                        fallback_desc += f" during {time}"
                elif isinstance(location, str) and location.strip():
                    fallback_desc += f" at {location}"
                
                # Try to extract from dialogues
                dialogues = scene.get('dialogues', [])
                if dialogues and len(dialogues) > 0:
                    first_dialogue = dialogues[0]
                    if isinstance(first_dialogue, dict) and first_dialogue.get('line'):
                        fallback_desc += f" - dialogue scene with {first_dialogue.get('character', 'character')}"
                
                scene_descriptions.append(fallback_desc)
                logger.info(f"Created fallback description for scene {i}: {fallback_desc}")
        
        if not scene_descriptions:
            raise ValueError("No valid scene descriptions found in any scenes")
        
        logger.info(f"Extracted {len(scene_descriptions)} scene descriptions")
        
        result = await one_liner_agent.process_scenes(scene_descriptions)
        return {"success": True, "data": result}
    except Exception as e:
        logger.error(f"Error in one-liner generation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Additional frontend-compatible endpoints
@app.post("/api/storyboard")
async def generate_storyboard_frontend(request: dict):
    """Frontend-compatible storyboard generation endpoint."""
    try:
        script_results = request.get("script_results", {})
        shot_settings = request.get("shot_settings", {})
        
        result = await storyboard_coordinator.generate_storyboard(
            script_results,
            shot_settings
        )
        return {"success": True, "data": result}
    except Exception as e:
        logger.error(f"Error in storyboard generation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/storyboard/batch")
async def generate_storyboard_batch_frontend(request: dict):
    """Frontend-compatible batch storyboard generation endpoint."""
    try:
        script_results = request.get("script_results", {})
        shot_settings = request.get("shot_settings", {})
        
        result = await storyboard_coordinator.generate_storyboard(
            script_results,
            shot_settings
        )
        return {"success": True, "data": result}
    except Exception as e:
        logger.error(f"Error in batch storyboard generation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Model configuration endpoint
@app.get("/api/config/model")
async def get_model_config():
    """Get current model configuration."""
    from base_config import get_model_config
    return {"success": True, "data": get_model_config()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)