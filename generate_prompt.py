#!/usr/bin/env python3
"""
Generate Context-Aware AI Prompts
Simple CLI tool to generate rich prompts for code analysis, enhancement, or refactoring.

Usage:
    python3 generate_prompt.py

Then follow the interactive prompts.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "code-intelligence"))

from context_builder.context_assembler import ContextAssembler
from parsers.treesitter.context_aware_prompt_generator import ContextAwarePromptGenerator


def main():
    print("="*80)
    print("🤖 CONTEXT-AWARE PROMPT GENERATOR")
    print("="*80)
    print("\nThis tool generates AI-ready prompts with full codebase context.")
    print("Perfect for use with Claude, GPT-4, Cursor, or Copilot.\n")

    # Configuration
    index_path = "code-intelligence/data/index.json"
    repo_path = "/Users/venureddy/Downloads/PeritaWorkspace"

    # Check if index exists
    if not Path(index_path).exists():
        print(f"❌ Error: Index not found at {index_path}")
        print("Please run indexing first.")
        return

    # Interactive input
    print("What do you want to do?")
    print("1. Analyze a component")
    print("2. Enhance a component (add features)")
    print("3. Refactor a component")
    print("4. Fix a bug")
    print("5. Add a new feature")

    choice = input("\nChoice (1-5): ").strip()

    intent_map = {
        "1": "analyze",
        "2": "enhance",
        "3": "refactor",
        "4": "bugfix",
        "5": "feature"
    }

    intent = intent_map.get(choice, "analyze")

    print(f"\nYou selected: {intent.upper()}")

    # Get target component
    print("\nWhat component/file do you want to work with?")
    print("Examples: AssetListGrid.tsx, LocationDisplay, useAssets")
    target = input("Target file/component: ").strip()

    if not target:
        print("❌ Error: Target cannot be empty")
        return

    # Get description
    print(f"\nDescribe what you want to {intent}:")
    description = input("> ").strip()

    if not description:
        description = f"{intent.title()} {target}"

    # Get max components
    print("\nHow much context do you want?")
    print("1. Minimal (5 components)")
    print("2. Normal (10 components)")
    print("3. Comprehensive (20 components)")
    context_choice = input("Choice (1-3, default 2): ").strip() or "2"

    max_comps_map = {"1": 5, "2": 10, "3": 20}
    max_components = max_comps_map.get(context_choice, 10)

    print(f"\n{'='*80}")
    print("GENERATING PROMPT...")
    print(f"{'='*80}")
    print(f"Intent: {intent}")
    print(f"Target: {target}")
    print(f"Description: {description}")
    print(f"Max context: {max_components} components")

    # Initialize assembler
    assembler = ContextAssembler(index_path, repo_path)

    # Get context
    try:
        context = assembler.assemble_context(
            query=description,
            target_files=[target],
            intent=intent,
            max_components=max_components
        )
    except Exception as e:
        print(f"\n❌ Error assembling context: {e}")
        return

    # Generate prompt
    generator = ContextAwarePromptGenerator(context, repo_path)
    prompt = generator.generate(
        user_description=description,
        intent=intent
    )

    # Show summary
    print(f"\n{'='*80}")
    print("✅ PROMPT GENERATED")
    print(f"{'='*80}")

    print(f"\n📊 Context Included:")
    for layer, comps in context['layers'].items():
        if comps:
            print(f"  {layer}: {len(comps)} components")

    api_count = len(context.get('api_contracts', []))
    if api_count:
        print(f"  API contracts: {api_count}")

    print(f"\n📝 Prompt Stats:")
    print(f"  Characters: {len(prompt):,}")
    print(f"  Lines: {len(prompt.splitlines()):,}")
    print(f"  Code blocks: {prompt.count('```')//2}")

    # Save prompt
    safe_target = target.replace('/', '_').replace('.', '_')
    output_file = Path(f"generated_prompt_{safe_target}_{intent}.md")
    output_file.write_text(prompt)

    print(f"\n💾 Saved to: {output_file.absolute()}")

    # Offer to show preview
    show = input("\nShow preview? (y/n, default n): ").strip().lower()
    if show == 'y':
        print(f"\n{'─'*80}")
        print("PREVIEW (first 80 lines):")
        print(f"{'─'*80}\n")
        lines = prompt.splitlines()[:80]
        for line in lines:
            print(line)
        if len(prompt.splitlines()) > 80:
            print(f"\n... ({len(prompt.splitlines()) - 80} more lines)")
        print(f"\n{'─'*80}")

    print(f"\n✅ Done! Copy the prompt from {output_file.name} and paste into:")
    print("   - Claude Code")
    print("   - Cursor")
    print("   - GitHub Copilot Chat")
    print("   - ChatGPT")
    print("   - Any AI coding assistant")

    print(f"\n{'='*80}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Cancelled by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
