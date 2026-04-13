"""
Ontology Formatter for Phi3

Absolute minimal formatting. Components = source of truth.
"""

from typing import Dict, List, Any


class OntologyFormatter:
    """Minimal ontology formatting for Phi3."""

    @staticmethod
    def format_for_phi3(context: Dict[str, Any]) -> str:
        """
        Format ontology context - absolute minimum.

        Only includes:
        1. Selected components (always)
        2. System type (always)
        3. Code snippet (if available, max 30 lines)

        NO dependencies section.
        NO verbose headers.
        NO assumptions.

        Args:
            context: Ontology context from OntologyContextBuilder

        Returns:
            Minimal formatted string
        """
        sections = []

        # 1. Components (source of truth)
        sections.append(OntologyFormatter._format_components(context))

        # 2. System type (context for Phi3)
        sections.append(OntologyFormatter._format_system_type(context))

        # 3. Code (if available, very limited)
        code_section = OntologyFormatter._format_code(context)
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
    def _format_code(context: Dict[str, Any]) -> str:
        """Format code - max 30 lines for Phi3."""
        file_snippet = context.get('file_snippet', '')
        file_content = context.get('file_content', '')

        source = file_snippet if file_snippet else file_content

        if not source:
            return None

        # Very aggressive limit for Phi3 (30 lines max)
        lines = source.split('\n')[:30]
        truncated_source = '\n'.join(lines)

        return f"""CURRENT CODE (first 30 lines):
```
{truncated_source}
```"""

    @staticmethod
    def format_user_request(
        prompt_type: str,
        title: str,
        description: str
    ) -> str:
        """Format user request - minimal."""
        type_map = {
            'enhancement': 'Enhancement',
            'bug_fix': 'Bug Fix',
            'new_feature': 'New Feature',
            'refactoring': 'Refactoring',
            'analysis': 'Analysis',
            'feature_extension': 'Feature Extension'
        }

        label = type_map.get(prompt_type, prompt_type.title())

        return f"""USER REQUEST:
Type: {label}
Title: {title}
Description: {description}"""

    @staticmethod
    def format_task_instructions(prompt_type: str) -> str:
        """Minimal task guidance - not used anymore."""
        return ""
