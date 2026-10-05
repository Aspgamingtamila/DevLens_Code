"""AI Provider Factory."""

from typing import Optional
from .base import AIProvider
from .mock_provider import MockAIProvider
from .gemini_provider import GeminiAIProvider
from ..config import settings


def get_ai_provider(provider_name: Optional[str] = None) -> AIProvider:
    """Returns requested or default AI provider instance."""
    name = (provider_name or settings.DEFAULT_AI_PROVIDER).lower()
    if name == "gemini":
        return GeminiAIProvider()
    # Default to hermetic mock provider
    return MockAIProvider()
