"""
Example usage of the Tree Sitter Global Parser and Ontology Generator.

This script demonstrates how to:
1. Parse a codebase using Tree Sitter
2. Generate ontologies/graphs from the parsed code
3. Visualize and analyze the code structure
4. Export results in various formats
"""

import sys
from pathlib import Path

# Add the code-intelligence directory to the path
sys.path.insert(0, str(Path(__file__).parent))

from code_intelligence.parsers.treesitter import TreeSitterParser, OntologyGenerator


def example_1_basic_parsing():
    """Example 1: Basic parsing of a repository."""
    print("\n" + "=" * 70)
    print("EXAMPLE 1: Basic Repository Parsing")
    print("=" * 70)

    # Initialize the parser with your repository path
    repo_path = "./demo-repo"  # Change this to your repository path
    parser = TreeSitterParser(repo_path)

    # Parse the entire repository
    results = parser.parse_repository()

    # Display summary
    print("\nParsing Summary:")
    print(f"  Total files parsed: {results['summary']['total_files']}")
    print(f"  Languages detected: {', '.join(results['summary']['languages'])}")
    print("\nEntity counts:")
    for entity_type, count in results['summary']['entity_counts'].items():
        if count > 0:
            print(f"  {entity_type}: {count}")

    # Save results to JSON
    parser.save_results("./data/treesitter/parsed_results.json")

    return parser, results


def example_2_ontology_generation(parser, results):
    """Example 2: Generate ontology/graph from parsed data."""
    print("\n" + "=" * 70)
    print("EXAMPLE 2: Ontology Generation")
    print("=" * 70)

    # Create ontology generator
    ontology = OntologyGenerator(results)

    # Build the ontology graph
    graph = ontology.build_ontology()

    # Print statistics
    ontology.print_statistics()

    # Save the ontology in different formats
    ontology.save_ontology("./data/treesitter/ontology.graphml", format="graphml")
    ontology.save_ontology("./data/treesitter/ontology.json", format="json")

    return ontology, graph


def example_3_visualizations(ontology):
    """Example 3: Create various visualizations."""
    print("\n" + "=" * 70)
    print("EXAMPLE 3: Visualizations")
    print("=" * 70)

    # Visualize the complete ontology
    print("\nGenerating complete ontology visualization...")
    ontology.visualize(
        "./data/treesitter/visualizations/complete_ontology.png",
        layout="spring",
        figsize=(24, 18)
    )

    # Visualize only classes and interfaces
    print("Generating class hierarchy visualization...")
    ontology.visualize(
        "./data/treesitter/visualizations/class_hierarchy.png",
        layout="hierarchical",
        node_types=["class", "interface"],
        figsize=(20, 15)
    )

    # Visualize functions and methods
    print("Generating function graph...")
    ontology.visualize(
        "./data/treesitter/visualizations/functions.png",
        layout="spring",
        node_types=["function", "method"],
        figsize=(20, 15)
    )


def example_4_inheritance_analysis(ontology):
    """Example 4: Analyze inheritance relationships."""
    print("\n" + "=" * 70)
    print("EXAMPLE 4: Inheritance Analysis")
    print("=" * 70)

    # Get all classes
    classes = [
        node for node, attrs in ontology.graph.nodes(data=True)
        if attrs.get("type") == "class"
    ]

    if classes:
        # Analyze the first class with inheritance
        for class_id in classes[:3]:  # Check first 3 classes
            print(f"\nAnalyzing class: {class_id}")

            # Get inheritance tree
            tree = ontology.get_inheritance_tree(class_id)

            if tree.get("children"):
                print("  Inheritance tree:")
                _print_tree(tree, indent=2)
            else:
                print("  No inheritance relationships found")
    else:
        print("\nNo classes found in the parsed code.")


def _print_tree(tree, indent=0):
    """Helper function to print inheritance tree."""
    if "id" in tree:
        print(" " * indent + f"- {tree['id']}")
    for child in tree.get("children", []):
        _print_tree(child, indent + 2)


def example_5_dependency_analysis(ontology):
    """Example 5: Analyze dependencies."""
    print("\n" + "=" * 70)
    print("EXAMPLE 5: Dependency Analysis")
    print("=" * 70)

    # Get all entities
    all_entities = list(ontology.graph.nodes())

    if all_entities:
        # Analyze dependencies for the first few entities
        for entity_id in all_entities[:5]:
            entity = ontology.graph.nodes[entity_id]

            # Get dependency graph
            dep_graph = ontology.get_dependency_graph(entity_id, depth=2)

            if dep_graph.number_of_edges() > 0:
                print(f"\n{entity.get('name', entity_id)} ({entity.get('type')}):")
                print(f"  Dependencies: {dep_graph.number_of_edges()} connections")

                # Show direct dependencies
                successors = list(ontology.graph.successors(entity_id))
                if successors:
                    print("  Direct dependencies:")
                    for dep in successors[:5]:  # Show first 5
                        dep_node = ontology.graph.nodes[dep]
                        print(f"    - {dep_node.get('name', dep)} ({dep_node.get('type')})")


def example_6_neo4j_export(ontology):
    """Example 6: Export to Neo4j Cypher format."""
    print("\n" + "=" * 70)
    print("EXAMPLE 6: Neo4j Export")
    print("=" * 70)

    # Export to Neo4j Cypher statements
    ontology.export_to_neo4j_cypher("./data/treesitter/neo4j_import.cypher")

    print("\nYou can now import this into Neo4j using:")
    print("  cat data/treesitter/neo4j_import.cypher | cypher-shell")


def example_7_query_entities(parser):
    """Example 7: Query specific entities."""
    print("\n" + "=" * 70)
    print("EXAMPLE 7: Query Entities")
    print("=" * 70)

    # Find all Python classes
    python_classes = [
        cls for cls in parser.entities.get("classes", [])
        if cls.get("language") == "python"
    ]

    print(f"\nFound {len(python_classes)} Python classes:")
    for cls in python_classes[:5]:  # Show first 5
        print(f"  - {cls['name']} in {cls['file_path']}:{cls['line_start']}")

    # Find all TypeScript interfaces
    ts_interfaces = [
        iface for iface in parser.entities.get("interfaces", [])
        if "typescript" in iface.get("language", "")
    ]

    print(f"\nFound {len(ts_interfaces)} TypeScript interfaces:")
    for iface in ts_interfaces[:5]:  # Show first 5
        print(f"  - {iface['name']} in {iface['file_path']}:{iface['line_start']}")

    # Find all functions with specific patterns
    async_functions = [
        func for func in parser.entities.get("functions", [])
        if "async" in func.get("name", "").lower()
    ]

    print(f"\nFound {len(async_functions)} async functions:")
    for func in async_functions[:5]:  # Show first 5
        print(f"  - {func['name']} in {func['file_path']}:{func['line_start']}")


def example_8_language_statistics(parser):
    """Example 8: Language-specific statistics."""
    print("\n" + "=" * 70)
    print("EXAMPLE 8: Language Statistics")
    print("=" * 70)

    # Count entities by language
    language_stats = {}

    for entity_type, entity_list in parser.entities.items():
        for entity in entity_list:
            lang = entity.get("language", "unknown")
            if lang not in language_stats:
                language_stats[lang] = {}

            if entity_type not in language_stats[lang]:
                language_stats[lang][entity_type] = 0

            language_stats[lang][entity_type] += 1

    # Print statistics
    for language, stats in sorted(language_stats.items()):
        print(f"\n{language.upper()}:")
        total = sum(stats.values())
        print(f"  Total entities: {total}")
        for entity_type, count in sorted(stats.items(), key=lambda x: -x[1]):
            print(f"    {entity_type}: {count}")


def main():
    """Run all examples."""
    print("\n" + "=" * 70)
    print("TREE SITTER GLOBAL PARSER - EXAMPLES")
    print("=" * 70)
    print("\nThis script demonstrates the capabilities of the Tree Sitter parser")
    print("and ontology generator for code analysis.\n")

    try:
        # Example 1: Basic parsing
        parser, results = example_1_basic_parsing()

        # Example 2: Ontology generation
        ontology, graph = example_2_ontology_generation(parser, results)

        # Example 3: Visualizations
        example_3_visualizations(ontology)

        # Example 4: Inheritance analysis
        example_4_inheritance_analysis(ontology)

        # Example 5: Dependency analysis
        example_5_dependency_analysis(ontology)

        # Example 6: Neo4j export
        example_6_neo4j_export(ontology)

        # Example 7: Query entities
        example_7_query_entities(parser)

        # Example 8: Language statistics
        example_8_language_statistics(parser)

        print("\n" + "=" * 70)
        print("ALL EXAMPLES COMPLETED SUCCESSFULLY!")
        print("=" * 70)
        print("\nGenerated files:")
        print("  - ./data/treesitter/parsed_results.json")
        print("  - ./data/treesitter/ontology.graphml")
        print("  - ./data/treesitter/ontology.json")
        print("  - ./data/treesitter/neo4j_import.cypher")
        print("  - ./data/treesitter/visualizations/*.png")
        print()

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
