# TASK.md - ADK Agent Coordinator Testing Task

## TASK
Create a Python script that processes film scripts through the SD1 ADK Agent Coordinator pipeline and stores each individual agent response in separate JSON files with comprehensive testing capabilities.

## SCOPE
**Included:**
- Test the 3-agent ADK sequential pipeline with PDF and text inputs
- Call the ADK Agent Coordinator programmatically 
- Extract individual agent responses from coordinator output
- Store each agent's response in separate JSON files with proper timestamps
- Organize outputs in structured folders with clear naming conventions
- Error handling and comprehensive logging for script execution
- Ensure all 3 ADK agent responses are captured individually
- Support both Black Panther PDF and text input testing

**Excluded:**
- Frontend UI modifications
- Database schema changes  
- Authentication/authorization updates
- Manual API testing or external API calls

## FILES INVOLVED
- `test_adk_pipeline_comprehensive.py` - New comprehensive test script to be created
- `src/script_ingestion/coordinator.py` - 3-agent ADK script processing pipeline
- `src/script_ingestion/agents/` - Individual ADK agent implementations
  - `adk_eighths_calculator_proper.py` - Google ADK Eighths Calculator Agent
  - `adk_scene_breakdown_cards_agent.py` - Google ADK Scene Breakdown Cards Agent  
  - `adk_department_coordinator_agent.py` - Google ADK Department Coordinator Agent
- `data/scripts/` - Output directory for processed scripts
- `data/scripts/agents/` - Individual ADK agent response storage
- `data/scripts/metadata/` - Script metadata storage
- `data/scripts/reports/` - Generated reports from each agent

## CONTEXT NEEDED
- **Script Ingestion System**: Uses 3 specialized Google ADK agents in sequential pipeline
  1. **ADK Eighths Calculator Agent**: Calculates industry-standard eighths, timing, and complexity
  2. **ADK Scene Breakdown Cards Agent**: Generates production breakdown cards with crew estimates
  3. **ADK Department Coordinator Agent**: Coordinates all department requirements and resources
- **Processing Flow**: PDF/Text → Coordinator → 3 ADK Agents → Individual JSON files + Reports
- **ADK Pattern**: All agents use Google ADK tool-based architecture with LlmAgent and Runner
- **PDF Support**: Built-in PDF parsing capability using PyPDF2

## SUCCESS CRITERIA
1. Film script (PDF or text) successfully processed through ADK pipeline
2. All 3 ADK agent responses captured individually with success status
3. Separate JSON files created for each agent output with timestamps
4. Files organized in timestamped folders under `data/scripts/`
5. Each agent response stored with proper structure and metadata
6. Comprehensive reports generated from each agent
7. Error handling preserves partial results when agents fail
8. Both PDF and text input modes tested successfully

## DEPENDENCIES
- Python virtual environment activated (`source venv/bin/activate` or `source myenv/bin/activate`)
- Google ADK SDK properly installed and configured
- Google Gemini 2.0 Flash model access configured
- PyPDF2 for PDF text extraction
- All ADK agent dependencies (google.adk.agents, google.adk.runners, etc.)
- Data directories exist and are writable
- Black Panther PDF available for testing

## DOCUMENTATION
- **Google ADK Documentation**: https://google.github.io/adk-docs/
  - Complete reference for Google Agent Development Kit (ADK)
  - LlmAgent creation and tool function patterns
  - Runner configuration and session management
  - ToolContext state management and tool orchestration
  - Best practices for multi-agent ADK architectures
  - Integration guides for Gemini models

## ESTIMATED EFFORT
**Complexity**: Medium-High (ADK integration complexity)
**Time**: 15-20 minutes
**Components**: ADK agent testing, data processing, comprehensive file organization

## IMPLEMENTATION STEPS
1. **Setup Environment**:
   ```bash
   cd sd1
   source venv/bin/activate  # or source myenv/bin/activate
   ```
2. Create `test_adk_pipeline_comprehensive.py` with proper ADK imports
3. Define test script content and PDF path configuration  
4. Implement comprehensive testing for both PDF and text inputs
5. Add detailed agent response parsing and validation
6. Create organized folder structure for each agent's output
7. Add comprehensive error handling and progress logging
8. Generate formatted reports for each agent
9. **Execute Testing**:
   ```bash
   python test_adk_pipeline_comprehensive.py
   ```

## VALIDATION STEPS
1. **Environment Setup**:
   ```bash
   cd sd1
   source venv/bin/activate  # or source myenv/bin/activate
   ```
2. **Test Individual Agents** (Optional):
   ```bash
   # Test individual ADK agents
   cd src/script_ingestion/agents
   python adk_eighths_calculator_proper.py
   python adk_scene_breakdown_cards_agent.py  
   python adk_department_coordinator_agent.py
   ```
3. **Run Comprehensive Pipeline Test**:
   ```bash
   cd ../../../  # Back to sd1 root
   python test_adk_pipeline_comprehensive.py
   ```
4. **Verify Results**:
   - Confirm script processing completes for both input types
   - Check individual agent JSON files exist and contain valid data
   - Validate folder structure matches organized pattern
   - Ensure all 3 ADK agents completed with success status
   - Verify comprehensive logs show detailed processing progress
   - Confirm generated reports contain meaningful analysis

## ADK AGENT ARCHITECTURE

### 1. ADK Eighths Calculator Agent
- **Purpose**: Industry-standard script timing and complexity analysis
- **Tools**: 
  - `determine_complexity_tool`: Scene complexity calculation
  - `calculate_single_scene_tool`: Individual scene eighths
  - `calculate_all_scenes_tool`: Complete script processing
  - `generate_report_tool`: Formatted industry reports
- **Output**: Eighths breakdown, shoot days, complexity analysis, industry report

### 2. ADK Scene Breakdown Cards Agent  
- **Purpose**: Production breakdown cards with crew estimates
- **Tools**:
  - `analyze_scene_requirements_tool`: Production requirements analysis
  - `create_breakdown_card_tool`: Individual breakdown cards
  - `estimate_crew_size_tool`: Crew size calculations
  - `generate_all_breakdown_cards_tool`: Complete breakdown processing
  - `analyze_scheduling_requirements_tool`: Scheduling analysis
- **Output**: Breakdown cards, crew estimates, scheduling analysis, production notes

### 3. ADK Department Coordinator Agent
- **Purpose**: Department coordination and resource allocation
- **Tools**:
  - `analyze_department_requirements_tool`: Department needs analysis
  - `coordinate_all_departments_tool`: Full coordination
  - `analyze_cross_department_coordination_tool`: Inter-department coordination
  - `create_resource_allocation_plan_tool`: Resource planning
  - `generate_crew_scheduling_tool`: Crew scheduling
- **Output**: Department analysis, resource allocation, crew scheduling, coordination recommendations

## EXPECTED OUTPUT STRUCTURE
```
data/scripts/
├── script_YYYYMMDD_HHMMSS.json              # Main processed script
├── metadata/
│   └── metadata_YYYYMMDD_HHMMSS.json        # Processing metadata
├── reports/
│   ├── eighths_report_YYYYMMDD_HHMMSS.txt   # ADK Eighths Calculator report
│   ├── breakdown_cards_YYYYMMDD_HHMMSS.json # Scene breakdown cards  
│   └── department_analysis_YYYYMMDD_HHMMSS.json # Department coordination
└── agents/
    ├── adk_eighths_calculator_YYYYMMDD_HHMMSS.json       # Eighths agent output
    ├── adk_scene_breakdown_cards_YYYYMMDD_HHMMSS.json    # Breakdown agent output
    └── adk_department_coordinator_YYYYMMDD_HHMMSS.json   # Department agent output
```

## TEST SCRIPT REQUIREMENTS
The Python script must include:
- **ADK Integration**: Proper Google ADK imports and agent initialization
- **Async Processing**: Use async/await for coordinator processing
- **PDF/Text Handling**: Support both PDF files and direct text input
- **JSON Handling**: Parse ADK agent responses and extract structured data
- **File Operations**: Create organized directories and save individual JSON files
- **Error Handling**: Comprehensive try/catch blocks with partial result preservation
- **Logging**: Detailed progress and status messages for each agent
- **Validation**: Verify each ADK agent completed successfully

## TEST SCRIPT STRUCTURE
```python
import asyncio
import os
import sys
import json
from datetime import datetime

# ADK Pipeline imports
sys.path.append('/Users/varunisrani/Desktop/mckays-app-template 3/sd1')
from src.script_ingestion.coordinator import ScriptIngestionCoordinator

# Configuration
BLACK_PANTHER_PDF = "/Users/varunisrani/Desktop/mckays-app-template 3/BLACK_PANTHER.pdf"
SAMPLE_SCRIPT_TEXT = """[Sample script content]"""

# Main testing functions
async def test_adk_pipeline_with_pdf():
    # Test PDF processing through 3-agent ADK pipeline
    pass

async def test_adk_pipeline_with_text():
    # Test text processing through 3-agent ADK pipeline  
    pass

def save_agent_outputs_individually(result, timestamp):
    # Extract and save each ADK agent output to separate JSON files
    pass

def generate_comprehensive_report(result):
    # Generate summary report of all ADK agent outputs
    pass

async def main():
    # Run comprehensive tests
    pass

if __name__ == "__main__":
    asyncio.run(main())
```

## SAMPLE TEST CONTENT
```
SAMPLE FILM SCRIPT: "THE HEIST"

FADE IN:
EXT. DOWNTOWN BANK - DAY
A sleek, modern bank building stands prominently on the corner. TRAFFIC flows steadily past.

INT. BANK LOBBY - CONTINUOUS  
ALEX MORGAN (30s), sharply dressed, enters through revolving doors. Multiple SECURITY CAMERAS track the movement.

ALEX
(to TELLER)
I'd like to make a withdrawal.

The TELLER (20s) smiles professionally.

TELLER
Of course, sir. How much would you like to withdraw?

ALEX
(grinning)
Everything.

ALEX produces a small device. All lights flicker and DIE.

FADE TO BLACK.
```

## EXECUTION INSTRUCTIONS

### **Quick Start**:
```bash
# Navigate to project directory
cd sd1

# Activate virtual environment 
source venv/bin/activate  # or source myenv/bin/activate

# Run comprehensive pipeline test
python test_adk_pipeline_comprehensive.py
```

### **Individual Agent Testing**:
```bash
# Test agents individually (from sd1 root)
cd src/script_ingestion/agents

# Run each ADK agent individually
python adk_eighths_calculator_proper.py
python adk_scene_breakdown_cards_agent.py
python adk_department_coordinator_agent.py

# Return to root for full pipeline test
cd ../../../
python test_adk_pipeline_comprehensive.py
```

### **Expected Command Output**:
```
🎯 STARTING COMPREHENSIVE ADK AGENT PIPELINE TESTS
⏰ Start time: 2024-XX-XX XX:XX:XX

🔵🔵🔵🔵🔵🔵🔵🔵🔵🔵 TEST 1: PDF PROCESSING 🔵🔵🔵🔵🔵🔵🔵🔵🔵🔵
================================================================================
TESTING ADK PIPELINE WITH PDF INPUT
================================================================================
📄 Using PDF file: /Users/.../BLACK_PANTHER.pdf

🎬 Initializing ScriptIngestionCoordinator...
✅ Coordinator initialized with 3 ADK agents

🚀 Starting 3-agent ADK sequential pipeline...

💾 Saving individual agent outputs...
   ✅ Saved: data/scripts/agents/adk_eighths_calculator_pdf_YYYYMMDD_HHMMSS.json
   ✅ Saved: data/scripts/agents/adk_scene_breakdown_cards_pdf_YYYYMMDD_HHMMSS.json
   ✅ Saved: data/scripts/agents/adk_department_coordinator_pdf_YYYYMMDD_HHMMSS.json
```

## NOTES
- **Environment**: Always activate virtual environment before running scripts
- **Location**: Execute all commands from `sd1` root directory
- **Individual Testing**: Each ADK agent can be run standalone for debugging
- Each ADK agent response stored with individual timestamps and metadata
- Processing status tracked throughout 3-agent sequential pipeline
- Error handling ensures partial results preserved even if individual agents fail
- All files use structured JSON format with proper indentation
- Comprehensive logging shows detailed progress for each ADK agent
- Reports generated in both JSON and human-readable text formats
- Support for department focus filtering (camera, lighting, etc.)
- Validation levels supported (strict vs lenient error handling)