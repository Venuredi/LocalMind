"""
FastAPI REST API for Code Intelligence System
Provides endpoints for querying code context, dependencies, and impact analysis.
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse, StreamingResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from pathlib import Path
import json
import io
from datetime import datetime
import asyncio
import queue
import threading

import sys
sys.path.append(str(Path(__file__).parent.parent))

from context_builder.context_assembler import ContextAssembler
from graph.graph_builder import GraphBuilder
from embeddings.vector_store import VectorStore
from embeddings.semantic_enrichment import SemanticEnricher
from prompt.context_builder import OntologyContextBuilder
from prompt.template_engine import PromptTemplateEngine

# Initialize FastAPI app
app = FastAPI(
    title="Code Intelligence API",
    description="Cross-Layer Context Engine for multi-stack repositories",
    version="1.0.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state (loaded on startup)
INDEX_PATH = "./code-intelligence/data/index.json"
REPO_PATH = "/Users/venureddy/Downloads/PeritaWorkspace"
index_data = None
graph_builder = None
context_assembler = None
vector_store = None
semantic_enricher = None

# Progress tracking for indexing
progress_queue = queue.Queue()
current_indexing_status = {
    "step": 0,
    "step_name": "Idle",
    "total_steps": 5,
    "files_processed": 0,
    "total_files": 0,
    "current_file": "",
    "status_messages": [],
    "is_running": False,
    "is_complete": False,
    "success": False,
    "stats": {}
}

# Mount static files (for web UI)
web_dir = Path(__file__).parent.parent / "web"
if web_dir.exists():
    app.mount("/static", StaticFiles(directory=str(web_dir)), name="static")


# Models
class IndexRequest(BaseModel):
    repo_path: str


class QueryRequest(BaseModel):
    query: str
    include_tests: bool = False
    max_components: int = 20
    target_files: Optional[List[str]] = None
    intent: Optional[str] = None


class ComponentQuery(BaseModel):
    component_id: str
    include_dependencies: bool = True


class ImpactAnalysisRequest(BaseModel):
    component_ids: List[str]


class PromptGenerationRequest(BaseModel):
    type: str  # enhancement, bug_fix, new_feature, etc.
    title: str
    description: str
    components: List[str]  # Component names
    target_files: Optional[List[str]] = None


# Startup
@app.on_event("startup")
async def startup_event():
    """Load index and build graph on startup."""
    global index_data, graph_builder, context_assembler, vector_store, semantic_enricher

    index_path = Path(INDEX_PATH)

    if index_path.exists():
        print("Loading existing index...")

        with open(index_path, "r") as f:
            index_data = json.load(f)

        # Build graph
        graph_builder = GraphBuilder(index_data)
        graph_builder.build_graph()

        # Initialize context assembler
        context_assembler = ContextAssembler(
            str(index_path), REPO_PATH, graph_builder
        )

        # Initialize vector store
        vector_store = VectorStore()

        # Initialize semantic enricher
        semantic_enricher = SemanticEnricher()

        print("✅ System initialized successfully")
    else:
        print("⚠️  No index found. Please index a repository first.")


# Serve web UI
@app.get("/", response_class=HTMLResponse)
async def serve_web_ui():
    """Serve the web UI."""
    web_file = Path(__file__).parent.parent / "web" / "index.html"
    if web_file.exists():
        return FileResponse(web_file)
    return {"status": "ok", "message": "Code Intelligence API", "indexed": index_data is not None}


# API Health check
@app.get("/api/health")
async def health_check():
    """API health check endpoint."""
    return {
        "status": "ok",
        "message": "Code Intelligence API",
        "indexed": index_data is not None,
    }


# Background indexing function
def index_repository_background(repo_path: str):
    """Index repository in background thread with progress tracking."""
    global index_data, graph_builder, context_assembler, vector_store, semantic_enricher, REPO_PATH, current_indexing_status

    try:
        current_indexing_status["is_running"] = True
        current_indexing_status["is_complete"] = False
        current_indexing_status["success"] = False
        current_indexing_status["status_messages"] = []
        start_time = datetime.now()

        def add_status(msg):
            current_indexing_status["status_messages"].append(msg)
            progress_queue.put(current_indexing_status.copy())

        # Step 1: Initialize
        current_indexing_status["step"] = 1
        current_indexing_status["step_name"] = "Initializing indexer"
        add_status(f"Starting indexing for: {repo_path}")

        from indexer.unified_indexer import UnifiedIndexer

        # Resolve path
        repo_path_obj = Path(repo_path)
        if not repo_path_obj.is_absolute():
            project_root = Path(__file__).parent.parent.parent
            repo_path_obj = (project_root / repo_path_obj).resolve()

        REPO_PATH = str(repo_path_obj)
        add_status(f"Repository path resolved: {REPO_PATH}")

        # Step 2: Index repository
        current_indexing_status["step"] = 2
        current_indexing_status["step_name"] = "Scanning and parsing files"
        add_status("Indexing repository...")

        def progress_callback(message):
            if "Processing" in message or message.endswith((".ts", ".tsx", ".dart", ".py", ".js", ".jsx")):
                current_indexing_status["files_processed"] += 1
                current_indexing_status["current_file"] = message
            else:
                add_status(message)
            progress_queue.put(current_indexing_status.copy())

        indexer = UnifiedIndexer(REPO_PATH, progress_callback=progress_callback)

        # Get total files count
        all_files = list(repo_path_obj.rglob("*"))
        current_indexing_status["total_files"] = len([f for f in all_files if f.is_file()])

        index_data = indexer.index_repository()
        add_status(f"✅ Indexed {len(index_data.get('components', []))} components")

        # Step 3: Enrich with semantics
        current_indexing_status["step"] = 3
        current_indexing_status["step_name"] = "Enriching with semantic information"
        add_status("Enriching components with semantic information...")

        if semantic_enricher:
            components = index_data.get("components", [])
            enriched = semantic_enricher.enrich_components(components)
            index_data["components"] = enriched
            add_status(f"✅ Enriched {len(enriched)} components")

        # Step 4: Build graph
        current_indexing_status["step"] = 4
        current_indexing_status["step_name"] = "Building dependency graph"
        add_status("Building dependency graph...")

        graph_builder = GraphBuilder(index_data)
        graph_builder.build_graph()
        add_status(f"✅ Graph built: {graph_builder.graph.number_of_nodes()} nodes, {graph_builder.graph.number_of_edges()} edges")

        # Step 5: Finalize
        current_indexing_status["step"] = 5
        current_indexing_status["step_name"] = "Saving and finalizing"
        add_status("Saving index...")

        indexer.save_index(INDEX_PATH)
        add_status(f"✅ Saved to {INDEX_PATH}")

        # Initialize context assembler
        context_assembler = ContextAssembler(INDEX_PATH, REPO_PATH, graph_builder)
        add_status("✅ Context assembler initialized")

        # Index in vector store
        if vector_store:
            components = index_data.get("components", [])
            vector_store.index_components(components)
            add_status("✅ Vector store updated")

        # Complete
        elapsed = (datetime.now() - start_time).total_seconds()
        current_indexing_status["is_complete"] = True
        current_indexing_status["success"] = True
        current_indexing_status["stats"] = {
            "components": len(index_data.get("components", [])),
            "relationships": len(index_data.get("relationships", [])),
            "apis": len(index_data.get("apis", [])),
            "elapsed_seconds": elapsed
        }
        add_status(f"✅ COMPLETE! Indexed in {elapsed:.1f} seconds")

    except Exception as e:
        current_indexing_status["is_complete"] = True
        current_indexing_status["success"] = False
        current_indexing_status["status_messages"].append(f"❌ Error: {str(e)}")
        progress_queue.put(current_indexing_status.copy())


# Index repository (start background task)
@app.post("/api/index")
async def index_repository(request: IndexRequest):
    """Start repository indexing in background."""
    global current_indexing_status

    if current_indexing_status["is_running"]:
        raise HTTPException(status_code=409, detail="Indexing already in progress")

    repo_path = request.repo_path

    # Validate path
    repo_path_obj = Path(repo_path)
    if not repo_path_obj.is_absolute():
        project_root = Path(__file__).parent.parent.parent
        repo_path_obj = (project_root / repo_path_obj).resolve()

    if not repo_path_obj.exists():
        raise HTTPException(status_code=404, detail=f"Repository not found at: {repo_path}")

    # Reset status
    current_indexing_status = {
        "step": 0,
        "step_name": "Starting...",
        "total_steps": 5,
        "files_processed": 0,
        "total_files": 0,
        "current_file": "",
        "status_messages": ["Initializing indexer..."],
        "is_running": True,
        "is_complete": False,
        "success": False,
        "stats": {}
    }

    # Put initial status in queue
    progress_queue.put(current_indexing_status.copy())

    # Start background thread
    thread = threading.Thread(
        target=index_repository_background,
        args=(repo_path,),
        daemon=True
    )
    thread.start()

    return {"status": "started", "message": "Indexing started in background"}


# Progress stream endpoint (SSE)
@app.get("/api/index/progress")
async def index_progress():
    """Stream indexing progress updates via Server-Sent Events."""
    async def generate():
        while True:
            try:
                # Get latest status from queue (non-blocking)
                status = progress_queue.get(timeout=1)
                yield f"data: {json.dumps(status)}\n\n"

                if status.get("is_complete"):
                    break
            except queue.Empty:
                # Send heartbeat with current status
                yield f"data: {json.dumps(current_indexing_status)}\n\n"

            await asyncio.sleep(0.1)

    return StreamingResponse(generate(), media_type="text/event-stream")


# Get current indexing status
@app.get("/api/index/status")
async def get_index_status():
    """Get current indexing status."""
    return current_indexing_status


# Query for context
@app.post("/api/query")
async def query_context(request: QueryRequest):
    """
    Query for code context.

    Example: "Fix login issue", "How does user registration work?"
    """
    if not context_assembler:
        raise HTTPException(
            status_code=503, detail="System not initialized. Please index a repository first."
        )

    try:
        context = context_assembler.assemble_context(
            request.query,
            include_tests=request.include_tests,
            max_components=request.max_components,
            target_files=request.target_files,
            intent=request.intent,
        )

        # Format for AI
        formatted = context_assembler.format_for_ai(context)

        return {
            "query": request.query,
            "context": context,
            "formatted_context": formatted,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Get component details
@app.get("/api/components/{component_id}")
async def get_component(
    component_id: str,
    include_dependencies: bool = Query(True),
):
    """Get details for a specific component."""
    if not graph_builder:
        raise HTTPException(
            status_code=503, detail="System not initialized"
        )

    try:
        context = graph_builder.get_component_context(
            component_id, include_deps=include_dependencies
        )

        if not context:
            raise HTTPException(status_code=404, detail="Component not found")

        return context

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# List all components
@app.get("/api/components")
async def list_components(
    layer: Optional[str] = None,
    type: Optional[str] = None,
    limit: int = Query(100, le=1000),
):
    """List all components with optional filtering."""
    if not index_data:
        raise HTTPException(
            status_code=503, detail="System not initialized"
        )

    try:
        components = index_data.get("components", [])

        # Filter by layer
        if layer:
            components = [c for c in components if c.get("layer") == layer]

        # Filter by type
        if type:
            components = [c for c in components if c.get("type") == type]

        # Limit results
        components = components[:limit]

        return {
            "total": len(components),
            "components": components,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Get dependency graph
@app.get("/api/graph")
async def get_graph():
    """Get the full dependency graph."""
    if not graph_builder:
        raise HTTPException(
            status_code=503, detail="System not initialized"
        )

    try:
        graph = graph_builder.graph

        # Convert to serializable format
        nodes = []
        for node in graph.nodes():
            nodes.append({
                "id": node,
                **graph.nodes[node]
            })

        edges = []
        for u, v, data in graph.edges(data=True):
            edges.append({
                "from": u,
                "to": v,
                **data
            })

        return {
            "nodes": nodes,
            "edges": edges,
            "stats": {
                "total_nodes": len(nodes),
                "total_edges": len(edges),
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Get flow from component
@app.get("/api/flow/{component_id}")
async def get_flow(component_id: str):
    """Get the full execution flow from a component."""
    if not context_assembler:
        raise HTTPException(
            status_code=503, detail="System not initialized"
        )

    try:
        flow = context_assembler.get_flow_context(component_id)

        return flow

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Impact analysis
@app.post("/api/impact")
async def analyze_impact(request: ImpactAnalysisRequest):
    """
    Analyze the impact of changing specific components.

    Returns what else would be affected.
    """
    if not graph_builder:
        raise HTTPException(
            status_code=503, detail="System not initialized"
        )

    try:
        impact = {
            "changed_components": request.component_ids,
            "affected_components": [],
            "affected_apis": [],
            "affected_tests": [],
        }

        # Find all dependents
        affected = set()
        for comp_id in request.component_ids:
            dependents = graph_builder.find_dependents(comp_id, depth=10)
            affected.update(dependents)

        # Get component details
        components = index_data.get("components", [])
        component_map = {c["id"]: c for c in components}

        for comp_id in affected:
            if comp_id in component_map:
                comp = component_map[comp_id]
                impact["affected_components"].append({
                    "id": comp_id,
                    "name": comp["name"],
                    "type": comp["type"],
                    "layer": comp["layer"],
                    "file_path": comp["file_path"],
                })

        # Find affected APIs
        apis = index_data.get("apis", [])
        for api in apis:
            handler = api.get("handler", "")
            for comp_id in request.component_ids:
                if comp_id in handler:
                    impact["affected_apis"].append(api)
                    break

        return impact

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Search components
@app.get("/api/search")
async def search_components(
    q: str = Query(..., min_length=2),
    limit: int = Query(20, le=100),
):
    """Search for components by name or description."""
    if not index_data:
        raise HTTPException(
            status_code=503, detail="System not initialized"
        )

    try:
        components = index_data.get("components", [])
        query_lower = q.lower()

        # Search
        results = []
        for component in components:
            name = (component.get("name") or "").lower()
            description = (component.get("description") or "").lower()
            file_path = (component.get("file_path") or "").lower()

            # Skip components with no meaningful name
            if not name:
                continue

            if query_lower in name or query_lower in description or query_lower in file_path:
                results.append({
                    "id": component.get("id", ""),
                    "name": component.get("name", ""),
                    "type": component.get("type", "unknown"),
                    "layer": component.get("layer", "unknown"),
                    "file_path": component.get("file_path", ""),
                    "description": component.get("description"),
                })

        results = results[:limit]

        return {
            "query": q,
            "total": len(results),
            "results": results,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Get API contracts
@app.get("/api/contracts")
async def get_api_contracts(
    method: Optional[str] = None,
):
    """Get all API contracts."""
    if not index_data:
        raise HTTPException(
            status_code=503, detail="System not initialized"
        )

    try:
        contracts = index_data.get("apis", [])

        # Filter by method if specified
        if method:
            contracts = [c for c in contracts if c.get("method") == method.upper()]

        return {
            "total": len(contracts),
            "contracts": contracts,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# System stats
@app.get("/api/stats")
async def get_stats():
    """Get system statistics."""
    if not index_data:
        raise HTTPException(
            status_code=503, detail="System not initialized"
        )

    try:
        components = index_data.get("components", [])
        relationships = index_data.get("relationships", [])
        apis = index_data.get("apis", [])
        infrastructure = index_data.get("infrastructure", [])

        # Count by layer
        layer_counts = {}
        for comp in components:
            layer = comp.get("layer", "unknown")
            layer_counts[layer] = layer_counts.get(layer, 0) + 1

        # Count by type
        type_counts = {}
        for comp in components:
            comp_type = comp.get("type", "unknown")
            type_counts[comp_type] = type_counts.get(comp_type, 0) + 1

        return {
            "metadata": index_data.get("metadata", {}),
            "totals": {
                "components": len(components),
                "relationships": len(relationships),
                "apis": len(apis),
                "infrastructure": len(infrastructure),
            },
            "by_layer": layer_counts,
            "by_type": type_counts,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Export ontology as downloadable JSON
@app.get("/api/export/ontology")
async def export_ontology():
    """Export the full code ontology as a downloadable JSON file."""
    if not index_data:
        raise HTTPException(
            status_code=503,
            detail="No index available. Please index a repository first."
        )
    try:
        components = index_data.get("components", [])
        export_payload = {
            "export_info": {
                "exported_at": datetime.utcnow().isoformat() + "Z",
                "generator": "Code Intelligence System",
                "version": "1.0.0",
                "stats": {
                    "total_components": len(components),
                    "total_relationships": len(index_data.get("relationships", [])),
                    "total_apis": len(index_data.get("apis", [])),
                    "total_infrastructure": len(index_data.get("infrastructure", [])),
                },
            },
            "metadata": index_data.get("metadata", {}),
            "components": components,
            "relationships": index_data.get("relationships", []),
            "apis": index_data.get("apis", []),
            "infrastructure": index_data.get("infrastructure", []),
        }
        json_bytes = json.dumps(export_payload, indent=2, ensure_ascii=False).encode("utf-8")
        filename = f"ontology_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        return StreamingResponse(
            io.BytesIO(json_bytes),
            media_type="application/json",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"',
                "Content-Length": str(len(json_bytes)),
            },
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Generate ontology-guided prompt
@app.post("/api/prompt/generate")
async def generate_prompt(request: PromptGenerationRequest):
    """
    Generate ontology-guided prompt for AI-assisted development.

    This endpoint:
    1. Extracts context from the ontology for specified components
    2. Builds dependency graph and related component information
    3. Generates a rich, structured prompt using templates
    4. Returns the prompt along with metadata

    Request:
        {
            "type": "enhancement|bug_fix|new_feature|refactoring|analysis",
            "title": "Enhancement title",
            "description": "What to do",
            "components": ["SurgeonsService", "SurgeonsRepository"],
            "target_files": ["path/to/file.ts"]  # optional
        }

    Response:
        {
            "prompt": "Full generated prompt text",
            "context": {
                "components_found": [...],
                "dependencies": [...],
                "dtos": [...],
                ...
            },
            "metadata": {
                "type": "enhancement",
                "component_count": 2,
                "has_source_code": true,
                ...
            }
        }
    """
    if not index_data or not graph_builder:
        raise HTTPException(
            status_code=503,
            detail="System not initialized. Please index a repository first."
        )

    try:
        # Initialize context builder
        context_builder = OntologyContextBuilder(index_data, graph_builder.graph)

        # Build context for each component
        full_context = {}
        components_found = []
        components_not_found = []

        for component_name in request.components:
            # Use strict context builder with validation
            comp_context = context_builder.build_context_strict(component_name)

            # Check if component was found
            if 'error' in comp_context:
                components_not_found.append({
                    'name': component_name,
                    'error': comp_context['error'],
                    'suggestions': comp_context.get('suggestions', [])
                })
            else:
                # Check validation
                validation = comp_context.get('validation', {})
                if validation.get('errors'):
                    components_not_found.append({
                        'name': component_name,
                        'error': f"Validation failed: {'; '.join(validation['errors'])}",
                        'warnings': validation.get('warnings', [])
                    })
                else:
                    components_found.append(comp_context.get('component', {}))

                    # Merge contexts if multiple components
                    if not full_context:
                        full_context = comp_context
                    else:
                        full_context = context_builder.merge_contexts(full_context, comp_context)

        # If no components found, return error with suggestions
        if not components_found:
            return {
                "error": "No components found in ontology",
                "components_not_found": components_not_found,
                "suggestion": "Please check component names. Available components can be listed via /api/components"
            }

        # Generate prompt using template engine
        template_engine = PromptTemplateEngine()

        try:
            generated_prompt = template_engine.generate(
                prompt_type=request.type,
                context=full_context,
                user_description=request.description,
                title=request.title
            )
        except ValueError as e:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid prompt type: {str(e)}. Available types: {template_engine.get_available_types()}"
            )

        # Build response
        return {
            "prompt": generated_prompt,
            "context": {
                "components_found": [
                    {
                        "name": comp.get("name"),
                        "type": comp.get("type"),
                        "layer": comp.get("layer"),
                        "file_path": comp.get("file_path")
                    }
                    for comp in components_found
                ],
                "components_not_found": components_not_found,
                "dependencies": full_context.get("dependencies", []),
                "dependents": full_context.get("dependents", []),
                "related_dtos": full_context.get("related_dtos", []),
                "related_repositories": full_context.get("related_repositories", []),
                "related_services": full_context.get("related_services", []),
                "related_controllers": full_context.get("related_controllers", []),
                "file_paths": [comp.get("file_path") for comp in components_found],
                "dependency_chain": full_context.get("dependency_chain", ""),
                "tech_stack": full_context.get("tech_stack", "")
            },
            "metadata": {
                "type": request.type,
                "component_count": len(components_found),
                "has_source_code": bool(full_context.get("file_content")),
                "generated_at": datetime.utcnow().isoformat(),
                "available_prompt_types": template_engine.get_available_types(),
                "validation": full_context.get("validation", {}),
                "categorized_dependencies": full_context.get("categorized_dependencies", {}),
                "constructor_dependencies": full_context.get("constructor_dependencies", []),
                "dependencies_count": len(full_context.get("dependencies", []))
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Prompt generation failed: {str(e)}")


# Get available prompt types
@app.get("/api/prompt/types")
async def get_prompt_types():
    """Get list of available prompt types."""
    template_engine = PromptTemplateEngine()

    return {
        "available_types": template_engine.get_available_types(),
        "descriptions": {
            "enhancement": "Improve existing code (performance, structure, type safety)",
            "bug_fix": "Fix bugs while maintaining existing functionality",
            "new_feature": "Add new functionality to existing components",
            "refactoring": "Restructure code without changing functionality",
            "analysis": "Analyze code and provide insights",
            "feature_extension": "Extend existing features with new capabilities"
        }
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
