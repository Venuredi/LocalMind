#!/usr/bin/env python3
"""Quick ontology diagnostic."""

import json
import networkx as nx
from pathlib import Path
import sys

def diagnose(ontology_path: str):
    """Run quick diagnostic."""

    # Load ontology
    try:
        with open(ontology_path) as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"❌ Ontology file not found: {ontology_path}")
        print("\nGenerate an ontology first:")
        print("  python example_treesitter_usage.py")
        sys.exit(1)

    graph = nx.node_link_graph(data)

    print("🔍 ONTOLOGY DIAGNOSTIC")
    print("="*60)

    # Node type breakdown
    node_types = {}
    for _, attrs in graph.nodes(data=True):
        node_type = attrs.get("type", "unknown")
        node_types[node_type] = node_types.get(node_type, 0) + 1

    print("\n📦 Node Types:")
    for node_type, count in sorted(node_types.items(), key=lambda x: -x[1]):
        status = "✅" if count > 0 else "❌"
        print(f"  {status} {node_type:20} {count:>5}")

    # Edge type breakdown
    edge_types = {}
    for _, _, attrs in graph.edges(data=True):
        edge_type = attrs.get("relationship", "unknown")
        edge_types[edge_type] = edge_types.get(edge_type, 0) + 1

    print("\n🔗 Edge Types:")
    for edge_type, count in sorted(edge_types.items(), key=lambda x: -x[1]):
        print(f"     {edge_type:20} {count:>5}")

    # Critical checks
    print("\n🔥 Critical Checks:")

    checks = {
        "UI components exist": any(
            t in node_types for t in ["component", "widget", "screen"]
        ),
        "API endpoints exist": node_types.get("api_endpoint", 0) > 0,
        "Controllers exist": node_types.get("controller", 0) > 0,
        "Services exist": node_types.get("service", 0) > 0,
        "DTOs exist": node_types.get("dto", 0) > 0,
        "Repositories exist": node_types.get("repository", 0) > 0,
        "Entities exist": any(
            t in node_types for t in ["entity", "model", "prisma_model"]
        ),
        "API call edges exist": any(
            t in edge_types for t in ["calls_api", "exposes_endpoint", "api"]
        ),
        "Execution edges exist": any(
            t in edge_types for t in [
                "calls_service",
                "uses_repository",
                "execution"
            ]
        ),
    }

    for check, passed in checks.items():
        status = "✅" if passed else "❌"
        print(f"  {status} {check}")

    # Stats
    print("\n📊 Statistics:")
    print(f"     Total Nodes:      {graph.number_of_nodes():>5}")
    print(f"     Total Edges:      {graph.number_of_edges():>5}")
    print(f"     API Endpoints:    {node_types.get('api_endpoint', 0):>5}")
    print(f"     Controllers:      {node_types.get('controller', 0):>5}")
    print(f"     Services:         {node_types.get('service', 0):>5}")
    print(f"     DTOs:             {node_types.get('dto', 0):>5}")
    print(f"     Repositories:     {node_types.get('repository', 0):>5}")

    # Cross-layer traceability
    print("\n🔍 Cross-Layer Traceability:")

    # Find API endpoints
    endpoints = [
        n for n, d in graph.nodes(data=True)
        if d.get("type") == "api_endpoint"
    ]

    if endpoints:
        traceable = 0
        for endpoint in endpoints:
            if can_trace_to_data_layer(graph, endpoint):
                traceable += 1

        coverage = (traceable / len(endpoints) * 100) if endpoints else 0
        status = "✅" if coverage > 50 else "❌"
        print(f"  {status} Traceable endpoints: {traceable}/{len(endpoints)} ({coverage:.1f}%)")
    else:
        print("  ❌ No API endpoints found - cannot verify traceability")

    # Overall
    passed_count = sum(1 for p in checks.values() if p)
    total_count = len(checks)

    print(f"\n{'='*60}")
    print(f"RESULT: {passed_count}/{total_count} checks passed")

    if passed_count == total_count:
        print("✅ Ontology looks COMPLETE")
    else:
        print("❌ Ontology is INCOMPLETE")
        print("\nSee ONTOLOGY_COMPLETENESS_FIX_PLAN.md for fixes")

    print("="*60)


def can_trace_to_data_layer(graph: nx.Graph, start_node: str) -> bool:
    """Check if we can trace from start_node to data layer."""
    visited = set()
    queue = [start_node]

    while queue:
        current = queue.pop(0)

        if current in visited:
            continue

        visited.add(current)

        # Check if we reached data layer
        node_data = graph.nodes.get(current, {})
        node_type = node_data.get("type", "")
        node_layer = node_data.get("layer", "")

        if node_layer == "data" or node_type in ["repository", "entity", "model"]:
            return True

        # Continue BFS
        try:
            for successor in graph.successors(current):
                queue.append(successor)
        except:
            # Undirected graph
            for neighbor in graph.neighbors(current):
                queue.append(neighbor)

    return False


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python diagnose_ontology.py <ontology.json>")
        print("\nExample:")
        print("  python diagnose_ontology.py data/ontology.json")
        sys.exit(1)

    diagnose(sys.argv[1])
