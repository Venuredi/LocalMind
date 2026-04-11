"""
Example: How to use the Code Intelligence System programmatically.
"""

from pathlib import Path
from code_intelligence.indexer.unified_indexer import UnifiedIndexer
from code_intelligence.graph.graph_builder import GraphBuilder
from code_intelligence.context_builder.context_assembler import ContextAssembler


def main():
    # Paths
    demo_repo = Path("./demo-repo")
    data_dir = Path("./data")
    data_dir.mkdir(exist_ok=True)

    print("=" * 60)
    print("Code Intelligence System - Example Usage")
    print("=" * 60)

    # Step 1: Index the repository
    print("\n1️⃣  Indexing repository...")
    indexer = UnifiedIndexer(str(demo_repo))
    index_data = indexer.index_repository()
    index_path = data_dir / "index.json"
    indexer.save_index(str(index_path))

    # Step 2: Build the dependency graph
    print("\n2️⃣  Building dependency graph...")
    graph_builder = GraphBuilder(index_data)
    graph = graph_builder.build_graph()

    # Save graph
    graph_path = data_dir / "graph.graphml"
    graph_builder.save_graph(str(graph_path))

    # Visualize graph
    viz_path = data_dir / "graph.png"
    graph_builder.visualize(str(viz_path), layout="spring")

    # Step 3: Query for context
    print("\n3️⃣  Querying for context...")
    assembler = ContextAssembler(str(index_path), str(demo_repo), graph_builder)

    # Example queries
    queries = [
        "Fix login issue",
        "How does user registration work?",
        "Debug authentication problems",
    ]

    for query in queries:
        print(f"\n📝 Query: '{query}'")
        context = assembler.assemble_context(query)

        print(f"   {context['summary']}")

        # Save context
        query_safe = query.replace(" ", "_").replace("?", "")
        context_path = data_dir / f"context_{query_safe}.txt"

        formatted = assembler.format_for_ai(context)

        with open(context_path, "w") as f:
            f.write(formatted)

        print(f"   Context saved to: {context_path}")

    # Step 4: Get component flow
    print("\n4️⃣  Getting execution flow...")

    # Find a screen component
    components = index_data.get("components", [])
    screen_components = [c for c in components if c["type"] in ["screen", "page"]]

    if screen_components:
        entry_point = screen_components[0]["id"]
        print(f"   Entry point: {entry_point}")

        flow = assembler.get_flow_context(entry_point)

        for layer, comps in flow["flow"].items():
            if comps:
                print(f"\n   {layer}:")
                for comp in comps:
                    print(f"     - {comp['name']} ({comp['type']})")

    # Step 5: Impact analysis
    print("\n5️⃣  Impact analysis...")

    # Find AuthService or similar
    auth_components = [
        c["id"] for c in components if "auth" in c["name"].lower() and c["type"] == "service"
    ]

    if auth_components:
        comp_id = auth_components[0]
        print(f"   Analyzing impact of changing: {comp_id}")

        dependents = graph_builder.find_dependents(comp_id, depth=3)

        print(f"   Affects {len(dependents)} components:")

        component_map = {c["id"]: c for c in components}

        for dep_id in list(dependents)[:5]:  # Show first 5
            if dep_id in component_map:
                comp = component_map[dep_id]
                print(f"     - {comp['name']} ({comp['type']}) in {comp['layer']}")

        if len(dependents) > 5:
            print(f"     ... and {len(dependents) - 5} more")

    # Step 6: Show statistics
    print("\n6️⃣  Statistics...")
    print(f"   Total components: {len(components)}")
    print(f"   Total relationships: {len(index_data.get('relationships', []))}")
    print(f"   Total API endpoints: {len(index_data.get('apis', []))}")

    # Group by layer
    layer_counts = {}
    for comp in components:
        layer = comp.get("layer", "unknown")
        layer_counts[layer] = layer_counts.get(layer, 0) + 1

    print("\n   Components by layer:")
    for layer, count in sorted(layer_counts.items()):
        print(f"     {layer}: {count}")

    print("\n" + "=" * 60)
    print("✅ Example completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()
