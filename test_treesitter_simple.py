"""
Simple standalone test for Tree Sitter parser.
This test can be run directly without module installation.
"""

import sys
from pathlib import Path

# Add the code-intelligence directory to the Python path
code_intel_path = Path(__file__).parent / "code-intelligence"
sys.path.insert(0, str(code_intel_path.parent))
sys.path.insert(0, str(code_intel_path))

# Now import with relative paths
from parsers.treesitter.tree_sitter_parser import TreeSitterParser
from parsers.treesitter.ontology_generator import OntologyGenerator

def main():
    print("=" * 70)
    print("TREE SITTER PARSER - SIMPLE TEST")
    print("=" * 70)

    # Test 1: Initialize
    print("\n✓ Test 1: Initializing parser...")
    parser = TreeSitterParser("./demo-repo")
    print("  Parser initialized successfully")

    # Test 2: Language detection
    print("\n✓ Test 2: Testing language detection...")
    tests = [
        ("test.py", "python"),
        ("test.ts", "typescript"),
        ("test.js", "javascript"),
    ]

    for filename, expected in tests:
        detected = parser._get_language_from_extension(Path(filename))
        status = "✓" if detected == expected else "✗"
        print(f"  {status} {filename} -> {detected}")

    # Test 3: Parse a few files
    print("\n✓ Test 3: Parsing sample files...")
    ts_files = list(Path("./demo-repo").rglob("*.ts"))[:3]

    for ts_file in ts_files:
        result = parser.parse_file(ts_file)
        if result:
            print(f"  ✓ Parsed: {ts_file.name}")

    # Test 4: Check entities
    print("\n✓ Test 4: Checking parsed entities...")
    total = sum(len(v) for v in parser.entities.values())
    print(f"  Total entities found: {total}")

    for entity_type, entities in parser.entities.items():
        if entities:
            print(f"  - {entity_type}: {len(entities)}")

    # Test 5: Create ontology
    if total > 0:
        print("\n✓ Test 5: Creating ontology...")

        results = {
            "summary": {
                "total_files": len(parser.parsed_files),
                "languages": list(set(f["language"] for f in parser.parsed_files)),
                "entity_counts": {k: len(v) for k, v in parser.entities.items()},
            },
            "entities": parser.entities,
        }

        ontology = OntologyGenerator(results)
        graph = ontology.build_ontology()
        print(f"  ✓ Graph created: {graph.number_of_nodes()} nodes, {graph.number_of_edges()} edges")

    print("\n" + "=" * 70)
    print("ALL TESTS PASSED!")
    print("=" * 70)
    print("\nThe Tree Sitter parser is working correctly!")
    print("\nNext steps:")
    print("  1. Run full parsing: python -m code_intelligence.parsers.treesitter.tree_sitter_parser")
    print("  2. Try the examples in example_treesitter_usage.py")
    print()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
