#!/usr/bin/env python3
"""
Generate Ontology - Simple Console Version

No GUI, no threads, just straightforward processing with console output.
Use this if the GUI version has issues.
"""

import sys
import json
from pathlib import Path
from datetime import datetime

# Add code-intelligence to path
sys.path.insert(0, str(Path(__file__).parent / "code-intelligence"))

from parsers.nestjs.optimized_nestjs_parser import OptimizedNestJSParser
from parsers.treesitter.parser_adapter import ParserAdapter
from parsers.treesitter.ontology_generator import OntologyGenerator
from validation.ontology_validator import OntologyValidator


def print_header(text):
    """Print a header."""
    print(f"\n{'='*70}")
    print(f"{text}")
    print(f"{'='*70}")


def print_status(text, indent=1):
    """Print status message."""
    print(f"{'  ' * indent}{text}")


def main(repo_path: str = None):
    """
    Generate ontology with simple console output.

    Args:
        repo_path: Path to repository
    """
    print_header("🚀 Ontology Generation - Simple Console Mode")

    # Configuration
    if repo_path is None:
        repo_path = Path(__file__).parent / "demo-repo" / "backend"
    else:
        repo_path = Path(repo_path)

    output_dir = Path(__file__).parent / "data"
    output_dir.mkdir(exist_ok=True)

    # Check if repo exists
    if not repo_path.exists():
        print(f"\n❌ Repository not found at: {repo_path}")
        print("\nUsage:")
        print(f"  python {Path(__file__).name} [repo_path]")
        print("\nExample:")
        print(f"  python {Path(__file__).name} /Users/venureddy/Downloads/PeritaWorkspace")
        return False

    start_time = datetime.now()

    try:
        # Step 1: Parse NestJS backend
        print_header("Step 1/7: Parsing NestJS Backend")

        files_processed = [0]  # Use list to modify in closure

        def progress_callback(message):
            if message.endswith(".ts"):
                files_processed[0] += 1
                if files_processed[0] % 50 == 0:
                    print_status(f"Processed {files_processed[0]} files...")
            else:
                print_status(message)

        print_status("Creating parser...")
        nestjs_parser = OptimizedNestJSParser(
            str(repo_path),
            progress_callback=progress_callback,
            max_workers=4,
            use_cache=True
        )

        print_status("Finding TypeScript files...")
        ts_files = [
            f for f in repo_path.rglob("*.ts")
            if not nestjs_parser._is_excluded(f)
        ]
        print_status(f"Found {len(ts_files)} TypeScript files (excluding node_modules, etc.)")

        print_status("Parsing files (this may take a few minutes)...")
        nestjs_data = nestjs_parser.parse()

        # Show parsing stats
        stats = nestjs_parser.get_stats()
        print_status(f"✅ Parsed {stats['processed_files']} files")
        print_status(f"   Cached: {stats['cached_files']} files")
        if 'elapsed_seconds' in stats:
            print_status(f"   Time: {stats['elapsed_seconds']:.1f}s")

        print_status("\nComponents found:")
        print_status(f"  Controllers:      {len(nestjs_data.get('controllers', []))}", 2)
        print_status(f"  Services:         {len(nestjs_data.get('services', []))}", 2)
        print_status(f"  DTOs:             {len(nestjs_data.get('dtos', []))}", 2)
        print_status(f"  Entities:         {len(nestjs_data.get('entities', []))}", 2)
        print_status(f"  Repositories:     {len(nestjs_data.get('repositories', []))}", 2)

        # Step 2: Adapt to ontology format
        print_header("Step 2/7: Adapting to Ontology Format")

        adapter = ParserAdapter()
        ontology_data = adapter.adapt("nestjs", nestjs_data)

        entities = ontology_data.get("entities", {})
        print_status("Converted to ontology format:")
        for entity_type, entity_list in entities.items():
            if entity_list:
                print_status(f"  {entity_type:20} {len(entity_list):>5}", 2)

        # Step 3: Generate ontology graph
        print_header("Step 3/7: Generating Ontology Graph")

        generator = OntologyGenerator(ontology_data)
        graph = generator.build_ontology()

        print_status(f"✅ Graph created:")
        print_status(f"   Nodes: {graph.number_of_nodes()}", 2)
        print_status(f"   Edges: {graph.number_of_edges()}", 2)

        # Step 4: Save ontology
        print_header("Step 4/7: Saving Ontology Files")

        ontology_file = output_dir / "ontology.json"
        generator.save_ontology(str(ontology_file), format="json")
        print_status(f"✅ Saved: {ontology_file}")

        graphml_file = output_dir / "ontology.graphml"
        generator.save_ontology(str(graphml_file), format="graphml")
        print_status(f"✅ Saved: {graphml_file}")

        # Step 5: Validate ontology
        print_header("Step 5/7: Validating Ontology Completeness")

        validator = OntologyValidator(graph)
        results = validator.validate_coverage()

        # Show key metrics
        print_status("Validation Results:")
        print_status(f"  API Endpoints:    {results['api_coverage']['total_endpoints']}", 2)
        print_status(f"  Services:         {results['service_coverage']['total_services']}", 2)
        print_status(f"  Repositories:     {results['repository_coverage']['total_repositories']}", 2)
        print_status(f"  Cross-layer:      {results['cross_layer_paths']['coverage_percent']}%", 2)

        # Save validation report
        validation_file = output_dir / "validation_report.json"
        validator.export_validation_report(str(validation_file))
        print_status(f"✅ Saved: {validation_file}")

        # Step 6: Generate call graph
        print_header("Step 6/7: Generating Call Graph")

        call_graph = generator.get_call_graph()
        print_status(f"✅ Call graph created:")
        print_status(f"   Nodes: {call_graph.number_of_nodes()}", 2)
        print_status(f"   Edges: {call_graph.number_of_edges()}", 2)

        # Save call graph
        import networkx as nx
        call_graph_file = output_dir / "call_graph.json"
        call_graph_data = nx.node_link_data(call_graph)
        with open(call_graph_file, "w") as f:
            json.dump(call_graph_data, f, indent=2)
        print_status(f"✅ Saved: {call_graph_file}")

        # Step 7: Generate statistics
        print_header("Step 7/7: Generating Statistics")

        stats_file = output_dir / "ontology_stats.json"
        stats = generator.get_statistics()
        with open(stats_file, "w") as f:
            json.dump(stats, f, indent=2)
        print_status(f"✅ Saved: {stats_file}")

        # Final summary
        summary = validator.get_coverage_summary()

        print_header("✅ COMPLETE - Final Summary")
        print_status(f"Overall Status: {summary['overall_status']}")
        print_status(f"Health: {summary['health']}")
        print_status(f"Score: {summary['score']}%")
        print_status(f"\nOutput files in: {output_dir}")

        elapsed = (datetime.now() - start_time).total_seconds()
        print_status(f"\nTotal time: {elapsed:.1f} seconds")

        if summary["score"] >= 80:
            print_status("\n✅ SUCCESS: Ontology is complete and ready to use!")
        elif summary["score"] >= 60:
            print_status("\n⚠️  PARTIAL SUCCESS: Ontology is mostly complete")
        else:
            print_status("\n❌ INCOMPLETE: Ontology has significant gaps")

        print(f"\n{'='*70}\n")

        return True

    except KeyboardInterrupt:
        print_header("❌ Interrupted by User")
        return False

    except Exception as e:
        print_header("❌ Error Occurred")
        print_status(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    # Get repo path from command line
    repo_path = None
    if len(sys.argv) > 1:
        repo_path = sys.argv[1]

    success = main(repo_path=repo_path)

    sys.exit(0 if success else 1)
