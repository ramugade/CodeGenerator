"""Anthropic LLM service with structured output via tool use (Directive 03)."""
from typing import Type, TypeVar
from pydantic import BaseModel
from anthropic import AsyncAnthropic
from app.core.config import settings
from app.services.llm.base import BaseLLMService, TokenUsage
from app.services.llm.output_parser import OutputParser

T = TypeVar("T", bound=BaseModel)


class AnthropicService(BaseLLMService):
    """Anthropic LLM service using tool use for structured output.

    Uses Anthropic's tool calling feature to enforce schema (Directive 03).
    """

    # Pricing per 1M tokens (as of 2025)
    PRICING = {
        "claude-3-opus-20240229": {"input": 15.00, "output": 75.00},
        "claude-3-sonnet-20240229": {"input": 3.00, "output": 15.00},
        "claude-3-haiku-20240307": {"input": 0.25, "output": 1.25},
    }

    def __init__(self, model: str = "claude-3-sonnet-20240229"):
        """Initialize Anthropic service.

        Args:
            model: Anthropic model name
        """
        super().__init__(model)
        self.client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)

    async def generate_structured(
        self,
        prompt: str,
        schema: Type[T],
        system_message: str | None = None,
    ) -> tuple[T, TokenUsage]:
        """Generate structured output using Anthropic's tool use.

        Uses tool calling to enforce structured output (Directive 03).

        Args:
            prompt: User prompt
            schema: Pydantic model to enforce
            system_message: Optional system message

        Returns:
            Tuple of (validated output, token usage)

        Raises:
            InvalidOutputError: If output doesn't match schema
        """
        # Convert Pydantic schema to Anthropic tool definition
        tool_definition = {
            "name": "submit_result",
            "description": f"Submit the result matching the schema: {schema.__name__}",
            "input_schema": schema.model_json_schema(),
        }

        # Prepare system message
        system = system_message or "You are a helpful AI assistant."

        # Call Anthropic with tool use
        response = await self.client.messages.create(
            model=self.model,
            max_tokens=4096,
            system=system,
            messages=[{"role": "user", "content": prompt}],
            tools=[tool_definition],
            tool_choice={"type": "tool", "name": "submit_result"},  # Force tool use
        )

        # Extract tool use response
        tool_use_block = None
        for block in response.content:
            if block.type == "tool_use" and block.name == "submit_result":
                tool_use_block = block
                break

        if not tool_use_block:
            raise ValueError("Anthropic did not use the tool as expected")

        # Parse and validate
        import json
        raw_output = json.dumps(tool_use_block.input)
        parsed_output = OutputParser.parse_structured_output(raw_output, schema)

        # Track token usage (Directive 09)
        token_usage = TokenUsage(
            prompt_tokens=response.usage.input_tokens,
            completion_tokens=response.usage.output_tokens,
            total_tokens=response.usage.input_tokens + response.usage.output_tokens,
            model=self.model,
            provider="anthropic",
        )
        token_usage.cost_usd = self.calculate_cost(token_usage)
        self.last_token_usage = token_usage

        return parsed_output, token_usage

    def calculate_cost(self, token_usage: TokenUsage) -> float:
        """Calculate cost for Anthropic API call.

        Args:
            token_usage: Token usage info

        Returns:
            Cost in USD
        """
        pricing = self.PRICING.get(
            self.model, self.PRICING["claude-3-sonnet-20240229"]
        )

        input_cost = (token_usage.prompt_tokens / 1_000_000) * pricing["input"]
        output_cost = (token_usage.completion_tokens / 1_000_000) * pricing["output"]

        return input_cost + output_cost
