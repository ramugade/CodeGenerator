"""LLM service factory for provider switching."""
from typing import Literal
from app.services.llm.base import BaseLLMService
from app.services.llm.openai_service import OpenAIService
from app.services.llm.anthropic_service import AnthropicService

LLMProvider = Literal["openai", "anthropic"]


class LLMFactory:
    """Factory for creating LLM service instances."""

    @staticmethod
    def create(
        provider: LLMProvider = "openai",
        model: str | None = None,
    ) -> BaseLLMService:
        """Create an LLM service instance.

        Args:
            provider: LLM provider ("openai" or "anthropic")
            model: Optional specific model name. If None, uses default for provider.

        Returns:
            LLM service instance

        Raises:
            ValueError: If provider is unknown
        """
        if provider == "openai":
            default_model = "gpt-4-turbo-preview"
            return OpenAIService(model=model or default_model)
        elif provider == "anthropic":
            default_model = "claude-3-sonnet-20240229"
            return AnthropicService(model=model or default_model)
        else:
            raise ValueError(
                f"Unknown LLM provider: {provider}. Must be 'openai' or 'anthropic'"
            )
