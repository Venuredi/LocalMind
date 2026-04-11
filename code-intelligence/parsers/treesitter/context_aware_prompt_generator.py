"""
Context-Aware Prompt Generator
Generates AI-ready prompts with rich contextual information based on user intent.
"""

from pathlib import Path
from typing import Dict, List, Any, Optional
import json
from datetime import datetime


class ContextAwarePromptGenerator:
    """
    Generates prompts with comprehensive context including:
    - Target file source code
    - Related components (dependencies, children, parents)
    - API clients and endpoints used
    - Types/DTOs referenced
    - Database models accessed
    - Usage examples from codebase
    """

    def __init__(self, context_data: Dict[str, Any], repo_path: str):
        """
        Initialize with context from ContextAssembler.

        Args:
            context_data: Output from ContextAssembler.assemble_context()
            repo_path: Path to repository root
        """
        self.context = context_data
        self.repo_path = Path(repo_path)

    def generate(self,
                 user_description: str,
                 intent: str = "enhance") -> str:
        """
        Generate a comprehensive prompt based on user description.

        Args:
            user_description: What the user wants to do (e.g., "Add pagination to AssetListGrid")
            intent: Intent type (analyze, enhance, refactor, bugfix, feature)

        Returns:
            Formatted prompt ready for AI tools
        """
        target_files = self.context.get('target_files', [])
        target_name = target_files[0] if target_files else "target component"

        # Build prompt sections
        sections = []

        # Header
        sections.append(self._build_header(user_description, intent, target_name))

        # Target source code
        sections.append(self._build_target_source_section())

        # Related context
        sections.append(self._build_related_components_section())

        # API & Data context
        if intent in ["enhance", "feature", "bugfix"]:
            sections.append(self._build_api_context_section())
            sections.append(self._build_data_context_section())

        # Dependencies & Usage
        sections.append(self._build_dependencies_section())

        # Task instructions
        sections.append(self._build_task_instructions(intent, user_description))

        # Footer
        sections.append(self._build_footer())

        return "\n\n".join(filter(None, sections))

    def _build_header(self, description: str, intent: str, target: str) -> str:
        """Build prompt header."""
        icon_map = {
            "analyze": "🔍",
            "enhance": "⚡",
            "refactor": "♻️",
            "bugfix": "🐛",
            "feature": "✨",
            "test": "🧪"
        }

        icon = icon_map.get(intent, "📝")
        title = intent.title()

        return f"""{icon} **{title} Request**

## Objective
{description}

**Target:** `{target}`
**Context:** Full codebase analysis with dependencies"""

    def _build_target_source_section(self) -> str:
        """Build target file source code section."""
        target_files = self.context.get('target_files', [])
        if not target_files:
            return ""

        # Find target component in context
        target_component = None
        target_source = None

        for layer_name, components in self.context.get('layers', {}).items():
            for comp in components:
                file_path = comp.get('file_path', '')
                for target in target_files:
                    if target.lower() in file_path.lower():
                        if comp.get('source_code'):
                            target_component = comp
                            target_source = comp['source_code']
                            break
                if target_source:
                    break
            if target_source:
                break

        if not target_source:
            return "## Target Source Code\n\n*Source code not available*"

        # Determine language from file extension
        file_path = target_component.get('file_path', '')
        ext = Path(file_path).suffix
        lang_map = {
            '.ts': 'typescript',
            '.tsx': 'typescript',
            '.js': 'javascript',
            '.jsx': 'javascript',
            '.py': 'python',
            '.dart': 'dart',
        }
        lang = lang_map.get(ext, 'typescript')

        lines_count = len(target_source.splitlines())

        return f"""## Target Source Code

**File:** `{target_component.get('file_path')}`
**Type:** {target_component.get('type')}
**Lines:** {lines_count}

```{lang}
{target_source}
```"""

    def _build_related_components_section(self) -> str:
        """Build section showing related components."""
        target_files = self.context.get('target_files', [])

        # Collect all non-target components
        related = []
        for layer_name, components in self.context.get('layers', {}).items():
            for comp in components:
                file_path = comp.get('file_path', '')
                # Skip target file itself
                is_target = any(t.lower() in file_path.lower() for t in target_files)
                if not is_target and comp.get('source_code'):
                    related.append({
                        'name': comp['name'],
                        'type': comp['type'],
                        'file': comp['file_path'],
                        'layer': layer_name,
                        'source': comp['source_code']
                    })

        if not related:
            return ""

        section = ["## Related Components\n"]
        section.append("These components are used by or related to the target:\n")

        # Group by type
        by_type = {}
        for comp in related:
            comp_type = comp['type']
            if comp_type not in by_type:
                by_type[comp_type] = []
            by_type[comp_type].append(comp)

        # Show each type
        for comp_type, comps in sorted(by_type.items()):
            section.append(f"\n### {comp_type.title()}s\n")
            for comp in comps[:3]:  # Limit to 3 per type
                lines = len(comp['source'].splitlines())
                section.append(f"**{comp['name']}** (`{comp['file']}`) - {lines} lines")

                # Show abbreviated source for context
                if lines < 30:
                    ext = Path(comp['file']).suffix
                    lang = 'typescript' if ext in ['.ts', '.tsx'] else 'javascript'
                    section.append(f"```{lang}\n{comp['source']}\n```\n")
                else:
                    # Just show first 20 lines
                    preview = '\n'.join(comp['source'].splitlines()[:20])
                    ext = Path(comp['file']).suffix
                    lang = 'typescript' if ext in ['.ts', '.tsx'] else 'javascript'
                    section.append(f"```{lang}\n{preview}\n// ... ({lines - 20} more lines)\n```\n")

        return '\n'.join(section)

    def _build_api_context_section(self) -> str:
        """Build API endpoints context."""
        apis = self.context.get('api_contracts', [])
        if not apis:
            return ""

        section = ["## API Endpoints\n"]
        section.append("These API endpoints are relevant to this component:\n")

        for api in apis[:10]:  # Limit to 10
            method = api.get('method', 'GET')
            endpoint = api.get('endpoint', 'N/A')
            handler = api.get('handler', 'N/A')
            section.append(f"- **{method}** `{endpoint}` → `{handler}`")

        return '\n'.join(section)

    def _build_data_context_section(self) -> str:
        """Build data models context."""
        data_components = self.context.get('layers', {}).get('data', [])
        if not data_components:
            return ""

        section = ["## Data Models\n"]
        section.append("These data models are relevant:\n")

        for comp in data_components[:5]:  # Limit to 5
            section.append(f"- **{comp['name']}** ({comp['type']}) - `{comp['file_path']}`")

        return '\n'.join(section)

    def _build_dependencies_section(self) -> str:
        """Build dependencies section."""
        # Collect all imports/dependencies from components
        all_imports = set()

        for layer_name, components in self.context.get('layers', {}).items():
            for comp in components:
                # Would need to parse imports from source code
                # For now, just list the files
                pass

        # For now, skip this section or make it simple
        return ""

    def _build_task_instructions(self, intent: str, description: str) -> str:
        """Build task-specific instructions."""

        if intent == "analyze":
            return """## Analysis Tasks

Please analyze the code and provide:

1. **Summary**: What this code does and its role
2. **Code Quality**: Identify any code smells, anti-patterns, or bugs
3. **Performance**: Flag any performance concerns or optimization opportunities
4. **Type Safety**: Note any type-safety issues or improvements
5. **Best Practices**: Suggest improvements aligned with React/TypeScript best practices
6. **Dependencies**: Comment on the dependency choices and usage patterns"""

        elif intent == "enhance":
            return f"""## Enhancement Tasks

Please enhance the code based on: **{description}**

Focus on:

1. **Implementation**: Add the requested enhancement cleanly and efficiently
2. **Performance**: Ensure any new code is optimized (use useMemo, useCallback where appropriate)
3. **Type Safety**: Maintain strict TypeScript typing
4. **UX**: Consider loading states, error handling, and edge cases
5. **Testing**: Suggest what should be tested
6. **Documentation**: Add JSDoc comments for complex logic

**Constraints:**
- Maintain existing coding patterns and style
- Don't break existing functionality
- Follow Material-UI and React best practices
- Keep the component composable and reusable"""

        elif intent == "refactor":
            return """## Refactoring Tasks

Please refactor the code for:

1. **Clarity**: Improve code readability and maintainability
2. **Performance**: Optimize for better performance
3. **Modularity**: Extract reusable logic into hooks or utilities
4. **Type Safety**: Strengthen TypeScript types
5. **Best Practices**: Apply modern React patterns (hooks, composition)

**Constraints:**
- Maintain the same external API and behavior
- Don't introduce breaking changes
- Keep test compatibility"""

        elif intent == "bugfix":
            return f"""## Bug Fix Tasks

Please fix the issue: **{description}**

Approach:

1. **Root Cause**: Identify the root cause of the bug
2. **Fix**: Implement a clean, minimal fix
3. **Validation**: Explain how to verify the fix works
4. **Prevention**: Suggest how to prevent similar issues
5. **Testing**: Recommend test cases to add

**Constraints:**
- Minimal code changes
- No unrelated refactoring
- Maintain backward compatibility"""

        elif intent == "feature":
            return f"""## Feature Implementation

Please implement: **{description}**

Requirements:

1. **Design**: Plan the implementation approach
2. **Implementation**: Write clean, typed, performant code
3. **Integration**: Integrate smoothly with existing code
4. **UX**: Include proper loading, error, and empty states
5. **Types**: Add comprehensive TypeScript types
6. **Documentation**: Add JSDoc and inline comments

**Quality Standards:**
- Follow existing patterns and conventions
- Use appropriate React hooks (useMemo, useCallback, etc.)
- Handle all edge cases
- Make it testable"""

        else:
            return f"""## Task

{description}

Please provide a complete, production-ready solution."""

    def _build_footer(self) -> str:
        """Build prompt footer."""
        return f"""---
*Generated by LocalMind Code Intelligence - {datetime.now().strftime('%Y-%m-%d %H:%M')}*
*Full codebase context with {len(self.context.get('layers', {}).get('frontend-web', []))} frontend, {len(self.context.get('layers', {}).get('backend', []))} backend, {len(self.context.get('layers', {}).get('data', []))} data components*"""
