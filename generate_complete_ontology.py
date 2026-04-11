#!/usr/bin/env python3
"""
Generate Complete Ontology with API/Service Layer Support

This script uses the enhanced ontology pipeline:
1. Parse NestJS/Angular/React code
2. Adapt to unified format
3. Generate ontology with API/service edges
4. Validate completeness
5. Generate visualizations and reports
"""

import sys
import json
from pathlib import Path

# Add code-intelligence to path
sys.path.insert(0, str(Path(__file__).parent / "code-intelligence"))

from parsers.nestjs.enhanced_nestjs_parser import EnhancedNestJSParser
from parsers.treesitter.parser_adapter import ParserAdapter
from parsers.treesitter.ontology_generator import OntologyGenerator
from validation.ontology_validator import OntologyValidator


def main():
    """Generate complete ontology with validation."""

    print("=" * 70)
    print("🚀 Complete Ontology Generation Pipeline")
    print("=" * 70)

    # Configuration
    repo_path = Path(__file__).parent / "demo-repo" / "backend"
    output_dir = Path(__file__).parent / "data"
    output_dir.mkdir(exist_ok=True)

    # Check if demo repo exists
    if not repo_path.exists():
        print(f"\n⚠️  Demo repository not found at: {repo_path}")
        print("This script expects a demo-repo/backend directory.")
        print("\nYou can modify the repo_path in the script to point to your repository.")
        return

    # Step 1: Parse NestJS backend
    print("\n" + "=" * 70)
    print("📝 Step 1: Parsing NestJS Backend")
    print("=" * 70)

    nestjs_parser = EnhancedNestJSParser(str(repo_path))
    nestjs_data = nestjs_parser.parse()

    # Show parsing stats
    print(f"\nParsed NestJS components:")
    print(f"  Controllers:      {len(nestjs_data.get('controllers', []))}")
    print(f"  Services:         {len(nestjs_data.get('services', []))}")
    print(f"  DTOs:             {len(nestjs_data.get('dtos', []))}")
    print(f"  Entities:         {len(nestjs_data.get('entities', []))}")
    print(f"  Repositories:     {len(nestjs_data.get('repositories', []))}")
    print(f"  GraphQL Resolvers:{len(nestjs_data.get('graphql_resolvers', []))}")
    print(f"  Modules:          {len(nestjs_data.get('modules', []))}")

    # Step 2: Adapt to ontology format
    print("\n" + "=" * 70)
    print("🔄 Step 2: Adapting to Ontology Format")
    print("=" * 70)

    adapter = ParserAdapter()
    ontology_data = adapter.adapt("nestjs", nestjs_data)

    entities = ontology_data.get("entities", {})
    print(f"\nAdapted entities:")
    for entity_type, entity_list in entities.items():
        if entity_list:
            print(f"  {entity_type:20} {len(entity_list):>5}")

    # Step 3: Generate ontology graph
    print("\n" + "=" * 70)
    print("🔨 Step 3: Generating Ontology Graph")
    print("=" * 70)

    generator = OntologyGenerator(ontology_data)
    graph = generator.build_ontology()

    # Save ontology
    ontology_file = output_dir / "ontology.json"
    generator.save_ontology(str(ontology_file), format="json")

    # Save as GraphML for Neo4j
    graphml_file = output_dir / "ontology.graphml"
    generator.save_ontology(str(graphml_file), format="graphml")

    # Step 4: Validate ontology
    print("\n" + "=" * 70)
    print("✅ Step 4: Validating Ontology Completeness")
    print("=" * 70)

    validator = OntologyValidator(graph)
    validator.print_report()

    # Export validation report
    validation_file = output_dir / "validation_report.json"
    validator.export_validation_report(str(validation_file))

    # Step 5: Generate statistics
    print("\n" + "=" * 70)
    print("📊 Step 5: Ontology Statistics")
    print("=" * 70)

    generator.print_statistics()

    # Step 6: Generate call graph
    print("\n" + "=" * 70)
    print("📞 Step 6: Generating Call Graph")
    print("=" * 70)

    call_graph = generator.get_call_graph()
    print(f"\nCall Graph:")
    print(f"  Nodes: {call_graph.number_of_nodes()}")
    print(f"  Edges: {call_graph.number_of_edges()}")

    # Save call graph
    import networkx as nx
    call_graph_file = output_dir / "call_graph.json"
    call_graph_data = nx.node_link_data(call_graph)
    with open(call_graph_file, "w") as f:
        json.dump(call_graph_data, f, indent=2)
    print(f"  Saved to: {call_graph_file}")

    # Step 7: Generate visualization (optional)
    print("\n" + "=" * 70)
    print("🎨 Step 7: Generating Visualizations (Optional)")
    print("=" * 70)

    try:
        # Visualize API layer only (more readable)
        viz_file = output_dir / "ontology_api_layer.png"
        generator.visualize(
            str(viz_file),
            layout="hierarchical",
            node_types=["controller", "api_endpoint", "service", "repository"]
        )
        print(f"  ✅ API layer visualization saved to: {viz_file}")
    except Exception as e:
        print(f"  ⚠️  Visualization skipped (optional): {e}")

    # Final summary
    print("\n" + "=" * 70)
    print("🎉 Ontology Generation Complete!")
    print("=" * 70)

    print(f"\n📁 Output files:")
    print(f"  Ontology (JSON):       {ontology_file}")
    print(f"  Ontology (GraphML):    {graphml_file}")
    print(f"  Validation Report:     {validation_file}")
    print(f"  Call Graph:            {call_graph_file}")

    print("\n💡 Next steps:")
    print("  1. Review validation report for completeness")
    print("  2. Run diagnostic: python diagnose_ontology.py data/ontology.json")
    print("  3. Import GraphML into Neo4j for graph queries")

    # Get validation summary
    summary = validator.get_coverage_summary()

    if summary["score"] >= 80:
        print("\n✅ SUCCESS: Ontology is complete and ready to use!")
    elif summary["score"] >= 60:
        print("\n⚠️  PARTIAL SUCCESS: Ontology is mostly complete, some gaps remain")
    else:
        print("\n❌ INCOMPLETE: Ontology has significant gaps")
        print("   Review ONTOLOGY_COMPLETENESS_FIX_PLAN.md for solutions")

    print("\n" + "=" * 70 + "\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
