#!/usr/bin/env python3
"""
Generate Ontology with Progress GUI

High-performance ontology generation with real-time progress tracking.
"""

import sys
import json
from pathlib import Path

# Add code-intelligence to path
sys.path.insert(0, str(Path(__file__).parent / "code-intelligence"))

from parsers.nestjs.optimized_nestjs_parser import OptimizedNestJSParser
from parsers.treesitter.parser_adapter import ParserAdapter
from parsers.treesitter.ontology_generator import OntologyGenerator
from validation.ontology_validator import OntologyValidator
from utils.progress_tracker import ProgressTracker, ConsoleProgressTracker


def main(repo_path: str = None, use_gui: bool = True):
    """
    Generate complete ontology with progress tracking.

    Args:
        repo_path: Path to repository (default: demo-repo/backend)
        use_gui: Whether to show GUI progress window
    """

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
        sys.exit(1)

    # Create progress tracker
    if use_gui:
        try:
            tracker = ProgressTracker(
                title="Ontology Generation - LocalMind",
                total_steps=7
            )
        except Exception as e:
            print(f"⚠️  Could not create GUI: {e}")
            print("   Falling back to console mode")
            tracker = ConsoleProgressTracker(total_steps=7)
    else:
        tracker = ConsoleProgressTracker(total_steps=7)

    tracker.start()

    try:
        # Step 1: Parse NestJS backend
        tracker.update_step(1, "Parsing NestJS Backend")

        def progress_callback(message):
            if message.endswith(".ts"):
                tracker.update_file(message)
            else:
                tracker.add_status(message)

        # Use optimized parser
        nestjs_parser = OptimizedNestJSParser(
            str(repo_path),
            progress_callback=progress_callback,
            max_workers=4,
            use_cache=True
        )

        # Find files first to set progress bar
        ts_files = [
            f for f in repo_path.rglob("*.ts")
            if not nestjs_parser._is_excluded(f)
        ]
        tracker.set_total_files(len(ts_files))
        tracker.add_status(f"Found {len(ts_files)} TypeScript files")

        # Parse
        nestjs_data = nestjs_parser.parse()

        # Check for cancellation
        if tracker.is_cancelled():
            tracker.add_status("Operation cancelled by user")
            tracker.complete(success=False)
            return

        # Show parsing stats
        stats = nestjs_parser.get_stats()
        tracker.add_status(f"✅ Parsed {stats['processed_files']} files")
        tracker.add_status(f"   Cached: {stats['cached_files']} files")
        if 'elapsed_seconds' in stats:
            tracker.add_status(f"   Time: {stats['elapsed_seconds']:.1f}s")
        if 'files_per_second' in stats:
            tracker.add_status(f"   Speed: {stats['files_per_second']:.1f} files/sec")

        tracker.add_status(f"\nComponents found:")
        tracker.add_status(f"  Controllers:      {len(nestjs_data.get('controllers', []))}")
        tracker.add_status(f"  Services:         {len(nestjs_data.get('services', []))}")
        tracker.add_status(f"  DTOs:             {len(nestjs_data.get('dtos', []))}")
        tracker.add_status(f"  Entities:         {len(nestjs_data.get('entities', []))}")
        tracker.add_status(f"  Repositories:     {len(nestjs_data.get('repositories', []))}")

        # Step 2: Adapt to ontology format
        tracker.update_step(2, "Adapting to Ontology Format")

        adapter = ParserAdapter()
        ontology_data = adapter.adapt("nestjs", nestjs_data)

        entities = ontology_data.get("entities", {})
        tracker.add_status(f"Converted to ontology format:")
        for entity_type, entity_list in entities.items():
            if entity_list:
                tracker.add_status(f"  {entity_type:20} {len(entity_list):>5}")

        # Check for cancellation
        if tracker.is_cancelled():
            tracker.complete(success=False)
            return

        # Step 3: Generate ontology graph
        tracker.update_step(3, "Generating Ontology Graph")

        generator = OntologyGenerator(ontology_data)
        graph = generator.build_ontology()

        tracker.add_status(f"✅ Graph created:")
        tracker.add_status(f"   Nodes: {graph.number_of_nodes()}")
        tracker.add_status(f"   Edges: {graph.number_of_edges()}")

        # Step 4: Save ontology
        tracker.update_step(4, "Saving Ontology Files")

        ontology_file = output_dir / "ontology.json"
        generator.save_ontology(str(ontology_file), format="json")
        tracker.add_status(f"✅ Saved: {ontology_file}")

        graphml_file = output_dir / "ontology.graphml"
        generator.save_ontology(str(graphml_file), format="graphml")
        tracker.add_status(f"✅ Saved: {graphml_file}")

        # Check for cancellation
        if tracker.is_cancelled():
            tracker.complete(success=False)
            return

        # Step 5: Validate ontology
        tracker.update_step(5, "Validating Ontology Completeness")

        validator = OntologyValidator(graph)
        results = validator.validate_coverage()

        # Show key metrics
        tracker.add_status(f"\nValidation Results:")
        tracker.add_status(f"  API Endpoints:    {results['api_coverage']['total_endpoints']}")
        tracker.add_status(f"  Services:         {results['service_coverage']['total_services']}")
        tracker.add_status(f"  Repositories:     {results['repository_coverage']['total_repositories']}")
        tracker.add_status(f"  Cross-layer:      {results['cross_layer_paths']['coverage_percent']}%")

        # Save validation report
        validation_file = output_dir / "validation_report.json"
        validator.export_validation_report(str(validation_file))
        tracker.add_status(f"✅ Saved: {validation_file}")

        # Step 6: Generate call graph
        tracker.update_step(6, "Generating Call Graph")

        call_graph = generator.get_call_graph()
        tracker.add_status(f"✅ Call graph created:")
        tracker.add_status(f"   Nodes: {call_graph.number_of_nodes()}")
        tracker.add_status(f"   Edges: {call_graph.number_of_edges()}")

        # Save call graph
        import networkx as nx
        call_graph_file = output_dir / "call_graph.json"
        call_graph_data = nx.node_link_data(call_graph)
        with open(call_graph_file, "w") as f:
            json.dump(call_graph_data, f, indent=2)
        tracker.add_status(f"✅ Saved: {call_graph_file}")

        # Step 7: Generate statistics
        tracker.update_step(7, "Generating Statistics")

        stats_file = output_dir / "ontology_stats.json"
        stats = generator.get_statistics()
        with open(stats_file, "w") as f:
            json.dump(stats, f, indent=2)
        tracker.add_status(f"✅ Saved: {stats_file}")

        # Final summary
        summary = validator.get_coverage_summary()

        tracker.add_status(f"\n{'='*60}")
        tracker.add_status("📊 FINAL SUMMARY")
        tracker.add_status(f"{'='*60}")
        tracker.add_status(f"Overall Status: {summary['overall_status']}")
        tracker.add_status(f"Health: {summary['health']}")
        tracker.add_status(f"Score: {summary['score']}%")
        tracker.add_status(f"\nOutput files in: {output_dir}")

        # Mark complete
        tracker.complete(success=True)

        # Keep window open for a bit
        if use_gui:
            import time
            time.sleep(3)

        return {
            "success": True,
            "output_dir": str(output_dir),
            "summary": summary,
        }

    except KeyboardInterrupt:
        tracker.add_status("\n❌ Interrupted by user")
        tracker.complete(success=False)
        return {"success": False, "error": "Interrupted"}

    except Exception as e:
        tracker.add_status(f"\n❌ Error: {e}")
        tracker.complete(success=False)
        import traceback
        traceback.print_exc()
        return {"success": False, "error": str(e)}

    finally:
        # Close tracker
        if use_gui:
            import time
            time.sleep(2)
        tracker.close()


if __name__ == "__main__":
    # Get repo path from command line
    repo_path = None
    if len(sys.argv) > 1:
        repo_path = sys.argv[1]

    # Check if user wants console mode
    use_gui = "--no-gui" not in sys.argv

    result = main(repo_path=repo_path, use_gui=use_gui)

    if result and result.get("success"):
        sys.exit(0)
    else:
        sys.exit(1)
