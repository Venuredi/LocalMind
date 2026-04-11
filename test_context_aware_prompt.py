#!/usr/bin/env python3
"""
Test Context-Aware Prompt Generation
Demonstrates generating rich, contextual prompts based on user descriptions.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "code-intelligence"))

from context_builder.context_assembler import ContextAssembler
from parsers.treesitter.context_aware_prompt_generator import ContextAwarePromptGenerator


def test_context_aware_prompt():
    """Test generating a context-rich prompt for AssetListGrid."""

    print("="*80)
    print("CONTEXT-AWARE PROMPT GENERATION TEST")
    print("="*80)

    # Setup
    index_path = "code-intelligence/data/index.json"
    repo_path = "/Users/venureddy/Downloads/PeritaWorkspace"

    print(f"\nIndex: {index_path}")
    print(f"Repo:  {repo_path}")

    # Initialize assembler
    assembler = ContextAssembler(index_path, repo_path)

    # Test scenarios
    test_cases = [
        {
            "description": "Add virtualization to AssetListGrid to handle 10,000+ rows efficiently",
            "target": "AssetListGrid.tsx",
            "intent": "enhance",
            "max_components": 20
        },
        {
            "description": "Analyze the LocationDisplay component for performance issues",
            "target": "LocationDisplay.tsx",
            "intent": "analyze",
            "max_components": 10
        },
        {
            "description": "Refactor useAssetListGridState hook to use React Query",
            "target": "useAssetListGridState",
            "intent": "refactor",
            "max_components": 15
        }
    ]

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'='*80}")
        print(f"TEST CASE {i}: {test_case['intent'].upper()}")
        print(f"{'='*80}")
        print(f"Description: {test_case['description']}")
        print(f"Target: {test_case['target']}")

        # Get context
        context = assembler.assemble_context(
            query=test_case['description'],
            target_files=[test_case['target']],
            intent=test_case['intent'],
            max_components=test_case['max_components']
        )

        # Generate prompt
        generator = ContextAwarePromptGenerator(context, repo_path)
        prompt = generator.generate(
            user_description=test_case['description'],
            intent=test_case['intent']
        )

        # Show summary
        print(f"\n📊 Context Summary:")
        for layer, comps in context['layers'].items():
            if comps:
                print(f"  {layer}: {len(comps)} components")

        api_count = len(context.get('api_contracts', []))
        if api_count:
            print(f"  API contracts: {api_count}")

        print(f"\n📝 Prompt Stats:")
        print(f"  Length: {len(prompt):,} characters")
        print(f"  Lines: {len(prompt.splitlines()):,}")
        print(f"  Code blocks: {prompt.count('```')//2}")

        # Save prompt
        output_file = Path(f"test_prompt_case_{i}_{test_case['intent']}.md")
        output_file.write_text(prompt)
        print(f"\n✅ Saved to: {output_file.absolute()}")

        # Show first 50 lines of prompt
        if i == 1:  # Only show full detail for first test
            print(f"\n{'─'*80}")
            print("GENERATED PROMPT (first 1000 chars):")
            print(f"{'─'*80}")
            print(prompt[:1000])
            print("\n... (truncated)")
            print(f"{'─'*80}")

    print(f"\n{'='*80}")
    print("✅ ALL TESTS COMPLETED")
    print(f"{'='*80}")
    print("\nGenerated prompts saved to:")
    for i in range(1, len(test_cases) + 1):
        print(f"  - test_prompt_case_{i}_*.md")


if __name__ == "__main__":
    test_context_aware_prompt()
