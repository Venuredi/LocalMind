"""
Example: Using Requirements to Generate AI-Ready Prompts

This demonstrates how to use the Tree Sitter ontology to generate
context-rich prompts for code generation tools like Claude, GPT-4, Copilot, etc.
"""

import sys
from pathlib import Path

# Add to path
sys.path.insert(0, str(Path.cwd() / "code-intelligence"))

from parsers.treesitter import TreeSitterParser
from parsers.treesitter.prompt_generator import PromptGenerator


def example_1_basic_feature_prompt():
    """Example 1: Generate prompt for a new feature."""
    print("\n" + "=" * 70)
    print("EXAMPLE 1: Generate Prompt for New Feature")
    print("=" * 70)

    # Step 1: Parse the codebase
    print("\n1. Parsing codebase...")
    parser = TreeSitterParser("./demo-repo")
    results = parser.parse_repository()

    # Step 2: Create prompt generator
    print("\n2. Initializing prompt generator...")
    prompt_gen = PromptGenerator(results, "./demo-repo")

    # Step 3: Define requirement
    requirement = "Add user profile editing feature with avatar upload"

    # Step 4: Generate prompt
    print(f"\n3. Generating prompt for: {requirement}")
    prompt = prompt_gen.generate_prompt(
        requirement=requirement,
        context_type="feature",
        constraints=[
            "Must work with existing authentication system",
            "Support image files up to 5MB",
            "Use TypeScript with React hooks"
        ]
    )

    # Step 5: Save prompt
    output_path = "./data/treesitter/prompts/feature_user_profile.md"
    prompt_gen.save_prompt(prompt, output_path)

    print(f"\n✅ Prompt generated and saved to: {output_path}")
    print(f"📊 Prompt length: {len(prompt)} characters")

    # Display preview
    print("\n" + "=" * 70)
    print("PREVIEW (first 500 characters):")
    print("=" * 70)
    print(prompt[:500] + "...")

    return prompt


def example_2_bugfix_prompt():
    """Example 2: Generate prompt for a bug fix."""
    print("\n" + "=" * 70)
    print("EXAMPLE 2: Generate Prompt for Bug Fix")
    print("=" * 70)

    parser = TreeSitterParser("./demo-repo")
    results = parser.parse_repository()

    prompt_gen = PromptGenerator(results, "./demo-repo")

    requirement = "Fix authentication token not refreshing on API calls"

    prompt = prompt_gen.generate_prompt(
        requirement=requirement,
        context_type="bugfix",
        related_files=[
            "src/hooks/useAuth.ts",
            "src/services/apiClient.ts"
        ]
    )

    output_path = "./data/treesitter/prompts/bugfix_token_refresh.md"
    prompt_gen.save_prompt(prompt, output_path)

    print(f"✅ Bugfix prompt saved to: {output_path}")

    return prompt


def example_3_refactor_prompt():
    """Example 3: Generate prompt for refactoring."""
    print("\n" + "=" * 70)
    print("EXAMPLE 3: Generate Prompt for Refactoring")
    print("=" * 70)

    parser = TreeSitterParser("./demo-repo")
    results = parser.parse_repository()

    prompt_gen = PromptGenerator(results, "./demo-repo")

    requirement = "Refactor authentication logic to use a custom hook pattern"

    prompt = prompt_gen.generate_prompt(
        requirement=requirement,
        context_type="refactor",
        constraints=[
            "Maintain backward compatibility",
            "Follow React hooks best practices",
            "Improve testability"
        ]
    )

    output_path = "./data/treesitter/prompts/refactor_auth_hook.md"
    prompt_gen.save_prompt(prompt, output_path)

    print(f"✅ Refactor prompt saved to: {output_path}")

    return prompt


def example_4_test_prompt():
    """Example 4: Generate prompt for writing tests."""
    print("\n" + "=" * 70)
    print("EXAMPLE 4: Generate Prompt for Test Writing")
    print("=" * 70)

    parser = TreeSitterParser("./demo-repo")
    results = parser.parse_repository()

    prompt_gen = PromptGenerator(results, "./demo-repo")

    requirement = "Write comprehensive unit tests for authentication service"

    prompt = prompt_gen.generate_prompt(
        requirement=requirement,
        context_type="test",
        related_files=[
            "src/services/apiClient.ts",
            "src/hooks/useAuth.ts"
        ],
        constraints=[
            "Use Jest and React Testing Library",
            "Cover happy path and error scenarios",
            "Mock API calls appropriately"
        ]
    )

    output_path = "./data/treesitter/prompts/test_auth_service.md"
    prompt_gen.save_prompt(prompt, output_path)

    print(f"✅ Test prompt saved to: {output_path}")

    return prompt


def example_5_batch_generation():
    """Example 5: Generate multiple prompts from a requirements list."""
    print("\n" + "=" * 70)
    print("EXAMPLE 5: Batch Prompt Generation")
    print("=" * 70)

    parser = TreeSitterParser("./demo-repo")
    results = parser.parse_repository()

    prompt_gen = PromptGenerator(results, "./demo-repo")

    # Define multiple requirements
    requirements = [
        {
            "requirement": "Add dark mode toggle to user settings",
            "context_type": "feature",
            "constraints": ["Use CSS variables", "Save preference to localStorage"]
        },
        {
            "requirement": "Implement password reset functionality",
            "context_type": "feature",
            "constraints": ["Send email with reset link", "Token expires in 1 hour"]
        },
        {
            "requirement": "Add loading states to all API calls",
            "context_type": "feature",
            "constraints": ["Use consistent loading indicator", "Handle timeouts"]
        },
        {
            "requirement": "Fix form validation not showing error messages",
            "context_type": "bugfix",
            "constraints": ["Must work with existing form components"]
        },
    ]

    # Generate all prompts
    generated_files = prompt_gen.generate_batch_prompts(
        requirements=requirements,
        output_dir="./data/treesitter/prompts/batch"
    )

    print(f"\n✅ Generated {len(generated_files)} prompts:")
    for filepath in generated_files:
        print(f"  - {filepath}")

    return generated_files


def example_6_use_prompt_with_ai():
    """Example 6: How to use the generated prompt with AI tools."""
    print("\n" + "=" * 70)
    print("EXAMPLE 6: Using Generated Prompts with AI Tools")
    print("=" * 70)

    print("""
How to use the generated prompts:

1. **Claude / ChatGPT (Web Interface)**
   - Copy the entire prompt from the generated .md file
   - Paste it into the chat interface
   - The AI will have full context of your codebase

2. **Cursor / Copilot (IDE)**
   - Open the generated prompt file in your IDE
   - Copy the relevant sections
   - Paste into the AI chat or use as context

3. **API Integration**
   - Read the prompt file programmatically
   - Send to OpenAI/Anthropic API with your code
   - Get AI-generated implementation

4. **Command Line**
   ```bash
   # Example with Claude API (pseudocode)
   cat ./data/treesitter/prompts/feature_user_profile.md | claude-cli
   ```

The generated prompts include:
✓ Project context and structure
✓ Relevant existing code
✓ Code patterns and conventions
✓ Similar implementations as examples
✓ Dependencies and imports
✓ Technical constraints
✓ Specific task requirements
✓ Expected output format

This gives the AI everything it needs to generate code that:
- Follows your existing patterns
- Integrates seamlessly with your codebase
- Respects your constraints and conventions
- Is production-ready
    """)


def example_7_custom_prompt_workflow():
    """Example 7: Custom workflow with manual analysis."""
    print("\n" + "=" * 70)
    print("EXAMPLE 7: Custom Workflow with Analysis")
    print("=" * 70)

    parser = TreeSitterParser("./demo-repo")
    results = parser.parse_repository()

    # Show what the system found
    print("\nCodebase Analysis:")
    print(f"  Languages: {', '.join(results['summary']['languages'])}")
    print(f"  Total files: {results['summary']['total_files']}")
    print("\n  Entities:")
    for entity_type, count in results['summary']['entity_counts'].items():
        if count > 0:
            print(f"    {entity_type}: {count}")

    # Create custom requirement based on analysis
    if "typescript" in results['summary']['languages']:
        requirement = "Add TypeScript interface for API responses with strict typing"
    elif "python" in results['summary']['languages']:
        requirement = "Add Python dataclasses for API data models"
    else:
        requirement = "Add data validation layer for API responses"

    print(f"\n  Generated requirement: {requirement}")

    prompt_gen = PromptGenerator(results, "./demo-repo")

    prompt = prompt_gen.generate_prompt(
        requirement=requirement,
        context_type="feature",
        include_patterns=True,
        include_examples=True
    )

    output_path = "./data/treesitter/prompts/custom_requirement.md"
    prompt_gen.save_prompt(prompt, output_path)

    print(f"\n✅ Custom prompt saved to: {output_path}")


def main():
    """Run all examples."""
    print("\n" + "=" * 70)
    print("PROMPT GENERATION FROM REQUIREMENTS - EXAMPLES")
    print("=" * 70)
    print("\nDemonstrating how to generate AI-ready prompts from requirements")
    print("using the Tree Sitter code ontology.\n")

    try:
        # Example 1: Basic feature
        example_1_basic_feature_prompt()

        # Example 2: Bug fix
        example_2_bugfix_prompt()

        # Example 3: Refactoring
        example_3_refactor_prompt()

        # Example 4: Test writing
        example_4_test_prompt()

        # Example 5: Batch generation
        example_5_batch_generation()

        # Example 6: Usage instructions
        example_6_use_prompt_with_ai()

        # Example 7: Custom workflow
        example_7_custom_prompt_workflow()

        print("\n" + "=" * 70)
        print("ALL EXAMPLES COMPLETED SUCCESSFULLY!")
        print("=" * 70)
        print("\nGenerated prompts are in: ./data/treesitter/prompts/")
        print("\nYou can now:")
        print("  1. Review the generated prompts")
        print("  2. Copy them to your AI tool (Claude, GPT-4, Copilot)")
        print("  3. Get context-aware code generation")
        print()

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
