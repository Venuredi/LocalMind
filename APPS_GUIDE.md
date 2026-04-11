# Application Guide

## You have TWO different web applications:

### 1. Ontology Generator (Port 5001) ⭐ USE THIS FOR GENERATION
- **Purpose**: Generate code ontology from a repository WITH PROGRESS BAR
- **File**: `web_server.py`
- **Start**: `python3 web_server.py`
- **URL**: http://localhost:5001
- **Features**:
  - Real-time progress tracking
  - Visual progress bars
  - Step-by-step status updates
  - File processing counter

### 2. Code Intelligence API (Port 8000)
- **Purpose**: Query existing ontology, search components, get context
- **File**: `code-intelligence/api/main.py`
- **Already running**: Yes (currently on port 8000)
- **URL**: http://localhost:8000
- **Features**:
  - Query code context
  - Search components
  - Impact analysis
  - Export ontology

## Quick Start for Ontology Generation:

```bash
# Stop looking at port 8000 - that's the wrong app!
# Start the ontology generator instead:
python3 web_server.py

# Then open: http://localhost:5001
```

## What you were seeing:
- Port 8000 = FastAPI app (no progress bar, for querying only)
- Port 5001 = Flask app (HAS progress bar, for generation)
