"""Base LLM service interface."""
from abc import ABC, abstractmethod
from typing import TypeVar, Type
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class TokenUsage(BaseModel):
    """Token usage for a single LLM call (Directive 09)."""

    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    model: str
    provider: str
    cost_usd: float = 0.0  # Calculated based on provider pricing


class BaseLLMService(ABC):
    """Abstract base class for LLM services.

    Supports both OpenAI and Anthropic providers.
    All services must enforce structured output (Directive 03).
    """

    def __init__(self, model: str):
        """Initialize LLM service.

        Args:
            model: Model name (e.g., "gpt-4", "claude-3-opus-20240229")
        """
        self.model = model
        self.last_token_usage: TokenUsage | None = None

    @abstractmethod
    async def generate_structured(
        self,
        prompt: str,
        schema: Type[T],
        system_message: str | None = None,
    ) -> tuple[T, TokenUsage]:
        """Generate structured output matching the given Pydantic schema.

        This is the core method that enforces Directive 03 (structured output).

        Args:
            prompt: User prompt
            schema: Pydantic model schema to enforce
            system_message: Optional system message

        Returns:
            Tuple of (validated output, token usage)

        Raises:
            InvalidOutputError: If LLM doesn't follow schema
        """
        pass

    @abstractmethod
    def calculate_cost(self, token_usage: TokenUsage) -> float:
        """Calculate cost in USD for the token usage.

        Each provider has different pricing.

        Args:
            token_usage: Token usage info

        Returns:
            Cost in USD
        """
        pass

    def get_last_token_usage(self) -> TokenUsage | None:
        """Get token usage from last call (Directive 09)."""
        return self.last_token_usage
