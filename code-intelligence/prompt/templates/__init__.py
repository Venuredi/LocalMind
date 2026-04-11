"""
Prompt Templates

Provides various templates for different prompt types:
- Enhancement
- Bug Fix
- New Feature
- Refactoring
- Analysis
- Feature Extension
"""

from .base_template import BasePromptTemplate
from .enhancement import EnhancementTemplate
from .bug_fix import BugFixTemplate
from .new_feature import NewFeatureTemplate
from .refactoring import RefactoringTemplate
from .analysis import AnalysisTemplate
from .feature_extension import FeatureExtensionTemplate

__all__ = [
    'BasePromptTemplate',
    'EnhancementTemplate',
    'BugFixTemplate',
    'NewFeatureTemplate',
    'RefactoringTemplate',
    'AnalysisTemplate',
    'FeatureExtensionTemplate',
]
