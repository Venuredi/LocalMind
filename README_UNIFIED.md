# LocalMind - Unified Code Intelligence Platform

## Overview
LocalMind is a unified code intelligence platform that indexes multi-stack repositories and provides:
- Real-time code ontology generation with progress tracking
- Interactive dependency graph visualization
- AI-ready prompt generation with full codebase context
- Cross-layer relationship analysis

## Quick Start

### 1. Start LocalMind Server
```bash
cd code-intelligence
python3 -m uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

### 2. Open Web Interface
Navigate to: **http://localhost:8000**

## Features

### 1. Connect Repository (with Real-Time Progress)
- Enter your repository path
- Click "Index Repository"
- Watch real-time progress bars showing:
  - Overall progress (steps 1-5)
  - File processing progress
  - Current file being parsed
  - Live status log
- See comprehensive stats when complete

### 2. Code Ontology Visualization
- Interactive graph of your entire codebase
- Filter by layer (Frontend, Backend, Data, etc.)
- Search and zoom functionality
- Click nodes to see dependencies and relationships
- Export ontology as JSON

### 3. Prompt Builder
- Describe what you want to build/fix
- System auto-detects intent (feature, bugfix, enhancement, etc.)
- Analyzes affected components across all layers
- Generates optimized AI prompts ready for Cursor/Claude
- Shows impact analysis

### 4. Statistics
- Component counts by layer and type
- Relationship metrics
- API endpoint inventory

## Technology Stack

### Backend (FastAPI)
- **API Server**: `code-intelligence/api/main.py`
- **Features**:
  - Server-Sent Events (SSE) for real-time progress
  - Background threading for indexing
  - Cross-layer context assembly
  - Vector store integration

### Frontend (Vanilla JS)
- **Web UI**: `code-intelligence/web/`
  - `index.html` - Main UI structure
  - `app.js` - Application logic with SSE client
  - `style.css` - Styling with progress bar components

### Indexers & Parsers
- **Unified Indexer**: Coordinates all language-specific parsers
- **Supported Languages**:
  - TypeScript/NestJS (Backend)
  - React (Web Frontend)
  - Angular (Web Frontend)
  - Flutter/Dart (Mobile)
  - Terraform (Infrastructure)
  - Kubernetes/ArgoCD (Deployment)

### Progress Tracking Architecture
```
1. User clicks "Index Repository"
2. Frontend calls POST /api/index
3. Backend starts indexing in background thread
4. Backend pushes updates to progress_queue
5. Frontend connects to GET /api/index/progress (SSE)
6. Real-time updates stream to UI
7. Progress bars and logs update live
8. Completion triggers final stats display
```

## Performance Optimizations

### Optimized NestJS Parser
- Multi-threaded parsing (4 workers)
- File caching to avoid re-parsing
- Incremental updates
- Progress callbacks for real-time feedback

### Background Processing
- Non-blocking API endpoints
- Threading for CPU-intensive tasks
- Queue-based progress communication
- Graceful error handling

## API Endpoints

### Indexing
- `POST /api/index` - Start background indexing
- `GET /api/index/progress` - SSE stream for real-time updates
- `GET /api/index/status` - Current indexing status

### Query & Analysis
- `POST /api/query` - Query codebase with natural language
- `GET /api/components` - List all components
- `GET /api/components/{id}` - Get component details
- `POST /api/impact` - Analyze change impact

### Visualization
- `GET /api/graph` - Full dependency graph
- `GET /api/stats` - Repository statistics
- `GET /api/export/ontology` - Download ontology JSON

## Architecture Comparison

### Before (Two Apps)
- **web_server.py** (Port 5001) - Standalone ontology generator
- **LocalMind** (Port 8000) - Query/visualization only
- Disconnected workflows

### After (Unified)
- **LocalMind** (Port 8000) - Everything in one place
  - Ontology generation with progress
  - Visualization
  - AI prompt generation
  - Full-stack analysis

## Development

### Project Structure
```
LocalMind/
├── code-intelligence/
│   ├── api/
│   │   └── main.py              # FastAPI server with SSE
│   ├── web/
│   │   ├── index.html           # UI with progress components
│   │   ├── app.js               # Frontend logic + SSE client
│   │   └── style.css            # Styles + progress bars
│   ├── indexer/
│   │   └── unified_indexer.py   # Multi-language indexer
│   ├── parsers/                 # Language-specific parsers
│   ├── context_builder/         # Context assembly
│   └── data/                    # Generated ontology files
└── web_server.py                # (Archived - no longer needed)
```

### Adding New Features
1. Backend changes in `api/main.py`
2. Frontend changes in `web/app.js`
3. Server auto-reloads with `--reload` flag

## Next Steps

1. **Try it out**:
   - Start the server
   - Open http://localhost:8000
   - Index your repository
   - Watch the progress bars!

2. **Explore the ontology**:
   - Click "Code Ontology" tab
   - Visualize your codebase structure
   - Search for specific components

3. **Generate AI prompts**:
   - Click "Prompt Builder" tab
   - Describe your task
   - Get context-aware prompts for AI tools

## Benefits of Unified Application

✅ Single URL (http://localhost:8000)
✅ Consistent user experience
✅ Real-time progress tracking
✅ All features integrated
✅ Better resource management
✅ Easier to maintain
✅ Professional appearance

Enjoy your unified LocalMind experience! 🎉
