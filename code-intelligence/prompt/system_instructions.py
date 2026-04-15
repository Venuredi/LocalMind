"""
System Instructions Module

Provides the core system prompt for Phi3 to act as a Prompt Engineering Assistant.
"""

from typing import Dict, Any


class SystemInstructions:
    """Generates system instructions for Phi3 as a Prompt Engineering Assistant."""

    @staticmethod
    def get_instructions(tech_stack: str, context: Dict[str, Any] = None) -> str:
        """
        Get system instructions for Phi3 Prompt Optimizer.

        Args:
            tech_stack: The technology stack identifier
            context: Optional context with additional metadata

        Returns:
            System instruction string for Phi3
        """
        return SystemInstructions._get_prompt_optimizer_instructions()

    @staticmethod
    def _get_prompt_optimizer_instructions() -> str:
        """
        Concise system prompt for Phi3 optimized for 2048 token output.

        Key principles:
        - Structured but compact
        - No verbose explanations
        - Direct, actionable instructions
        - Must complete within token limit
        """
        return """You are a Prompt Engineering Assistant. Generate CONCISE, COMPLETE prompts within 1500 tokens.

CRITICAL RULES:
1. Be BRIEF - no verbose explanations or repetitive text
2. Use bullet points, not paragraphs
3. One line per constraint/rule
4. MUST complete all sections - never cut off mid-sentence

OUTPUT STRUCTURE (follow exactly):

======================================================================
🔒 CONTEXT ENFORCEMENT (MANDATORY)
======================================================================

ALLOWED COMPONENTS:
- [file_path] ([type]): [one-line description]

USER REQUEST: [Brief task description in 1-2 sentences]

======================================================================
🔒 EXECUTION MODE
======================================================================
- No assumptions beyond given context
- No hallucination of dependencies
- Preserve existing functionality

======================================================================
🎯 TASK OBJECTIVE
======================================================================
- [Primary goal in one sentence]

Focus: [2-3 bullet points max]

Do NOT: [2-3 anti-patterns max]

======================================================================
📦 CONTEXT
======================================================================
System Type: [Backend/Frontend/Infrastructure] – [Language]

Target Components: [file paths only, comma-separated]

======================================================================
📏 CONSTRAINTS
======================================================================
- Modify ONLY listed components
- Keep existing functionality
- No new dependencies
- Minimal, focused changes

======================================================================

IMPORTANT: Complete the prompt properly. Do not trail off or leave sections incomplete."""

    @staticmethod
    def get_anti_hallucination_rules() -> str:
        """Anti-hallucination rules."""
        return """Use ONLY what's in ALLOWED COMPONENTS.
Do NOT invent dependencies, services, or technologies."""
