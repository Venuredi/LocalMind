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
from prompt.phi3_prompt_engine import Phi3PromptEngine

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
    generation_method: Optional[str] = "llm"  # "llm" or "template"


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
        current_indexing_status["is_running"] = False
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
        current_indexing_status["is_running"] = False
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
@app.get("/api/components/{component_id:path}")
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

        # Critical validation: MUST have selected components
        if not components_found:
            print("[PROMPT_GEN] ❌ No components selected - cannot generate prompt")
            return {
                "error": "Please select components before generating prompt",
                "components_not_found": components_not_found,
                "suggestion": "Select at least one component from the ontology. Available components: /api/components"
            }

        # Generate prompt using user's selected method
        print(f"[PROMPT_GEN] Starting prompt generation for type: {request.type}")
        generated_prompt = None
        generation_method_param = request.generation_method or "llm"

        if generation_method_param == "template":
            # User explicitly requested template - skip LLM
            print("[PROMPT_GEN] User selected template generation method")
            template_engine = PromptTemplateEngine()
            try:
                generated_prompt = template_engine.generate(
                    prompt_type=request.type,
                    context=full_context,
                    user_description=request.description,
                    title=request.title
                )
                generation_method = "template"
                print(f"[PROMPT_GEN] ✅ Template generation succeeded, prompt length: {len(generated_prompt)}")
            except ValueError as e:
                print(f"[PROMPT_GEN] ❌ Template generation failed: {e}")
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid prompt type: {str(e)}. Available types: {template_engine.get_available_types()}"
                )
        else:
            # User requested LLM (or default) - use configured provider from settings
            generation_method = None
            try:
                # Get configured LLM provider from settings
                from config.settings import get_settings
                settings = get_settings()
                active_provider = settings.llm.active_provider.value
                provider_config = getattr(settings.llm, active_provider)

                print(f"[PROMPT_GEN] User selected LLM generation method, using provider: {active_provider} ({provider_config.model})")

                # Create LLM provider from settings
                llm_provider = LLMProviderFactory.create_from_settings()

                if llm_provider is None:
                    raise RuntimeError(f"LLM provider '{active_provider}' not properly configured")

                print(f"[PROMPT_GEN] {active_provider} provider initialized, generating prompt...")

                # Build the prompt for the LLM
                from prompt.system_instructions import SystemInstructions
                from prompt.ontology_formatter import OntologyFormatter

                system_instructions = SystemInstructions()
                formatter = OntologyFormatter()

                # Get tech stack from context
                tech_stack = full_context.get('tech_stack', 'unknown')
                system_prompt = system_instructions.get_instructions(tech_stack, full_context)

                # Format the user prompt
                formatted_context = formatter.format_for_phi3(full_context)
                user_prompt = f"""Generate an AI-ready prompt for the following task:

Task Type: {request.type}
Title: {request.title}
Description: {request.description}

Context:
{formatted_context}

Generate a comprehensive, well-structured prompt that an AI coding assistant can use to complete this task.
Include relevant code context, constraints, and clear instructions."""

                # Generate using the configured LLM
                generated_prompt = llm_provider.generate(
                    prompt=user_prompt,
                    system_prompt=system_prompt,
                    max_tokens=provider_config.max_tokens,
                    temperature=provider_config.temperature
                )

                generation_method = f"llm ({active_provider})"
                print(f"[PROMPT_GEN] ✅ LLM generation succeeded using {active_provider}, prompt length: {len(generated_prompt)}")

            except (RuntimeError, Exception) as llm_error:
                # Fallback to template-based generation if LLM fails
                print(f"[PROMPT_GEN] ⚠️ LLM generation failed ({str(llm_error)}), falling back to templates")
                template_engine = PromptTemplateEngine()
                try:
                    generated_prompt = template_engine.generate(
                        prompt_type=request.type,
                        context=full_context,
                        user_description=request.description,
                        title=request.title
                    )
                    generation_method = "template"
                    print(f"[PROMPT_GEN] ✅ Template generation succeeded, prompt length: {len(generated_prompt)}")
                except ValueError as e:
                    print(f"[PROMPT_GEN] ❌ Template generation also failed: {e}")
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
                "generation_method": generation_method,
                "available_prompt_types": ["new_feature", "feature_extension", "enhancement", "bug_fix", "refactoring", "analysis"],
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


# Generate ontology-guided prompt with streaming
@app.post("/api/prompt/generate/stream")
async def generate_prompt_stream(request: PromptGenerationRequest):
    """
    Generate ontology-guided prompt with real-time streaming.

    Provides token-by-token streaming for better UX during long LLM generations.
    Eliminates timeout issues and provides real-time feedback.

    Returns Server-Sent Events (SSE) stream.
    """
    if not index_data or not graph_builder:
        raise HTTPException(
            status_code=503,
            detail="System not initialized. Please index a repository first."
        )

    async def generate():
        """Async generator for streaming response."""
        try:
            # Step 1: Build context (same as regular endpoint)
            context_builder = OntologyContextBuilder(index_data, graph_builder.graph)
            full_context = {}
            components_found = []
            components_not_found = []

            for component_name in request.components:
                comp_context = context_builder.build_context_strict(component_name)

                if 'error' in comp_context:
                    components_not_found.append({
                        'name': component_name,
                        'error': comp_context['error']
                    })
                else:
                    validation = comp_context.get('validation', {})
                    if validation.get('errors'):
                        components_not_found.append({
                            'name': component_name,
                            'error': f"Validation failed: {'; '.join(validation['errors'])}"
                        })
                    else:
                        components_found.append(comp_context.get('component', {}))
                        if not full_context:
                            full_context = comp_context
                        else:
                            full_context = context_builder.merge_contexts(full_context, comp_context)

            # Validate components
            if not components_found:
                yield f"data: {json.dumps({'type': 'error', 'message': 'Please select components before generating prompt'})}\n\n"
                return

            # Step 2: Generate based on user's selected method
            generation_method = request.generation_method or "llm"

            if generation_method == "template":
                # User explicitly requested template - skip LLM
                yield f"data: {json.dumps({'type': 'status', 'message': 'Using template engine...', 'progress': 20})}\n\n"

                template_engine = PromptTemplateEngine()
                prompt = template_engine.generate(
                    prompt_type=request.type,
                    context=full_context,
                    user_description=request.description,
                    title=request.title
                )

                yield f"data: {json.dumps({'type': 'complete', 'full_prompt': prompt, 'method': 'template'})}\n\n"

            else:
                # User requested LLM (or default) - use configured provider from settings
                from config.settings import get_settings
                settings = get_settings()
                active_provider = settings.llm.active_provider.value
                provider_config = getattr(settings.llm, active_provider)

                yield f"data: {json.dumps({'type': 'status', 'message': f'Initializing {active_provider.upper()} LLM...', 'progress': 10})}\n\n"

                try:
                    # Create LLM provider from settings
                    llm_provider = LLMProviderFactory.create_from_settings()

                    if llm_provider is None:
                        raise RuntimeError(f"LLM provider '{active_provider}' not properly configured")

                    yield f"data: {json.dumps({'type': 'status', 'message': f'Generating prompt with {active_provider} ({provider_config.model})...', 'progress': 20})}\n\n"

                    # Build the prompt for the LLM
                    from prompt.system_instructions import SystemInstructions
                    from prompt.ontology_formatter import OntologyFormatter

                    system_instructions = SystemInstructions()
                    formatter = OntologyFormatter()

                    # Get tech stack from context
                    tech_stack = full_context.get('tech_stack', 'unknown')
                    system_prompt = system_instructions.get_instructions(tech_stack, full_context)

                    # Format the user prompt
                    formatted_context = formatter.format_for_phi3(full_context)
                    user_prompt = f"""Generate an AI-ready prompt for the following task:

Task Type: {request.type}
Title: {request.title}
Description: {request.description}

Context:
{formatted_context}

Generate a comprehensive, well-structured prompt that an AI coding assistant can use to complete this task.
Include relevant code context, constraints, and clear instructions."""

                    # Stream chunks from the configured LLM
                    accumulated = ""
                    for chunk in llm_provider.generate_stream(
                        prompt=user_prompt,
                        system_prompt=system_prompt,
                        max_tokens=provider_config.max_tokens,
                        temperature=provider_config.temperature
                    ):
                        accumulated += chunk
                        yield f"data: {json.dumps({'type': 'chunk', 'content': chunk})}\n\n"

                    # Send completion
                    yield f"data: {json.dumps({'type': 'complete', 'full_prompt': accumulated, 'method': 'llm', 'provider': active_provider, 'model': provider_config.model})}\n\n"

                except Exception as llm_error:
                    # Fallback to template (non-streaming)
                    print(f"[STREAM] LLM failed, falling back to template: {llm_error}")
                    yield f"data: {json.dumps({'type': 'status', 'message': 'LLM unavailable, using template fallback...', 'progress': 50})}\n\n"

                    template_engine = PromptTemplateEngine()
                    prompt = template_engine.generate(
                        prompt_type=request.type,
                        context=full_context,
                        user_description=request.description,
                        title=request.title
                    )

                    # Send complete template-generated prompt
                    yield f"data: {json.dumps({'type': 'complete', 'full_prompt': prompt, 'method': 'template'})}\n\n"

        except Exception as e:
            import traceback
            traceback.print_exc()
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # Disable nginx buffering
        }
    )


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


# =============================================================================
# SETTINGS / ADMINISTRATION ENDPOINTS
# =============================================================================

from config.settings import (
    SettingsManager,
    AppSettings,
    LLMProvider,
    PromptGenerationMethod,
    get_settings,
    update_settings
)
from llm.llm_provider import LLMProviderFactory

# Initialize settings manager
settings_manager = SettingsManager()


class LLMConfigUpdate(BaseModel):
    """Model for updating LLM provider configuration."""
    provider: str  # ollama, openai, anthropic, google
    enabled: Optional[bool] = None
    api_key: Optional[str] = None
    model: Optional[str] = None
    host: Optional[str] = None  # For Ollama
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    organization: Optional[str] = None  # For OpenAI


class PromptSettingsUpdate(BaseModel):
    """Model for updating prompt generation settings."""
    generation_method: Optional[str] = None  # template, llm, hybrid
    fallback_to_template: Optional[bool] = None
    validate_output: Optional[bool] = None
    enhance_safety: Optional[bool] = None


class SetActiveProviderRequest(BaseModel):
    """Model for setting active LLM provider."""
    provider: str  # ollama, openai, anthropic, google


class TestProviderRequest(BaseModel):
    """Model for testing a provider configuration."""
    provider: str
    api_key: Optional[str] = None
    model: Optional[str] = None
    host: Optional[str] = None


@app.get("/api/settings")
async def get_all_settings():
    """Get all application settings."""
    settings = get_settings()

    # Mask API keys for security (show only last 4 chars)
    settings_dict = settings.model_dump()

    for provider in ['openai', 'anthropic', 'google']:
        api_key = settings_dict['llm'][provider].get('api_key', '')
        if api_key and len(api_key) > 4:
            settings_dict['llm'][provider]['api_key'] = '****' + api_key[-4:]

    return {
        "success": True,
        "settings": settings_dict
    }


@app.get("/api/settings/llm")
async def get_llm_settings():
    """Get LLM-specific settings."""
    settings = get_settings()
    providers = settings_manager.get_available_providers()
    active_config = settings_manager.get_active_llm_config()

    return {
        "success": True,
        "active_provider": settings.llm.active_provider.value,
        "providers": providers,
        "active_config": active_config,
        "llm_enabled": settings_manager.is_llm_enabled()
    }


@app.get("/api/settings/prompt")
async def get_prompt_settings():
    """Get prompt generation settings."""
    settings = get_settings()

    return {
        "success": True,
        "generation_method": settings.prompt.generation_method.value,
        "fallback_to_template": settings.prompt.fallback_to_template,
        "validate_output": settings.prompt.validate_output,
        "enhance_safety": settings.prompt.enhance_safety,
        "available_methods": ["template", "llm", "hybrid"]
    }


@app.put("/api/settings/llm/active")
async def set_active_llm_provider(request: SetActiveProviderRequest):
    """Set the active LLM provider."""
    valid_providers = ['ollama', 'openai', 'anthropic', 'google']

    if request.provider not in valid_providers:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid provider. Must be one of: {valid_providers}"
        )

    updates = {"llm": {"active_provider": request.provider}}
    update_settings(updates)

    return {
        "success": True,
        "message": f"Active provider set to {request.provider}",
        "active_provider": request.provider
    }


@app.put("/api/settings/llm/{provider}")
async def update_llm_provider_settings(provider: str, config: LLMConfigUpdate):
    """Update settings for a specific LLM provider."""
    valid_providers = ['ollama', 'openai', 'anthropic', 'google']

    if provider not in valid_providers:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid provider. Must be one of: {valid_providers}"
        )

    # Build update dict
    updates = {"llm": {provider: {}}}

    if config.enabled is not None:
        updates["llm"][provider]["enabled"] = config.enabled
    if config.api_key is not None:
        updates["llm"][provider]["api_key"] = config.api_key
    if config.model is not None:
        updates["llm"][provider]["model"] = config.model
    if config.temperature is not None:
        updates["llm"][provider]["temperature"] = config.temperature
    if config.max_tokens is not None:
        updates["llm"][provider]["max_tokens"] = config.max_tokens

    # Provider-specific fields
    if provider == 'ollama' and config.host is not None:
        updates["llm"][provider]["host"] = config.host
    if provider == 'openai' and config.organization is not None:
        updates["llm"][provider]["organization"] = config.organization

    updated_settings = update_settings(updates)

    return {
        "success": True,
        "message": f"Updated {provider} settings",
        "provider": provider
    }


@app.put("/api/settings/prompt")
async def update_prompt_settings(config: PromptSettingsUpdate):
    """Update prompt generation settings."""
    updates = {"prompt": {}}

    if config.generation_method is not None:
        valid_methods = ['template', 'llm', 'hybrid']
        if config.generation_method not in valid_methods:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid generation method. Must be one of: {valid_methods}"
            )
        updates["prompt"]["generation_method"] = config.generation_method

    if config.fallback_to_template is not None:
        updates["prompt"]["fallback_to_template"] = config.fallback_to_template
    if config.validate_output is not None:
        updates["prompt"]["validate_output"] = config.validate_output
    if config.enhance_safety is not None:
        updates["prompt"]["enhance_safety"] = config.enhance_safety

    update_settings(updates)

    return {
        "success": True,
        "message": "Prompt settings updated"
    }


@app.post("/api/settings/llm/test")
async def test_llm_provider(request: TestProviderRequest):
    """Test connection to an LLM provider."""
    config = {}

    if request.provider == 'ollama':
        config['host'] = request.host or "http://localhost:11434"
        config['model'] = request.model or "phi3:mini"
    elif request.provider in ['openai', 'anthropic', 'google']:
        if not request.api_key:
            # Try to get from saved settings
            settings = get_settings()
            provider_settings = getattr(settings.llm, request.provider)
            config['api_key'] = provider_settings.api_key
        else:
            config['api_key'] = request.api_key

        if request.model:
            config['model'] = request.model

    result = LLMProviderFactory.test_provider(request.provider, config)

    return {
        "success": result["success"],
        "message": result["message"],
        "model_info": result.get("model_info"),
        "provider": request.provider
    }


@app.get("/api/settings/llm/models/{provider}")
async def get_available_models(provider: str):
    """Get available models for a provider."""
    models = {
        "ollama": [
            {"id": "phi3:mini", "name": "Phi-3 Mini", "description": "Fast, lightweight model"},
            {"id": "llama3.2", "name": "Llama 3.2", "description": "Meta's latest model"},
            {"id": "mistral", "name": "Mistral 7B", "description": "High quality open model"},
            {"id": "codellama", "name": "Code Llama", "description": "Optimized for code"},
            {"id": "deepseek-coder", "name": "DeepSeek Coder", "description": "Code-focused model"}
        ],
        "openai": [
            {"id": "gpt-4o", "name": "GPT-4o", "description": "Most capable model"},
            {"id": "gpt-4o-mini", "name": "GPT-4o Mini", "description": "Fast and affordable"},
            {"id": "gpt-4-turbo", "name": "GPT-4 Turbo", "description": "Balanced performance"},
            {"id": "gpt-3.5-turbo", "name": "GPT-3.5 Turbo", "description": "Legacy model"}
        ],
        "anthropic": [
            {"id": "claude-sonnet-4-20250514", "name": "Claude Sonnet 4", "description": "Latest balanced model"},
            {"id": "claude-3-5-sonnet-20241022", "name": "Claude 3.5 Sonnet", "description": "Best for coding"},
            {"id": "claude-3-haiku-20240307", "name": "Claude 3 Haiku", "description": "Fast and efficient"},
            {"id": "claude-3-opus-20240229", "name": "Claude 3 Opus", "description": "Most capable"}
        ],
        "google": [
            {"id": "gemini-1.5-pro", "name": "Gemini 1.5 Pro", "description": "Most capable"},
            {"id": "gemini-1.5-flash", "name": "Gemini 1.5 Flash", "description": "Fast and efficient"},
            {"id": "gemini-2.0-flash", "name": "Gemini 2.0 Flash", "description": "Latest fast model"}
        ]
    }

    if provider not in models:
        raise HTTPException(status_code=400, detail=f"Unknown provider: {provider}")

    return {
        "success": True,
        "provider": provider,
        "models": models[provider]
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
