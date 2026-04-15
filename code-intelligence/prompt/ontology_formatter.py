"""
Ontology Formatter for Phi3

Compact formatting optimized for 2048 token output limit.
Components = source of truth. Brevity = priority.
"""

from typing import Dict, List, Any


class OntologyFormatter:
    """Compact ontology formatting for Phi3 with token awareness."""

    # Approximate tokens per character (conservative estimate)
    CHARS_PER_TOKEN = 4
    # Target context budget (leave room for LLM output)
    MAX_CONTEXT_TOKENS = 500
    MAX_CONTEXT_CHARS = MAX_CONTEXT_TOKENS * CHARS_PER_TOKEN

    @staticmethod
    def format_for_phi3(context: Dict[str, Any]) -> str:
        """
        Format ontology context - compact and token-aware.

        Prioritizes:
        1. Component identification (always)
        2. System type (always)
        3. Code snippet (if budget allows, max 20 lines)

        Args:
            context: Ontology context from OntologyContextBuilder

        Returns:
            Compact formatted string within token budget
        """
        sections = []
        char_budget = OntologyFormatter.MAX_CONTEXT_CHARS

        # 1. Components (source of truth) - always include
        components_section = OntologyFormatter._format_components(context)
        sections.append(components_section)
        char_budget -= len(components_section)

        # 2. System type - always include
        system_section = OntologyFormatter._format_system_type(context)
        sections.append(system_section)
        char_budget -= len(system_section)

        # 3. Code (if budget allows)
        if char_budget > 200:  # Only include if we have room
            code_section = OntologyFormatter._format_code(context, max_chars=char_budget - 100)
            if code_section:
                sections.append(code_section)

        return "\n\n".join(filter(None, sections))

    @staticmethod
    def _format_components(context: Dict[str, Any]) -> str:
        """Format selected components - absolute minimum."""
        component = context.get('component', {})

        if not component:
            return "SELECTED COMPONENTS:\nNone"

        name = component.get('name', 'Unknown')
        comp_type = component.get('type', 'unknown')
        file_path = component.get('file_path', '')

        return f"""SELECTED COMPONENTS:
- {file_path} ({comp_type})"""

    @staticmethod
    def _format_system_type(context: Dict[str, Any]) -> str:
        """System type - just the facts."""
        layer = context.get('layer', 'unknown')
        file_path = context.get('file_path', '')

        # Language from extension
        language = 'Unknown'
        if file_path:
            if file_path.endswith('.tf'):
                language = 'Terraform'
            elif file_path.endswith(('.yaml', '.yml')):
                language = 'YAML'
            elif file_path.endswith('.ts'):
                language = 'TypeScript'
            elif file_path.endswith('.js'):
                language = 'JavaScript'
            elif file_path.endswith('.py'):
                language = 'Python'
            elif file_path.endswith('.go'):
                language = 'Go'
            elif file_path.endswith('.cs'):
                language = 'C#'
            elif file_path.endswith('.java'):
                language = 'Java'

        # System type from layer
        if layer == 'infrastructure':
            system_type = 'Infrastructure'
        elif layer == 'backend':
            system_type = 'Backend'
        elif layer in ('frontend-web', 'frontend-mobile'):
            system_type = 'Frontend'
        elif layer == 'data':
            system_type = 'Data'
        else:
            system_type = 'Unknown'

        return f"SYSTEM TYPE: {system_type} ({language})"

    @staticmethod
    def _format_code(context: Dict[str, Any], max_chars: int = 800) -> str:
        """Format code - respects character budget for token awareness."""
        file_snippet = context.get('file_snippet', '')
        file_content = context.get('file_content', '')

        source = file_snippet if file_snippet else file_content

        if not source:
            return None

        # Calculate max lines based on character budget
        # Reserve ~100 chars for header/formatting
        available_chars = max_chars - 100
        max_lines = min(20, available_chars // 60)  # ~60 chars per line average

        lines = source.split('\n')[:max_lines]
        truncated_source = '\n'.join(lines)

        # Ensure we don't exceed budget
        if len(truncated_source) > available_chars:
            truncated_source = truncated_source[:available_chars] + '\n...'

        line_count = len(lines)
        return f"""CODE EXCERPT ({line_count} lines):
```
{truncated_source}
```"""

    @staticmethod
    def format_user_request(
        prompt_type: str,
        title: str,
        description: str,
        max_desc_chars: int = 300
    ) -> str:
        """Format user request - compact with description limit."""
        type_map = {
            'enhancement': 'Enhancement',
            'bug_fix': 'Bug Fix',
            'new_feature': 'New Feature',
            'refactoring': 'Refactoring',
            'analysis': 'Analysis',
            'feature_extension': 'Feature Extension'
        }

        label = type_map.get(prompt_type, prompt_type.title())

        # Truncate description if too long
        desc = description
        if len(description) > max_desc_chars:
            desc = description[:max_desc_chars].rsplit(' ', 1)[0] + '...'

        return f"""REQUEST: {label} - {title}
{desc}"""

    @staticmethod
    def format_task_instructions(prompt_type: str) -> str:
        """Minimal task guidance - not used anymore."""
        return ""
