"""
Main CLI entry point for Code Intelligence System.

Usage:
    python -m code_intelligence index --repo ./demo-repo
    python -m code_intelligence query --query "Fix login issue"
    python -m code_intelligence serve
"""

import click
from pathlib import Path
import json
import sys

from indexer.unified_indexer import UnifiedIndexer
from graph.graph_builder import GraphBuilder
from context_builder.context_assembler import ContextAssembler


@click.group()
def cli():
    """Cross-Layer Context Engine - Code Intelligence System"""
    pass


@cli.command()
@click.option(
    "--repo",
    required=True,
    type=click.Path(exists=True),
    help="Path to repository to index",
)
@click.option(
    "--output",
    default="./data/index.json",
    type=click.Path(),
    help="Output path for index file",
)
def index(repo, output):
    """Index a repository."""
    click.echo(f"🔍 Indexing repository: {repo}")

    # Create indexer
    indexer = UnifiedIndexer(repo)

    # Index the repository
    index_data = indexer.index_repository()

    # Save index
    indexer.save_index(output)

    click.echo(f"\n✅ Repository indexed successfully!")


@cli.command()
@click.option(
    "--index-file",
    default="./data/index.json",
    type=click.Path(exists=True),
    help="Path to index JSON file",
)
@click.option(
    "--output-graph",
    default="./data/graph.graphml",
    type=click.Path(),
    help="Output path for graph file",
)
@click.option(
    "--output-viz",
    default="./data/graph.png",
    type=click.Path(),
    help="Output path for visualization",
)
@click.option(
    "--layout",
    default="spring",
    type=click.Choice(["spring", "kamada_kawai", "circular"]),
    help="Visualization layout algorithm",
)
def graph(index_file, output_graph, output_viz, layout):
    """Build and visualize the dependency graph."""
    click.echo(f"📊 Building graph from: {index_file}")

    # Load index
    with open(index_file, "r") as f:
        index_data = json.load(f)

    # Build graph
    builder = GraphBuilder(index_data)
    builder.build_graph()

    # Save graph
    builder.save_graph(output_graph)

    # Visualize
    click.echo(f"🎨 Creating visualization...")
    builder.visualize(output_viz, layout=layout)

    click.echo(f"\n✅ Graph built successfully!")


@cli.command()
@click.option(
    "--index-file",
    default="./data/index.json",
    type=click.Path(exists=True),
    help="Path to index JSON file",
)
@click.option(
    "--repo",
    required=True,
    type=click.Path(exists=True),
    help="Path to repository",
)
@click.option(
    "--query",
    required=True,
    help="Query string (e.g., 'Fix login issue')",
)
@click.option(
    "--output",
    default="./data/context.txt",
    type=click.Path(),
    help="Output file for context",
)
def query(index_file, repo, query, output):
    """Query for code context."""
    click.echo(f"🔍 Query: {query}")

    # Create context assembler
    assembler = ContextAssembler(index_file, repo)

    # Assemble context
    context = assembler.assemble_context(query)

    # Format for AI
    formatted = assembler.format_for_ai(context)

    # Save
    output_path = Path(output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(formatted)

    # Also save JSON
    json_output = output_path.with_suffix(".json")
    with open(json_output, "w", encoding="utf-8") as f:
        json.dump(context, f, indent=2, ensure_ascii=False)

    click.echo(f"\n✅ Context saved to: {output_path}")
    click.echo(f"✅ JSON context saved to: {json_output}")

    # Print summary to console
    click.echo(f"\n{context['summary']}")


@cli.command()
@click.option(
    "--index-file",
    default="./data/index.json",
    type=click.Path(exists=True),
    help="Path to index JSON file",
)
@click.option(
    "--repo",
    required=True,
    type=click.Path(exists=True),
    help="Path to repository",
)
@click.option(
    "--component",
    required=True,
    help="Component ID (e.g., 'LoginScreen', 'AuthController')",
)
def flow(index_file, repo, component):
    """Get execution flow from a component."""
    click.echo(f"🔄 Getting flow from: {component}")

    # Create context assembler
    assembler = ContextAssembler(index_file, repo)

    # Get flow
    flow_context = assembler.get_flow_context(component)

    # Print flow
    click.echo(f"\n📊 Flow from {component}:\n")

    for layer, components in flow_context["flow"].items():
        if components:
            click.echo(f"\n{layer.upper()}:")
            for comp in components:
                click.echo(f"  - {comp['name']} ({comp['type']})")
                click.echo(f"    {comp['file_path']}:{comp['line_start']}")


@cli.command()
@click.option(
    "--index-file",
    default="./data/index.json",
    type=click.Path(exists=True),
    help="Path to index JSON file",
)
@click.option(
    "--component",
    required=True,
    multiple=True,
    help="Component IDs to analyze (can specify multiple)",
)
def impact(index_file, component):
    """Analyze the impact of changing components."""
    click.echo(f"⚠️  Analyzing impact of changes to: {', '.join(component)}")

    # Load index
    with open(index_file, "r") as f:
        index_data = json.load(f)

    # Build graph
    builder = GraphBuilder(index_data)
    builder.build_graph()

    # Find all affected components
    affected = set()
    for comp_id in component:
        dependents = builder.find_dependents(comp_id, depth=10)
        affected.update(dependents)

    # Print results
    click.echo(f"\n📊 Impact Analysis:\n")
    click.echo(f"Changed components: {len(component)}")
    click.echo(f"Affected components: {len(affected)}")

    if affected:
        click.echo(f"\nAffected components:")

        components = {c["id"]: c for c in index_data.get("components", [])}

        for comp_id in affected:
            if comp_id in components:
                comp = components[comp_id]
                click.echo(
                    f"  - {comp['name']} ({comp['type']}) in {comp['layer']}"
                )


@cli.command()
@click.option(
    "--host",
    default="0.0.0.0",
    help="Host to bind to",
)
@click.option(
    "--port",
    default=8000,
    type=int,
    help="Port to bind to",
)
@click.option(
    "--reload",
    is_flag=True,
    help="Enable auto-reload for development",
)
def serve(host, port, reload):
    """Start the REST API server."""
    import uvicorn

    click.echo(f"🚀 Starting Code Intelligence API server...")
    click.echo(f"   Host: {host}")
    click.echo(f"   Port: {port}")
    click.echo(f"   API docs: http://{host}:{port}/docs")

    uvicorn.run(
        "api.main:app",
        host=host,
        port=port,
        reload=reload,
    )


@cli.command()
@click.option(
    "--index-file",
    default="./data/index.json",
    type=click.Path(exists=True),
    help="Path to index JSON file",
)
def stats(index_file):
    """Show statistics about the indexed repository."""
    with open(index_file, "r") as f:
        index_data = json.load(f)

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

    click.echo("\n📊 Repository Statistics\n")

    click.echo("Totals:")
    click.echo(f"  Components: {len(components)}")
    click.echo(f"  Relationships: {len(relationships)}")
    click.echo(f"  API Endpoints: {len(apis)}")
    click.echo(f"  Infrastructure: {len(infrastructure)}")

    click.echo("\nBy Layer:")
    for layer, count in sorted(layer_counts.items()):
        click.echo(f"  {layer}: {count}")

    click.echo("\nBy Type:")
    for comp_type, count in sorted(type_counts.items()):
        click.echo(f"  {comp_type}: {count}")

    # API endpoints
    if apis:
        click.echo(f"\nAPI Endpoints ({len(apis)}):")
        for api in apis[:10]:  # Show first 10
            click.echo(f"  {api['method']} {api['endpoint']}")

        if len(apis) > 10:
            click.echo(f"  ... and {len(apis) - 10} more")


if __name__ == "__main__":
    cli()
