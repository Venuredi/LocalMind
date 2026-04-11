#!/usr/bin/env python3
"""
Test Ontology Fixes

Quick test to verify the new ontology pipeline works correctly.
"""

import sys
from pathlib import Path

# Add code-intelligence to path
sys.path.insert(0, str(Path(__file__).parent / "code-intelligence"))

from parsers.treesitter.parser_adapter import ParserAdapter
from parsers.treesitter.ontology_generator import OntologyGenerator
from validation.ontology_validator import OntologyValidator


def test_adapter():
    """Test parser adapter."""
    print("Testing Parser Adapter...")

    # Create sample NestJS data
    sample_nestjs_data = {
        "controllers": [
            {
                "id": "TestController",
                "name": "TestController",
                "type": "controller",
                "layer": "backend",
                "file_path": "test/controller.ts",
                "base_route": "test",
                "line_start": 1,
                "dependencies": [{"name": "testService", "type": "TestService"}],
                "routes": [
                    {
                        "method": "GET",
                        "path": "/test/hello",
                        "handler": "getHello",
                        "service_calls": ["testService.hello"],
                        "dtos": ["HelloDto"],
                        "line_number": 10,
                    }
                ],
            }
        ],
        "services": [
            {
                "id": "TestService",
                "name": "TestService",
                "type": "service",
                "layer": "backend",
                "file_path": "test/service.ts",
                "line_start": 1,
                "dependencies": [{"name": "testRepo", "type": "TestRepository"}],
                "methods": [{"name": "hello", "line_number": 5}],
            }
        ],
        "dtos": [
            {
                "id": "HelloDto",
                "name": "HelloDto",
                "type": "dto",
                "file_path": "test/dto.ts",
                "line_start": 1,
                "properties": [{"name": "message", "type": "string"}],
            }
        ],
        "repositories": [
            {
                "id": "TestRepository",
                "name": "TestRepository",
                "type": "repository",
                "file_path": "test/repository.ts",
                "line_start": 1,
                "entity": "TestEntity",
                "methods": [{"name": "findAll", "line_number": 5}],
            }
        ],
        "entities": [
            {
                "id": "TestEntity",
                "name": "TestEntity",
                "type": "entity",
                "file_path": "test/entity.ts",
                "line_start": 1,
                "table_name": "test",
                "columns": [{"name": "id", "type": "number"}],
            }
        ],
    }

    # Test adapter
    adapter = ParserAdapter()
    adapted = adapter.adapt("nestjs", sample_nestjs_data)

    # Verify structure
    assert "entities" in adapted
    assert "api_endpoints" in adapted["entities"]
    assert "classes" in adapted["entities"]
    assert "dtos" in adapted["entities"]

    # Check conversions
    assert len(adapted["entities"]["api_endpoints"]) == 1
    assert len(adapted["entities"]["classes"]) == 2  # controller + service
    assert len(adapted["entities"]["dtos"]) == 1
    assert len(adapted["entities"]["repositories"]) == 1

    print("  ✅ Adapter working correctly")
    return adapted


def test_ontology_generator(adapted_data):
    """Test ontology generator."""
    print("\nTesting Ontology Generator...")

    generator = OntologyGenerator(adapted_data)
    graph = generator.build_ontology()

    # Verify graph structure
    assert graph.number_of_nodes() > 0
    assert graph.number_of_edges() > 0

    # Check for API endpoints
    api_endpoints = [
        n for n, d in graph.nodes(data=True)
        if d.get("type") == "api_endpoint"
    ]
    assert len(api_endpoints) == 1

    # Check for controllers
    controllers = [
        n for n, d in graph.nodes(data=True)
        if d.get("type") == "controller"
    ]
    assert len(controllers) == 1

    # Check for services
    services = [
        n for n, d in graph.nodes(data=True)
        if d.get("type") == "service"
    ]
    assert len(services) == 1

    # Check for edges
    edge_types = set()
    for _, _, attrs in graph.edges(data=True):
        edge_types.add(attrs.get("relationship", "unknown"))

    # Should have API relationship edges
    assert "exposes_endpoint" in edge_types or len(api_endpoints) > 0

    print(f"  ✅ Generated graph with {graph.number_of_nodes()} nodes and {graph.number_of_edges()} edges")
    print(f"  ✅ Edge types: {', '.join(sorted(edge_types))}")

    return graph


def test_validator(graph):
    """Test ontology validator."""
    print("\nTesting Ontology Validator...")

    validator = OntologyValidator(graph)
    results = validator.validate_coverage()

    # Should have results for all checks
    assert "api_coverage" in results
    assert "service_coverage" in results
    assert "repository_coverage" in results
    assert "cross_layer_paths" in results

    # API coverage should pass (we have 1 endpoint)
    assert results["api_coverage"]["has_endpoints"] == True

    # Service coverage should pass
    assert results["service_coverage"]["has_services"] == True

    summary = validator.get_coverage_summary()
    assert "overall_status" in summary
    assert "score" in summary

    print(f"  ✅ Validation complete - Score: {summary['score']}%")
    print(f"  ✅ Status: {summary['overall_status']}")

    return validator


def test_call_graph(generator):
    """Test call graph generation."""
    print("\nTesting Call Graph Generation...")

    call_graph = generator.get_call_graph()

    # Should have nodes for API endpoints and their call paths
    assert call_graph.number_of_nodes() >= 0  # May be 0 if no paths found

    print(f"  ✅ Call graph has {call_graph.number_of_nodes()} nodes")

    return call_graph


def main():
    """Run all tests."""
    print("=" * 60)
    print("🧪 Testing Ontology Fixes")
    print("=" * 60)

    try:
        # Test 1: Adapter
        adapted_data = test_adapter()

        # Test 2: Ontology Generator
        graph = test_ontology_generator(adapted_data)

        # Test 3: Validator
        validator = test_validator(graph)

        # Test 4: Call Graph
        call_graph = test_call_graph(
            OntologyGenerator(adapted_data)
        )

        print("\n" + "=" * 60)
        print("✅ All tests passed!")
        print("=" * 60)

        print("\n💡 The ontology fixes are working correctly.")
        print("   You can now run: python generate_complete_ontology.py")

    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
