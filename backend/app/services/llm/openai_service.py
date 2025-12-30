"""OpenAI LLM service with structured output enforcement (Directive 03)."""
from typing import Type, TypeVar
from pydantic import BaseModel
from openai import AsyncOpenAI
from app.core.config import settings
from app.services.llm.base import BaseLLMService, TokenUsage
from app.services.llm.output_parser import OutputParser, InvalidOutputError

T = TypeVar("T", bound=BaseModel)


class OpenAIService(BaseLLMService):
    """OpenAI LLM service using response_format for structured output.

    Uses OpenAI's native JSON mode to enforce schema compliance (Directive 03).
    """

    # Pricing per 1M tokens (as of 2025)
    PRICING = {
        "gpt-4-turbo-preview": {"input": 10.00, "output": 30.00},
        "gpt-4": {"input": 30.00, "output": 60.00},
        "gpt-3.5-turbo": {"input": 0.50, "output": 1.50},
    }

    def __init__(self, model: str = "gpt-4-turbo-preview"):
        """Initialize OpenAI service.

        Args:
            model: OpenAI model name
        """
        super().__init__(model)
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    async def generate_structured(
        self,
        prompt: str,
        schema: Type[T],
        system_message: str | None = None,
    ) -> tuple[T, TokenUsage]:
        """Generate structured output using OpenAI's response_format.

        Uses JSON mode to enforce structured output (Directive 03).

        Args:
            prompt: User prompt
            schema: Pydantic model to enforce
            system_message: Optional system message

        Returns:
            Tuple of (validated output, token usage)

        Raises:
            InvalidOutputError: If output doesn't match schema
        """
        # Prepare messages
        messages = []
        if system_message:
            messages.append({"role": "system", "content": system_message})

        # Add schema requirements to prompt
        # Get field descriptions for a clearer prompt
        json_schema = schema.model_json_schema()
        properties = json_schema.get("properties", {})
        required = json_schema.get("required", [])

        field_descriptions = []
        for field_name, field_info in properties.items():
            desc = field_info.get("description", "")
            field_type = field_info.get("type", "string")
            is_required = " (required)" if field_name in required else ""
            field_descriptions.append(f'  "{field_name}": {field_type}{is_required} - {desc}')

        schema_prompt = (
            f"{prompt}\n\n"
            f"CRITICAL: Return ONLY valid JSON with these fields:\n"
            f"{chr(10).join(field_descriptions)}\n\n"
            f"DO NOT include schema descriptions. Return actual data values.\n"
            f"DO NOT wrap in markdown code fences. Return raw JSON only."
        )
        messages.append({"role": "user", "content": schema_prompt})

        # Call OpenAI with JSON mode (Directive 03)
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            response_format={"type": "json_object"},  # Enforce JSON output
            temperature=0.7,
        )

        # Extract response
        raw_output = response.choices[0].message.content

        # Parse and validate (will raise InvalidOutputError if malformed)
        parsed_output = OutputParser.parse_structured_output(raw_output, schema)

        # Track token usage (Directive 09)
        token_usage = TokenUsage(
            prompt_tokens=response.usage.prompt_tokens,
            completion_tokens=response.usage.completion_tokens,
            total_tokens=response.usage.total_tokens,
            model=self.model,
            provider="openai",
        )
        token_usage.cost_usd = self.calculate_cost(token_usage)
        self.last_token_usage = token_usage

        return parsed_output, token_usage

    def calculate_cost(self, token_usage: TokenUsage) -> float:
        """Calculate cost for OpenAI API call.

        Args:
            token_usage: Token usage info

        Returns:
            Cost in USD
        """
        pricing = self.PRICING.get(self.model, self.PRICING["gpt-4-turbo-preview"])

        input_cost = (token_usage.prompt_tokens / 1_000_000) * pricing["input"]
        output_cost = (token_usage.completion_tokens / 1_000_000) * pricing["output"]

        return input_cost + output_cost
