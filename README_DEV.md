# SD1 Film Production AI System - Development Guide

## Quick Start

### Option 1: Auto-Reload Development Server (Recommended)
```bash
# Start development server with auto-reload
./start_dev.sh

# Or directly with Python
python3 dev_server.py
```

### Option 2: Standard Uvicorn Server
```bash
# Start without auto-reload
uvicorn api:app --host 0.0.0.0 --port 8000 --reload
```

## Features

### 🔄 Auto-Reload Development Server
- **File Watching**: Automatically detects changes in `.py` files
- **Smart Restart**: Restarts server only when necessary with debouncing
- **Live Logs**: Real-time server output in terminal
- **Graceful Shutdown**: Clean server shutdown with Ctrl+C

### 📡 API Endpoints
- **Root**: `GET /` - System information and available endpoints
- **Health Check**: `GET /health` - Comprehensive system health status
- **Script Ingestion**: `POST /api/script/ingest` - Process scripts
- **Character Analysis**: `POST /api/characters` - Analyze characters
- **Schedule Generation**: `POST /api/schedule` - Generate schedules
- **Budget Estimation**: `POST /api/budget` - Create budgets
- **One-Liner Generation**: `POST /api/one-liner` - Generate scene summaries
- **Storyboard Generation**: `POST /api/storyboard` - Create storyboards

### 🐛 Debug Information
The `/api/one-liner` endpoint now provides detailed logging:
- Request data structure analysis
- Scene extraction process
- Error details with context

## Environment Setup

### Required Environment Variables
```bash
export GOOGLE_API_KEY="your_google_api_key_here"
export REPLICATE_API_TOKEN="your_replicate_token_here"  # Optional for storyboards
```

### Dependencies
- **Core**: FastAPI, Uvicorn, Google Gen AI SDK
- **Development**: Watchdog (for file monitoring)
- **Optional**: Replicate (for image generation)

## Development Workflow

1. **Start Development Server**:
   ```bash
   ./start_dev.sh
   ```

2. **Make Changes**: Edit any `.py` file in the project

3. **Auto-Restart**: Server automatically restarts when changes are detected

4. **Test API**: Use the interactive docs at `http://localhost:8000/docs`

5. **Monitor Logs**: Watch terminal for real-time server output and debugging info

## Debugging Tips

### One-Liner API Issues
- Check the logs for detailed request data structure
- The endpoint handles nested `script_data` structures
- Supports multiple field names for scene descriptions

### Health Check
Visit `/health` to see:
- Component initialization status
- Environment configuration
- API key availability

### Common Issues
1. **Import Errors**: Ensure all dependencies are installed
2. **API Key Missing**: Check environment variables
3. **Port Conflicts**: Change port in `dev_server.py` if needed

## File Structure Monitoring
The development server watches:
- Root directory (`.`)
- Source directory (`src/`)
- All subdirectories recursively

Changes to any `.py` file trigger an automatic restart.