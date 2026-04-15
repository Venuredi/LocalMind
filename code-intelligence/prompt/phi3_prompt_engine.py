"""
Phi3 Prompt Engine

Orchestrates LLM-based prompt generation using Phi3 while maintaining
ontology constraints and preventing hallucinations.

Token-aware: Manages input/output to fit within 2048 token limit.
"""

from typing import Dict, Any, Optional
import logging
import sys
from pathlib import Path

# Add parent directory for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from llm.phi3_service import Phi3Service
from prompt.system_instructions import SystemInstructions
from prompt.ontology_formatter import OntologyFormatter
from prompt.prompt_validator import PromptValidator

logger = logging.getLogger(__name__)


def estimate_tokens(text: str) -> int:
    """
    Estimate token count for text.

    Uses a conservative estimate of ~4 characters per token.
    This is approximate but works well for English text and code.
    """
    if not text:
        return 0
    # Rough estimate: 1 token ≈ 4 characters for English
    # Add 10% buffer for safety
    return int(len(text) / 4 * 1.1)


class Phi3PromptEngine:
    """
    Generates ontology-guided prompts using Phi3 LLM.

    This engine:
    1. Formats ontology context for Phi3
    2. Generates system instructions based on tech stack
    3. Uses Phi3 to create adaptive prompts
    4. Validates output against ontology constraints
    5. Enhances with safety guardrails
    """

    def __init__(self, phi3_service: Optional[Phi3Service] = None):
        """
        Initialize Phi3 Prompt Engine.

        Args:
            phi3_service: Optional Phi3Service instance. Creates new one if not provided.
        """
        self.phi3_service = phi3_service or Phi3Service()
        self.system_instructions = SystemInstructions()
        self.formatter = OntologyFormatter()

        # Check if Phi3 is available
        if not self.phi3_service.is_available():
            logger.warning("Phi3 model not available. Engine will fail on generation.")
            raise RuntimeError(
                "Phi3 model not available. Please run 'ollama pull phi3:mini' to install."
            )

        logger.info("Phi3PromptEngine initialized successfully")

    def generate(
        self,
        prompt_type: str,
        context: Dict[str, Any],
        user_description: str,
        title: str,
        validate: bool = True,
        enhance: bool = True,
        max_tokens: int = 2048,
        temperature: float = 0.7
    ) -> Dict[str, Any]:
        """
        Generate ontology-guided prompt using Phi3.

        Token-aware: Manages input size to allow adequate output space.

        Args:
            prompt_type: Type of prompt (enhancement, bug_fix, etc.)
            context: Ontology context from OntologyContextBuilder
            user_description: User's description of the task
            title: Task title
            validate: Whether to validate the generated prompt
            enhance: Whether to enhance with safety guardrails
            max_tokens: Maximum tokens for Phi3 generation
            temperature: Sampling temperature (0.0-1.0)

        Returns:
            Dictionary with generated prompt and metadata
        """
        try:
            # Step 1: Build system instructions
            tech_stack = context.get('tech_stack', 'unknown')
            system_prompt = self._build_system_prompt(tech_stack, prompt_type)

            # Step 2: Format ontology context
            ontology_context = self.formatter.format_for_phi3(context)

            # Step 3: Format user request
            user_request = self.formatter.format_user_request(
                prompt_type, title, user_description
            )

            # Step 4: Build Phi3 input
            phi3_input = self._build_phi3_input(
                ontology_context,
                user_request,
                prompt_type
            )

            # Step 4.5: Token budget check
            input_tokens = estimate_tokens(system_prompt) + estimate_tokens(phi3_input)
            # Reserve tokens for output (aim for ~1500 output tokens to stay safe)
            max_input_tokens = 2500  # Phi3 context is ~4096, reserve for output

            if input_tokens > max_input_tokens:
                logger.warning(f"Input too large ({input_tokens} tokens), trimming context")
                # Reduce context by using shorter description
                user_request = self.formatter.format_user_request(
                    prompt_type, title, user_description[:200]
                )
                phi3_input = self._build_phi3_input(
                    ontology_context,
                    user_request,
                    prompt_type
                )

            logger.info(f"Generating prompt with Phi3 (type: {prompt_type}, stack: {tech_stack}, input_tokens: ~{estimate_tokens(phi3_input)})")

            # Step 5: Generate with Phi3
            generated_prompt = self.phi3_service.generate(
                prompt=phi3_input,
                system_prompt=system_prompt,
                max_tokens=max_tokens,
                temperature=temperature
            )

            logger.info(f"Phi3 generated {len(generated_prompt)} characters")

            # Step 6: Validate
            validation_result = None
            if validate:
                validator = PromptValidator(context)
                is_valid, errors, warnings = validator.validate(generated_prompt)

                validation_result = validator.get_validation_summary(
                    is_valid, errors, warnings
                )

                logger.info(
                    f"Validation: {'PASSED' if is_valid else 'FAILED'} "
                    f"({len(errors)} errors, {len(warnings)} warnings)"
                )

                # Enhance with safety guardrails if enabled
                if enhance:
                    generated_prompt = validator.enhance_prompt(generated_prompt)
                    logger.info("Prompt enhanced with safety guardrails")

            # Step 7: Build response
            return {
                'prompt': generated_prompt,
                'metadata': {
                    'generator': 'phi3',
                    'model': self.phi3_service.model_name,
                    'prompt_type': prompt_type,
                    'tech_stack': tech_stack,
                    'length': len(generated_prompt),
                    'tokens_generated': len(generated_prompt.split()),  # Rough estimate
                    'temperature': temperature,
                    'validated': validate,
                    'enhanced': enhance
                },
                'validation': validation_result,
                'success': True
            }

        except Exception as e:
            logger.error(f"Phi3 prompt generation failed: {e}", exc_info=True)
            return {
                'prompt': None,
                'error': str(e),
                'success': False,
                'metadata': {
                    'generator': 'phi3',
                    'prompt_type': prompt_type,
                }
            }

    def generate_stream(
        self,
        prompt_type: str,
        context: Dict[str, Any],
        user_description: str,
        title: str,
        max_tokens: int = 2048,
        temperature: float = 0.7
    ):
        """
        Generate ontology-guided prompt using Phi3 with streaming.

        Args:
            prompt_type: Type of prompt (enhancement, bug_fix, etc.)
            context: Ontology context from OntologyContextBuilder
            user_description: User's description of the task
            title: Task title
            max_tokens: Maximum tokens for Phi3 generation
            temperature: Sampling temperature (0.0-1.0)

        Yields:
            Generated prompt chunks as they arrive
        """
        try:
            # Step 1: Build system instructions
            tech_stack = context.get('tech_stack', 'unknown')
            system_prompt = self._build_system_prompt(tech_stack, prompt_type)

            # Step 2: Format ontology context
            ontology_context = self.formatter.format_for_phi3(context)

            # Step 3: Format user request
            user_request = self.formatter.format_user_request(
                prompt_type, title, user_description
            )

            # Step 4: Build Phi3 input
            phi3_input = self._build_phi3_input(
                ontology_context,
                user_request,
                prompt_type
            )

            logger.info(f"Streaming prompt generation with Phi3 (type: {prompt_type}, stack: {tech_stack})")

            # Step 5: Stream generate with Phi3
            for chunk in self.phi3_service.generate_stream(
                prompt=phi3_input,
                system_prompt=system_prompt,
                max_tokens=max_tokens,
                temperature=temperature
            ):
                yield chunk

        except Exception as e:
            logger.error(f"Phi3 streaming generation failed: {e}", exc_info=True)
            raise RuntimeError(f"Phi3 streaming generation failed: {e}")

    def _build_system_prompt(self, tech_stack: str, prompt_type: str) -> str:
        """Build system prompt for Phi3 - minimal and focused."""
        # Get the core prompt optimizer instructions
        # (already includes structure, rules, and guidance)
        return self.system_instructions.get_instructions(tech_stack)

    def _build_phi3_input(
        self,
        ontology_context: str,
        user_request: str,
        prompt_type: str
    ) -> str:
        """
        Build the user input for Phi3 Prompt Optimizer.

        System prompt contains all instructions and structure.
        We just provide clean data: user request + ontology facts.
        """
        # Just pass the data - no extra instructions or wrapping
        return f"""{user_request}

{ontology_context}"""

    def is_available(self) -> bool:
        """Check if Phi3 engine is available."""
        return self.phi3_service.is_available()

    def get_model_info(self) -> Optional[Dict[str, Any]]:
        """Get Phi3 model information."""
        return self.phi3_service.get_model_info()


class HybridPromptEngine:
    """
    Hybrid engine that uses Phi3 for complex tasks and templates for simple ones.

    Decision logic:
    - Use Phi3: Complex tasks, multiple components, custom requirements
    - Use Templates: Simple tasks, single component, standard operations
    """

    def __init__(
        self,
        phi3_service: Optional[Phi3Service] = None,
        template_engine = None
    ):
        """
        Initialize hybrid engine.

        Args:
            phi3_service: Optional Phi3Service instance
            template_engine: Optional PromptTemplateEngine instance
        """
        # Try to initialize Phi3 engine
        try:
            self.phi3_engine = Phi3PromptEngine(phi3_service)
            self.phi3_available = True
            logger.info("Phi3 engine available")
        except Exception as e:
            self.phi3_engine = None
            self.phi3_available = False
            logger.warning(f"Phi3 engine not available: {e}")

        # Template engine fallback
        if template_engine is None:
            from prompt.template_engine import PromptTemplateEngine
            self.template_engine = PromptTemplateEngine()
        else:
            self.template_engine = template_engine

    def generate(
        self,
        prompt_type: str,
        context: Dict[str, Any],
        user_description: str,
        title: str,
        use_llm: Optional[bool] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate prompt using best available method.

        Args:
            prompt_type: Type of prompt
            context: Ontology context
            user_description: User description
            title: Task title
            use_llm: Force LLM (True) or template (False). None = auto-decide
            **kwargs: Additional arguments for generators

        Returns:
            Generated prompt with metadata
        """
        # Determine which engine to use
        should_use_llm = self._should_use_llm(
            prompt_type, context, user_description, use_llm
        )

        if should_use_llm and self.phi3_available:
            logger.info(f"Using Phi3 engine for {prompt_type}")
            result = self.phi3_engine.generate(
                prompt_type=prompt_type,
                context=context,
                user_description=user_description,
                title=title,
                **kwargs
            )
            result['metadata']['engine'] = 'phi3'
            return result
        else:
            logger.info(f"Using template engine for {prompt_type}")
            prompt = self.template_engine.generate(
                prompt_type=prompt_type,
                context=context,
                user_description=user_description,
                title=title
            )
            return {
                'prompt': prompt,
                'metadata': {
                    'generator': 'template',
                    'engine': 'template',
                    'prompt_type': prompt_type,
                    'length': len(prompt)
                },
                'validation': None,
                'success': True
            }

    def _should_use_llm(
        self,
        prompt_type: str,
        context: Dict[str, Any],
        user_description: str,
        force: Optional[bool]
    ) -> bool:
        """
        Decide whether to use LLM or template.

        Args:
            prompt_type: Type of prompt
            context: Ontology context
            user_description: User description
            force: Force decision (overrides auto-decision)

        Returns:
            True to use LLM, False to use template
        """
        # If forced, respect it
        if force is not None:
            return force and self.phi3_available

        # If Phi3 not available, use template
        if not self.phi3_available:
            return False

        # Auto-decision logic
        complexity_score = 0

        # Factor 1: Multiple components
        component_count = len(context.get('dependencies', [])) + len(context.get('dependents', []))
        if component_count > 5:
            complexity_score += 2

        # Factor 2: Long description (custom requirements)
        if len(user_description) > 200:
            complexity_score += 1

        # Factor 3: Specific prompt types benefit from LLM
        llm_preferred_types = ['feature_extension', 'analysis', 'refactoring']
        if prompt_type in llm_preferred_types:
            complexity_score += 2

        # Factor 4: Complex architecture
        if context.get('dependency_chain') and len(context.get('dependency_chain', '')) > 100:
            complexity_score += 1

        # Decision threshold
        USE_LLM_THRESHOLD = 3
        return complexity_score >= USE_LLM_THRESHOLD
