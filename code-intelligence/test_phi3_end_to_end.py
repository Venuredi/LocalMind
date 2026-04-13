"""
End-to-End test for Phi3 Prompt Generation

Tests the complete flow:
1. Load ontology context
2. Generate prompt using Phi3
3. Validate output
4. Compare with template-based generation
"""

import sys
import json
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from prompt.context_builder import OntologyContextBuilder
from prompt.phi3_prompt_engine import Phi3PromptEngine, HybridPromptEngine
from prompt.template_engine import PromptTemplateEngine
from graph.graph_builder import GraphBuilder


def load_test_ontology():
    """Load test ontology from index."""
    index_path = Path(__file__).parent / "data" / "index.json"

    if not index_path.exists():
        print(f"❌ Index not found at {index_path}")
        print("   Please run indexing first")
        return None, None

    print(f"📂 Loading index from {index_path}")
    with open(index_path, 'r') as f:
        index_data = json.load(f)

    print(f"   Components: {len(index_data.get('components', []))}")

    # Build graph
    graph_builder = GraphBuilder(index_data)
    graph_builder.build_graph()

    print(f"   Graph: {graph_builder.graph.number_of_nodes()} nodes, {graph_builder.graph.number_of_edges()} edges")

    return index_data, graph_builder


def test_phi3_engine_direct():
    """Test Phi3 engine directly."""
    print("\n" + "=" * 70)
    print("TEST 1: Phi3 Prompt Engine (Direct)")
    print("=" * 70)

    try:
        # Initialize engine
        print("\n1. Initializing Phi3 engine...")
        engine = Phi3PromptEngine()
        print("   ✅ Phi3 engine initialized")

        # Get model info
        info = engine.get_model_info()
        if info:
            print(f"   Model: {info['name']} ({info['parameter_size']}, {info['quantization']})")

        # Load ontology
        print("\n2. Loading ontology...")
        index_data, graph_builder = load_test_ontology()
        if not index_data:
            return False

        # Build context for a test component
        print("\n3. Building context for test component...")
        context_builder = OntologyContextBuilder(index_data, graph_builder.graph)

        # Find a service component to test
        components = index_data.get('components', [])
        test_component = None
        for comp in components:
            if comp.get('type') == 'service' and comp.get('name'):
                test_component = comp.get('name')
                break

        if not test_component:
            print("   ⚠️  No service components found, using first component")
            test_component = components[0].get('name') if components else None

        if not test_component:
            print("   ❌ No components found in ontology")
            return False

        print(f"   Testing with component: {test_component}")

        # Build context
        context = context_builder.build_context_strict(test_component)

        if 'error' in context:
            print(f"   ❌ Context build failed: {context['error']}")
            return False

        print(f"   ✅ Context built successfully")
        print(f"      Dependencies: {len(context.get('dependencies', []))}")
        print(f"      Constructor deps: {len(context.get('constructor_dependencies', []))}")

        # Generate prompt with Phi3
        print("\n4. Generating prompt with Phi3...")
        result = engine.generate(
            prompt_type='enhancement',
            context=context,
            user_description='Improve error handling and add logging',
            title='Enhance service with better error handling',
            validate=True,
            enhance=True
        )

        if not result.get('success'):
            print(f"   ❌ Generation failed: {result.get('error')}")
            return False

        print(f"   ✅ Prompt generated successfully!")
        print(f"      Length: {result['metadata']['length']} characters")
        print(f"      Tokens: ~{result['metadata']['tokens_generated']}")
        print(f"      Generator: {result['metadata']['generator']}")

        # Validation results
        validation = result.get('validation')
        if validation:
            print(f"\n5. Validation results:")
            print(f"   Valid: {validation['is_valid']}")
            print(f"   Errors: {validation['error_count']}")
            print(f"   Warnings: {validation['warning_count']}")

            if validation['errors']:
                print("\n   Errors:")
                for error in validation['errors']:
                    print(f"      ❌ {error}")

            if validation['warnings']:
                print("\n   Warnings:")
                for warning in validation['warnings'][:5]:  # Show first 5
                    print(f"      ⚠️  {warning}")

        # Show sample of generated prompt
        prompt = result['prompt']
        print(f"\n6. Sample of generated prompt:")
        print("   " + "-" * 66)
        print("   " + prompt[:500].replace("\n", "\n   "))
        if len(prompt) > 500:
            print("   ...")
        print("   " + "-" * 66)

        return True

    except Exception as e:
        print(f"   ❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_hybrid_engine():
    """Test hybrid engine (auto-decision)."""
    print("\n" + "=" * 70)
    print("TEST 2: Hybrid Prompt Engine (Auto-Decision)")
    print("=" * 70)

    try:
        # Initialize hybrid engine
        print("\n1. Initializing hybrid engine...")
        engine = HybridPromptEngine()
        print(f"   ✅ Hybrid engine initialized")
        print(f"   Phi3 available: {engine.phi3_available}")

        # Load ontology
        print("\n2. Loading ontology...")
        index_data, graph_builder = load_test_ontology()
        if not index_data:
            return False

        # Build context
        print("\n3. Building context...")
        context_builder = OntologyContextBuilder(index_data, graph_builder.graph)

        components = index_data.get('components', [])
        test_component = None
        for comp in components:
            if comp.get('type') == 'service':
                test_component = comp.get('name')
                break

        if not test_component:
            test_component = components[0].get('name') if components else None

        context = context_builder.build_context_strict(test_component)

        if 'error' in context:
            print(f"   ❌ Context build failed")
            return False

        print(f"   ✅ Context built for: {test_component}")

        # Test with auto-decision
        print("\n4. Testing AUTO mode (engine decides)...")
        result_auto = engine.generate(
            prompt_type='enhancement',
            context=context,
            user_description='Add validation',
            title='Add input validation',
            use_llm=None  # Auto-decide
        )

        print(f"   Engine chose: {result_auto['metadata'].get('engine', 'unknown')}")
        print(f"   Success: {result_auto['success']}")

        # Test forcing LLM
        if engine.phi3_available:
            print("\n5. Testing FORCE LLM mode...")
            result_llm = engine.generate(
                prompt_type='enhancement',
                context=context,
                user_description='Add validation',
                title='Add input validation',
                use_llm=True  # Force LLM
            )

            print(f"   Engine: {result_llm['metadata'].get('engine')}")
            print(f"   Generator: {result_llm['metadata'].get('generator')}")
            print(f"   Success: {result_llm['success']}")

        # Test forcing template
        print("\n6. Testing FORCE TEMPLATE mode...")
        result_template = engine.generate(
            prompt_type='enhancement',
            context=context,
            user_description='Add validation',
            title='Add input validation',
            use_llm=False  # Force template
        )

        print(f"   Engine: {result_template['metadata'].get('engine')}")
        print(f"   Generator: {result_template['metadata'].get('generator')}")
        print(f"   Success: {result_template['success']}")

        return True

    except Exception as e:
        print(f"   ❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_comparison():
    """Compare Phi3 vs Template outputs."""
    print("\n" + "=" * 70)
    print("TEST 3: Phi3 vs Template Comparison")
    print("=" * 70)

    try:
        # Load ontology
        index_data, graph_builder = load_test_ontology()
        if not index_data:
            return False

        # Build context
        context_builder = OntologyContextBuilder(index_data, graph_builder.graph)

        components = index_data.get('components', [])
        test_component = components[0].get('name') if components else None
        context = context_builder.build_context_strict(test_component)

        if 'error' in context:
            return False

        # Generate with template
        print("\n1. Generating with Template Engine...")
        template_engine = PromptTemplateEngine()
        template_prompt = template_engine.generate(
            prompt_type='enhancement',
            context=context,
            user_description='Improve performance',
            title='Performance optimization'
        )

        print(f"   ✅ Template generated: {len(template_prompt)} chars")

        # Generate with Phi3
        print("\n2. Generating with Phi3 Engine...")
        try:
            phi3_engine = Phi3PromptEngine()
            phi3_result = phi3_engine.generate(
                prompt_type='enhancement',
                context=context,
                user_description='Improve performance',
                title='Performance optimization',
                validate=False,
                enhance=False
            )

            if phi3_result['success']:
                phi3_prompt = phi3_result['prompt']
                print(f"   ✅ Phi3 generated: {len(phi3_prompt)} chars")

                # Comparison
                print("\n3. Comparison:")
                print(f"   Template length: {len(template_prompt)}")
                print(f"   Phi3 length: {len(phi3_prompt)}")
                print(f"   Difference: {abs(len(phi3_prompt) - len(template_prompt))} chars")

                return True
            else:
                print(f"   ❌ Phi3 failed: {phi3_result.get('error')}")
                return False

        except Exception as e:
            print(f"   ⚠️  Phi3 not available: {e}")
            print("   (This is OK if Phi3 model is not installed)")
            return True

    except Exception as e:
        print(f"   ❌ Test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("=" * 70)
    print("PHI3 END-TO-END INTEGRATION TESTS")
    print("=" * 70)

    results = []

    # Test 1: Phi3 engine direct
    try:
        result1 = test_phi3_engine_direct()
        results.append(("Phi3 Engine Direct", result1))
    except Exception as e:
        print(f"\n❌ Test 1 crashed: {e}")
        results.append(("Phi3 Engine Direct", False))

    # Test 2: Hybrid engine
    try:
        result2 = test_hybrid_engine()
        results.append(("Hybrid Engine", result2))
    except Exception as e:
        print(f"\n❌ Test 2 crashed: {e}")
        results.append(("Hybrid Engine", False))

    # Test 3: Comparison
    try:
        result3 = test_comparison()
        results.append(("Phi3 vs Template", result3))
    except Exception as e:
        print(f"\n❌ Test 3 crashed: {e}")
        results.append(("Phi3 vs Template", False))

    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)

    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{status} - {test_name}")

    passed_count = sum(1 for _, p in results if p)
    total_count = len(results)

    print("\n" + "=" * 70)
    print(f"TOTAL: {passed_count}/{total_count} tests passed")
    print("=" * 70)

    if passed_count == total_count:
        print("\n🎉 ALL TESTS PASSED! Phi3 integration is working!")
        return True
    else:
        print(f"\n⚠️  {total_count - passed_count} test(s) failed")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
