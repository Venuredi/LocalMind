"""
Code Intelligence System
A cross-layer context engine for multi-stack repositories.
"""

__version__ = "1.0.0"

from .indexer.unified_indexer import UnifiedIndexer
from .graph.graph_builder import GraphBuilder
from .context_builder.context_assembler import ContextAssembler

__all__ = [
    "UnifiedIndexer",
    "GraphBuilder",
    "ContextAssembler",
]
