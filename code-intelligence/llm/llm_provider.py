"""
LLM Provider Abstraction Layer

Provides a unified interface for multiple LLM providers:
- Ollama (Local)
- OpenAI
- Anthropic Claude
- Google Gemini
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, Generator
import logging

logger = logging.getLogger(__name__)


class BaseLLMProvider(ABC):
    """Abstract base class for LLM providers."""

    @abstractmethod
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 2048,
        temperature: float = 0.7
    ) -> str:
        """Generate a response from the LLM."""
        pass

    @abstractmethod
    def generate_stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 2048,
        temperature: float = 0.7
    ) -> Generator[str, None, None]:
        """Generate a streaming response from the LLM."""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if the provider is available and configured."""
        pass

    @abstractmethod
    def get_model_info(self) -> Optional[Dict[str, Any]]:
        """Get information about the current model."""
        pass


class OllamaProvider(BaseLLMProvider):
    """Ollama (local) LLM provider."""

    def __init__(self, host: str = "http://localhost:11434", model: str = "phi3:mini"):
        self.host = host
        self.model = model
        self._client = None

    @property
    def client(self):
        if self._client is None:
            try:
                import ollama
                self._client = ollama.Client(host=self.host)
            except ImportError:
                logger.error("ollama package not installed")
                raise RuntimeError("ollama package not installed. Run: pip install ollama")
        return self._client

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 2048,
        temperature: float = 0.7
    ) -> str:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = self.client.chat(
            model=self.model,
            messages=messages,
            options={"num_predict": max_tokens, "temperature": temperature}
        )
        return response['message']['content']

    def generate_stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 2048,
        temperature: float = 0.7
    ) -> Generator[str, None, None]:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        stream = self.client.chat(
            model=self.model,
            messages=messages,
            stream=True,
            options={"num_predict": max_tokens, "temperature": temperature}
        )
        for chunk in stream:
            if 'message' in chunk and 'content' in chunk['message']:
                yield chunk['message']['content']

    def is_available(self) -> bool:
        try:
            models = self.client.list()
            return any(self.model in m.model for m in models.models)
        except Exception as e:
            logger.error(f"Ollama not available: {e}")
            return False

    def get_model_info(self) -> Optional[Dict[str, Any]]:
        try:
            models = self.client.list()
            for m in models.models:
                if self.model in m.model:
                    return {
                        "provider": "ollama",
                        "name": m.model,
                        "size": m.size,
                        "family": getattr(m.details, 'family', 'unknown')
                    }
        except Exception:
            pass
        return None


class OpenAIProvider(BaseLLMProvider):
    """OpenAI API provider."""

    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4o-mini",
        organization: Optional[str] = None
    ):
        self.api_key = api_key
        self.model = model
        self.organization = organization
        self._client = None

    @property
    def client(self):
        if self._client is None:
            try:
                from openai import OpenAI
                self._client = OpenAI(
                    api_key=self.api_key,
                    organization=self.organization
                )
            except ImportError:
                raise RuntimeError("openai package not installed. Run: pip install openai")
        return self._client

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 2048,
        temperature: float = 0.7
    ) -> str:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature
        )
        return response.choices[0].message.content

    def generate_stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 2048,
        temperature: float = 0.7
    ) -> Generator[str, None, None]:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        stream = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
            stream=True
        )
        for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    def is_available(self) -> bool:
        if not self.api_key:
            return False
        try:
            # Simple check - list models
            self.client.models.list()
            return True
        except Exception as e:
            logger.error(f"OpenAI not available: {e}")
            return False

    def get_model_info(self) -> Optional[Dict[str, Any]]:
        return {
            "provider": "openai",
            "name": self.model,
            "type": "cloud"
        }


class AnthropicProvider(BaseLLMProvider):
    """Anthropic Claude API provider."""

    def __init__(self, api_key: str, model: str = "claude-3-haiku-20240307"):
        self.api_key = api_key
        self.model = model
        self._client = None

    @property
    def client(self):
        if self._client is None:
            try:
                import anthropic
                self._client = anthropic.Anthropic(api_key=self.api_key)
            except ImportError:
                raise RuntimeError("anthropic package not installed. Run: pip install anthropic")
        return self._client

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 2048,
        temperature: float = 0.7
    ) -> str:
        message = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            system=system_prompt or "",
            messages=[{"role": "user", "content": prompt}]
        )
        return message.content[0].text

    def generate_stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 2048,
        temperature: float = 0.7
    ) -> Generator[str, None, None]:
        with self.client.messages.stream(
            model=self.model,
            max_tokens=max_tokens,
            system=system_prompt or "",
            messages=[{"role": "user", "content": prompt}]
        ) as stream:
            for text in stream.text_stream:
                yield text

    def is_available(self) -> bool:
        if not self.api_key:
            return False
        try:
            # Test with minimal request
            self.client.messages.create(
                model=self.model,
                max_tokens=10,
                messages=[{"role": "user", "content": "hi"}]
            )
            return True
        except Exception as e:
            logger.error(f"Anthropic not available: {e}")
            return False

    def get_model_info(self) -> Optional[Dict[str, Any]]:
        return {
            "provider": "anthropic",
            "name": self.model,
            "type": "cloud"
        }


class GoogleProvider(BaseLLMProvider):
    """Google Gemini API provider."""

    def __init__(self, api_key: str, model: str = "gemini-1.5-flash"):
        self.api_key = api_key
        self.model = model
        self._client = None

    @property
    def client(self):
        if self._client is None:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                self._client = genai.GenerativeModel(self.model)
            except ImportError:
                raise RuntimeError("google-generativeai package not installed. Run: pip install google-generativeai")
        return self._client

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 2048,
        temperature: float = 0.7
    ) -> str:
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{prompt}"

        response = self.client.generate_content(
            full_prompt,
            generation_config={
                "max_output_tokens": max_tokens,
                "temperature": temperature
            }
        )
        return response.text

    def generate_stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 2048,
        temperature: float = 0.7
    ) -> Generator[str, None, None]:
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{prompt}"

        response = self.client.generate_content(
            full_prompt,
            generation_config={
                "max_output_tokens": max_tokens,
                "temperature": temperature
            },
            stream=True
        )
        for chunk in response:
            if chunk.text:
                yield chunk.text

    def is_available(self) -> bool:
        if not self.api_key:
            return False
        try:
            self.client.generate_content("hi", generation_config={"max_output_tokens": 10})
            return True
        except Exception as e:
            logger.error(f"Google Gemini not available: {e}")
            return False

    def get_model_info(self) -> Optional[Dict[str, Any]]:
        return {
            "provider": "google",
            "name": self.model,
            "type": "cloud"
        }


class LLMProviderFactory:
    """Factory for creating LLM provider instances based on settings."""

    @staticmethod
    def create_from_settings() -> Optional[BaseLLMProvider]:
        """
        Create an LLM provider based on current application settings.

        Returns:
            BaseLLMProvider instance or None if not configured
        """
        try:
            from config.settings import settings_manager

            settings = settings_manager.settings
            active_provider = settings.llm.active_provider.value

            if active_provider == "ollama":
                config = settings.llm.ollama
                if config.enabled:
                    return OllamaProvider(
                        host=config.host,
                        model=config.model
                    )

            elif active_provider == "openai":
                config = settings.llm.openai
                if config.enabled and config.api_key:
                    return OpenAIProvider(
                        api_key=config.api_key,
                        model=config.model,
                        organization=config.organization
                    )

            elif active_provider == "anthropic":
                config = settings.llm.anthropic
                if config.enabled and config.api_key:
                    return AnthropicProvider(
                        api_key=config.api_key,
                        model=config.model
                    )

            elif active_provider == "google":
                config = settings.llm.google
                if config.enabled and config.api_key:
                    return GoogleProvider(
                        api_key=config.api_key,
                        model=config.model
                    )

            logger.warning(f"No valid LLM provider configured for: {active_provider}")
            return None

        except Exception as e:
            logger.error(f"Error creating LLM provider: {e}")
            return None

    @staticmethod
    def create(
        provider: str,
        **kwargs
    ) -> Optional[BaseLLMProvider]:
        """
        Create a specific LLM provider instance.

        Args:
            provider: Provider name (ollama, openai, anthropic, google)
            **kwargs: Provider-specific configuration

        Returns:
            BaseLLMProvider instance
        """
        providers = {
            "ollama": OllamaProvider,
            "openai": OpenAIProvider,
            "anthropic": AnthropicProvider,
            "google": GoogleProvider
        }

        if provider not in providers:
            raise ValueError(f"Unknown provider: {provider}")

        return providers[provider](**kwargs)

    @staticmethod
    def test_provider(provider: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Test a provider configuration.

        Args:
            provider: Provider name
            config: Provider configuration

        Returns:
            Test result with status and message
        """
        try:
            instance = LLMProviderFactory.create(provider, **config)
            if instance is None:
                return {"success": False, "message": "Failed to create provider instance"}

            is_available = instance.is_available()
            model_info = instance.get_model_info()

            if is_available:
                return {
                    "success": True,
                    "message": "Connection successful",
                    "model_info": model_info
                }
            else:
                return {
                    "success": False,
                    "message": "Provider not available or model not found"
                }

        except Exception as e:
            return {
                "success": False,
                "message": str(e)
            }
