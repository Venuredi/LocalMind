"""Phi3 LLM service using Ollama for ontology-guided prompt generation."""

import ollama
import re
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


def ensure_complete_output(text: str) -> str:
    """
    Post-process LLM output to ensure it ends cleanly without mid-sentence truncation.

    Strategies:
    1. If ends with section divider, keep as-is
    2. If ends mid-sentence, find last complete sentence/section
    3. Add proper closing if truncated
    """
    if not text:
        return text

    text = text.rstrip()

    # Check if already ends cleanly
    clean_endings = [
        '======================================================================',
        '```',
        '.',
        '!',
        '?',
        ':',
        '- ',
        '\n',
    ]

    for ending in clean_endings:
        if text.endswith(ending):
            return text

    # Find last complete section (marked by ===== divider)
    section_pattern = r'={50,}'
    sections = list(re.finditer(section_pattern, text))

    if sections:
        # Find the last complete section
        last_section_end = sections[-1].end()

        # Look for content after the last divider
        remaining = text[last_section_end:].strip()

        # If remaining content is incomplete (no proper ending), trim to last complete section
        if remaining and not any(remaining.endswith(e.strip()) for e in clean_endings if e.strip()):
            # Find last sentence end in remaining
            sentence_ends = [remaining.rfind('.'), remaining.rfind('!'), remaining.rfind('?'), remaining.rfind('\n-')]
            last_sentence = max(sentence_ends)

            if last_sentence > 0:
                text = text[:last_section_end] + '\n' + remaining[:last_sentence + 1]
            else:
                # No complete sentence, just use up to last divider
                text = text[:last_section_end]
    else:
        # No section dividers, find last complete sentence
        sentence_ends = [text.rfind('. '), text.rfind('.\n'), text.rfind('!\n'), text.rfind('?\n')]
        last_sentence = max(sentence_ends)

        if last_sentence > len(text) * 0.7:  # Only truncate if we keep most of the content
            text = text[:last_sentence + 1]

    # Add closing divider if prompt looks incomplete
    if '🔒 CONTEXT ENFORCEMENT' in text and not text.rstrip().endswith('='):
        text = text.rstrip() + '\n\n======================================================================'

    return text


class Phi3Service:
    """Service for interacting with Phi3 model via Ollama."""

    def __init__(self, model_name: str = "phi3:mini"):
        """
        Initialize Phi3 service.

        Args:
            model_name: Name of the Phi3 model in Ollama (default: phi3:mini)
        """
        self.model_name = model_name
        self.client = ollama.Client()
        logger.info(f"Phi3Service initialized with model: {model_name}")

    def generate(
        self,
        prompt: str,
        max_tokens: int = 2048,
        temperature: float = 0.7,
        system_prompt: Optional[str] = None
    ) -> str:
        """
        Generate response from Phi3.

        Args:
            prompt: The input prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0.0-1.0)
            system_prompt: Optional system-level instructions

        Returns:
            Generated text response

        Raises:
            RuntimeError: If generation fails
        """
        try:
            # Build messages
            messages = []
            if system_prompt:
                messages.append({
                    'role': 'system',
                    'content': system_prompt
                })
            messages.append({
                'role': 'user',
                'content': prompt
            })

            # Generate response
            response = self.client.chat(
                model=self.model_name,
                messages=messages,
                options={
                    "num_predict": max_tokens,
                    "temperature": temperature,
                }
            )

            generated_text = response['message']['content']
            logger.debug(f"Generated {len(generated_text)} characters (raw)")

            # Post-process to ensure clean ending
            processed_text = ensure_complete_output(generated_text)
            if len(processed_text) != len(generated_text):
                logger.info(f"Output cleaned: {len(generated_text)} -> {len(processed_text)} chars")

            return processed_text

        except Exception as e:
            logger.error(f"Phi3 generation failed: {e}")
            raise RuntimeError(f"Phi3 generation failed: {e}")

    def generate_stream(
        self,
        prompt: str,
        max_tokens: int = 2048,
        temperature: float = 0.7,
        system_prompt: Optional[str] = None
    ):
        """
        Generate response from Phi3 with streaming support.

        Args:
            prompt: The input prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0.0-1.0)
            system_prompt: Optional system-level instructions

        Yields:
            Generated text chunks as they arrive

        Raises:
            RuntimeError: If generation fails
        """
        try:
            # Build messages
            messages = []
            if system_prompt:
                messages.append({
                    'role': 'system',
                    'content': system_prompt
                })
            messages.append({
                'role': 'user',
                'content': prompt
            })

            # Generate response with streaming
            stream = self.client.chat(
                model=self.model_name,
                messages=messages,
                stream=True,  # Enable streaming
                options={
                    "num_predict": max_tokens,
                    "temperature": temperature,
                }
            )

            # Yield chunks as they arrive
            for chunk in stream:
                if 'message' in chunk and 'content' in chunk['message']:
                    yield chunk['message']['content']

        except Exception as e:
            logger.error(f"Phi3 streaming generation failed: {e}")
            raise RuntimeError(f"Phi3 streaming generation failed: {e}")

    def generate_simple(self, prompt: str, max_tokens: int = 2048) -> str:
        """
        Simple generation using the generate API (no chat).

        Args:
            prompt: The input prompt
            max_tokens: Maximum tokens to generate

        Returns:
            Generated text response

        Raises:
            RuntimeError: If generation fails
        """
        try:
            response = self.client.generate(
                model=self.model_name,
                prompt=prompt,
                options={
                    "num_predict": max_tokens,
                    "temperature": 0.7,
                }
            )
            return response['response']
        except Exception as e:
            logger.error(f"Phi3 simple generation failed: {e}")
            raise RuntimeError(f"Phi3 simple generation failed: {e}")

    def is_available(self) -> bool:
        """
        Check if Phi3 model is available in Ollama.

        Returns:
            True if model is available, False otherwise
        """
        try:
            models = self.client.list()
            available = any(self.model_name in m.model for m in models.models)
            logger.info(f"Phi3 model {self.model_name} available: {available}")
            return available
        except Exception as e:
            logger.error(f"Failed to check model availability: {e}")
            return False

    def get_model_info(self) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about the Phi3 model.

        Returns:
            Dictionary with model details or None if not available
        """
        try:
            models = self.client.list()
            for m in models.models:
                if self.model_name in m.model:
                    return {
                        'name': m.model,
                        'size': m.size,
                        'modified_at': str(m.modified_at),
                        'parameter_size': m.details.parameter_size,
                        'quantization': m.details.quantization_level,
                        'family': m.details.family
                    }
            return None
        except Exception as e:
            logger.error(f"Failed to get model info: {e}")
            return None
