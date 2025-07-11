# 🎬 SD1 Film Production AI System - Architecture Report

## 📋 Executive Summary

SD1 is a comprehensive AI-powered film production planning system built with Python, utilizing Google Gemini 2.5 Flash for AI processing and FastAPI for API services. The system implements a **Coordinator-Agent Pattern** with 5 coordinators orchestrating 15 specialized agents across 6 functional modules.

## 🏗️ System Architecture Overview

### 🔧 Core Components
- **1 Main API Server** (`api.py`) - FastAPI-based central API
- **5 Coordinators** - High-level orchestrators for each functional module
- **15 Specialized Agents** - Domain-specific AI agents
- **6 Functional Modules** - Script ingestion, character breakdown, scheduling, budgeting, storyboard generation, one-liner generation

---

## 🌐 API Endpoints Analysis

### 🖥️ Main API Server (`api.py`)
**Total API Endpoints: 18**

#### ⚙️ Core System Endpoints (3)
- `GET /` - System status and endpoint discovery 📊
- `GET /health` - Comprehensive health check 🩺
- `GET /api/config/model` - Model configuration ⚙️

#### 📝 Script Ingestion Endpoints (4)
- `POST /api/script/ingest` - Main script processing 📄
- `POST /api/script/text` - Frontend text processing 💬
- `POST /api/script/upload` - File upload processing 📤
- `POST /api/script/file` - Alternative file processing 📁

#### 🎭 Character Analysis Endpoints (2)
- `POST /api/character/analyze` - Character analysis 🎭
- `POST /api/characters` - Frontend character analysis 👥

#### 📅 Scheduling Endpoints (2)
- `POST /api/schedule/generate` - Schedule generation 📅
- `POST /api/schedule` - Frontend schedule generation 🗓️

#### 💰 Budgeting Endpoints (2)
- `POST /api/budget/estimate` - Budget estimation 💰
- `POST /api/budget` - Frontend budget estimation 💸

#### 🎨 Storyboard Endpoints (3)
- `POST /api/storyboard/generate` - Storyboard generation 🎨
- `POST /api/storyboard` - Frontend storyboard generation 🖼️
- `POST /api/storyboard/batch` - Batch storyboard generation 🎬

#### 📝 One-Liner Endpoints (2)
- `POST /api/oneliners/generate` - One-liner generation 📝
- `POST /api/one-liner` - Frontend one-liner generation ✨

---

## 🎯 Coordinators Analysis

### 1. 📝 Script Ingestion Coordinator
**Input**: Raw script text, validation level, department focus  
**Output**: Structured script data, metadata, validation results  
**Agents**: ScriptParserAgent, MetadataAgent, ValidatorAgent  
**Data Flow**: Script Text → Parse → Extract Metadata → Validate → Structured Output

### 2. 🎭 Character Breakdown Coordinator  
**Input**: Structured script data  
**Output**: Character profiles, relationships, scene matrix  
**Agents**: DialogueProfilerAgent, AttributeMapperAgent  
**Data Flow**: Script Data → Analyze Dialogue → Map Attributes → Character Profiles

### 3. 📅 Scheduling Coordinator
**Input**: Scene data, crew data, constraints, start date  
**Output**: Optimized schedule, calendar data, Gantt charts  
**Agents**: LocationOptimizerAgent, CrewAllocatorAgent, ScheduleGeneratorAgent  
**Data Flow**: Scene Data → Optimize Locations → Allocate Crew → Generate Schedule

### 4. 💰 Budgeting Coordinator
**Input**: Production data, location data, crew data, constraints  
**Output**: Cost breakdowns, optimizations, tracking metrics  
**Agents**: CostEstimatorAgent, BudgetOptimizerAgent, BudgetTrackerAgent  
**Data Flow**: Production Data → Estimate Costs → Optimize Budget → Track Expenses

### 5. 🎨 Storyboard Coordinator
**Input**: Scene data, shot settings  
**Output**: Storyboard images, formatted displays, export options  
**Agents**: PromptGeneratorAgent, ImageGeneratorAgent, StoryboardFormatterAgent  
**Data Flow**: Scene Data → Generate Prompts → Create Images → Format Storyboard

---

## 🤖 Agents Inventory

### 📝 Script Ingestion Module (3 Agents)
1. **🔍 ScriptParserAgent** - Parses raw scripts into structured data
2. **📊 MetadataAgent** - Extracts technical metadata and requirements
3. **✅ ValidatorAgent** - Validates data integrity and compliance

### 🎭 Character Breakdown Module (2 Agents)
4. **💬 DialogueProfilerAgent** - Analyzes character dialogue and relationships
5. **👤 AttributeMapperAgent** - Maps physical attributes and costume requirements

### 📅 Scheduling Module (3 Agents)
6. **📍 LocationOptimizerAgent** - Optimizes shooting locations using TSP algorithms
7. **👥 CrewAllocatorAgent** - Allocates crew and equipment with union rule compliance
8. **📅 ScheduleGeneratorAgent** - Generates detailed shooting schedules

### 💰 Budgeting Module (3 Agents)
9. **💸 CostEstimatorAgent** - Estimates costs using Indian market rates
10. **📊 BudgetOptimizerAgent** - Optimizes budget allocation with scenario analysis
11. **📈 BudgetTrackerAgent** - Tracks expenses with health monitoring

### 🎨 Storyboard Module (3 Agents)
12. **💡 PromptGeneratorAgent** - Generates AI image prompts
13. **🖼️ ImageGeneratorAgent** - Creates images using Replicate (Flux Schnell)
14. **🎬 StoryboardFormatterAgent** - Formats storyboards for display/export

### ✨ One-Liner Module (1 Agent)
15. **📝 OneLinerAgent** - Generates concise scene summaries

---

## 🔄 Data Flow Architecture

### 🚀 Primary Data Flow Pipeline
```
Raw Script → Script Ingestion → Character Breakdown → Scheduling → Budgeting → Storyboard → One-Liner
```

### 📊 Input/Output Data Structures

#### 📝 Script Ingestion
- **Input**: `script_text` (string), `validation_level` (string), `department_focus` (list)
- **Output**: `{parsed_data, metadata, validation, statistics, ui_metadata, saved_paths}`

#### 🎭 Character Breakdown
- **Input**: Structured script data from script ingestion
- **Output**: `{characters, relationships, scene_matrix, statistics}`

#### 📅 Scheduling
- **Input**: Scene data, crew data, start date, constraints
- **Output**: `{location_plan, crew_allocation, schedule, calendar_data, gantt_data, summary}`

#### 💰 Budgeting
- **Input**: Production data, location data, crew data, constraints
- **Output**: `{budget_breakdown, total_budget, summary, recommendations, cash_flow_analysis}`

#### 🎨 Storyboard
- **Input**: Scene data, shot settings
- **Output**: `{scenes, metadata, saved_path, export_options}`

#### ✨ One-Liner
- **Input**: Scene descriptions array
- **Output**: `{one_liners, metadata, cache_info}`

---

## 🛠️ Technical Architecture

### 🤖 AI Model Configuration
- **Primary Model**: Google Gemini 2.5 Flash 🧠
- **Configuration**: Temperature 0.7, Max tokens 8000, Top-p 0.95, Top-k 20
- **Fallback**: Comprehensive error handling with graceful degradation

### 💾 Data Persistence
- **Storage**: Timestamped JSON files in structured directories
- **Locations**: `data/scripts/`, `data/characters/`, `data/schedules/`, `data/budgets/`, `data/storyboards/`
- **Static Access**: Web-accessible paths for frontend consumption

### 🚨 Error Handling
- **Pattern**: Try-catch blocks with detailed logging
- **Fallbacks**: Safe defaults for all operations
- **Monitoring**: Health checks and system status monitoring

---

## ⚡ Performance & Scalability

### 🔀 Concurrent Processing
- **Async Architecture**: All coordinators use async/await patterns
- **Batch Processing**: Supported for storyboard generation
- **Caching**: TTL-based caching for one-liner generation

### 📈 Resource Management
- **API Limits**: Respect Google Gemini and Replicate rate limits
- **Memory**: Efficient JSON processing with streaming where possible
- **Storage**: Organized file structure with cleanup capabilities

---

## 🔐 Security & Compliance

### 🛡️ API Security
- **CORS**: Configured for cross-origin requests
- **Input Validation**: Comprehensive validation at all entry points
- **Error Handling**: Safe error responses without sensitive information

### 📋 Industry Standards
- **SMPTE Compliance**: Metadata validation
- **DGA Compliance**: Call sheet generation
- **Union Rules**: Crew allocation validation

---

## 📊 Summary Statistics

| Component Type | Count | Purpose | Emoji |
|---|---|---|---|
| **API Endpoints** | 18 | External interface | 🌐 |
| **Coordinators** | 5 | High-level orchestration | 🎯 |
| **Agents** | 15 | Specialized AI processing | 🤖 |
| **Modules** | 6 | Functional domains | 📦 |
| **Data Stores** | 6 | Persistent storage locations | 💾 |
| **AI Models** | 1 | Google Gemini 2.5 Flash | 🧠 |
| **External APIs** | 2 | Google AI, Replicate | 🔗 |

## 🎯 Key Features

### 🌟 Production-Ready Capabilities
- ✅ End-to-end automation from script to storyboard
- ✅ Regional optimization for Indian film industry
- ✅ Real-time budget tracking and optimization
- ✅ Union rule compliance for crew scheduling
- ✅ SMPTE and DGA standard compliance
- ✅ Comprehensive error handling and monitoring

### 🚀 AI-Powered Intelligence
- 🧠 Google Gemini 2.5 Flash for all text processing
- 🎨 Replicate Flux Schnell for image generation
- 📊 Advanced optimization algorithms (TSP for locations)
- 🔄 Intelligent caching and retry mechanisms
- 📈 Predictive budget analysis and health monitoring

### 🎬 Film Industry Focus
- 🎭 Character analysis and relationship mapping
- 📅 Location-optimized shooting schedules
- 💰 Indian market-specific cost templates
- 🎨 Professional storyboard generation
- 📝 Production-ready documentation formats

## 🔧 Technology Stack

### 🖥️ Backend Technologies
- **FastAPI** - High-performance web framework
- **Python 3.9+** - Core programming language
- **Google Gemini 2.5 Flash** - Primary AI model
- **Replicate** - Image generation service
- **NetworkX** - Graph algorithms for optimization
- **Uvicorn** - ASGI server

### 📊 Data & Storage
- **JSON** - Primary data format
- **File System** - Timestamped data persistence
- **Caching** - TTL-based performance optimization
- **Static Files** - Web-accessible media storage

### 🎨 Export & Integration
- **PDF** - Storyboard and document export
- **HTML** - Slideshow and presentation formats
- **Calendar** - Industry-standard scheduling formats
- **Gantt Charts** - Project management visualization

---

## 🏁 Conclusion

The SD1 system provides a **comprehensive, production-ready solution** for film pre-production planning with end-to-end automation from script ingestion through storyboard generation. Optimized for the **Indian film industry** with regional cost templates and local production workflows, it represents a significant advancement in AI-powered film production technology.

**🎬 Ready for Production | 🤖 AI-Powered | 🇮🇳 India-Optimized**

---

*Report Generated: 2025-07-04*  
*System Version: 1.0.0*  
*AI Model: Google Gemini 2.5 Flash*