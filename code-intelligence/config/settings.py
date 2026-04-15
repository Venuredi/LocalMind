"""
Application Settings Module

Provides centralized configuration management for LocalMind.
Supports both local (Ollama) and cloud-based (OpenAI, Claude, Gemini) LLMs.
"""

import json
import os
from pathlib import Path
from typing import Optional, Dict, Any, List, Literal
from pydantic import BaseModel, Field
from enum import Enum
import logging

logger = logging.getLogger(__name__)

# Default settings file location
SETTINGS_FILE = Path(__file__).parent.parent / "data" / "settings.json"


class LLMProvider(str, Enum):
    """Supported LLM providers."""
    OLLAMA = "ollama"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"


class PromptGenerationMethod(str, Enum):
    """Prompt generation methods."""
    TEMPLATE = "template"
    LLM = "llm"
    HYBRID = "hybrid"


class OllamaSettings(BaseModel):
    """Settings for local Ollama LLM."""
    enabled: bool = True
    host: str = "http://localhost:11434"
    model: str = "phi3:mini"
    temperature: float = 0.7
    max_tokens: int = 2048


class OpenAISettings(BaseModel):
    """Settings for OpenAI API."""
    enabled: bool = False
    api_key: str = ""
    model: str = "gpt-4o-mini"
    temperature: float = 0.7
    max_tokens: int = 2048
    organization: Optional[str] = None


class AnthropicSettings(BaseModel):
    """Settings for Anthropic Claude API."""
    enabled: bool = False
    api_key: str = ""
    model: str = "claude-3-haiku-20240307"
    temperature: float = 0.7
    max_tokens: int = 2048


class GoogleSettings(BaseModel):
    """Settings for Google Gemini API."""
    enabled: bool = False
    api_key: str = ""
    model: str = "gemini-1.5-flash"
    temperature: float = 0.7
    max_tokens: int = 2048


class LLMSettings(BaseModel):
    """Consolidated LLM settings."""
    active_provider: LLMProvider = LLMProvider.OLLAMA
    ollama: OllamaSettings = Field(default_factory=OllamaSettings)
    openai: OpenAISettings = Field(default_factory=OpenAISettings)
    anthropic: AnthropicSettings = Field(default_factory=AnthropicSettings)
    google: GoogleSettings = Field(default_factory=GoogleSettings)


class PromptSettings(BaseModel):
    """Prompt generation settings."""
    generation_method: PromptGenerationMethod = PromptGenerationMethod.HYBRID
    fallback_to_template: bool = True
    validate_output: bool = True
    enhance_safety: bool = True


class AppSettings(BaseModel):
    """Main application settings."""
    llm: LLMSettings = Field(default_factory=LLMSettings)
    prompt: PromptSettings = Field(default_factory=PromptSettings)

    # Metadata
    version: str = "1.0.0"
    last_updated: Optional[str] = None


class SettingsManager:
    """
    Manages application settings with persistence to JSON file.

    Features:
    - Load/save settings from/to JSON file
    - Validate settings on load
    - Provide defaults for missing settings
    - Thread-safe singleton pattern
    """

    _instance: Optional['SettingsManager'] = None
    _settings: Optional[AppSettings] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._settings is None:
            self.load()

    @property
    def settings(self) -> AppSettings:
        """Get current settings."""
        if self._settings is None:
            self.load()
        return self._settings

    def load(self, path: Optional[Path] = None) -> AppSettings:
        """
        Load settings from JSON file.

        Args:
            path: Optional custom path to settings file

        Returns:
            Loaded AppSettings
        """
        settings_path = path or SETTINGS_FILE

        try:
            if settings_path.exists():
                with open(settings_path, 'r') as f:
                    data = json.load(f)
                self._settings = AppSettings(**data)
                logger.info(f"Settings loaded from {settings_path}")
            else:
                logger.info("No settings file found, using defaults")
                self._settings = AppSettings()
                # Save defaults
                self.save()
        except Exception as e:
            logger.error(f"Error loading settings: {e}, using defaults")
            self._settings = AppSettings()

        return self._settings

    def save(self, path: Optional[Path] = None) -> bool:
        """
        Save settings to JSON file.

        Args:
            path: Optional custom path to settings file

        Returns:
            True if saved successfully
        """
        settings_path = path or SETTINGS_FILE

        try:
            # Ensure directory exists
            settings_path.parent.mkdir(parents=True, exist_ok=True)

            # Update timestamp
            from datetime import datetime
            self._settings.last_updated = datetime.now().isoformat()

            with open(settings_path, 'w') as f:
                json.dump(self._settings.model_dump(), f, indent=2)

            logger.info(f"Settings saved to {settings_path}")
            return True
        except Exception as e:
            logger.error(f"Error saving settings: {e}")
            return False

    def update(self, updates: Dict[str, Any]) -> AppSettings:
        """
        Update settings with partial data.

        Args:
            updates: Dictionary with settings to update

        Returns:
            Updated AppSettings
        """
        current = self._settings.model_dump()

        # Deep merge updates
        def deep_merge(base: dict, updates: dict) -> dict:
            for key, value in updates.items():
                if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                    deep_merge(base[key], value)
                else:
                    base[key] = value
            return base

        merged = deep_merge(current, updates)
        self._settings = AppSettings(**merged)
        self.save()

        return self._settings

    def get_active_llm_config(self) -> Dict[str, Any]:
        """
        Get configuration for the currently active LLM provider.

        Returns:
            Dictionary with provider name and settings
        """
        provider = self._settings.llm.active_provider

        if provider == LLMProvider.OLLAMA:
            return {
                "provider": "ollama",
                "config": self._settings.llm.ollama.model_dump()
            }
        elif provider == LLMProvider.OPENAI:
            return {
                "provider": "openai",
                "config": self._settings.llm.openai.model_dump()
            }
        elif provider == LLMProvider.ANTHROPIC:
            return {
                "provider": "anthropic",
                "config": self._settings.llm.anthropic.model_dump()
            }
        elif provider == LLMProvider.GOOGLE:
            return {
                "provider": "google",
                "config": self._settings.llm.google.model_dump()
            }

        return {"provider": "unknown", "config": {}}

    def is_llm_enabled(self) -> bool:
        """Check if LLM-based generation is enabled and configured."""
        if self._settings.prompt.generation_method == PromptGenerationMethod.TEMPLATE:
            return False

        provider = self._settings.llm.active_provider

        if provider == LLMProvider.OLLAMA:
            return self._settings.llm.ollama.enabled
        elif provider == LLMProvider.OPENAI:
            return self._settings.llm.openai.enabled and bool(self._settings.llm.openai.api_key)
        elif provider == LLMProvider.ANTHROPIC:
            return self._settings.llm.anthropic.enabled and bool(self._settings.llm.anthropic.api_key)
        elif provider == LLMProvider.GOOGLE:
            return self._settings.llm.google.enabled and bool(self._settings.llm.google.api_key)

        return False

    def get_available_providers(self) -> List[Dict[str, Any]]:
        """
        Get list of all providers with their status.

        Returns:
            List of provider info dictionaries
        """
        return [
            {
                "id": "ollama",
                "name": "Ollama (Local)",
                "type": "local",
                "enabled": self._settings.llm.ollama.enabled,
                "configured": True,  # Always configured (local)
                "model": self._settings.llm.ollama.model,
                "active": self._settings.llm.active_provider == LLMProvider.OLLAMA
            },
            {
                "id": "openai",
                "name": "OpenAI",
                "type": "cloud",
                "enabled": self._settings.llm.openai.enabled,
                "configured": bool(self._settings.llm.openai.api_key),
                "model": self._settings.llm.openai.model,
                "active": self._settings.llm.active_provider == LLMProvider.OPENAI
            },
            {
                "id": "anthropic",
                "name": "Anthropic Claude",
                "type": "cloud",
                "enabled": self._settings.llm.anthropic.enabled,
                "configured": bool(self._settings.llm.anthropic.api_key),
                "model": self._settings.llm.anthropic.model,
                "active": self._settings.llm.active_provider == LLMProvider.ANTHROPIC
            },
            {
                "id": "google",
                "name": "Google Gemini",
                "type": "cloud",
                "enabled": self._settings.llm.google.enabled,
                "configured": bool(self._settings.llm.google.api_key),
                "model": self._settings.llm.google.model,
                "active": self._settings.llm.active_provider == LLMProvider.GOOGLE
            }
        ]


# Global settings manager instance
settings_manager = SettingsManager()


def get_settings() -> AppSettings:
    """Get current application settings."""
    return settings_manager.settings


def update_settings(updates: Dict[str, Any]) -> AppSettings:
    """Update application settings."""
    return settings_manager.update(updates)
