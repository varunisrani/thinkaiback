# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

### Development
- `pip install -e .` - Install the package in development mode
- `python app.py` - Start the main application (likely Streamlit-based)
- `uvicorn app:app --reload` - Start FastAPI server if using API mode

### Code Quality
- `black .` - Format code (Black formatter available in requirements)
- `pytest` - Run tests
- `pytest-asyncio` - Run async tests

### Package Management
- `pip install -r requirements.txt` - Install all dependencies
- `pip freeze > requirements.txt` - Update requirements file

## Architecture

SD1 is a comprehensive AI-powered film production planning and management system built with Python. The system uses a modular, agent-based architecture with specialized coordinators for different aspects of film production.

### Core Architecture Pattern

The system follows a **Coordinator-Agent Pattern** where each major function is managed by a coordinator that orchestrates multiple specialized agents:

```
src/
├── [module]/
│   ├── coordinator.py      # Orchestrates the workflow
│   └── agents/            # Specialized AI agents
│       ├── agent1.py
│       └── agent2.py
```

### Key Modules

#### Script Ingestion (`src/script_ingestion/`)
- **Coordinator**: `ScriptIngestionCoordinator` - Main orchestrator for script processing
- **Agents**: Parser, Metadata Extractor, Validator
- **Purpose**: Converts raw scripts into structured data with metadata and validation

#### Storyboard Generation (`src/storyboard/`)
- **Coordinator**: `StoryboardCoordinator` - Manages visual storyboard creation
- **Agents**: Prompt Generator, Image Generator, Storyboard Formatter
- **Purpose**: Creates visual storyboards from scene data with AI-generated images

#### Scheduling (`src/scheduling/`)
- **Agents**: Location Optimizer, Crew Allocator, Schedule Generator
- **Purpose**: Optimizes filming schedules considering locations, crew, and equipment

#### Character Breakdown (`src/character_breakdown/`)
- **Agents**: Dialogue Profiler, Attribute Mapper
- **Purpose**: Analyzes characters for casting and continuity requirements

#### Budgeting (`src/budgeting/`)
- **Agents**: Cost Estimator, Budget Optimizer, Budget Tracker
- **Purpose**: Estimates costs and tracks budget throughout production

#### One-Liner Generation (`src/one_liner/`)
- **Purpose**: Creates concise scene summaries for quick reference

### Configuration System

- **Base Config**: `src/base_config.py` contains model configurations and agent instructions
- **Model**: Uses Google Gemini 2.5 Flash for all agents with standardized parameters
- **Agent Instructions**: Centralized system-specific prompts for each agent type
- **Model Parameters**: Temperature (0.7), max tokens (2000), reasoning effort (medium), top_p (0.95), top_k (20)

### Data Storage

- **Structure**: All generated data stored in `data/` with timestamped files
- **Types**: Scripts, storyboards, schedules, character profiles, budgets
- **Utility**: `src/storage_utils.py` provides centralized storage management
- **Static Files**: `static/storage/` contains UI-accessible results

### Key Dependencies

- **AI/ML**: Google Gen AI SDK (Gemini 2.5 Flash), Replicate
- **Web**: FastAPI, Streamlit, Uvicorn
- **Data**: Pandas, NumPy, NetworkX
- **Visualization**: Plotly, Matplotlib, Altair

### Critical Implementation Details

1. **Async Processing**: All coordinators use async methods for AI agent orchestration
2. **Error Handling**: Comprehensive logging and error recovery in coordinators
3. **Data Persistence**: Timestamped JSON files for all generated content
4. **Modular Design**: Each module can be used independently or as part of pipeline
5. **Agent Specialization**: Each agent has specific prompts and responsibilities defined in base_config.py

### Environment Setup

Required environment variables (likely in `.env`):
- `GOOGLE_API_KEY` - Google Gen AI SDK credentials for Gemini 2.5 Flash
- `REPLICATE_API_KEY` - Replicate API key (for image generation)

### Migration Notes

The system has been updated from OpenAI GPT-4.1-mini to Google Gemini 2.5 Flash:
- All AI calls now use the unified Google Gen AI SDK
- Backward compatibility maintained through function aliases
- Enhanced reasoning capabilities with configurable reasoning effort
- Improved cost-effectiveness and performance