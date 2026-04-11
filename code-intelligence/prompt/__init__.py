"""
Ontology-Guided Prompt Generation Module

This module provides intelligent prompt generation using the code ontology.
It extracts context from indexed components and generates rich, structured prompts
for AI-assisted development tasks.
"""

from .context_builder import OntologyContextBuilder
from .template_engine import PromptTemplateEngine

__all__ = ['OntologyContextBuilder', 'PromptTemplateEngine']
