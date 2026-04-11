"""
Prompt Template Engine

Orchestrates prompt generation by selecting the appropriate template
and applying context to generate the final prompt.
"""

from typing import Dict, Any
from .templates.enhancement import EnhancementTemplate
from .templates.bug_fix import BugFixTemplate
from .templates.new_feature import NewFeatureTemplate
from .templates.refactoring import RefactoringTemplate
from .templates.analysis import AnalysisTemplate
from .templates.feature_extension import FeatureExtensionTemplate


class PromptTemplateEngine:
    """
    Generates prompts by selecting and applying appropriate templates.

    Supports different prompt types:
    - enhancement: Improve existing code
    - bug_fix: Fix bugs
    - new_feature: Add new functionality
    - refactoring: Restructure code
    - analysis: Analyze code
    - feature_extension: Extend existing feature
    """

    def __init__(self):
        """Initialize template engine with available templates."""
        self.templates = {
            'enhancement': EnhancementTemplate(),
            'bug_fix': BugFixTemplate(),
            'new_feature': NewFeatureTemplate(),
            'refactoring': RefactoringTemplate(),
            'analysis': AnalysisTemplate(),
            'feature_extension': FeatureExtensionTemplate(),
        }

    def generate(self,
                 prompt_type: str,
                 context: Dict[str, Any],
                 user_description: str,
                 title: str) -> str:
        """
        Generate a prompt using the appropriate template.

        Args:
            prompt_type: Type of prompt (enhancement, bug_fix, etc.)
            context: Ontology context from OntologyContextBuilder
            user_description: User's description of what they want
            title: Title of the task

        Returns:
            Fully formatted prompt string

        Raises:
            ValueError: If prompt_type is not supported
        """
        # Normalize prompt type
        prompt_type = prompt_type.lower().strip()

        # Check if template exists
        if prompt_type not in self.templates:
            raise ValueError(
                f"Unsupported prompt type: '{prompt_type}'. "
                f"Available types: {', '.join(self.templates.keys())}"
            )

        # Get template
        template = self.templates[prompt_type]

        # Generate prompt
        prompt = template.generate(context, user_description, title)

        return prompt

    def get_available_types(self) -> list:
        """Get list of available prompt types."""
        return list(self.templates.keys())

    def add_template(self, prompt_type: str, template):
        """
        Add a custom template.

        Args:
            prompt_type: Name/type of the template
            template: Template instance (must extend BasePromptTemplate)
        """
        self.templates[prompt_type] = template
