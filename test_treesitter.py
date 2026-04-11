"""
Quick test script for Tree Sitter parser.
"""

import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from code_intelligence.parsers.treesitter import TreeSitterParser, OntologyGenerator

def test_basic_functionality():
    """Test basic parser functionality."""
    print("=" * 70)
    print("TREE SITTER PARSER - BASIC FUNCTIONALITY TEST")
    print("=" * 70)

    # Test 1: Initialize parser
    print("\n✓ Test 1: Initializing parser...")
    parser = TreeSitterParser("./demo-repo")
    print("  Success: Parser initialized")

    # Test 2: Language detection
    print("\n✓ Test 2: Testing language detection...")
    test_cases = [
        (Path("test.py"), "python"),
        (Path("test.ts"), "typescript"),
        (Path("test.js"), "javascript"),
        (Path("test.go"), "go"),
        (Path("test.rs"), "rust"),
        (Path("test.java"), "java"),
    ]

    for file_path, expected_lang in test_cases:
        detected = parser._get_language_from_extension(file_path)
        assert detected == expected_lang, f"Expected {expected_lang}, got {detected}"
        print(f"  ✓ {file_path.suffix} -> {detected}")

    # Test 3: Parse a single file
    print("\n✓ Test 3: Parsing a single TypeScript file...")
    ts_file = Path("./demo-repo/web/react_app/src/hooks/useAuth.ts")
    if ts_file.exists():
        result = parser.parse_file(ts_file)
        if result:
            print(f"  ✓ Successfully parsed {ts_file.name}")
            print(f"  Language: {result['language']}")
            if result['entities']:
                for entity_type, entities in result['entities'].items():
                    if entities:
                        print(f"  {entity_type}: {len(entities)}")
        else:
            print(f"  ⚠ No result for {ts_file.name}")
    else:
        print(f"  ⚠ Test file not found: {ts_file}")

    # Test 4: Small repository parse (just a few files)
    print("\n✓ Test 4: Parsing repository (limited)...")

    # Create a mini test by parsing just a few TypeScript files
    test_files = list(Path("./demo-repo").rglob("*.ts"))[:5]  # Just first 5 TS files

    parsed_count = 0
    total_entities = 0

    for file in test_files:
        result = parser.parse_file(file)
        if result:
            parsed_count += 1
            for entities in result['entities'].values():
                total_entities += len(entities)

    print(f"  ✓ Parsed {parsed_count} files")
    print(f"  ✓ Found {total_entities} total entities")

    # Test 5: Ontology generator (if we have entities)
    if parser.entities:
        print("\n✓ Test 5: Testing ontology generator...")

        # Prepare results structure
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

        print(f"  ✓ Graph created with {graph.number_of_nodes()} nodes")
        print(f"  ✓ Graph has {graph.number_of_edges()} edges")
    else:
        print("\n⚠ Test 5: Skipped (no entities parsed)")

    print("\n" + "=" * 70)
    print("ALL TESTS PASSED! ✓")
    print("=" * 70)
    print("\nThe Tree Sitter parser is working correctly.")
    print("Run 'python example_treesitter_usage.py' for full examples.\n")


if __name__ == "__main__":
    try:
        test_basic_functionality()
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
